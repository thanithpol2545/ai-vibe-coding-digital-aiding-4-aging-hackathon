import streamlit as st
import cv2, numpy as np, tempfile, os, sys, time, json

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config
from hand_tracker import HandTracker
from features import FeatureExtractor
from classifier import DominanceClassifier
import guidance as _g
import session
from report import AssessmentReport
from logger import setup_logger

logger = setup_logger("app")

st.set_page_config(page_title="Hand Assessment AI", page_icon="✋", layout="wide")

st.markdown("""
<style>
.stApp { background: #f0f2f6; }
.stButton>button { width: 100%; }
.metric-card {
    background: white; border-radius: 10px; padding: 15px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin: 5px 0;
}
.risk-high { color: #dc3545; font-weight: bold; }
.risk-moderate { color: #ffc107; font-weight: bold; }
.risk-low { color: #28a745; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("🖐️ ระบบวิเคราะห์มือสำหรับผู้สูงอายุ")
st.markdown("วิเคราะห์การเคลื่อนไหวมือ เพื่อตรวจสอบความถนัดและภาวะ Learned Non-Use")

# ─── Sidebar ───
st.sidebar.header("👤 ข้อมูลผู้ป่วย")
patient_name = st.sidebar.text_input("ชื่อ-นามสกุล", value=st.session_state.get("patient_name", ""), key="patient_name_input")
patient_age = st.sidebar.number_input("อายุ", min_value=0, max_value=120, value=st.session_state.get("patient_age", 65), key="patient_age_input")
patient_notes = st.sidebar.text_area("บันทึกเพิ่มเติม", value=st.session_state.get("patient_notes", ""), key="patient_notes_input", max_chars=200)
st.sidebar.markdown("---")

st.sidebar.header("⚙️ ตั้งค่า")
input_mode = st.sidebar.radio("โหมดอินพุต", ["Upload Video", "Webcam (Live)"], format_func=lambda x: "📂 อัปโหลดวิดีโอ" if x == "Upload Video" else "📷 กล้องเว็บแคม")
test_type = st.sidebar.selectbox("แบบทดสอบ", ["Finger Tapping", "Reach-to-Target", "Combined"], format_func=lambda x: {"Finger Tapping": "👆 แตะนิ้ว", "Reach-to-Target": "🏃 เอื้อมแขน", "Combined": "🔄 ผสมทั้งสอง"}[x])
duration = st.sidebar.slider("ระยะเวลาบันทึก (วินาที)", 5, 30, 10)

# ─── Initialize ───
@st.cache_resource
def get_tracker():
    return HandTracker()

@st.cache_resource
def get_classifier():
    return DominanceClassifier()

tracker = get_tracker()
classifier = get_classifier()

# ─── Session State ───
for key in ["recording", "result", "left_feats", "right_feats", "frame_count", "cam_state", "saved_session_id"]:
    if key not in st.session_state:
        st.session_state[key] = None if key in ["result", "saved_session_id"] else (
            {} if key in ["left_feats", "right_feats"] else (
                False if key == "recording" else ("preview" if key == "cam_state" else 0)
            )
        )


def process_video_progressive(video_path: str, progress_bar, frame_placeholder, status_text, test_type="Finger Tapping"):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_data = []
    frame_idx = 0
    step = 3

    left_feats_total = config.HandFeatures(hand="Left")
    right_feats_total = config.HandFeatures(hand="Right")
    result_preview = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        display = frame_rgb.copy()

        if frame_idx % step == 0:
            hands = tracker.process_frame(frame)
            if hands:
                frame_data.append({
                    "frame": frame_idx,
                    "time_sec": frame_idx / fps,
                    "hands": hands,
                })

                for h in hands:
                    for lm in h["landmarks"]:
                        cx, cy = int(lm[0]), int(lm[1])
                        cv2.circle(display, (cx, cy), 4, (0, 255, 0), -1)
                    color = (0, 0, 255) if h["hand"] == "Left" else (255, 0, 0)
                    cv2.putText(display, h["hand"], (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        if len(frame_data) >= 3:
            data = {"fps": fps, "frames": frame_data}
            extractor = FeatureExtractor(data)
            left_feats_total = extractor.extract_all("Left", "tapping")
            right_feats_total = extractor.extract_all("Right", "tapping")
            sym_index = extractor.compute_symmetry_index(left_feats_total, right_feats_total)
            left_feats_total.symmetry_index = sym_index
            right_feats_total.symmetry_index = sym_index

            result_preview = classifier.classify(left_feats_total, right_feats_total)

            hand_label = f"Dom:{result_preview.dominant_hand} LNU:{result_preview.learned_non_use_risk:.0%}"
            risk_color = (255, 0, 0) if result_preview.is_learned_non_use else (0, 200, 0)
            cv2.putText(display, hand_label, (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, risk_color, 2)

        progress = min(frame_idx / total, 1.0) if total > 0 else 0
        progress_bar.progress(progress)
        status_text.text(f"Processing frame {frame_idx}/{total} ({progress*100:.0f}%) — Detections: {len(frame_data)}")
        frame_placeholder.image(display, channels="RGB")
        frame_idx += 1

    cap.release()

    if not frame_data:
        return None

    data = {"fps": fps, "frames": frame_data}
    extractor = FeatureExtractor(data)
    left_feats = extractor.extract_all("Left", "tapping")
    right_feats = extractor.extract_all("Right", "tapping")
    sym_index = extractor.compute_symmetry_index(left_feats, right_feats)

    if test_type in ["Reach-to-Target", "Combined"]:
        left_reach = extractor.extract_all("Left", "reach")
        right_reach = extractor.extract_all("Right", "reach")
        for attr in ["reach_time", "path_efficiency", "movement_smoothness"]:
            setattr(left_feats, attr, getattr(left_reach, attr, 0.0))
            setattr(right_feats, attr, getattr(right_reach, attr, 0.0))

    left_feats.symmetry_index = sym_index
    right_feats.symmetry_index = sym_index

    result = classifier.classify(left_feats, right_feats)
    return result


def display_metrics(result: config.ClassificationResult):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("🖐️ มือที่ถนัด", result.dominant_hand, f"มั่นใจ {result.confidence*100:.0f}%")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        risk_class = "risk-high" if result.is_learned_non_use else ("risk-moderate" if result.learned_non_use_risk > 0.25 else "risk-low")
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<span class="{risk_class}">⚠️ ความเสี่ยง Learned Non-Use: {result.learned_non_use_risk*100:.1f}%</span>', unsafe_allow_html=True)
        if result.is_learned_non_use:
            st.error("🔴 เสี่ยงสูง — แนะนำให้พบแพทย์")
        elif result.learned_non_use_risk > 0.25:
            st.warning("🟡 ความไม่สมดุลปานกลาง — ควรติดตาม")
        else:
            st.success("✅ ปกติ — รูปแบบการเคลื่อนไหวสมมาตรดี")
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("**📋 รายละเอียด**")
        st.write(result.details)
        st.markdown('</div>', unsafe_allow_html=True)

    st.subheader("📊 เปรียบเทียบคุณลักษณะ")
    cols = st.columns(2)
    with cols[0]:
        st.markdown("**👈 มือซ้าย**")
        lf = result.left_features
        st.json({
            "ความเร็วในการแตะ": f"{lf.tapping_speed:.2f} ครั้ง/วินาที",
            "ความสม่ำเสมอ": f"{lf.tap_regularity:.2f}",
            "ความเร็วสูงสุด": f"{lf.avg_peak_velocity:.4f}",
            "ประสิทธิภาพเส้นทาง": f"{lf.path_efficiency:.2f}",
            "ความลื่นไหล": f"{lf.movement_smoothness:.2f}",
            "ROM": f"{lf.range_of_motion:.3f}",
            "ดัชนีอาการสั่น": f"{lf.tremor_index:.3f}",
        })
    with cols[1]:
        st.markdown("**👉 มือขวา**")
        rf = result.right_features
        st.json({
            "ความเร็วในการแตะ": f"{rf.tapping_speed:.2f} ครั้ง/วินาที",
            "ความสม่ำเสมอ": f"{rf.tap_regularity:.2f}",
            "ความเร็วสูงสุด": f"{rf.avg_peak_velocity:.4f}",
            "ประสิทธิภาพเส้นทาง": f"{rf.path_efficiency:.2f}",
            "ความลื่นไหล": f"{rf.movement_smoothness:.2f}",
            "ROM": f"{rf.range_of_motion:.3f}",
            "ดัชนีอาการสั่น": f"{rf.tremor_index:.3f}",
        })

    st.subheader("🔄 วิเคราะห์ความสมมาตร")
    st.metric("ดัชนีความสมมาตร", f"{result.left_features.symmetry_index:.3f}",
              help="0=สมมาตรสมบูรณ์, ยิ่งสูง=ยิ่งไม่สมมาตร")


def _show_save_buttons(result):
    col_save, col_pdf = st.columns(2)
    with col_save:
        pname = st.session_state.get("patient_name_input", "").strip() or "ไม่ระบุชื่อ"
        if st.button("💾 บันทึกผลการประเมิน", type="primary", use_container_width=True):
            sid = session.save_session(
                patient_name=pname,
                patient_age=int(st.session_state.get("patient_age_input", 0)),
                patient_notes=st.session_state.get("patient_notes_input", ""),
                result=result,
            )
            st.session_state.saved_session_id = sid
            st.success(f"✅ บันทึกแล้ว (ID: {sid})")
    with col_pdf:
        if st.button("📄 ดาวน์โหลด PDF Report", type="secondary", use_container_width=True):
            try:
                report = AssessmentReport()
                pdf_bytes = report.generate(
                    result,
                    patient_name=st.session_state.get("patient_name_input", ""),
                    patient_age=int(st.session_state.get("patient_age_input", 0)),
                    patient_notes=st.session_state.get("patient_notes_input", ""),
                )
                st.download_button(
                    label="📥 คลิกเพื่อดาวน์โหลด PDF",
                    data=pdf_bytes,
                    file_name=f"hand_assessment_{result.dominant_hand}_{int(result.learned_non_use_risk*100)}pct.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดในการสร้าง PDF: {e}")
                logger.error("PDF generation failed: %s", e)


# ─── Main Content ───
if input_mode == "Upload Video":
    uploaded_file = st.file_uploader(
        "📂 อัปโหลดวิดีโอการเคลื่อนไหวมือ",
        type=["mp4", "avi", "mov", "webm"],
        help="บันทึกวิดีโอการแตะนิ้วหรือเอื้อมแขน แล้วอัปโหลดที่นี่"
    )
    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        st.markdown("### 🔄 กำลังประมวลผล")
        st.caption("แสดงวิดีโอพร้อมวิเคราะห์แบบ Real-time")
        progress_bar = st.progress(0)
        status_text = st.empty()
        frame_placeholder = st.empty()

        result = process_video_progressive(tmp_path, progress_bar, frame_placeholder, status_text, test_type)

        os.unlink(tmp_path)

        if result:
            progress_bar.progress(1.0)
            status_text.success("✅ วิเคราะห์เสร็จสิ้น!")
            display_metrics(result)
            _show_save_buttons(result)
        else:
            status_text.error("⚠️ ตรวจไม่พบมือ — ลองใช้วิดีโออื่น")
            st.warning("ตรวจสอบให้แน่ใจว่ามือทั้งสองข้างอยู่ในเฟรมและมีการเคลื่อนไหว")

        if st.button("🔄 วิเคราะห์วิดีโออื่น"):
            st.rerun()

else:
    st.info("📷 **โหมดกล้องเว็บแคม** — วางมือในกรอบ ระบบจะเริ่มอัตโนมัติ")

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    if not cap.isOpened():
        st.error("❌ ไม่สามารถเปิดกล้องได้ — ตรวจสอบการเชื่อมต่อกล้องเว็บแคม")
        st.stop()
    FRAME_WINDOW = st.empty()
    status_text = st.empty()

    state = st.session_state.get("cam_state", "preview")
    hands_ready = 0
    all_frames = {"fps": 30, "total_frames": 0, "frames": []}
    webcam_step = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if state == "preview":
            display = _g.draw_setup_overlay(frame.copy(), test_type)
            hands = tracker.process_frame(frame)
            in_zone = False

            if hands:
                h, w = frame.shape[:2]
                zx1, zy1 = int(w * 0.08), int(h * 0.18)
                zx2, zy2 = int(w * 0.92), int(h * 0.52)
                for hh in hands:
                    wx, wy = int(hh["landmarks"][0][0]), int(hh["landmarks"][0][1])
                    if zx1 < wx < zx2 and zy1 < wy < zy2:
                        in_zone = True
                        break
                if in_zone:
                    hands_ready += 1
                    _g._txt(display, f"✅ มืออยู่ในตำแหน่ง ({hands_ready})", 10, h - 80, (0, 255, 0), 0.5, 1)
                if hands_ready >= 8 and in_zone:
                    state = "countdown"
                    st.session_state.cam_state = "countdown"
                    continue
            else:
                hands_ready = 0

            FRAME_WINDOW.image(display, channels="BGR")
            status_text.info("🔄 รอให้มืออยู่ในกรอบสีเขียว...")
            time.sleep(0.03)

        elif state == "countdown":
            cam_fail = False
            for i in range(3, 0, -1):
                if cam_fail:
                    break
                t0 = time.time()
                while time.time() - t0 < 0.7:
                    ret, frame = cap.read()
                    if not ret:
                        cam_fail = True
                        break
                    _g.draw_countdown(frame, i)
                    FRAME_WINDOW.image(frame, channels="BGR")
            if cam_fail:
                break
            state = "recording"
            st.session_state.cam_state = "recording"
            st.session_state.rec_start = time.time()
            st.session_state.frame_count = 0
            continue

        elif state == "recording":
            start_time = st.session_state.rec_start
            while (time.time() - start_time) < duration:
                ret, frame = cap.read()
                if not ret:
                    break
                webcam_step += 1
                hands_detected = False

                if webcam_step % 2 == 0:
                    hands = tracker.process_frame(frame)
                    if hands:
                        hands_detected = True
                        all_frames["frames"].append({
                            "frame": st.session_state.frame_count,
                            "time_sec": time.time() - start_time,
                            "hands": hands,
                        })
                        for hh in hands:
                            for lm in hh["landmarks"]:
                                cx, cy = int(lm[0]), int(lm[1])
                                cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)
                            clr = (255, 0, 0) if hh["hand"] == "Left" else (0, 0, 255)
                            cv2.putText(frame, hh["hand"], (10, 65),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, clr, 2)

                elapsed = int(time.time() - start_time)
                _g.draw_recording_overlay(frame, hands_detected, test_type, elapsed, duration)
                st.session_state.frame_count += 1
                FRAME_WINDOW.image(frame, channels="BGR")
                status_text.info("🔴 กำลังบันทึก...")

            all_frames["total_frames"] = st.session_state.frame_count
            if len(all_frames["frames"]) > 5:
                feat_type = "tapping" if test_type in ["Finger Tapping", "Combined"] else "reach"
                ex = FeatureExtractor(all_frames)
                lf = ex.extract_all("Left", feat_type)
                rf = ex.extract_all("Right", feat_type)
                if test_type in ["Reach-to-Target", "Combined"]:
                    lf_reach = ex.extract_all("Left", "reach")
                    rf_reach = ex.extract_all("Right", "reach")
                    for attr in ["reach_time", "path_efficiency", "movement_smoothness"]:
                        setattr(lf, attr, getattr(lf_reach, attr, 0.0))
                        setattr(rf, attr, getattr(rf_reach, attr, 0.0))
                sym = ex.compute_symmetry_index(lf, rf)
                lf.symmetry_index = sym
                rf.symmetry_index = sym
                st.session_state.result = classifier.classify(lf, rf)
            state = "done"
            st.session_state.cam_state = "done"
            st.balloons()
            continue

        elif state == "done":
            _g._txt(frame, "✅ เสร็จสิ้น!", frame.shape[1] // 2 - 80, frame.shape[0] // 2, (0, 255, 0), 1, 3)
            FRAME_WINDOW.image(frame, channels="BGR")
            status_text.success("✅ บันทึกเสร็จสิ้น!")
            break

    cap.release()

    if st.session_state.get("cam_state") == "done" and st.session_state.result:
        display_metrics(st.session_state.result)
        _show_save_buttons(st.session_state.result)
        if st.button("🔄 ทดสอบใหม่"):
            for k in ["result", "cam_state", "saved_session_id"]:
                st.session_state[k] = None if k in ["result", "saved_session_id"] else "preview"
            st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 🏥 ข้อมูลทางคลินิก")
st.sidebar.info(
    "เครื่องมือนี้วิเคราะห์ **ความเร็ว ความแม่นยำ และคุณภาพการเคลื่อนไหว** "
    "เพื่อแยกแยะระหว่างความถนัดธรรมชาติกับภาวะ Learned Non-Use "
    "ออกแบบมาเพื่อคัดกรองผู้สูงอายุ"
)
st.sidebar.markdown("### 📝 เคล็ดลับ")
st.sidebar.info(
    "**เพื่อผลลัพธ์ที่ดีที่สุด:**\n"
    "- 🪑 นั่งหลังตรง มือระดับอก\n"
    "- 📏 ห่างกล้องประมาณ 50 ซม.\n"
    "- 🖐️ หันฝ่ามือเข้าหากล้อง\n"
    "- ☀️ แสงสว่างเพียงพอ = ตรวจจับดีขึ้น\n"
    "- ⌚ ถอดนาฬิกา แหวน ถุงมือ\n"
    "- 👆 แตะนิ้วให้ใหญ่และเร็ว\n"
    "- ซ้าย/ขวาบนจอ = ตรงข้ามกับมือจริง"
)
st.sidebar.markdown("### 📚 เอกสารอ้างอิง")
st.sidebar.markdown(
    "- Amprimo et al. (2023) — MediaPipe hand tracking for neurorehab\n"
    "- Kwakkel et al. (2015) — Learned Non-Use after stroke\n"
    "- Taub et al. (2006) — CIMT protocol\n"
    "- Balasubramanian et al. (2015) — SPARC smoothness metric"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📋 ประวัติการประเมิน")
if st.sidebar.button("🔄 โหลดประวัติ"):
    st.rerun()
history = session.list_sessions(10)
if history:
    for h in history:
        ts = h["timestamp"][:16] if h["timestamp"] else "?"
        dominant = h.get("dominant_hand", "?")
        risk = h.get("lnu_risk", 0)
        label = f"{h['patient_name']} | {dominant} | {risk*100:.0f}%"
        if st.sidebar.button(label, key=f"hist_{h['session_id']}", use_container_width=True):
            loaded = session.load_session(h["session_id"])
            if loaded:
                st.session_state.loaded_session = loaded
                st.rerun()
else:
    st.sidebar.caption("ยังไม่มีประวัติ")

if st.session_state.get("loaded_session"):
    with st.sidebar.expander("📌 ดูผลล่าสุด"):
        ls = st.session_state.loaded_session
        st.json(ls.get("result", {}))
