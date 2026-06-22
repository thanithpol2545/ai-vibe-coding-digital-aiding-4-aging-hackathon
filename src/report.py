import os
import io
from datetime import datetime
import config
from fpdf import FPDF


class AssessmentReport:
    def __init__(self):
        self.pdf = FPDF(orientation="P", unit="mm", format="A4")
        self.pdf.add_font("THSarabun", "", os.path.join(config.BASE_DIR, "assets", "fonts", "THSarabunNew.ttf"), uni=True)

    def _header(self):
        self.pdf.set_font("THSarabun", "", 16)
        self.pdf.cell(0, 10, "Hand Assessment AI - Report", align="C", new_x="LMARGIN", new_y="NEXT")
        self.pdf.set_font("THSarabun", "", 10)
        self.pdf.cell(0, 6, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", align="C", new_x="LMARGIN", new_y="NEXT")
        self.pdf.line(10, self.pdf.get_y(), 200, self.pdf.get_y())
        self.pdf.ln(4)

    def _section(self, title):
        self.pdf.set_font("THSarabun", "", 13)
        self.pdf.set_fill_color(230, 230, 240)
        self.pdf.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT", fill=True)
        self.pdf.ln(2)

    def _metric_row(self, label, left_val, right_val, unit=""):
        self.pdf.set_font("THSarabun", "", 11)
        self.pdf.cell(70, 7, label, border=1)
        self.pdf.cell(30, 7, f"L: {left_val}{unit}", border=1, align="C")
        self.pdf.cell(30, 7, f"R: {right_val}{unit}", border=1, align="C")
        diff = abs(left_val - right_val)
        denom = max(abs(left_val), abs(right_val), 1e-10)
        asym = diff / denom
        self.pdf.cell(30, 7, f"Asym: {asym:.2f}", border=1, align="C", new_x="LMARGIN", new_y="NEXT")

    def generate(self, result, patient_name="", patient_age=0, patient_notes="") -> bytes:
        self.pdf.add_page()
        self._header()

        if patient_name:
            self.pdf.set_font("THSarabun", "", 11)
            self.pdf.cell(0, 7, f"Patient: {patient_name}", new_x="LMARGIN", new_y="NEXT")
            if patient_age:
                self.pdf.cell(0, 7, f"Age: {patient_age}", new_x="LMARGIN", new_y="NEXT")
            if patient_notes:
                self.pdf.multi_cell(0, 6, f"Notes: {patient_notes}")
            self.pdf.ln(3)

        self._section("Classification Result")
        self.pdf.set_font("THSarabun", "", 11)
        self.pdf.cell(0, 7, f"Dominant Hand: {result.dominant_hand}  (Confidence: {result.confidence*100:.0f}%)", new_x="LMARGIN", new_y="NEXT")
        self.pdf.cell(0, 7, f"Learned Non-Use Risk: {result.learned_non_use_risk*100:.1f}%", new_x="LMARGIN", new_y="NEXT")
        risk = "HIGH" if result.is_learned_non_use else ("MODERATE" if result.learned_non_use_risk > 0.25 else "LOW")
        self.pdf.cell(0, 7, f"LNU Status: {risk}", new_x="LMARGIN", new_y="NEXT")
        self.pdf.multi_cell(0, 6, f"Details: {result.details}")
        self.pdf.ln(3)

        self._section("Symmetry Analysis")
        self.pdf.set_font("THSarabun", "", 11)
        sym = result.left_features.symmetry_index
        self.pdf.cell(0, 7, f"Symmetry Index: {sym:.3f}  (0 = perfect symmetry)", new_x="LMARGIN", new_y="NEXT")
        self.pdf.ln(2)

        self._section("Left vs Right Hand Comparison")
        lf = result.left_features
        rf = result.right_features
        self.pdf.set_font("THSarabun", "", 10)
        self.pdf.cell(70, 7, "Metric", border=1)
        self.pdf.cell(30, 7, "Left", border=1, align="C")
        self.pdf.cell(30, 7, "Right", border=1, align="C")
        self.pdf.cell(30, 7, "Asymmetry", border=1, align="C")
        self.pdf.ln()

        for label, lv, rv in [
            ("Tapping Speed (taps/s)", lf.tapping_speed, rf.tapping_speed),
            ("Tap Regularity", lf.tap_regularity, rf.tap_regularity),
            ("Path Efficiency", lf.path_efficiency, rf.path_efficiency),
            ("Movement Smoothness", lf.movement_smoothness, rf.movement_smoothness),
            ("Range of Motion", lf.range_of_motion, rf.range_of_motion),
            ("Tremor Index", lf.tremor_index, rf.tremor_index),
        ]:
            self._metric_row(label, round(lv, 3), round(rv, 3))

        self.pdf.ln(4)
        self._section("Interpretation Guide")
        self.pdf.set_font("THSarabun", "", 10)
        guide = (
            "- Learned Non-Use: pathological disuse of one hand despite physical capability.\n"
            "- Natural Dominance: normal asymmetry where the dominant hand performs ~10-20% better.\n"
            "- LNU Risk > 45%: suggests possible Learned Non-Use, recommend clinical referral.\n"
            "- Asymmetry > 0.30: moderate asymmetry, monitor for improvement.\n"
            "- Tremor Index > 3.0: elevated tremor activity, may indicate neurological involvement."
        )
        self.pdf.multi_cell(0, 6, guide)

        return bytes(self.pdf.output())
