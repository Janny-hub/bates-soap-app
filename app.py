import streamlit as st
from supabase import create_client, Client
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.markdown("""
<style>
.stApp {background-color:#f4fbf7;}
h1,h2,h3 {color:#087f5b;}
.stButton>button {background-color:#0ca678;color:white;border-radius:10px;}
</style>
""", unsafe_allow_html=True)

st.set_page_config(
    page_title="MediFlow AI Clinical EMR",
    layout="wide"
)


# ==========================================
# SUPABASE CONNECTION
# ==========================================

SUPABASE_URL = st.secrets.get(
    "SUPABASE_URL",
    ""
)

SUPABASE_KEY = st.secrets.get(
    "SUPABASE_KEY",
    ""
)


@st.cache_resource
def init_supabase():

    if SUPABASE_URL and SUPABASE_KEY:

        return create_client(
            SUPABASE_URL,
            SUPABASE_KEY
        )

    return None



supabase = init_supabase()



# ==========================================
# LOAD DATABASE
# ==========================================


@st.cache_data(ttl=600)
def load_database():

    if not supabase:
        return [], []


    medicines = (
        supabase
        .table("pnf_medicines")
        .select("*")
        .execute()
    )


    diagnoses = (
        supabase
        .table("doh_diagnoses")
        .select("*")
        .execute()
    )


    return (

        medicines.data or [],

        diagnoses.data or []

    )



pnf_medicines, doh_diagnoses = load_database()



# ==========================================
# SOAP NARRATIVE GENERATOR
# ==========================================


def generate_soap(data):


    report = f"""

# Clinical SOAP Note


**Patient Name:** {data['name']}

**Age / Sex:** {data['age']}-year-old {data['sex']}

**Date / Time:** {data['date']}

**Setting:** Primary Care Outpatient Clinic



# S – Subjective



## Chief Complaint


The patient presented with the chief complaint of "{data['chief']}."



## History of Present Illness


The patient is a {data['age']}-year-old {data['sex']} who presents with a {data['duration']} history of {data['chief'].lower()}.


The condition started {data['onset']}. The patient describes the symptoms as {data['character']}. Symptoms are aggravated by {data['aggravating']} and relieved by {data['alleviating']}.


Associated symptoms include {data['associated']}.



## Past Medical History


The patient has a history of {data['pmh']}.



## Family History


Family history is significant for {data['family']}.



## Personal and Social History


The patient reports {data['social']}.



## Review of Systems


General review reveals {data['ros_general']}.


HEENT review reveals {data['ros_heent']}.


Respiratory review reveals {data['ros_respiratory']}.


Thorax review reveals {data['ros_thorax']}.


Cardiovascular review reveals {data['ros_cardio']}.


Gastrointestinal review reveals {data['ros_gastro']}.


Genitourinary review reveals {data['ros_gu']}.


Musculoskeletal review reveals {data['ros_musculoskeletal']}.


Neurologic review reveals {data['ros_neuro']}.


Skin review reveals {data['ros_skin']}.





# O – Objective



## Vital Signs


Blood pressure was {data['bp']}, heart rate was {data['hr']} bpm, respiratory rate was {data['rr']} breaths/min, temperature was {data['temperature']} °C, oxygen saturation was {data['spo2']}% on room air, and BMI was {data['bmi']}.



## Physical Examination


{data['physical_exam']}





# A – Assessment



The primary diagnosis is {data['primary_dx']}.



The diagnosis is supported by {data['rationale']}.



Differential diagnoses include {data['differential']}.



The patient has the following comorbid condition/s: {data['comorbidity']}.





# P – Plan



## Diagnostics


{data['diagnostics']}



## Pharmacotherapy


{data['medications']}



## Patient Education


{data['education']}



## Follow-up


The patient was advised to return after {data['followup']} or seek immediate medical attention if symptoms worsen.





Attending Physician:

{data['physician']}



Intern:

{data['intern']}



Clerk:

{data['clerk']}


"""


    return report





# ==========================================
# MEDIFLOW AI SUPPORT MODULE
# ==========================================

def ai_diagnosis_suggestion(chief, symptoms):
    text = (chief + " " + symptoms).lower()
    result = []
    if "cough" in text or "sputum" in text:
        result.append(("Respiratory infection consideration",
        "Respiratory symptoms may indicate infection. Confirm through examination and appropriate diagnostic testing."))
    if "fever" in text:
        result.append(("Febrile illness evaluation",
        "Fever requires assessment of possible infectious or inflammatory causes."))
    if "chest pain" in text:
        result.append(("Cardiovascular assessment",
        "Chest pain requires evaluation for cardiac and other possible causes."))
    if not result:
        result.append(("Further clinical assessment required",
        "AI suggestion generated from available patient information."))
    return result


def ai_management_suggestion(primary_dx):
    return f"""AI Management Support:
Diagnosis reviewed: {primary_dx}

Recommended clinical workflow:
• Verify diagnosis using history, physical examination, and indicated diagnostics.
• Review medication appropriateness, allergies, contraindications, and interactions.
• Provide patient education and follow-up monitoring.
• Final treatment decisions require healthcare professional judgment.
"""


def create_pdf(report):
    buffer = io.BytesIO()
    document = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    elements = []
    for line in report.split("\n"):
        elements.append(Paragraph(line.replace("&", "and"), styles["Normal"]))
        elements.append(Spacer(1, 8))
    document.build(elements)
    buffer.seek(0)
    return buffer


# ==========================================
# APP TITLE
# ==========================================


st.title(
    "🩺 MediFlow AI Clinical EMR"
)



st.write(
    "AI-assisted SOAP documentation, diagnosis rationale, and clinical management support."
)



left, right = st.columns(2)




# ==========================================
# PATIENT + SUBJECTIVE
# ==========================================


with left:


    st.header(
        "Patient Information"
    )


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
        [
            "Male",
            "Female"
        ]
    )


    date = st.text_input(
        "Date / Time",
        "September 16, 2026 | 10:15 AM"
    )



    st.header(
        "History of Present Illness"
    )



    chief = st.text_input(
        "Chief Complaint",
        "Cough for 4 days and fever for 2 days"
    )


    duration = st.text_input(
        "Duration",
        "4-day"
    )


    onset = st.text_area(
        "Onset",
        "Started as dry cough progressing to productive cough"
    )


    character = st.text_area(
        "Character",
        "Productive cough with yellowish sputum"
    )


    aggravating = st.text_input(
        "Aggravating Factors",
        "Cold air and lying flat"
    )


    alleviating = st.text_input(
        "Alleviating Factors",
        "Warm water"
    )



    st.subheader(
        "Associated Symptoms"
    )


    symptom_list = [

        "Fever",
        "Chills",
        "Fatigue",
        "Weakness",
        "Weight loss",
        "Night sweats",

        "Cough",
        "Sputum production",
        "Shortness of breath",
        "Wheezing",
        "Chest pain",

        "Nasal congestion",
        "Runny nose",
        "Sore throat",

        "Headache",
        "Dizziness",

        "Nausea",
        "Vomiting",
        "Diarrhea",

        "Abdominal pain",

        "Dysuria",
        "Urinary frequency",

        "Joint pain",
        "Muscle pain"

    ]


    associated = st.multiselect(
        "Select Symptoms",
        symptom_list
    )


    associated = ", ".join(associated) if associated else "none"



    st.subheader(
        "Past Medical History"
    )


    disease_list = [

        "Hypertension",
        "Diabetes Mellitus Type 2",
        "Asthma",
        "COPD",
        "Tuberculosis",
        "Pneumonia",

        "Coronary Artery Disease",
        "Heart Failure",
        "Stroke",

        "Chronic Kidney Disease",

        "Hyperlipidemia",

        "Thyroid Disease",

        "Cancer",

        "GERD",

        "Depression",
        "Anxiety Disorder"

    ]


    pmh = st.multiselect(
        "Select Diseases",
        disease_list
    )


    pmh = ", ".join(pmh) if pmh else "No known medical illness"



    st.subheader(
        "Family History"
    )


    family = st.multiselect(
        "Family Diseases",
        disease_list
    )


    family = ", ".join(family) if family else "No significant family history"



    social = st.multiselect(
        "Social History",

        [

            "Non-smoker",
            "Smoker",
            "Former smoker",

            "Alcohol drinker",
            "No alcohol intake",

            "Vape user",

            "Occupational exposure",

            "Regular exercise"

        ]

    )


    social = ", ".join(social) if social else "No significant social history"
# ==========================================
# REVIEW OF SYSTEMS MODULE
# ==========================================


st.header("Review of Systems (ROS)")


# GENERAL

ros_general = st.multiselect(

    "ROS - General",

    [

        "Fever",
        "Chills",
        "Fatigue",
        "Weakness",
        "Weight loss",
        "Weight gain",
        "Night sweats",
        "Loss of appetite",
        "Sleep disturbance"

    ]

)



# HEENT

ros_heent = st.multiselect(

    "ROS - HEENT",

    [

        "Headache",
        "Dizziness",

        "Blurred vision",
        "Eye pain",

        "Ear pain",
        "Hearing loss",

        "Nasal congestion",
        "Runny nose",

        "Sinus pressure",

        "Sore throat",

        "Difficulty swallowing"

    ]

)



# RESPIRATORY

ros_respiratory = st.multiselect(

    "ROS - Respiratory",

    [

        "Cough",
        "Sputum production",

        "Shortness of breath",

        "Wheezing",

        "Hemoptysis",

        "Difficulty breathing",

        "Nocturnal cough"

    ]

)



# THORAX

ros_thorax = st.multiselect(

    "ROS - Thorax",

    [

        "Chest pain",

        "Chest tightness",

        "Chest tenderness",

        "Breast pain",

        "Breast mass"

    ]

)



# CARDIOVASCULAR

ros_cardio = st.multiselect(

    "ROS - Cardiovascular",

    [

        "Palpitations",

        "Chest pain",

        "Orthopnea",

        "Paroxysmal nocturnal dyspnea",

        "Leg swelling",

        "Exercise intolerance"

    ]

)



# GASTROINTESTINAL

ros_gastro = st.multiselect(

    "ROS - Gastrointestinal",

    [

        "Abdominal pain",

        "Nausea",

        "Vomiting",

        "Diarrhea",

        "Constipation",

        "Blood in stool",

        "Heartburn",

        "Loss of appetite"

    ]

)



# GENITOURINARY

ros_gu = st.multiselect(

    "ROS - Genitourinary",

    [

        "Dysuria",

        "Urinary frequency",

        "Urinary urgency",

        "Hematuria",

        "Flank pain",

        "Urinary incontinence",

        "Abnormal discharge"

    ]

)



# MUSCULOSKELETAL

ros_musculoskeletal = st.multiselect(

    "ROS - Musculoskeletal",

    [

        "Joint pain",

        "Joint swelling",

        "Muscle pain",

        "Back pain",

        "Muscle weakness",

        "Limited movement"

    ]

)



# NEUROLOGIC

ros_neuro = st.multiselect(

    "ROS - Neurologic",

    [

        "Headache",

        "Dizziness",

        "Numbness",

        "Tingling sensation",

        "Loss of consciousness",

        "Seizure",

        "Memory problems"

    ]

)



# SKIN

ros_skin = st.multiselect(

    "ROS - Skin",

    [

        "Rash",

        "Itching",

        "Skin discoloration",

        "Wound",

        "Skin lesions"

    ]

)



# Convert ROS to narrative


def ros_text(value):

    if value:

        return ", ".join(value)

    return "no significant symptoms reported"



ros_general = ros_text(ros_general)

ros_heent = ros_text(ros_heent)

ros_respiratory = ros_text(ros_respiratory)

ros_thorax = ros_text(ros_thorax)

ros_cardio = ros_text(ros_cardio)

ros_gastro = ros_text(ros_gastro)

ros_gu = ros_text(ros_gu)

ros_musculoskeletal = ros_text(ros_musculoskeletal)

ros_neuro = ros_text(ros_neuro)

ros_skin = ros_text(ros_skin)





# ==========================================
# PHYSICAL EXAMINATION MODULE
# ==========================================


st.header("Physical Examination")



# GENERAL EXAMINATION


general_exam_status = st.selectbox(

    "General Appearance",

    [

        "Unremarkable",

        "Alert and oriented",

        "Ill-looking",

        "In mild distress",

        "In moderate distress",

        "In severe distress"

    ]

)



general_positive = st.multiselect(

    "General Positive Findings",

    [

        "Pallor",

        "Cyanosis",

        "Dehydration",

        "Cachexia",

        "Feverish appearance",

        "Altered mental status"

    ]

)



general_negative = st.multiselect(

    "General Pertinent Negatives",

    [

        "No acute distress",

        "No pallor",

        "No cyanosis",

        "No dehydration",

        "No altered consciousness"

    ]

)





# HEENT EXAMINATION


heent_exam_status = st.selectbox(

    "HEENT Examination",

    [

        "Unremarkable",

        "Abnormal findings present"

    ]

)



heent_positive = st.multiselect(

    "HEENT Positive Findings",

    [

        "Pale conjunctiva",

        "Icteric sclera",

        "Nasal congestion",

        "Nasal discharge",

        "Pharyngeal erythema",

        "Tonsillar enlargement",

        "Tonsillar exudates",

        "Cervical lymphadenopathy"

    ]

)



heent_negative = st.multiselect(

    "HEENT Pertinent Negatives",

    [

        "No sinus tenderness",

        "No tonsillar exudates",

        "No oral lesions",

        "No cervical lymphadenopathy"

    ]

)





# RESPIRATORY EXAMINATION


resp_exam_status = st.selectbox(

    "Chest and Lung Examination",

    [

        "Unremarkable",

        "Abnormal findings present"

    ]

)



resp_positive = st.multiselect(

    "Respiratory Positive Findings",

    [

        "Crackles (rales)",

        "Rhonchi",

        "Wheezing",

        "Decreased breath sounds",

        "Bronchial breath sounds",

        "Accessory muscle use",

        "Intercostal retractions"

    ]

)



resp_negative = st.multiselect(

    "Respiratory Pertinent Negatives",

    [

        "No respiratory distress",

        "No cyanosis",

        "No hemoptysis",

        "No pleuritic chest pain",

        "No accessory muscle use",

        "No stridor"

    ]

)



# CARDIOVASCULAR


cardio_exam_status = st.selectbox(

    "Cardiovascular Examination",

    [

        "Unremarkable",

        "Abnormal findings present"

    ]

)



cardio_positive = st.multiselect(

    "Cardiovascular Positive Findings",

    [

        "Heart murmur",

        "Irregular rhythm",

        "Peripheral edema",

        "Jugular venous distension",

        "Weak pulses"

    ]

)



cardio_negative = st.multiselect(

    "Cardiovascular Pertinent Negatives",

    [

        "No chest pain",

        "No edema",

        "No JVD",

        "Regular rhythm",

        "Normal peripheral pulses"

    ]

)
# ==========================================
# ABDOMINAL EXAMINATION
# ==========================================


st.subheader("Abdominal Examination")


abdomen_status = st.selectbox(

    "Abdomen",

    [
        "Unremarkable",
        "Abnormal findings present"
    ]

)



abdomen_positive = st.multiselect(

    "Abdominal Positive Findings",

    [

        "Abdominal tenderness",

        "Right upper quadrant tenderness",

        "Left lower quadrant tenderness",

        "Guarding",

        "Rebound tenderness",

        "Abdominal distension",

        "Palpable mass",

        "Ascites"

    ]

)



abdomen_negative = st.multiselect(

    "Abdominal Pertinent Negatives",

    [

        "No abdominal tenderness",

        "No guarding",

        "No rebound tenderness",

        "No palpable mass",

        "Normal bowel sounds"

    ]

)





# ==========================================
# GENITOURINARY EXAMINATION
# ==========================================


st.subheader("Genitourinary Examination")


gu_exam_status = st.selectbox(

    "Genitourinary",

    [

        "Unremarkable",

        "Abnormal findings present"

    ]

)



gu_exam_positive = st.multiselect(

    "GU Positive Findings",

    [

        "Suprapubic tenderness",

        "Costovertebral angle tenderness",

        "Abnormal discharge",

        "Genital lesion",

        "Scrotal swelling"

    ]

)



gu_exam_negative = st.multiselect(

    "GU Pertinent Negatives",

    [

        "No CVA tenderness",

        "No suprapubic tenderness",

        "No abnormal discharge",

        "No lesions"

    ]

)





# ==========================================
# MUSCULOSKELETAL EXAMINATION
# ==========================================


st.subheader("Musculoskeletal Examination")


msk_status = st.selectbox(

    "Musculoskeletal",

    [

        "Unremarkable",

        "Abnormal findings present"

    ]

)



msk_positive = st.multiselect(

    "Musculoskeletal Positive Findings",

    [

        "Joint swelling",

        "Joint tenderness",

        "Reduced range of motion",

        "Muscle weakness",

        "Deformity",

        "Gait abnormality"

    ]

)



msk_negative = st.multiselect(

    "Musculoskeletal Pertinent Negatives",

    [

        "No joint swelling",

        "No deformity",

        "Full range of motion",

        "No muscle tenderness"

    ]

)





# ==========================================
# NEUROLOGIC EXAMINATION
# ==========================================


st.subheader("Neurologic Examination")


neuro_status = st.selectbox(

    "Neurologic",

    [

        "Unremarkable",

        "Abnormal findings present"

    ]

)



neuro_positive = st.multiselect(

    "Neurologic Positive Findings",

    [

        "Altered mental status",

        "Weakness",

        "Sensory deficit",

        "Abnormal gait",

        "Tremors",

        "Seizure activity"

    ]

)



neuro_negative = st.multiselect(

    "Neurologic Pertinent Negatives",

    [

        "Alert and oriented",

        "No focal neurologic deficit",

        "Normal gait",

        "No seizure activity"

    ]

)





# ==========================================
# PHYSICAL EXAMINATION NARRATIVE BUILDER
# ==========================================


def create_physical_exam():


    return f"""

General examination revealed the patient to be {general_exam_status}.
Positive findings include {', '.join(general_positive) if general_positive else 'No abnormal finding documented'}.
Pertinent negatives include {', '.join(general_negative) if general_negative else 'No abnormal finding documented'}.


HEENT examination was {heent_exam_status}.
Findings include {', '.join(heent_positive) if heent_positive else 'no significant abnormalities'}.
Pertinent negatives include {', '.join(heent_negative) if heent_negative else 'No abnormal finding documented'}.


Respiratory examination was {resp_exam_status}.
Positive findings include {', '.join(resp_positive) if resp_positive else 'no abnormal findings'}.
Pertinent negatives include {', '.join(resp_negative) if resp_negative else 'No abnormal finding documented'}.


Cardiovascular examination was {cardio_exam_status}.
Positive findings include {', '.join(cardio_positive) if cardio_positive else 'no significant abnormalities'}.
Pertinent negatives include {', '.join(cardio_negative) if cardio_negative else 'No abnormal finding documented'}.


Abdominal examination was {abdomen_status}.
Positive findings include {', '.join(abdomen_positive) if abdomen_positive else 'no significant abnormalities'}.
Pertinent negatives include {', '.join(abdomen_negative) if abdomen_negative else 'No abnormal finding documented'}.


Genitourinary examination was {gu_exam_status}.
Positive findings include {', '.join(gu_exam_positive) if gu_exam_positive else 'no significant abnormalities'}.
Pertinent negatives include {', '.join(gu_exam_negative) if gu_exam_negative else 'No abnormal finding documented'}.


Musculoskeletal examination was {msk_status}.
Positive findings include {', '.join(msk_positive) if msk_positive else 'no significant abnormalities'}.
Pertinent negatives include {', '.join(msk_negative) if msk_negative else 'No abnormal finding documented'}.


Neurologic examination was {neuro_status}.
Positive findings include {', '.join(neuro_positive) if neuro_positive else 'no significant abnormalities'}.
Pertinent negatives include {', '.join(neuro_negative) if neuro_negative else 'No abnormal finding documented'}.

"""





# ==========================================
# ASSESSMENT SECTION
# ==========================================


st.header("Assessment")



if doh_diagnoses:


    diagnosis_options = [

        f"{x['icd10_code']} - {x['description']}"

        for x in doh_diagnoses

    ]


else:


    diagnosis_options = [

        "I10 - Essential Hypertension",

        "J20.9 - Acute Bronchitis",

        "J18.9 - Pneumonia",

        "E11.9 - Type 2 Diabetes Mellitus",

        "J45.909 - Asthma"

    ]



selected_diagnosis = st.selectbox(

    "Primary Diagnosis",

    diagnosis_options

)



primary_dx = selected_diagnosis



rationale = st.text_area(

    "Clinical Rationale",

    "Diagnosis based on patient's history, review of systems, and physical examination findings."

)



differential = st.text_area(

    "Differential Diagnoses",

    "Other possible diagnoses considered based on clinical presentation."

)



comorbidity = st.text_input(

    "Comorbid Conditions",

    "None"

)
# ==========================================
# MEDICATION DATABASE
# ==========================================


st.header("Medication Management")



medication_database = {


"NCD - Hypertension":

[

"Amlodipine 5 mg tablet",

"Amlodipine 10 mg tablet",

"Losartan 50 mg tablet",

"Losartan + Hydrochlorothiazide tablet",

"Enalapril 5 mg tablet",

"Enalapril 10 mg tablet",

"Captopril 25 mg tablet",

"Hydrochlorothiazide 25 mg tablet",

"Metoprolol 50 mg tablet",

"Telmisartan 40 mg tablet"

],



"NCD - Diabetes Mellitus":

[

"Metformin 500 mg tablet",

"Metformin 850 mg tablet",

"Gliclazide 30 mg tablet",

"Gliclazide 60 mg tablet",

"Insulin Regular",

"NPH Insulin"

],



"NCD - Dyslipidemia":

[

"Atorvastatin 20 mg tablet",

"Atorvastatin 40 mg tablet",

"Simvastatin 20 mg tablet",

"Rosuvastatin 10 mg tablet"

],



"NCD - Cardiovascular Disease":

[

"Aspirin 80 mg tablet",

"Clopidogrel 75 mg tablet",

"Isosorbide Dinitrate tablet",

"Digoxin tablet",

"Furosemide tablet"

],



"NCD - Asthma / COPD":

[

"Salbutamol inhaler",

"Salbutamol nebulization solution",

"Ipratropium nebulization",

"Budesonide inhaler",

"Budesonide + Formoterol inhaler",

"Montelukast tablet",

"Prednisone tablet"

],



"Non-NCD - Fever / Pain":

[

"Paracetamol 500 mg tablet",

"Ibuprofen 400 mg tablet",

"Mefenamic Acid 500 mg capsule"

],



"Non-NCD - Respiratory Infection":

[

"Amoxicillin 500 mg capsule",

"Amoxicillin + Clavulanic Acid tablet",

"Azithromycin 500 mg tablet",

"Cefuroxime tablet",

"Cefixime capsule",

"Doxycycline capsule",

"Co-trimoxazole tablet"

],



"Non-NCD - Allergic Conditions":

[

"Cetirizine 10 mg tablet",

"Loratadine 10 mg tablet",

"Chlorphenamine tablet"

],



"Non-NCD - Gastrointestinal":

[

"Omeprazole 20 mg capsule",

"Antacid suspension",

"Oral Rehydration Salt",

"Loperamide capsule",

"Metoclopramide tablet"

],



"Non-NCD - Urinary Tract Infection":

[

"Nitrofurantoin capsule",

"Ciprofloxacin tablet",

"Co-trimoxazole tablet"

],



"Non-NCD - Skin Conditions":

[

"Clotrimazole cream",

"Mupirocin ointment",

"Hydrocortisone cream",

"Permethrin cream"

],



"Supplements":

[

"Iron + Folic Acid tablet",

"Folic Acid tablet",

"Vitamin C tablet",

"Calcium + Vitamin D"

]

}



med_category = st.selectbox(

    "Medication Category",

    list(medication_database.keys())

)



selected_meds = st.multiselect(

    "Select Medication",

    medication_database[med_category]

)



route = st.selectbox(

    "Route",

    [

        "Oral (PO)",

        "Inhalation",

        "Nebulization",

        "Topical",

        "Injection"

    ]

)



frequency = st.selectbox(

    "Frequency",

    [

        "Once daily (OD)",

        "Twice daily (BID)",

        "Three times daily (TID)",

        "Every 6 hours (q6h)",

        "Every 8 hours (q8h)",

        "As needed (PRN)"

    ]

)



duration = st.text_input(

    "Duration",

    "5 days"

)





def medication_narrative():


    if not selected_meds:

        return "No medications prescribed."


    text = ""


    for med in selected_meds:


        text += (

            f"The patient was prescribed {med}, "

            f"to be administered via {route}, "

            f"{frequency}, for {duration}. "

        )


    return text





# ==========================================
# PLAN SECTION
# ==========================================


st.header("AI Management and Medication Support")
ai_management = ai_management_suggestion(primary_dx)
st.info(ai_management)

st.header("Plan")



diagnostics = st.text_area(

    "Diagnostics / Workup",

    "Laboratory tests and imaging as clinically indicated."

)



education = st.text_area(

    "Patient Education",

    "Advised on medication compliance, lifestyle modification, hydration, nutrition, and warning signs."

)



followup = st.text_input(

    "Follow-up",

    "3-5 days or as clinically indicated"

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





# ==========================================
# GENERATE SOAP REPORT
# ==========================================


if st.button(

    "Generate Narrative SOAP Report",

    type="primary"

):


    physical_exam = create_physical_exam()



    medication_plan = medication_narrative()



    data = {


        "name": name,

        "age": age,

        "sex": sex,

        "date": date,


        "chief": chief,

        "duration": duration,

        "onset": onset,

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

        "ros_thorax": ros_thorax,

        "ros_cardio": ros_cardio,

        "ros_gastro": ros_gastro,

        "ros_gu": ros_gu,

        "ros_musculoskeletal": ros_musculoskeletal,

        "ros_neuro": ros_neuro,

        "ros_skin": ros_skin,


        "bp": bp if 'bp' in globals() else "",

        "hr": hr if 'hr' in globals() else "",

        "rr": rr if 'rr' in globals() else "",

        "temperature": temperature if 'temperature' in globals() else "",

        "spo2": spo2 if 'spo2' in globals() else "",

        "bmi": bmi if 'bmi' in globals() else "",


        "physical_exam": physical_exam,


        "primary_dx": primary_dx,

        "rationale": rationale,

        "differential": differential,

        "comorbidity": comorbidity,


        "diagnostics": diagnostics,

        "medications": medication_plan + "\n\n" + ai_management,

        "education": education,

        "followup": followup,


        "physician": physician,

        "intern": intern,

        "clerk": clerk

    }



    final_report = generate_soap(data)



    st.success(
        "SOAP Report Generated"
    )



    st.markdown(
        final_report
    )



    pdf_report = create_pdf(final_report)

    st.download_button(
        label="Download SOAP Report PDF",
        data=pdf_report,
        file_name="MediFlow_SOAP_Report.pdf",
        mime="application/pdf"
    )
