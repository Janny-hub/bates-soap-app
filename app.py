import streamlit as st
from supabase import create_client, Client


# =====================================
# PAGE CONFIGURATION
# =====================================

st.set_page_config(
    page_title="Bates SOAP Clinical Generator",
    layout="wide"
)


# =====================================
# SUPABASE CONNECTION
# =====================================

SUPABASE_URL = st.secrets.get("SUPABASE_URL", "")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")


@st.cache_resource
def init_supabase():

    if SUPABASE_URL and SUPABASE_KEY:
        return create_client(
            SUPABASE_URL,
            SUPABASE_KEY
        )

    return None


supabase = init_supabase()



# =====================================
# FETCH DOH / PNF DATABASE
# =====================================

@st.cache_data(ttl=600)
def fetch_database():

    if not supabase:
        return [], []


    medicines = (
        supabase
        .table("pnf_medicines")
        .select("*")
        .order("generic_name")
        .execute()
    )


    diagnoses = (
        supabase
        .table("doh_diagnoses")
        .select("*")
        .order("icd10_code")
        .execute()
    )


    return (
        medicines.data or [],
        diagnoses.data or []
    )



pnf_medicines, doh_diagnoses = fetch_database()



# =====================================
# NARRATIVE SOAP GENERATOR
# =====================================


def generate_soap(data):


    report = f"""

# Clinical SOAP Note


**Patient Name:** {data['name']}

**Age / Sex:** {data['age']}-year-old {data['sex']}

**Date / Time:** {data['date']}

**Setting:** Primary Care Outpatient Clinic



# S – Subjective



## Chief Complaint (CC)


The patient presented with the chief complaint of "{data['chief']}."



## History of Present Illness (HPI)


The patient is a {data['age']}-year-old {data['sex']} who presents with a {data['duration_of_illness']} history of {data['chief'].lower()}.


The symptoms started {data['onset_detail']}. The patient describes the condition as {data['character']}. The symptoms are aggravated by {data['aggravating']} and temporarily relieved by {data['alleviating']}.


The patient reports associated symptoms including {data['associated']}. The patient denies other significant symptoms not previously mentioned.



## Past Medical History


The patient has a history of {data['pmh']}.



## Family History


Family history is significant for {data['family']}.



## Personal and Social History


The patient reports {data['social']}.



## Review of Systems


Under the general system, the patient reports {data['ros_general']}.


HEENT review reveals {data['ros_heent']}.


Respiratory review reveals {data['ros_respiratory']}.


Cardiovascular review reveals {data['ros_cardio']}.





# O – Objective



## Vital Signs


The patient's vital signs were recorded as follows: blood pressure of {data['bp']}, heart rate of {data['hr']} beats per minute, respiratory rate of {data['rr']} breaths per minute, body temperature of {data['temperature']} °C, oxygen saturation of {data['spo2']}% on room air, with a BMI of {data['bmi']}.



## General Appearance


On physical examination, the patient was noted to be {data['general']}.



## HEENT Examination


HEENT examination revealed {data['heent']}.



## Bates Physical Examination – Chest and Lungs


Inspection of the chest revealed {data['inspection']}.


On palpation, the chest examination demonstrated {data['palpation']}.


Percussion of the lung fields revealed {data['percussion']}.


Auscultation revealed {data['auscultation']}.



## Cardiovascular Examination


Cardiovascular examination showed {data['cardiovascular']}.





# A – Assessment



Based on the patient's clinical history, physical examination findings, and available diagnostic information, the primary diagnosis is {data['primary_diagnosis']}.



The diagnosis is supported by the clinical presentation characterized by {data['clinical_rationale']}.



Differential diagnoses considered include {data['differential']}.



The patient also has a comorbid condition of {data['comorbidity']}.





# P – Plan



## Diagnostics / Workup


The recommended diagnostic approach includes {data['diagnostics']}.



Further investigation will be considered if symptoms persist, worsen, or if additional clinical findings develop.



## Therapeutics / Pharmacotherapy


The patient was advised regarding the following treatment plan: {data['medications']}.



## Non-Pharmacological Management and Patient Education


The patient was advised regarding {data['education']}.



## Follow-up and Safety Netting


The patient was instructed to return for follow-up evaluation after {data['followup']}.


The patient was advised to seek immediate medical attention for worsening symptoms such as difficulty breathing, chest pain, persistent high-grade fever, altered mental status, or other emergency warning signs.



**Attending Physician:** {data['physician']}


**Intern:** {data['intern']}


**Clerk:** {data['clerk']}


"""


    return report



# =====================================
# APPLICATION INTERFACE
# =====================================


st.title("🩺 Bates SOAP & PhilHealth Konsulta Clinical Generator")


st.write(
    "Generate a narrative clinical SOAP report based on Bates' Guide Physical Examination format."
)



left, right = st.columns(2)



# =====================================
# SUBJECTIVE INPUTS
# =====================================


with left:


    st.header("Patient Information")


    name = st.text_input(
        "Patient Name",
        "Juan Dela Cruz"
    )


    age = st.number_input(
        "Age",
        42
    )


    sex = st.selectbox(
        "Sex",
        [
            "Male",
            "Female"
        ]
    )


    date = st.text_input(
        "Date / Time",
        "September 16, 2026 | 10:15 AM"
    )



    st.header("Subjective Data")


    chief = st.text_input(
        "Chief Complaint",
        "Cough for 4 days and fever for 2 days"
    )


    duration_of_illness = st.text_input(
        "Duration of Illness",
        "4-day"
    )


    onset_detail = st.text_area(
        "HPI Onset",
        "started as dry tickling cough progressing to productive cough"
    )


    character = st.text_area(
        "Character",
        "productive cough with yellowish thick sputum"
    )


    aggravating = st.text_input(
        "Aggravating Factors",
        "cold air, deep inspiration, lying flat"
    )


    alleviating = st.text_input(
        "Alleviating Factors",
        "warm water"
    )


    associated = st.text_area(
        "Associated Symptoms",
        "fever, chills, nasal congestion, mild fatigue"
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
        "Non-smoker, occasional alcohol intake, office worker"
    )


    ros_general = st.text_input(
        "ROS General",
        "mild fever and chills"
    )


    ros_heent = st.text_input(
        "ROS HEENT",
        "nasal congestion and sore throat"
    )


    ros_respiratory = st.text_input(
        "ROS Respiratory",
        "cough and sputum production without shortness of breath"
    )


    ros_cardio = st.text_input(
        "ROS Cardiovascular",
        "no chest pain, palpitations, or edema"
    )
    # =====================================
# OBJECTIVE INPUTS
# =====================================


with right:


    st.header("Objective Data")


    bp = st.text_input(
        "Blood Pressure",
        "124/80 mmHg"
    )


    hr = st.number_input(
        "Heart Rate",
        84
    )


    rr = st.number_input(
        "Respiratory Rate",
        18
    )


    temperature = st.number_input(
        "Temperature",
        37.8
    )


    spo2 = st.number_input(
        "SpO2",
        98
    )


    bmi = st.text_input(
        "BMI",
        "24.2 kg/m²"
    )



    general = st.text_area(
        "General Appearance",
        "alert, oriented x3, well-nourished, hydrated, and in no apparent distress"
    )


    heent = st.text_area(
        "HEENT Examination",
        "mild nasal mucosal erythema with clear discharge and mild posterior pharyngeal erythema"
    )



    st.subheader(
        "Bates Chest and Lung Examination"
    )


    inspection = st.text_area(
        "Inspection",
        "symmetrical thoracic expansion with no retractions, deformities, or accessory muscle use"
    )


    palpation = st.text_area(
        "Palpation",
        "normal tactile fremitus bilaterally with trachea in midline position"
    )


    percussion = st.text_area(
        "Percussion",
        "resonant percussion note throughout all lung fields"
    )


    auscultation = st.text_area(
        "Auscultation",
        "coarse crackles and low-pitched rhonchi noted over the right lower lung field, partially clearing after coughing"
    )


    cardiovascular = st.text_area(
        "Cardiovascular Examination",
        "normal S1 and S2 heart sounds with regular rhythm and no murmurs, gallops, or friction rub"
    )



# =====================================
# ASSESSMENT SECTION
# =====================================


st.header("Assessment")



primary_diagnosis = st.text_input(
    "Primary Diagnosis",
    "Acute Bronchitis, unspecified (J20.9)"
)


clinical_rationale = st.text_area(
    "Clinical Rationale",
    "4-day productive cough following viral upper respiratory symptoms, low-grade fever, normal oxygen saturation, and absence of respiratory distress or consolidation findings"
)


differential = st.text_area(
    "Differential Diagnoses",
    "Community-Acquired Pneumonia (J18.9), Acute Upper Respiratory Infection (J06.9), Pulmonary Tuberculosis"
)


comorbidity = st.text_input(
    "Comorbid Condition",
    "Essential Hypertension (I10), controlled on Amlodipine"
)



# =====================================
# PLAN SECTION
# =====================================


st.header("Plan")



diagnostics = st.text_area(
    "Diagnostics / Workup",
    "Chest X-ray deferred at present; CBC and sputum examination not indicated unless symptoms worsen or persist"
)


medications = st.text_area(
    "Therapeutics / Pharmacotherapy",
    "Paracetamol 500 mg tablet as needed for fever; Salbutamol syrup as needed for cough; continue Amlodipine 5 mg once daily"
)


education = st.text_area(
    "Patient Education",
    "Increase oral fluid intake, maintain adequate rest, avoid smoke and respiratory irritants, practice hand hygiene, and use a mask when around household members"
)


followup = st.text_input(
    "Follow-up Schedule",
    "3-5 days or earlier if symptoms worsen"
)



physician = st.text_input(
    "Attending Physician",
    "________________"
)


intern = st.text_input(
    "Intern",
    "________________"
)


clerk = st.text_input(
    "Clerk",
    "________________"
)




# =====================================
# GENERATE REPORT
# =====================================


if st.button(
    "Generate Narrative SOAP Report",
    type="primary"
):


    soap_data = {


        "name": name,
        "age": age,
        "sex": sex,
        "date": date,


        "chief": chief,
        "duration_of_illness": duration_of_illness,
        "onset_detail": onset_detail,
        "character": character,
        "aggravating": aggravating,
        "alleviating": alleviating,
        "associated": associated,


        "pmh": pmh,
        "family": family,
        "social": social,


        "ros_general": ros_general,
        "ros_heent": ros_heent,
        "ros_respiratory": ros_respiratory,
        "ros_cardio": ros_cardio,


        "bp": bp,
        "hr": hr,
        "rr": rr,
        "temperature": temperature,
        "spo2": spo2,
        "bmi": bmi,


        "general": general,
        "heent": heent,


        "inspection": inspection,
        "palpation": palpation,
        "percussion": percussion,
        "auscultation": auscultation,


        "cardiovascular": cardiovascular,


        "primary_diagnosis": primary_diagnosis,
        "clinical_rationale": clinical_rationale,
        "differential": differential,
        "comorbidity": comorbidity,


        "diagnostics": diagnostics,
        "medications": medications,
        "education": education,
        "followup": followup,


        "physician": physician,
        "intern": intern,
        "clerk": clerk

    }



    final_report = generate_soap(
        soap_data
    )



    st.success(
        "SOAP Report Generated Successfully"
    )


    st.markdown(
        final_report
    )



    st.download_button(
        label="Download SOAP Report (.txt)",
        data=final_report,
        file_name="Clinical_SOAP_Report.txt",
        mime="text/plain"
    )
