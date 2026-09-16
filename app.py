import streamlit as st
from supabase import create_client, Client


# ==============================
# SUPABASE CONNECTION
# ==============================

SUPABASE_URL = st.secrets.get("SUPABASE_URL", "")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")


@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)


try:
    supabase = init_supabase()
except Exception:
    supabase = None


# ==============================
# FETCH DATABASE DATA
# ==============================

@st.cache_data(ttl=600)
def fetch_data():

    if not supabase:
        return [], []

    meds = (
        supabase
        .table("pnf_medicines")
        .select("*")
        .order("generic_name")
        .execute()
    )

    dx = (
        supabase
        .table("doh_diagnoses")
        .select("*")
        .order("icd10_code")
        .execute()
    )

    return meds.data or [], dx.data or []


pnf_meds, diagnoses = fetch_data()


# ==============================
# SOAP GENERATOR
# ==============================

def generate_soap(data):


    SOAP = f"""

# Clinical SOAP Note


**Patient Name:** {data['name']}

**Age / Sex:** {data['age']}-year-old {data['sex']}

**Date / Time:** {data['date']}

**Setting:** Primary Care Outpatient Clinic



# S – Subjective


## Chief Complaint (CC)

"{data['chief']}"


## History of Present Illness (HPI)


The patient is a {data['age']}-year-old {data['sex']} who presents with a 
{data['onset']} history of {data['chief'].lower()}.


- **Onset:** {data['onset_detail']}

- **Location/Radiation:** {data['location']}

- **Duration:** {data['duration']}

- **Character:** {data['character']}

- **Aggravating Factors:** {data['aggravating']}

- **Alleviating Factors:** {data['alleviating']}

- **Severity / Associated Symptoms:**
{data['associated']}



## Past Medical History

{data['pmh']}



## Family History

{data['family']}



## Personal & Social History

{data['social']}



## Review of Systems


**General:**

{data['ros_general']}


**HEENT:**

{data['ros_heent']}


**Respiratory:**

{data['ros_resp']}


**Cardiovascular:**

{data['ros_cardio']}




# O – Objective


## Vital Signs


- **BP:** {data['bp']}

- **Heart Rate:** {data['hr']} bpm

- **Respiratory Rate:** {data['rr']} breaths/min

- **Temperature:** {data['temp']} °C

- **SpO₂:** {data['spo2']} %

- **BMI:** {data['bmi']}



## General Appearance


{data['general']}



## HEENT


{data['heent']}



# Bates Physical Examination – Chest & Lungs


## Inspection

{data['inspection']}


## Palpation

{data['palpation']}


## Percussion

{data['percussion']}


## Auscultation

{data['auscultation']}



# Cardiovascular


{data['cardio']}




# A – Assessment


## Primary Diagnosis


{data['primary_dx']}



## Clinical Rationale


{data['rationale']}



## Differential Diagnoses


{data['differentials']}



## Comorbid Conditions


{data['comorbid']}




# P – Plan



## 1. Diagnostics / Workup


{data['diagnostics']}



## 2. Therapeutics / Pharmacotherapy


{data['medications']}



## 3. Non-Pharmacological & Patient Education


{data['education']}



## 4. Safety Netting & Follow-up


{data['followup']}



**Attending Physician:** {data['physician']}

**Intern:** {data['intern']}

**Clerk:** {data['clerk']}


"""

    return SOAP



# ==============================
# APP UI
# ==============================


st.set_page_config(
    page_title="Bates SOAP Generator",
    layout="wide"
)


st.title("🩺 Bates SOAP & PhilHealth Konsulta Clinical App")



col1,col2 = st.columns(2)



with col1:


    st.header("Patient Information")


    name = st.text_input(
        "Patient Name",
        "Juan Dela Cruz"
    )


    age = st.number_input(
        "Age",
        value=42
    )


    sex = st.selectbox(
        "Sex",
        ["Male","Female"]
    )


    date = st.text_input(
        "Date / Time",
        "September 16, 2026 | 10:15 AM"
    )



    st.header("Subjective")


    chief = st.text_input(
        "Chief Complaint",
        "Cough for 4 days and fever for 2 days"
    )


    onset = st.text_input(
        "Duration",
        "4-day"
    )


    onset_detail = st.text_area(
        "Onset",
        "Started as dry cough progressing to productive cough"
    )


    location = st.text_input(
        "Location/Radiation",
        "Retrosternal discomfort during coughing"
    )


    duration = st.text_input(
        "Duration Pattern",
        "Constant, worse at night"
    )


    character = st.text_area(
        "Character",
        "Productive cough with yellowish sputum"
    )


    aggravating = st.text_input(
        "Aggravating Factors",
        "Cold air, lying flat"
    )


    alleviating = st.text_input(
        "Alleviating Factors",
        "Warm water"
    )


    associated = st.text_area(
        "Associated Symptoms",
        "Fever, chills, nasal congestion, fatigue"
    )



    pmh = st.text_area(
        "Past Medical History",
        "Essential Hypertension controlled with Amlodipine"
    )


    family = st.text_area(
        "Family History",
        "Father with hypertension and diabetes"
    )


    social = st.text_area(
        "Personal/Social History",
        "Non-smoker, occasional alcohol intake"
    )



with col2:


    st.header("Objective")


    bp = st.text_input("BP","124/80 mmHg")

    hr = st.number_input("HR",84)

    rr = st.number_input("RR",18)

    temp = st.number_input("Temperature",37.8)

    spo2 = st.number_input("SpO2",98)


    bmi = st.text_input(
        "BMI",
        "24.2 kg/m²"
    )



    general = st.text_area(
        "General Appearance",
        "Alert, oriented, no respiratory distress"
    )


    heent = st.text_area(
        "HEENT Examination",
        "Mild pharyngeal erythema with clear nasal discharge"
    )



    inspection = st.text_area(
        "Inspection",
        "Symmetrical chest expansion, no retractions"
    )


    palpation = st.text_area(
        "Palpation",
        "Normal tactile fremitus, trachea midline"
    )


    percussion = st.text_area(
        "Percussion",
        "Resonant lung fields"
    )


    auscultation = st.text_area(
        "Auscultation",
        "Coarse crackles and rhonchi on right lower lung field"
    )


    cardio = st.text_area(
        "Cardiovascular",
        "Normal S1 and S2, no murmurs"
    )



st.header("Assessment")


primary_dx = st.text_input(
    "Primary Diagnosis",
    "Acute Bronchitis (J20.9)"
)


rationale = st.text_area(
    "Clinical Rationale",
    "Acute productive cough following viral symptoms with normal oxygen saturation"
)


differentials = st.text_area(
    "Differential Diagnoses",
    "CAP, AURI, Pulmonary Tuberculosis"
)


comorbid = st.text_input(
    "Comorbid Conditions",
    "Essential Hypertension (I10)"
)



st.header("Plan")


diagnostics = st.text_area(
    "Diagnostics",
    "Chest X-ray if symptoms worsen"
)


medications = st.text_area(
    "Medications",
    "Paracetamol 500mg PRN; Continue Amlodipine"
)


education = st.text_area(
    "Patient Education",
    "Hydration, rest, avoid smoke exposure"
)


followup = st.text_area(
    "Follow-up",
    "Return after 3-5 days or seek ER for warning signs"
)


physician = st.text_input(
    "Attending Physician"
)

intern = st.text_input(
    "Intern"
)

clerk = st.text_input(
    "Clerk"
)



if st.button(
    "Generate SOAP Report",
    type="primary"
):


    data = {

        "name":name,
        "age":age,
        "sex":sex,
        "date":date,

        "chief":chief,
        "onset":onset,
        "onset_detail":onset_detail,
        "location":location,
        "duration":duration,
        "character":character,
        "aggravating":aggravating,
        "alleviating":alleviating,
        "associated":associated,

        "pmh":pmh,
        "family":family,
        "social":social,

        "ros_general":"Positive for fever and chills",
        "ros_heent":"Positive for congestion",
        "ros_resp":"Positive for cough and sputum",
        "ros_cardio":"Negative for chest pain",

        "bp":bp,
        "hr":hr,
        "rr":rr,
        "temp":temp,
        "spo2":spo2,
        "bmi":bmi,

        "general":general,
        "heent":heent,

        "inspection":inspection,
        "palpation":palpation,
        "percussion":percussion,
        "auscultation":auscultation,

        "cardio":cardio,

        "primary_dx":primary_dx,
        "rationale":rationale,
        "differentials":differentials,
        "comorbid":comorbid,

        "diagnostics":diagnostics,
        "medications":medications,
        "education":education,
        "followup":followup,

        "physician":physician,
        "intern":intern,
        "clerk":clerk

    }


    result = generate_soap(data)


    st.markdown(result)


    st.download_button(
        "Download SOAP Report",
        result,
        file_name="SOAP_Report.txt"
    )
