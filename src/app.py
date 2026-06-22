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
import voice_guide as vg

logger = setup_logger("app")

st.set_page_config(page_title="Hand Assessment AI", page_icon="✋", layout="wide")

st.markdown("""
<style>
/* ── Elderly-friendly UI ── */
html { font-size: 18px; }
.stApp { background: #f0f2f6; }

/* Bigger all text */
p, li, .stMarkdown, .stText, .stCaption { font-size: 1.1rem !important; }
h1 { font-size: 2.2rem !important; }
h2 { font-size: 1.8rem !important; }
h3 { font-size: 1.5rem !important; }

/* Bigger buttons — min 56px height */
.stButton>button {
    width: 100%;
    min-height: 56px !important;
    font-size: 1.2rem !important;
    font-weight: 600 !important;
    padding: 12px 24px !important;
    border-radius: 14px !important;
}
div[data-testid="stBaseButton-primary"] button {
    min-height: 60px !important;
    font-size: 1.3rem !important;
}

/* Bigger sidebar inputs */
.sidebar .stTextInput input, .sidebar .stNumberInput input, .sidebar .stTextArea textarea {
    font-size: 1.1rem !important;
    min-height: 48px !important;
}
.sidebar .stSelectbox div[data-baseweb="select"] > div {
    min-height: 48px !important;
    font-size: 1.1rem !important;
}
.sidebar .stSlider label { font-size: 1.1rem !important; }
.sidebar .stCheckbox label { font-size: 1.1rem !important; }

/* Bigger radio buttons */
div[data-testid="stRadio"] label {
    font-size: 1.1rem !important;
    padding: 8px 0 !important;
}

/* File uploader bigger */
div[data-testid="stFileUploader"] section {
    padding: 24px !important;
    font-size: 1.1rem !important;
}

/* Metric cards */
.metric-card {
    background: white; border-radius: 16px; padding: 24px;
    box-shadow: 0 3px 8px rgba(0,0,0,0.12); margin: 10px 0;
}
.metric-card label { font-size: 1.1rem !important; }
.metric-card .stMetric label { font-size: 1rem !important; }
.metric-card .stMetric div[data-testid="metric-value"] {
    font-size: 1.8rem !important;
    font-weight: 700 !important;
}

/* Risk badges */
.risk-high { color: #dc3545; font-weight: bold; font-size: 1.2rem; }
.risk-moderate { color: #cc7700; font-weight: bold; font-size: 1.2rem; }
.risk-low { color: #1a8a3a; font-weight: bold; font-size: 1.2rem; }

/* Success/warning/error fonts */
.stAlert { font-size: 1.1rem !important; padding: 16px !important; }

/* Expander */
.streamlit-expanderHeader { font-size: 1.1rem !important; font-weight: 600 !important; }

/* Sidebar header */
.sidebar .stSidebar h2, .sidebar .stSidebar h3 { font-size: 1.3rem !important; }

/* Bigger info boxes */
.stInfo, .stSuccess, .stWarning, .stError { font-size: 1.1rem !important; padding: 16px !important; }

/* Column gap wider */
div[data-testid="column"] { gap: 1.5rem !important; }

/* Bigger expander content */
.streamlit-expanderContent p { font-size: 1.1rem !important; line-height: 1.7 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="font-size:2.2rem;text-align:center;">🖐️ ระบบวิเคราะห์มือสำหรับผู้สูงอายุ</h1>', unsafe_allow_html=True)
st.markdown('<p style="font-size:1.2rem;text-align:center;color:#444;">วิเคราะห์การเคลื่อนไหวมือ เพื่อตรวจสอบความถนัดและภาวะ Learned Non-Use</p>', unsafe_allow_html=True)

# ─── Sidebar ───
st.sidebar.markdown("## 👤 ข้อมูลผู้ป่วย")
patient_name = st.sidebar.text_input("ชื่อ-นามสกุล", value=st.session_state.get("patient_name", ""), key="patient_name_input", placeholder="เช่น สมชาย ใจดี")
patient_age = st.sidebar.number_input("อายุ (ปี)", min_value=0, max_value=120, value=st.session_state.get("patient_age", 65), key="patient_age_input")
patient_notes = st.sidebar.text_area("บันทึกเพิ่มเติม", value=st.session_state.get("patient_notes", ""), key="patient_notes_input", max_chars=200, placeholder="อาการหรือข้อสังเกต")
st.sidebar.markdown("---")

st.sidebar.markdown("## ⚙️ ตั้งค่า")
input_mode = st.sidebar.radio("เลือกวิธีใช้งาน", ["Upload Video", "Webcam (Live)"], format_func=lambda x: "📂 อัปโหลดวิดีโอ" if x == "Upload Video" else "📷 ใช้กล้องเว็บแคม")
test_type = st.sidebar.selectbox("แบบทดสอบ", ["Finger Tapping", "Reach-to-Target", "Combined"], format_func=lambda x: {"Finger Tapping": "👆 แตะนิ้ว", "Reach-to-Target": "🏃 เอื้อมแขน", "Combined": "🔄 ผสมทั้งสอง"}[x])
duration = st.sidebar.slider("⏱ ระยะเวลาบันทึก (วินาที)", 5, 30, 10)
voice_enabled = st.sidebar.checkbox("🔊 เปิดคำแนะนำด้วยเสียง", value=True)

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
for key in ["recording", "result", "left_feats", "right_feats", "frame_count", "cam_state", "saved_session_id", "voice_played"]:
    if key not in st.session_state:
        st.session_state[key] = None if key in ["result", "saved_session_id"] else (
            {} if key in ["left_feats", "right_feats", "voice_played"] else (
                False if key == "recording" else ("preview" if key == "cam_state" else 0)
            )
        )


def _play_cue(test_type: str, phase: str):
    if not st.session_state.get("voice_enabled", True):
        return ""
    key = f"{test_type}_{phase}"
    played = st.session_state.voice_played
    if played.get(key):
        return ""
    played[key] = True
    return vg.get_cue_audio(test_type, phase)


def _play_countdown(num: int):
    if not st.session_state.get("voice_enabled", True):
        return ""
    key = f"countdown_{num}"
    played = st.session_state.voice_played
    if played.get(key):
        return ""
    played[key] = True
    return vg.get_countdown_audio(num)


def _play_common(phase: str):
    if not st.session_state.get("voice_enabled", True):
        return ""
    key = f"common_{phase}"
    played = st.session_state.voice_played
    if played.get(key):
        return ""
    played[key] = True
    return vg.get_common_audio(phase)


def _draw_pose(frame, pose, arm_angles):
    if not pose:
        return
    POSE_CONNECTIONS = [
        (config.LEFT_SHOULDER, config.LEFT_ELBOW),
        (config.LEFT_ELBOW, config.LEFT_WRIST),
        (config.RIGHT_SHOULDER, config.RIGHT_ELBOW),
        (config.RIGHT_ELBOW, config.RIGHT_WRIST),
    ]
    colors = {"Left": (255, 100, 100), "Right": (100, 100, 255)}
    for side_name, (sh, el, wr) in {
        "Left": (config.LEFT_SHOULDER, config.LEFT_ELBOW, config.LEFT_WRIST),
        "Right": (config.RIGHT_SHOULDER, config.RIGHT_ELBOW, config.RIGHT_WRIST),
    }.items():
        if sh not in pose or el not in pose or wr not in pose:
            continue
        clr = colors.get(side_name, (200, 200, 200))
        sh_pt = (int(pose[sh]["x"]), int(pose[sh]["y"]))
        el_pt = (int(pose[el]["x"]), int(pose[el]["y"]))
        wr_pt = (int(pose[wr]["x"]), int(pose[wr]["y"]))
        for pt in [sh_pt, el_pt, wr_pt]:
            cv2.circle(frame, pt, 6, clr, -1)
            cv2.circle(frame, pt, 8, (255, 255, 255), 2)
        cv2.line(frame, sh_pt, el_pt, clr, 3)
        cv2.line(frame, el_pt, wr_pt, clr, 3)
    if arm_angles:
        for side in ["left", "right"]:
            key = f"{side}_elbow_angle"
            if key in arm_angles:
                lbl = f"{side.capitalize()} Elbow: {arm_angles[key]:.0f}°"
                clr = colors.get(side.capitalize(), (200, 200, 200))
                cv2.putText(frame, lbl, (10, 120 + (30 if side == "right" else 0)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, clr, 2)


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
            out = tracker.process_frame(frame)
            hands = out.get("hands", [])
            pose = out.get("pose")
            arm_angles = tracker._compute_arm_angles(pose) if pose else {}
            if hands or pose:
                entry = {
                    "frame": frame_idx,
                    "time_sec": frame_idx / fps,
                    "hands": hands,
                }
                if arm_angles:
                    entry["arm_angles"] = arm_angles
                frame_data.append(entry)

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
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:1.5rem;font-weight:700;">🖐️ มือที่ถนัด: {result.dominant_hand}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:1.1rem;color:#555;">มั่นใจ {result.confidence*100:.0f}%</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        risk_class = "risk-high" if result.is_learned_non_use else ("risk-moderate" if result.learned_non_use_risk > 0.25 else "risk-low")
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<span class="{risk_class}" style="font-size:1.3rem;">⚠️ ความเสี่ยง Learned Non-Use: {result.learned_non_use_risk*100:.1f}%</span>', unsafe_allow_html=True)
        if result.is_learned_non_use:
            st.error("🔴 เสี่ยงสูง — แนะนำให้พบแพทย์")
        elif result.learned_non_use_risk > 0.25:
            st.warning("🟡 ความไม่สมดุลปานกลาง — ควรติดตาม")
        else:
            st.success("✅ ปกติ — รูปแบบการเคลื่อนไหวสมมาตรดี")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("## 📊 เปรียบเทียบคุณลักษณะ")
    cols = st.columns(2)
    with cols[0]:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 👈 มือซ้าย")
        lf = result.left_features
        features = [
            ("ความเร็วในการแตะ", f"{lf.tapping_speed:.2f} ครั้ง/วินาที"),
            ("ความสม่ำเสมอ", f"{lf.tap_regularity:.2f}"),
            ("ความเร็วสูงสุด", f"{lf.avg_peak_velocity:.4f}"),
            ("ประสิทธิภาพเส้นทาง", f"{lf.path_efficiency:.2f}"),
            ("ความลื่นไหล", f"{lf.movement_smoothness:.2f}"),
            ("ROM", f"{lf.range_of_motion:.3f}"),
            ("ดัชนีอาการสั่น", f"{lf.tremor_index:.3f}"),
        ]
        for label, val in features:
            st.markdown(f'<div style="font-size:1rem;padding:4px 0;"><strong>{label}:</strong> {val}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with cols[1]:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 👉 มือขวา")
        rf = result.right_features
        features = [
            ("ความเร็วในการแตะ", f"{rf.tapping_speed:.2f} ครั้ง/วินาที"),
            ("ความสม่ำเสมอ", f"{rf.tap_regularity:.2f}"),
            ("ความเร็วสูงสุด", f"{rf.avg_peak_velocity:.4f}"),
            ("ประสิทธิภาพเส้นทาง", f"{rf.path_efficiency:.2f}"),
            ("ความลื่นไหล", f"{rf.movement_smoothness:.2f}"),
            ("ROM", f"{rf.range_of_motion:.3f}"),
            ("ดัชนีอาการสั่น", f"{rf.tremor_index:.3f}"),
        ]
        for label, val in features:
            st.markdown(f'<div style="font-size:1rem;padding:4px 0;"><strong>{label}:</strong> {val}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("## 🔄 วิเคราะห์ความสมมาตร")
    sym_val = result.left_features.symmetry_index
    sym_desc = "สมมาตรดี" if sym_val < 0.15 else "ไม่สมมาตรปานกลาง" if sym_val < 0.35 else "ไม่สมมาตรมาก"
    st.markdown(f'<div class="metric-card" style="text-align:center;"><span style="font-size:1.3rem;">📊 ดัชนีความสมมาตร: <strong>{sym_val:.3f}</strong> ({sym_desc})</span><br><span style="color:#888;">0=สมมาตรสมบูรณ์, ยิ่งสูง=ยิ่งไม่สมมาตร</span></div>', unsafe_allow_html=True)


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
            st.success(f"✅ บันทึกแล้ว (รหัส: {sid})")
    with col_pdf:
        if st.button("📄 ดาวน์โหลด PDF รายงาน", type="secondary", use_container_width=True):
            try:
                report = AssessmentReport()
                pdf_bytes = report.generate(
                    result,
                    patient_name=st.session_state.get("patient_name_input", ""),
                    patient_age=int(st.session_state.get("patient_age_input", 0)),
                    patient_notes=st.session_state.get("patient_notes_input", ""),
                )
                st.download_button(
                    label="📥 คลิกดาวน์โหลด PDF",
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
        help="เลือกไฟล์วิดีโอที่บันทึกการแตะนิ้วหรือเอื้อมแขน"
    )
    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        st.markdown("## 🔄 กำลังประมวลผล")
        st.markdown("แสดงวิดีโอพร้อมวิเคราะห์แบบเรียลไทม์")
        progress_bar = st.progress(0)
        status_text = st.empty()
        frame_placeholder = st.empty()

        result = process_video_progressive(tmp_path, progress_bar, frame_placeholder, status_text, test_type)

        os.unlink(tmp_path)

        if result:
            progress_bar.progress(1.0)
            status_text.success("✅ วิเคราะห์เสร็จสิ้น!")
            complete_audio = _play_common("complete")
            if complete_audio:
                st.markdown(complete_audio, unsafe_allow_html=True)
            display_metrics(result)
            _show_save_buttons(result)
        else:
            status_text.error("⚠️ ตรวจไม่พบมือ — ลองใช้วิดีโออื่น")
            st.warning("ตรวจสอบให้แน่ใจว่ามือทั้งสองข้างอยู่ในเฟรม")

        st.button("🔄 วิเคราะห์วิดีโออื่น", type="secondary", use_container_width=True, on_click=lambda: st.rerun())

else:
    st.markdown('<div style="background:#e8f4fd;padding:20px;border-radius:16px;font-size:1.2rem;text-align:center;">📷 <strong>โหมดกล้องเว็บแคม</strong> — วางมือในกรอบ ระบบจะเริ่มบันทึกอัตโนมัติ</div>', unsafe_allow_html=True)

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
            setup_audio = _play_cue(test_type, "setup")
            if setup_audio:
                st.markdown(setup_audio, unsafe_allow_html=True)
            out = tracker.process_frame(frame)
            hands = out.get("hands", [])
            pose = out.get("pose")
            arm_angles = tracker._compute_arm_angles(pose) if pose else {}
            _draw_pose(display, pose, arm_angles)
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
            status_text.markdown('<div style="background:#d4edda;padding:12px 20px;border-radius:14px;font-size:1.2rem;text-align:center;">🔄 กรุณาวางมือในกรอบสีเขียว...</div>', unsafe_allow_html=True)
            time.sleep(0.03)

        elif state == "countdown":
            _play_common("ready")
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
                countdown_audio = _play_countdown(i)
                if countdown_audio:
                    st.markdown(countdown_audio, unsafe_allow_html=True)
            if cam_fail:
                break
            state = "recording"
            st.session_state.cam_state = "recording"
            st.session_state.rec_start = time.time()
            st.session_state.frame_count = 0
            continue

        elif state == "recording":
            start_time = st.session_state.rec_start
            go_audio = _play_cue(test_type, "go")
            if go_audio:
                st.markdown(go_audio, unsafe_allow_html=True)
            last_voice_zone = "go"
            while (time.time() - start_time) < duration:
                ret, frame = cap.read()
                if not ret:
                    break
                webcam_step += 1
                hands_detected = False

                if webcam_step % 2 == 0:
                    out = tracker.process_frame(frame)
                    hands = out.get("hands", [])
                    pose = out.get("pose")
                    arm_angles = tracker._compute_arm_angles(pose) if pose else {}
                    _draw_pose(frame, pose, arm_angles)
                    if hands:
                        hands_detected = True
                        entry = {
                            "frame": st.session_state.frame_count,
                            "time_sec": time.time() - start_time,
                            "hands": hands,
                        }
                        if arm_angles:
                            entry["arm_angles"] = arm_angles
                        all_frames["frames"].append(entry)
                        for hh in hands:
                            for lm in hh["landmarks"]:
                                cx, cy = int(lm[0]), int(lm[1])
                                cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)
                            clr = (255, 0, 0) if hh["hand"] == "Left" else (0, 0, 255)
                            cv2.putText(frame, hh["hand"], (10, 65),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, clr, 2)

                elapsed = int(time.time() - start_time)
                remaining = duration - elapsed
                if remaining == 5 and last_voice_zone != "steady":
                    audio = _play_cue(test_type, "steady")
                    if audio:
                        st.markdown(audio, unsafe_allow_html=True)
                    last_voice_zone = "steady"
                elif remaining == 2 and last_voice_zone != "almost":
                    audio = _play_cue(test_type, "almost")
                    if audio:
                        st.markdown(audio, unsafe_allow_html=True)
                    last_voice_zone = "almost"
                _g.draw_recording_overlay(frame, hands_detected, test_type, elapsed, duration)
                st.session_state.frame_count += 1
                FRAME_WINDOW.image(frame, channels="BGR")
                status_text.markdown('<div style="background:#f8d7da;padding:10px 18px;border-radius:14px;font-size:1.2rem;text-align:center;">🔴 กำลังบันทึก... ({:.0f}%)</div>'.format(100 * elapsed / duration), unsafe_allow_html=True)

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
            done_audio = _play_cue(test_type, "done")
            if done_audio:
                st.markdown(done_audio, unsafe_allow_html=True)
            state = "done"
            st.session_state.cam_state = "done"
            st.balloons()
            continue

        elif state == "done":
            _g._txt(frame, "✅ เสร็จสิ้น!", frame.shape[1] // 2 - 120, frame.shape[0] // 2, (0, 255, 0), 1.2, 4)
            FRAME_WINDOW.image(frame, channels="BGR")
            status_text.markdown('<div style="background:#d4edda;padding:14px 22px;border-radius:14px;font-size:1.3rem;text-align:center;font-weight:700;">✅ บันทึกเสร็จสิ้น!</div>', unsafe_allow_html=True)
            break

    cap.release()

    if st.session_state.get("cam_state") == "done" and st.session_state.result:
        display_metrics(st.session_state.result)
        _show_save_buttons(st.session_state.result)
        st.button("🔄 ทดสอบใหม่", type="secondary", use_container_width=True, on_click=lambda: [
            st.session_state.update({k: None if k in ["result", "saved_session_id"] else "preview"})
            for k in ["result", "cam_state", "saved_session_id"]
        ] or st.rerun())

st.sidebar.markdown("---")
with st.sidebar.expander(f"📖 วิธีทำ {test_type}", expanded=True):
    guide_data = _g.EXERCISE_GUIDES.get(test_type, _g.EXERCISE_GUIDES["Finger Tapping"])
    for i, (emoji, text) in enumerate(guide_data["prep"]):
        st.markdown(f"**ขั้นตอนที่ {i+1}:** {emoji} {text}")
    st.markdown("---")
    st.markdown(f"**⏱ ระยะเวลา:** {duration} วินาที")
    st.markdown(f"**📍 ท่า:** {guide_data['position']}")
    if voice_enabled:
        st.markdown("🔊 **เปิดเสียงแนะนำ**")
    if guide_data["hand_pos"] == "center":
        st.image("assets/fonts/finger_tapping_guide.png", use_container_width=True)
    elif guide_data["hand_pos"] == "full_body":
        st.image("assets/fonts/reach_target_guide.png", use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.markdown("## 🏥 ข้อมูลทางคลินิก")
st.sidebar.info(
    "เครื่องมือนี้วิเคราะห์ **ความเร็ว ความแม่นยำ และคุณภาพการเคลื่อนไหว** "
    "เพื่อแยกแยะระหว่างความถนัดธรรมชาติกับภาวะ Learned Non-Use "
    "ออกแบบมาเพื่อคัดกรองผู้สูงอายุ"
)
st.sidebar.markdown("## 📝 เคล็ดลับ")
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
st.sidebar.markdown("## 📚 เอกสารอ้างอิง")
st.sidebar.markdown(
    "- Amprimo et al. (2023) — MediaPipe hand tracking for neurorehab\n"
    "- Kwakkel et al. (2015) — Learned Non-Use after stroke\n"
    "- Taub et al. (2006) — CIMT protocol\n"
    "- Balasubramanian et al. (2015) — SPARC smoothness metric"
)

st.sidebar.markdown("---")
st.sidebar.markdown("## 📋 ประวัติการประเมิน")
if st.sidebar.button("🔄 โหลดประวัติ", use_container_width=True):
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
