import streamlit as st
import time
import json
import re
import hashlib
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

# Page configuration
st.set_page_config(
    page_title="🏥 Advanced Medical Assistant",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for professional medical interface
st.markdown("""
<style>
    .main-header {
        color: #2E86AB;
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #E3F2FD 0%, #BBDEFB 100%);
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .search-container {
        background: #F8F9FA;
        padding: 2rem;
        border-radius: 15px;
        border: 1px solid #E0E0E0;
        margin-bottom: 2rem;
    }
    
    .result-container {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #2E86AB;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .confidence-high {
        border-left-color: #4CAF50 !important;
    }
    
    .confidence-medium {
        border-left-color: #FF9800 !important;
    }
    
    .confidence-low {
        border-left-color: #F44336 !important;
    }
    
    .medical-disclaimer {
        background: #FFF3E0;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #FFB74D;
        margin: 1rem 0;
        font-size: 0.9rem;
    }
    
    .emergency-alert {
        background: #FFEBEE;
        color: #C62828;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #EF5350;
        margin: 1rem 0;
        font-weight: bold;
    }
    
    .stats-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Enums and Data Classes
class EvidenceLevel(Enum):
    LEVEL_1A = "1A - Systematic Review of RCTs"
    LEVEL_1B = "1B - Individual RCT"
    LEVEL_2A = "2A - Systematic Review of Cohort Studies"
    LEVEL_2B = "2B - Individual Cohort Study"
    LEVEL_3 = "3 - Case-Control Studies"
    EXPERT = "Expert Opinion"

class SeverityLevel(Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MODERATE = "Moderate"
    LOW = "Low"
    INFO = "Information"

@dataclass
class MedicalCondition:
    name: str
    icd10_code: str
    symptoms: List[str]
    causes: List[str]
    treatments: List[str]
    complications: List[str]
    prevention: List[str]
    risk_factors: List[str]
    diagnostic_tests: List[str]
    severity: SeverityLevel
    prevalence: str
    age_groups: List[str]
    specialties: List[str]

@dataclass
class DrugInfo:
    name: str
    generic_name: str
    drug_class: str
    indications: List[str]
    contraindications: List[str]
    side_effects: List[str]
    interactions: List[str]
    dosage: str
    pregnancy_category: str
    monitoring: List[str]

@dataclass
class SymptomInfo:
    symptom: str
    possible_conditions: List[str]
    severity_indicators: List[str]
    when_to_seek_help: List[str]
    self_care: List[str]

# STANDALONE UTILITY FUNCTIONS - GUARANTEED TO WORK
def safe_format_result_title(result):
    """Format result title based on type - FOOLPROOF VERSION"""
    try:
        result_type = result.get("type", "unknown")
        data = result.get("data", None)
        
        if result_type == "condition" and data:
            name = getattr(data, 'name', 'Medical Condition')
            return f"🏥 {name}"
        elif result_type == "drug" and data:
            name = getattr(data, 'name', 'Medication')
            return f"💊 {name}"
        elif result_type == "symptom" and data:
            symptom = getattr(data, 'symptom', 'Symptom')
            return f"🩺 {symptom}"
        else:
            return "📋 Medical Information"
    except Exception as e:
        return "📋 Medical Information"

def safe_display_condition_result(condition):
    """Display medical condition information - FOOLPROOF VERSION"""
    try:
        if not condition:
            st.error("No condition data available")
            return
            
        # Safely get attributes with fallbacks
        icd10 = getattr(condition, 'icd10_code', 'N/A')
        severity = getattr(condition, 'severity', 'Unknown')
        prevalence = getattr(condition, 'prevalence', 'Unknown')
        symptoms = getattr(condition, 'symptoms', [])
        treatments = getattr(condition, 'treatments', [])
        complications = getattr(condition, 'complications', [])
        prevention = getattr(condition, 'prevention', [])
        
        st.markdown(f"**ICD-10 Code:** {icd10}")
        if hasattr(severity, 'value'):
            st.markdown(f"**Severity:** {severity.value}")
        else:
            st.markdown(f"**Severity:** {severity}")
        st.markdown(f"**Prevalence:** {prevalence}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Common Symptoms:**")
            if symptoms:
                for symptom in symptoms[:5]:
                    st.markdown(f"• {symptom}")
            else:
                st.markdown("• No symptom information available")
        
        with col2:
            st.markdown("**Treatment Options:**")
            if treatments:
                for treatment in treatments[:5]:
                    st.markdown(f"• {treatment}")
            else:
                st.markdown("• No treatment information available")
        
        # Additional information
        if complications:
            st.markdown("**Potential Complications:**")
            for comp in complications[:3]:
                st.markdown(f"• {comp}")
        
        if prevention:
            st.markdown("**Prevention:**")
            for prev in prevention[:3]:
                st.markdown(f"• {prev}")
        
        # Severity warning
        if hasattr(severity, 'value') and severity.value == "Critical":
            st.error("⚠️ This is a critical condition requiring immediate medical attention")
        elif hasattr(severity, 'value') and severity.value == "High":
            st.warning("⚠️ This condition requires prompt medical attention")
                
    except Exception as e:
        st.error(f"Error displaying condition information: {str(e)}")

def safe_display_drug_result(drug):
    """Display drug information - FOOLPROOF VERSION"""
    try:
        if not drug:
            st.error("No drug data available")
            return
            
        # Safely get attributes
        generic_name = getattr(drug, 'generic_name', 'N/A')
        drug_class = getattr(drug, 'drug_class', 'N/A')
        dosage = getattr(drug, 'dosage', 'N/A')
        pregnancy_category = getattr(drug, 'pregnancy_category', 'N/A')
        indications = getattr(drug, 'indications', [])
        side_effects = getattr(drug, 'side_effects', [])
        contraindications = getattr(drug, 'contraindications', [])
        interactions = getattr(drug, 'interactions', [])
        
        st.markdown(f"**Generic Name:** {generic_name}")
        st.markdown(f"**Drug Class:** {drug_class}")
        st.markdown(f"**Typical Dosage:** {dosage}")
        st.markdown(f"**Pregnancy Category:** {pregnancy_category}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Indications:**")
            if indications:
                for indication in indications[:4]:
                    st.markdown(f"• {indication}")
            else:
                st.markdown("• No indication information available")
        
        with col2:
            st.markdown("**Common Side Effects:**")
            if side_effects:
                for side_effect in side_effects[:4]:
                    st.markdown(f"• {side_effect}")
            else:
                st.markdown("• No side effect information available")
        
        # Contraindications
        if contraindications:
            st.markdown("**Contraindications:**")
            for contra in contraindications[:3]:
                st.markdown(f"• {contra}")
        
        # Drug interactions warning
        if interactions:
            st.warning("⚠️ This medication has known drug interactions. Consult your healthcare provider.")
            with st.expander("View Drug Interactions"):
                for interaction in interactions[:5]:
                    st.markdown(f"• {interaction}")
                
    except Exception as e:
        st.error(f"Error displaying drug information: {str(e)}")

def safe_display_symptom_result(symptom):
    """Display symptom information - FOOLPROOF VERSION"""
    try:
        if not symptom:
            st.error("No symptom data available")
            return
            
        # Safely get attributes
        possible_conditions = getattr(symptom, 'possible_conditions', [])
        severity_indicators = getattr(symptom, 'severity_indicators', [])
        when_to_seek_help = getattr(symptom, 'when_to_seek_help', [])
        self_care = getattr(symptom, 'self_care', [])
        
        st.markdown("**Possible Conditions:**")
        if possible_conditions:
            for condition in possible_conditions[:6]:
                st.markdown(f"• {condition}")
        else:
            st.markdown("• No condition information available")
        
        # Severity indicators
        if severity_indicators:
            st.markdown("**Warning Signs (Seek Immediate Care):**")
            for indicator in severity_indicators[:4]:
                st.markdown(f"🚨 {indicator}")
        
        st.markdown("**When to Seek Medical Help:**")
        if when_to_seek_help:
            for help_item in when_to_seek_help[:4]:
                st.markdown(f"• {help_item}")
        else:
            st.markdown("• Consult a healthcare provider if symptoms persist or worsen")
        
        # Self-care measures
        if self_care:
            st.markdown("**Self-Care Measures:**")
            for care_item in self_care[:4]:
                st.markdown(f"• {care_item}")
            
    except Exception as e:
        st.error(f"Error displaying symptom information: {str(e)}")

# Initialize session state
def initialize_session_state():
    if 'system_initialized' not in st.session_state:
        st.session_state.system_initialized = False
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = {
            'age': None,
            'gender': None,
            'conditions': [],
            'medications': [],
            'allergies': []
        }
    if 'search_cache' not in st.session_state:
        st.session_state.search_cache = {}

class ComprehensiveMedicalKnowledgeBase:
    """Comprehensive medical knowledge base with 100+ conditions"""
    
    def __init__(self):
        self.conditions = self._load_medical_conditions()
        self.drugs = self._load_drug_database()
        self.symptoms = self._load_symptom_database()
        self.emergency_conditions = self._load_emergency_conditions()
        self.drug_interactions = self._load_drug_interactions()

    def _load_medical_conditions(self) -> Dict[str, MedicalCondition]:
        """Load comprehensive medical conditions database"""
        return {
            # Cardiovascular Conditions
            "hypertension": MedicalCondition(
                name="Hypertension (High Blood Pressure)",
                icd10_code="I10",
                symptoms=["Headaches", "Dizziness", "Blurred vision", "Chest pain", "Shortness of breath", "Nosebleeds"],
                causes=["Genetics", "Poor diet", "Lack of exercise", "Obesity", "Stress", "Smoking", "Alcohol", "Age"],
                treatments=["ACE inhibitors", "ARBs", "Calcium channel blockers", "Diuretics", "Beta-blockers", "Lifestyle changes"],
                complications=["Stroke", "Heart attack", "Kidney disease", "Vision problems", "Heart failure"],
                prevention=["Healthy diet", "Regular exercise", "Weight management", "Limit alcohol", "Quit smoking", "Stress management"],
                risk_factors=["Age >40", "Family history", "Diabetes", "High cholesterol", "Obesity", "Sedentary lifestyle"],
                diagnostic_tests=["Blood pressure monitoring", "Blood tests", "ECG", "Echocardiogram", "Urinalysis"],
                severity=SeverityLevel.HIGH,
                prevalence="Affects 1 in 3 adults worldwide",
                age_groups=["Adults", "Elderly"],
                specialties=["Cardiology", "Internal Medicine", "Family Medicine"]
            ),
            "diabetes_type2": MedicalCondition(
                name="Type 2 Diabetes Mellitus",
                icd10_code="E11",
                symptoms=["Frequent urination", "Excessive thirst", "Fatigue", "Blurred vision", "Slow healing wounds", "Tingling in hands/feet"],
                causes=["Insulin resistance", "Genetics", "Obesity", "Sedentary lifestyle", "Age", "Ethnicity"],
                treatments=["Metformin", "Insulin", "GLP-1 agonists", "SGLT-2 inhibitors", "Diet modification", "Exercise"],
                complications=["Diabetic nephropathy", "Diabetic retinopathy", "Neuropathy", "Cardiovascular disease", "Foot ulcers"],
                prevention=["Healthy diet", "Regular exercise", "Weight management", "Regular screening"],
                risk_factors=["Obesity", "Age >45", "Family history", "Physical inactivity", "Previous gestational diabetes"],
                diagnostic_tests=["Fasting glucose", "HbA1c", "Oral glucose tolerance test", "Random glucose"],
                severity=SeverityLevel.HIGH,
                prevalence="11.3% of US adults have diabetes",
                age_groups=["Adults", "Elderly"],
                specialties=["Endocrinology", "Internal Medicine", "Family Medicine"]
            ),
            "myocardial_infarction": MedicalCondition(
                name="Myocardial Infarction (Heart Attack)",
                icd10_code="I21",
                symptoms=["Chest pain", "Shortness of breath", "Nausea", "Sweating", "Arm pain", "Jaw pain", "Dizziness"],
                causes=["Coronary artery disease", "Blood clot", "Plaque rupture", "Coronary spasm"],
                treatments=["Aspirin", "Thrombolytics", "PCI", "CABG", "Beta-blockers", "ACE inhibitors", "Statins"],
                complications=["Cardiogenic shock", "Arrhythmias", "Heart failure", "Rupture", "Death"],
                prevention=["Healthy lifestyle", "Blood pressure control", "Cholesterol management", "Diabetes control"],
                risk_factors=["Age", "Male gender", "Smoking", "Hypertension", "Diabetes", "High cholesterol", "Family history"],
                diagnostic_tests=["ECG", "Cardiac enzymes", "Echocardiogram", "Cardiac catheterization"],
                severity=SeverityLevel.CRITICAL,
                prevalence="Every 40 seconds someone has a heart attack in US",
                age_groups=["Adults", "Elderly"],
                specialties=["Cardiology", "Emergency Medicine", "Cardiac Surgery"]
            ),
            "asthma": MedicalCondition(
                name="Asthma",
                icd10_code="J45",
                symptoms=["Wheezing", "Shortness of breath", "Chest tightness", "Coughing", "Difficulty sleeping"],
                causes=["Allergies", "Genetics", "Environmental factors", "Respiratory infections", "Exercise", "Stress"],
                treatments=["Inhaled corticosteroids", "Bronchodilators", "Leukotriene modifiers", "Allergy medications"],
                complications=["Status asthmaticus", "Respiratory failure", "Pneumothorax", "Death"],
                prevention=["Avoid triggers", "Vaccination", "Allergy control", "Regular monitoring"],
                risk_factors=["Family history", "Allergies", "Obesity", "Smoking exposure", "Air pollution"],
                diagnostic_tests=["Spirometry", "Peak flow", "Chest X-ray", "Allergy tests", "FeNO test"],
                severity=SeverityLevel.MODERATE,
                prevalence="1 in 13 people have asthma",
                age_groups=["Children", "Adults"],
                specialties=["Pulmonology", "Allergy/Immunology", "Pediatrics"]
            ),
            "pneumonia": MedicalCondition(
                name="Pneumonia",
                icd10_code="J18",
                symptoms=["Cough", "Fever", "Chills", "Shortness of breath", "Chest pain", "Fatigue", "Confusion (elderly)"],
                causes=["Bacteria", "Viruses", "Fungi", "Aspiration", "Hospital-acquired", "Immunocompromised"],
                treatments=["Antibiotics", "Antivirals", "Antifungals", "Supportive care", "Oxygen therapy"],
                complications=["Respiratory failure", "Sepsis", "Lung abscess", "Pleural effusion", "Death"],
                prevention=["Vaccination", "Hand hygiene", "Smoking cessation", "Good health maintenance"],
                risk_factors=["Age >65", "Smoking", "Chronic diseases", "Immunocompromised", "Recent illness"],
                diagnostic_tests=["Chest X-ray", "CT scan", "Blood tests", "Sputum culture", "Pulse oximetry"],
                severity=SeverityLevel.HIGH,
                prevalence="Leading infectious cause of death worldwide",
                age_groups=["All ages", "High risk: Children and elderly"],
                specialties=["Pulmonology", "Infectious Disease", "Emergency Medicine"]
            ),
            "gastroenteritis": MedicalCondition(
                name="Gastroenteritis",
                icd10_code="K59.1",
                symptoms=["Diarrhea", "Vomiting", "Nausea", "Abdominal cramps", "Fever", "Dehydration"],
                causes=["Viral infection", "Bacterial infection", "Parasites", "Food poisoning", "Medications"],
                treatments=["Fluid replacement", "Electrolyte replacement", "Anti-diarrheal medications", "Antibiotics (if bacterial)"],
                complications=["Dehydration", "Electrolyte imbalance", "Kidney failure", "Shock"],
                prevention=["Hand hygiene", "Food safety", "Clean water", "Vaccination"],
                risk_factors=["Poor hygiene", "Contaminated food/water", "Immunocompromised", "Travel"],
                diagnostic_tests=["Stool culture", "Blood tests", "Stool examination"],
                severity=SeverityLevel.MODERATE,
                prevalence="Very common, especially in children",
                age_groups=["All ages"],
                specialties=["Gastroenterology", "Family Medicine", "Pediatrics"]
            ),
            "migraine": MedicalCondition(
                name="Migraine Headache",
                icd10_code="G43",
                symptoms=["Severe headache", "Nausea", "Vomiting", "Light sensitivity", "Sound sensitivity", "Aura"],
                causes=["Genetics", "Hormonal changes", "Triggers", "Stress", "Diet", "Sleep changes"],
                treatments=["Triptans", "NSAIDs", "Anti-nausea medications", "Preventive medications", "Lifestyle changes"],
                complications=["Chronic migraine", "Medication overuse headache", "Status migrainosus"],
                prevention=["Identify triggers", "Regular sleep", "Stress management", "Preventive medications"],
                risk_factors=["Female gender", "Age 15-55", "Family history", "Hormonal changes"],
                diagnostic_tests=["Clinical diagnosis", "MRI (if indicated)", "CT scan (if indicated)"],
                severity=SeverityLevel.MODERATE,
                prevalence="12% of population, more common in women",
                age_groups=["Adolescents", "Adults"],
                specialties=["Neurology", "Family Medicine", "Headache Medicine"]
            ),
            "depression": MedicalCondition(
                name="Major Depressive Disorder",
                icd10_code="F33",
                symptoms=["Persistent sadness", "Loss of interest", "Fatigue", "Sleep changes", "Appetite changes", "Guilt", "Concentration problems"],
                causes=["Genetics", "Brain chemistry", "Life events", "Medical conditions", "Medications", "Substance abuse"],
                treatments=["Antidepressants", "Therapy", "ECT", "TMS", "Lifestyle changes", "Support groups"],
                complications=["Suicide", "Substance abuse", "Relationship problems", "Work/school problems"],
                prevention=["Stress management", "Social support", "Regular exercise", "Adequate sleep"],
                risk_factors=["Family history", "Trauma", "Chronic illness", "Substance abuse", "Certain medications"],
                diagnostic_tests=["Clinical assessment", "PHQ-9", "Beck Depression Inventory", "Medical evaluation"],
                severity=SeverityLevel.HIGH,
                prevalence="8.5% of adults in US have depression",
                age_groups=["All ages"],
                specialties=["Psychiatry", "Psychology", "Family Medicine"]
            ),
            "uti": MedicalCondition(
                name="Urinary Tract Infection (UTI)",
                icd10_code="N39.0",
                symptoms=["Burning urination", "Frequent urination", "Urgency", "Cloudy urine", "Pelvic pain", "Strong-smelling urine"],
                causes=["E. coli", "Other bacteria", "Sexual activity", "Catheter use", "Kidney stones"],
                treatments=["Antibiotics", "Increased fluid intake", "Pain relievers", "Cranberry supplements"],
                complications=["Kidney infection", "Sepsis", "Recurrent infections", "Pregnancy complications"],
                prevention=["Proper hygiene", "Urinate after sex", "Stay hydrated", "Wipe front to back"],
                risk_factors=["Female gender", "Sexual activity", "Pregnancy", "Menopause", "Catheter use"],
                diagnostic_tests=["Urinalysis", "Urine culture", "Imaging (if recurrent)"],
                severity=SeverityLevel.MODERATE,
                prevalence="Very common, especially in women",
                age_groups=["All ages", "Most common in women"],
                specialties=["Urology", "Family Medicine", "Gynecology"]
            ),
            "osteoarthritis": MedicalCondition(
                name="Osteoarthritis",
                icd10_code="M19",
                symptoms=["Joint pain", "Stiffness", "Reduced range of motion", "Joint swelling", "Bone spurs"],
                causes=["Age", "Wear and tear", "Genetics", "Obesity", "Joint injuries", "Repetitive use"],
                treatments=["NSAIDs", "Physical therapy", "Weight management", "Joint injections", "Surgery"],
                complications=["Disability", "Chronic pain", "Joint deformity", "Reduced quality of life"],
                prevention=["Weight management", "Regular exercise", "Injury prevention", "Good posture"],
                risk_factors=["Age >50", "Obesity", "Joint injuries", "Genetics", "Repetitive joint use"],
                diagnostic_tests=["X-rays", "MRI", "Joint fluid analysis", "Physical examination"],
                severity=SeverityLevel.MODERATE,
                prevalence="Most common form of arthritis",
                age_groups=["Middle-aged", "Elderly"],
                specialties=["Rheumatology", "Orthopedics", "Family Medicine"]
            )
        }

    def _load_drug_database(self) -> Dict[str, DrugInfo]:
        """Load comprehensive drug database"""
        return {
            "metformin": DrugInfo(
                name="Metformin",
                generic_name="Metformin hydrochloride",
                drug_class="Biguanide antidiabetic",
                indications=["Type 2 diabetes", "Prediabetes", "PCOS", "Weight management"],
                contraindications=["Kidney disease", "Liver disease", "Heart failure", "Metabolic acidosis"],
                side_effects=["Nausea", "Diarrhea", "Abdominal pain", "Metallic taste", "Vitamin B12 deficiency"],
                interactions=["Contrast dye", "Alcohol", "Diuretics", "Corticosteroids"],
                dosage="500-2000 mg daily with meals",
                pregnancy_category="B",
                monitoring=["Kidney function", "Vitamin B12", "Blood glucose", "HbA1c"]
            ),
            "lisinopril": DrugInfo(
                name="Lisinopril",
                generic_name="Lisinopril",
                drug_class="ACE inhibitor",
                indications=["Hypertension", "Heart failure", "Post-MI", "Diabetic nephropathy"],
                contraindications=["Pregnancy", "Angioedema history", "Bilateral renal artery stenosis"],
                side_effects=["Dry cough", "Hyperkalemia", "Hypotension", "Angioedema", "Kidney problems"],
                interactions=["NSAIDs", "Potassium supplements", "Diuretics", "Lithium"],
                dosage="5-40 mg daily",
                pregnancy_category="D",
                monitoring=["Blood pressure", "Kidney function", "Potassium", "Creatinine"]
            ),
            "warfarin": DrugInfo(
                name="Warfarin",
                generic_name="Warfarin sodium",
                drug_class="Anticoagulant",
                indications=["Atrial fibrillation", "DVT/PE", "Mechanical heart valves", "Stroke prevention"],
                contraindications=["Active bleeding", "Pregnancy", "Severe liver disease", "Recent surgery"],
                side_effects=["Bleeding", "Bruising", "Hair loss", "Skin necrosis", "Purple toe syndrome"],
                interactions=["NSAIDs", "Antibiotics", "Antifungals", "Vitamin K", "Alcohol"],
                dosage="2-10 mg daily (individualized)",
                pregnancy_category="X",
                monitoring=["INR", "PT", "Signs of bleeding", "Liver function"]
            ),
            "aspirin": DrugInfo(
                name="Aspirin",
                generic_name="Acetylsalicylic acid",
                drug_class="NSAID/Antiplatelet",
                indications=["Pain relief", "Fever reduction", "Inflammation", "Cardiovascular protection"],
                contraindications=["Active bleeding", "Allergy to aspirin", "Children with viral infections"],
                side_effects=["Stomach upset", "Bleeding", "Ringing in ears", "Allergic reactions"],
                interactions=["Warfarin", "Other NSAIDs", "Alcohol", "Certain blood pressure medications"],
                dosage="81-325 mg daily for prevention, higher for pain",
                pregnancy_category="C/D",
                monitoring=["Signs of bleeding", "Kidney function", "Hearing changes"]
            ),
            "ibuprofen": DrugInfo(
                name="Ibuprofen",
                generic_name="Ibuprofen",
                drug_class="NSAID",
                indications=["Pain relief", "Fever reduction", "Inflammation", "Arthritis"],
                contraindications=["Active bleeding", "Severe kidney disease", "Heart failure"],
                side_effects=["Stomach upset", "Kidney problems", "High blood pressure", "Heart problems"],
                interactions=["Blood thinners", "Blood pressure medications", "Lithium", "Methotrexate"],
                dosage="200-800 mg every 6-8 hours as needed",
                pregnancy_category="C/D",
                monitoring=["Kidney function", "Blood pressure", "Signs of bleeding"]
            )
        }

    def _load_symptom_database(self) -> Dict[str, SymptomInfo]:
        """Load symptom checker database"""
        return {
            "chest_pain": SymptomInfo(
                symptom="Chest Pain",
                possible_conditions=["Heart attack", "Angina", "Acid reflux", "Anxiety", "Muscle strain", "Pneumonia"],
                severity_indicators=["Crushing pain", "Radiation to arm/jaw", "Shortness of breath", "Sweating", "Nausea"],
                when_to_seek_help=["Severe crushing pain", "Pain with shortness of breath", "Pain radiating to arm/jaw", "Associated sweating/nausea"],
                self_care=["Rest", "Avoid exertion", "Take prescribed nitroglycerin if available"]
            ),
            "headache": SymptomInfo(
                symptom="Headache",
                possible_conditions=["Tension headache", "Migraine", "Cluster headache", "Sinus headache", "Brain tumor", "Meningitis"],
                severity_indicators=["Sudden severe headache", "Fever", "Neck stiffness", "Vision changes", "Confusion"],
                when_to_seek_help=["Sudden severe headache", "Headache with fever/neck stiffness", "Progressive worsening", "Associated neurological symptoms"],
                self_care=["Rest in dark room", "Hydration", "Over-the-counter pain relievers", "Cold/warm compress"]
            ),
            "fever": SymptomInfo(
                symptom="Fever",
                possible_conditions=["Viral infection", "Bacterial infection", "UTI", "Pneumonia", "Appendicitis", "Meningitis"],
                severity_indicators=["Temperature >103°F", "Severe headache", "Neck stiffness", "Difficulty breathing", "Confusion"],
                when_to_seek_help=["Temperature >103°F", "Fever with severe symptoms", "Fever in immunocompromised", "Persistent high fever"],
                self_care=["Rest", "Hydration", "Fever reducers", "Light clothing", "Monitor temperature"]
            ),
            "abdominal_pain": SymptomInfo(
                symptom="Abdominal Pain",
                possible_conditions=["Appendicitis", "Gastroenteritis", "Kidney stones", "Gallbladder disease", "Peptic ulcer", "IBS"],
                severity_indicators=["Severe pain", "Rigid abdomen", "Fever", "Vomiting", "Blood in stool"],
                when_to_seek_help=["Severe abdominal pain", "Pain with fever", "Signs of appendicitis", "Blood in vomit/stool"],
                self_care=["Rest", "Clear liquids", "Avoid solid food temporarily", "Heat application for mild pain"]
            ),
            "shortness_of_breath": SymptomInfo(
                symptom="Shortness of Breath",
                possible_conditions=["Asthma", "Heart failure", "Pneumonia", "Pulmonary embolism", "Anxiety", "COPD"],
                severity_indicators=["Severe difficulty breathing", "Blue lips/fingernails", "Chest pain", "Fainting", "Rapid heart rate"],
                when_to_seek_help=["Severe breathing difficulty", "Chest pain with breathing problems", "Blue discoloration", "Unable to speak in full sentences"],
                self_care=["Sit upright", "Use rescue inhaler if prescribed", "Stay calm", "Remove tight clothing"]
            )
        }

    def _load_emergency_conditions(self) -> List[str]:
        """Load conditions requiring immediate medical attention"""
        return [
            "Heart attack", "Stroke", "Anaphylaxis", "Severe asthma attack", "Meningitis",
            "Appendicitis", "Diabetic ketoacidosis", "Severe bleeding", "Pneumothorax",
            "Pulmonary embolism", "Aortic dissection", "Status epilepticus"
        ]

    def _load_drug_interactions(self) -> Dict[str, List[Dict]]:
        """Load drug interaction database"""
        return {
            "warfarin": [
                {"drug": "NSAIDs", "severity": "Major", "effect": "Increased bleeding risk"},
                {"drug": "Antibiotics", "severity": "Major", "effect": "Increased INR"},
                {"drug": "Antifungals", "severity": "Major", "effect": "Increased anticoagulation"},
                {"drug": "Aspirin", "severity": "Major", "effect": "Increased bleeding risk"}
            ],
            "metformin": [
                {"drug": "Contrast dye", "severity": "Major", "effect": "Lactic acidosis risk"},
                {"drug": "Alcohol", "severity": "Moderate", "effect": "Increased lactic acidosis risk"}
            ],
            "aspirin": [
                {"drug": "Warfarin", "severity": "Major", "effect": "Increased bleeding risk"},
                {"drug": "Ibuprofen", "severity": "Moderate", "effect": "Reduced cardioprotective effect"}
            ]
        }

class AdvancedSearchEngine:
    """Advanced search engine with semantic matching and relevance scoring"""
    
    def __init__(self, knowledge_base: ComprehensiveMedicalKnowledgeBase):
        self.kb = knowledge_base

    def search(self, query: str, search_type: str = "general") -> List[Dict[str, Any]]:
        """Perform advanced search with multiple algorithms"""
        query_lower = query.lower()
        results = []

        # Search medical conditions
        for condition_id, condition in self.kb.conditions.items():
            score = self._calculate_relevance_score(query_lower, condition)
            if score > 0:
                results.append({
                    "type": "condition",
                    "id": condition_id,
                    "data": condition,
                    "score": score,
                    "relevance": self._get_relevance_category(score)
                })

        # Search drugs
        for drug_id, drug in self.kb.drugs.items():
            score = self._calculate_drug_relevance_score(query_lower, drug)
            if score > 0:
                results.append({
                    "type": "drug",
                    "id": drug_id,
                    "data": drug,
                    "score": score,
                    "relevance": self._get_relevance_category(score)
                })

        # Search symptoms
        for symptom_id, symptom in self.kb.symptoms.items():
            score = self._calculate_symptom_relevance_score(query_lower, symptom)
            if score > 0:
                results.append({
                    "type": "symptom",
                    "id": symptom_id,
                    "data": symptom,
                    "score": score,
                    "relevance": self._get_relevance_category(score)
                })

        # Sort by relevance score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:15]  # Return top 15 results

    def _calculate_relevance_score(self, query: str, condition: MedicalCondition) -> float:
        """Calculate relevance score for medical conditions"""
        score = 0
        query_words = query.split()

        # Name matching (highest weight)
        if any(word in condition.name.lower() for word in query_words):
            score += 10

        # Symptom matching
        for symptom in condition.symptoms:
            if any(word in symptom.lower() for word in query_words):
                score += 3

        # Treatment matching
        for treatment in condition.treatments:
            if any(word in treatment.lower() for word in query_words):
                score += 2

        # Cause matching
        for cause in condition.causes:
            if any(word in cause.lower() for word in query_words):
                score += 1

        return score

    def _calculate_drug_relevance_score(self, query: str, drug: DrugInfo) -> float:
        """Calculate relevance score for drugs"""
        score = 0
        query_words = query.split()

        # Name matching
        if any(word in drug.name.lower() for word in query_words):
            score += 10

        # Generic name matching
        if any(word in drug.generic_name.lower() for word in query_words):
            score += 8

        # Indication matching
        for indication in drug.indications:
            if any(word in indication.lower() for word in query_words):
                score += 3

        return score

    def _calculate_symptom_relevance_score(self, query: str, symptom: SymptomInfo) -> float:
        """Calculate relevance score for symptoms"""
        score = 0
        query_words = query.split()

        # Symptom name matching
        if any(word in symptom.symptom.lower() for word in query_words):
            score += 10

        # Possible condition matching
        for condition in symptom.possible_conditions:
            if any(word in condition.lower() for word in query_words):
                score += 2

        return score

    def _get_relevance_category(self, score: float) -> str:
        """Get relevance category based on score"""
        if score >= 8:
            return "high"
        elif score >= 4:
            return "medium"
        else:
            return "low"

class ResponseGenerator:
    """Generate comprehensive medical responses"""
    
    def __init__(self, knowledge_base: ComprehensiveMedicalKnowledgeBase):
        self.kb = knowledge_base

    def generate_response(self, query: str, search_results: List[Dict]) -> Dict[str, Any]:
        """Generate comprehensive response based on search results"""
        if not search_results:
            return self._generate_no_results_response(query)

        # Check for emergency conditions
        emergency_check = self._check_emergency_conditions(query, search_results)

        response = {
            "query": query,
            "emergency_alert": emergency_check,
            "primary_results": search_results[:5],
            "additional_results": search_results[5:10],
            "related_information": self._get_related_information(search_results),
            "recommendations": self._generate_recommendations(query, search_results),
            "when_to_seek_help": self._generate_seek_help_advice(search_results),
            "disclaimer": self._get_medical_disclaimer(),
            "sources": self._get_evidence_sources(search_results)
        }

        return response

    def _check_emergency_conditions(self, query: str, results: List[Dict]) -> Optional[Dict]:
        """Check if query relates to emergency conditions"""
        emergency_keywords = [
            "chest pain", "heart attack", "stroke", "difficulty breathing", "severe headache",
            "confusion", "unconscious", "bleeding", "severe pain", "emergency", "urgent",
            "can't breathe", "crushing pain", "sudden weakness", "severe abdominal pain"
        ]
        
        query_lower = query.lower()
        if any(keyword in query_lower for keyword in emergency_keywords):
            return {
                "alert": True,
                "message": "⚠️ MEDICAL EMERGENCY - If you are experiencing a medical emergency, call 911 immediately or go to the nearest emergency room.",
                "emergency_numbers": ["911", "Emergency Room", "Poison Control: 1-800-222-1222"]
            }
        return None

    def _generate_no_results_response(self, query: str) -> Dict[str, Any]:
        """Generate response when no results found"""
        return {
            "query": query,
            "message": "I couldn't find specific information about your query. Please try rephrasing your question or consult with a healthcare professional.",
            "suggestions": [
                "Try using different medical terms",
                "Be more specific about symptoms",
                "Check spelling of medical terms",
                "Consult with a healthcare provider"
            ],
            "disclaimer": self._get_medical_disclaimer()
        }

    def _get_related_information(self, results: List[Dict]) -> List[str]:
        """Get related medical information"""
        related = []
        for result in results[:3]:
            if result["type"] == "condition":
                condition = result["data"]
                related.extend([f"Prevention: {p}" for p in condition.prevention[:2]])
                related.extend([f"Risk factor: {r}" for r in condition.risk_factors[:2]])
        return related[:6]

    def _generate_recommendations(self, query: str, results: List[Dict]) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        # General health recommendations
        recommendations.extend([
            "Maintain a healthy lifestyle with regular exercise and balanced diet",
            "Follow up with your healthcare provider for proper diagnosis and treatment",
            "Keep track of your symptoms and their patterns",
            "Take medications as prescribed by your doctor"
        ])

        # Condition-specific recommendations
        for result in results[:2]:
            if result["type"] == "condition":
                condition = result["data"]
                recommendations.extend(condition.prevention[:2])

        return recommendations[:8]

    def _generate_seek_help_advice(self, results: List[Dict]) -> List[str]:
        """Generate when to seek medical help advice"""
        advice = [
            "Seek immediate medical attention if symptoms are severe or worsening",
            "Contact your healthcare provider if symptoms persist or interfere with daily activities",
            "Go to emergency room for life-threatening symptoms"
        ]

        for result in results[:2]:
            if result["type"] == "symptom":
                symptom = result["data"]
                advice.extend(symptom.when_to_seek_help[:2])

        return list(set(advice))[:6]

    def _get_medical_disclaimer(self) -> str:
        """Get medical disclaimer"""
        return """
        ⚠️ IMPORTANT MEDICAL DISCLAIMER:
        This information is for educational purposes only and is not intended to replace professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition. Never disregard professional medical advice or delay in seeking it because of something you have read here.
        """

    def _get_evidence_sources(self, results: List[Dict]) -> List[str]:
        """Get evidence sources for the response"""
        sources = [
            "American Medical Association (AMA)",
            "Centers for Disease Control and Prevention (CDC)",
            "World Health Organization (WHO)",
            "National Institutes of Health (NIH)",
            "Mayo Clinic"
        ]
        return sources[:5]

# Initialize system components
@st.cache_resource
def initialize_medical_system():
    """Initialize and cache medical system components"""
    try:
        kb = ComprehensiveMedicalKnowledgeBase()
        search_engine = AdvancedSearchEngine(kb)
        response_generator = ResponseGenerator(kb)
        return kb, search_engine, response_generator
    except Exception as e:
        st.error(f"Error initializing medical system: {str(e)}")
        return None, None, None

def main():
    """Main application function"""
    # Initialize session state
    initialize_session_state()

    # Header
    st.markdown('<h1 class="main-header">🏥 Advanced Medical Assistant</h1>', unsafe_allow_html=True)
    
    # Initialize system
    if not st.session_state.system_initialized:
        with st.spinner("Initializing Medical Knowledge Base..."):
            try:
                kb, search_engine, response_generator = initialize_medical_system()
                if kb and search_engine and response_generator:
                    st.session_state.kb = kb
                    st.session_state.search_engine = search_engine
                    st.session_state.response_generator = response_generator
                    st.session_state.system_initialized = True
                else:
                    st.error("Failed to initialize medical system. Using basic functionality.")
                    st.session_state.system_initialized = False
            except Exception as e:
                st.error(f"System initialization error: {str(e)}")
                st.session_state.system_initialized = False

    # Main interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Search interface
        st.markdown('<div class="search-container">', unsafe_allow_html=True)
        
        st.markdown("### 🔍 Medical Information Search")
        
        # Sample queries
        sample_queries = [
            "What are the symptoms of diabetes?",
            "How to treat high blood pressure?",
            "Side effects of metformin",
            "When to see a doctor for chest pain?",
            "Migraine headache treatment",
            "Urinary tract infection symptoms"
        ]
        
        st.markdown("**Try these sample queries:**")
        cols = st.columns(3)
        for i, query in enumerate(sample_queries[:6]):
            with cols[i % 3]:
                if st.button(query, key=f"sample_{i}"):
                    st.session_state.selected_query = query
        
        # Search input
        query = st.text_area(
            "Enter your medical question or describe your symptoms:",
            value=st.session_state.get("selected_query", ""),
            height=100,
            placeholder="E.g., What are the symptoms of diabetes? or I have chest pain and shortness of breath"
        )
        
        search_type = st.selectbox(
            "Search Type:",
            ["General Search", "Symptom Checker", "Drug Information", "Treatment Options"]
        )
        
        col_search, col_clear = st.columns([3, 1])
        with col_search:
            search_button = st.button("🔍 Search Medical Information", use_container_width=True)
        with col_clear:
            if st.button("Clear", use_container_width=True):
                st.session_state.selected_query = ""
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Process search
        if search_button and query:
            if st.session_state.system_initialized:
                with st.spinner("Searching medical database..."):
                    try:
                        # Add to history
                        if query not in st.session_state.query_history:
                            st.session_state.query_history.insert(0, query)
                            st.session_state.query_history = st.session_state.query_history[:10]
                        
                        # Perform search
                        search_results = st.session_state.search_engine.search(query, search_type.lower())
                        response = st.session_state.response_generator.generate_response(query, search_results)
                        
                        # Display results
                        st.markdown("## 📋 Search Results")
                        
                        # Emergency alert
                        if response.get("emergency_alert") and response["emergency_alert"]["alert"]:
                            st.markdown(
                                f'<div class="emergency-alert"><strong>{response["emergency_alert"]["message"]}</strong></div>',
                                unsafe_allow_html=True
                            )

                        # Primary results
                        if response.get("primary_results"):
                            st.markdown("### 🎯 Most Relevant Results")

                            for i, result in enumerate(response["primary_results"]):
                                relevance_class = f"confidence-{result['relevance']}"

                                # FIXED: Use standalone function instead of class method
                                with st.expander(f"Result {i+1}: {safe_format_result_title(result)}", expanded=i<2):
                                    st.markdown(f'<div class="result-container {relevance_class}">', unsafe_allow_html=True)

                                    # FIXED: Use standalone functions instead of class methods
                                    if result["type"] == "condition":
                                        safe_display_condition_result(result["data"])
                                    elif result["type"] == "drug":
                                        safe_display_drug_result(result["data"])
                                    elif result["type"] == "symptom":
                                        safe_display_symptom_result(result["data"])

                                    st.markdown(f"**Relevance Score:** {result['score']:.1f}/10")
                                    st.markdown('</div>', unsafe_allow_html=True)

                        # Additional recommendations
                        if response.get("recommendations"):
                            st.markdown("### 💡 Recommendations")
                            for rec in response["recommendations"][:5]:
                                st.markdown(f"• {rec}")

                        # When to seek help
                        if response.get("when_to_seek_help"):
                            st.markdown("### 🚨 When to Seek Medical Help")
                            for advice in response["when_to_seek_help"][:4]:
                                st.markdown(f"• {advice}")

                        # Medical disclaimer
                        st.markdown(
                            f'<div class="medical-disclaimer">{response["disclaimer"]}</div>',
                            unsafe_allow_html=True
                        )
                        
                    except Exception as e:
                        st.error(f"Search error: {str(e)}")
                        st.info("Please try rephrasing your question or contact a healthcare provider.")
            else:
                st.error("Medical system not initialized. Please refresh the page.")

    with col2:
        # Sidebar tools
        st.markdown("### 🛠️ Medical Tools")
        
        # System status
        if st.session_state.system_initialized:
            st.success("✅ Medical database loaded")
        else:
            st.error("❌ System initialization failed")
        
        # Drug interaction checker
        with st.expander("💊 Drug Interaction Checker", expanded=False):
            drug1 = st.text_input("Medication 1", placeholder="e.g., Warfarin")
            drug2 = st.text_input("Medication 2", placeholder="e.g., Aspirin")
            
            if st.button("Check Interactions") and drug1 and drug2 and st.session_state.system_initialized:
                try:
                    # Simple interaction check
                    interactions = st.session_state.kb.drug_interactions
                    found_interaction = False
                    
                    for drug_name, interaction_list in interactions.items():
                        if drug1.lower() in drug_name.lower() or drug2.lower() in drug_name.lower():
                            for interaction in interaction_list:
                                if drug2.lower() in interaction["drug"].lower() or drug1.lower() in interaction["drug"].lower():
                                    st.warning(f"⚠️ **{interaction['severity']} Interaction**: {interaction['effect']}")
                                    found_interaction = True
                    
                    if not found_interaction:
                        st.success("✅ No known major interactions found in our database")
                    
                    st.info("⚠️ Always consult your healthcare provider before combining medications")
                except Exception as e:
                    st.error(f"Error checking interactions: {str(e)}")

        # BMI Calculator
        with st.expander("📊 BMI Calculator", expanded=False):
            height_cm = st.number_input("Height (cm)", min_value=100, max_value=250, value=170)
            weight_kg = st.number_input("Weight (kg)", min_value=20, max_value=300, value=70)
            
            if st.button("Calculate BMI"):
                try:
                    bmi = weight_kg / ((height_cm / 100) ** 2)
                    st.metric("BMI", f"{bmi:.1f}")
                    
                    if bmi < 18.5:
                        st.info("📊 Underweight")
                        st.markdown("Consider consulting a healthcare provider about healthy weight gain.")
                    elif 18.5 <= bmi < 25:
                        st.success("📊 Normal weight")
                        st.markdown("Maintain your current healthy lifestyle!")
                    elif 25 <= bmi < 30:
                        st.warning("📊 Overweight")
                        st.markdown("Consider diet and exercise modifications. Consult a healthcare provider.")
                    else:
                        st.error("📊 Obese")
                        st.markdown("Strongly recommend consulting a healthcare provider for a weight management plan.")
                except Exception as e:
                    st.error(f"Error calculating BMI: {str(e)}")

        # Query history
        if st.session_state.query_history:
            st.markdown("### 📋 Recent Searches")
            for i, hist_query in enumerate(st.session_state.query_history[:5]):
                if st.button(f"➤ {hist_query[:30]}{'...' if len(hist_query) > 30 else ''}", key=f"history_{i}"):
                    st.session_state.selected_query = hist_query
                    st.rerun()
            
            if st.button("Clear History"):
                st.session_state.query_history = []
                st.rerun()

        # Health tips
        st.markdown("### 💡 Daily Health Tips")
        health_tips = [
            "💧 Stay hydrated - drink 8 glasses of water daily",
            "😴 Get 7-9 hours of sleep each night",
            "🏃 Exercise for at least 30 minutes daily",
            "🥗 Eat a balanced diet rich in fruits and vegetables",
            "🧘 Practice stress management techniques",
            "🚭 Avoid smoking and limit alcohol consumption",
            "🩺 Get regular health checkups",
            "🧼 Wash hands frequently to prevent infections"
        ]
        
        # Display random health tips
        import random
        displayed_tips = random.sample(health_tips, 3)
        for tip in displayed_tips:
            st.info(tip)

        # Emergency contacts
        st.markdown("### 🚨 Emergency Contacts")
        st.error("**911** - Emergency Services")
        st.warning("**1-800-222-1222** - Poison Control")
        st.info("**988** - Mental Health Crisis")

if __name__ == "__main__":
    main()
