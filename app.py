import streamlit as st
from supabase import create_client, Client

# 1. Fetch Supabase Credentials from Streamlit Secrets
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")

@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    supabase = init_supabase()
except Exception as e:
    supabase = None

# 2. SOAP Generator Logic
def generate_soap(chief_complaint, onset_days, quality, symptoms, bp, hr, rr, temp, spo2, inspection, auscultation, location, dx_codes):
    subj = f"Patient presents with a {onset_days}-day history of {chief_complaint.lower()}"
    if quality:
        subj += f" characterized as {quality.lower()}"
    if symptoms:
        subj += f", accompanied by {', '.join(symptoms).lower()}"
    subj += "."

    obj = f"Vital Signs: BP {bp} mmHg, HR {hr} bpm, RR {rr}/min, Temp {temp}°C, SpO2 {spo2}%."
    chest_findings = []
    if inspection:
        chest_findings.append(f"Inspection: {inspection.lower()}")
    if auscultation:
        chest_findings.append(f"Auscultation reveals {', '.join(auscultation).lower()}")

    if chest_findings:
        obj += f" Chest & Lungs: {'. '.join(chest_findings)}"
        if location:
            obj += f" localized to the {location.lower()}"
        obj += "."

    assessment = f"Diagnoses (DOH/ICD-10): {'; '.join(dx_codes)}" if dx_codes else "Assessment Pending."

    return subj, obj, assessment

# 3. Streamlit Interface Configuration
st.set_page_config(page_title="Bates SOAP & PhilHealth Konsulta", layout="wide")
st.title("🩺 Bates SOAP & PhilHealth Konsulta Clinical App")

@st.cache_data(ttl=600)
def fetch_doh_data():
    if not supabase:
        return [], []
    meds_res = supabase.table("pnf_medicines").select("*").order("generic_name").execute()
    dx_res = supabase.table("doh_diagnoses").select("*").order("icd10_code").execute()
    return meds_res.data or [], dx_res.data or []

pnf_meds, doh_diagnoses = fetch_doh_data()

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Subjective (History)")
    chief_complaint = st.text_input("Chief Complaint", "Cough")
    onset_days = st.number_input("Onset (Days)", min_value=1, value=3)
    quality = st.selectbox("Quality", ["Productive with yellowish phlegm", "Dry, hacking", "Paroxysmal"])
    symptoms = st.multiselect("Associated Symptoms", ["Fever", "Shortness of breath", "Chest pain", "Chills"])

    st.subheader("Objective (Bates Physical Exam - Chest & Lungs)")
    v_col1, v_col2, v_col3 = st.columns(3)
    with v_col1:
        bp = st.text_input("BP (mmHg)", "120/80")
        hr = st.number_input("HR (bpm)", value=88)
    with v_col2:
        rr = st.number_input("RR (/min)", value=20)
        temp = st.number_input("Temp (°C)", value=38.2)
    with v_col3:
        spo2 = st.number_input("SpO2 (%)", value=97)

    inspection = st.selectbox("Inspection Findings", ["Normal symmetrical expansion", "Asymmetrical expansion", "Use of accessory muscles"])
    auscultation = st.multiselect("Auscultation Findings", ["Clear breath sounds", "Crackles (Rales)", "Wheezing", "Rhonchi"])
    location = st.text_input("Location Modifier", "Right lower lung field")

with col2:
    st.subheader("Assessment (DOH PhilHealth Konsulta ICD-10)")
    dx_options = [f"{d['icd10_code']} - {d['description']}" for d in doh_diagnoses] if doh_diagnoses else ["I10 - Essential Hypertension", "J06.9 - Acute Upper Respiratory Infection"]
    selected_diagnoses = st.multiselect("Select Primary Care Diagnoses", dx_options)

    st.subheader("Plan (DOH PNF Prescription Helper)")
    med_options = [f"{m['generic_name']} ({m['formulation']}) [{m['category']}]" for m in pnf_meds] if pnf_meds else ["Paracetamol (500 mg Tablet)", "Amoxicillin (500 mg Capsule)"]
    selected_rx = st.multiselect("Prescribe PNF Essential Medicines", med_options)

    st.markdown("---")
    if st.button("Generate PhilHealth Konsulta Clinical Summary", type="primary"):
        subj_narrative, obj_narrative, assessment_narrative = generate_soap(
            chief_complaint, onset_days, quality, symptoms,
            bp, hr, rr, temp, spo2, inspection, auscultation, location, selected_diagnoses
        )

        st.markdown("### Subjective")
        st.info(subj_narrative)

        st.markdown("### Objective")
        st.success(obj_narrative)

        st.markdown("### Assessment")
        st.warning(assessment_narrative)

        st.markdown("### Plan (Prescriptions)")
        if selected_rx:
            for rx in selected_rx:
                st.write(f"- 💊 {rx}")
        else:
            st.write("No medications prescribed.")

        full_export = f"SUBJECTIVE:\n{subj_narrative}\n\nOBJECTIVE:\n{obj_narrative}\n\nASSESSMENT:\n{assessment_narrative}\n\nPLAN:\n" + "\n".join([f"- {r}" for r in selected_rx])
        st.text_area("PhilHealth Konsulta EMR Export Text", full_export, height=220)
