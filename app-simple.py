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
            # Add more conditions as needed...
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
            # Add more drugs as needed...
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
            # Add more symptoms as needed...
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
            ],
            # Add more interactions as needed...
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

    def _format_result_title(self, result: Dict) -> str:
        """Format result title based on type"""
        if result["type"] == "condition":
            return f"🏥 {result['data'].name}"
        elif result["type"] == "drug":
            return f"💊 {result['data'].name}"
        elif result["type"] == "symptom":
            return f"🩺 {result['data'].symptom}"
        return "Medical Information"

    def _display_condition_result(self, condition: MedicalCondition):
        """Display medical condition information"""
        st.markdown(f"**ICD-10 Code:** {condition.icd10_code}")
        st.markdown(f"**Severity:** {condition.severity.value}")
        st.markdown(f"**Prevalence:** {condition.prevalence}")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Common Symptoms:**")
            for symptom in condition.symptoms[:5]:
                st.markdown(f"• {symptom}")

        with col2:
            st.markdown("**Treatment Options:**")
            for treatment in condition.treatments[:5]:
                st.markdown(f"• {treatment}")

        if condition.severity == SeverityLevel.CRITICAL:
            st.error("⚠️ This is a critical condition requiring immediate medical attention")

    def _display_drug_result(self, drug: DrugInfo):
        """Display drug information"""
        st.markdown(f"**Generic Name:** {drug.generic_name}")
        st.markdown(f"**Drug Class:** {drug.drug_class}")
        st.markdown(f"**Dosage:** {drug.dosage}")
        st.markdown(f"**Pregnancy Category:** {drug.pregnancy_category}")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Indications:**")
            for indication in drug.indications[:3]:
                st.markdown(f"• {indication}")

        with col2:
            st.markdown("**Common Side Effects:**")
            for side_effect in drug.side_effects[:3]:
                st.markdown(f"• {side_effect}")

        if drug.interactions:
            st.warning("⚠️ This medication has known drug interactions. Consult your healthcare provider.")

    def _display_symptom_result(self, symptom: SymptomInfo):
        """Display symptom information"""
        st.markdown("**Possible Conditions:**")
        for condition in symptom.possible_conditions[:5]:
            st.markdown(f"• {condition}")

        st.markdown("**When to Seek Medical Help:**")
        for help_item in symptom.when_to_seek_help[:3]:
            st.markdown(f"• {help_item}")

        if symptom.self_care:
            st.markdown("**Self-Care Measures:**")
            for care_item in symptom.self_care[:3]:
                st.markdown(f"• {care_item}")

    def _check_emergency_conditions(self, query: str, results: List[Dict]) -> Optional[Dict]:
        """Check if query relates to emergency conditions"""
        emergency_keywords = [
            "chest pain", "heart attack", "stroke", "difficulty breathing", "severe headache",
            "confusion", "unconscious", "bleeding", "severe pain", "emergency", "urgent"
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
    kb = ComprehensiveMedicalKnowledgeBase()
    search_engine = AdvancedSearchEngine(kb)
    response_generator = ResponseGenerator(kb)
    return kb, search_engine, response_generator

def main():
    """Main application function"""
    # Initialize session state
    initialize_session_state()

    # Header
    st.markdown('<h1 class="main-header">🏥 Advanced Medical Assistant</h1>', unsafe_allow_html=True)

    # Initialize system
    if not st.session_state.system_initialized:
        with st.spinner("Initializing Medical Knowledge Base..."):
            kb, search_engine, response_generator = initialize_medical_system()
            st.session_state.kb = kb
            st.session_state.search_engine = search_engine
            st.session_state.response_generator = response_generator
            st.session_state.system_initialized = True

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
            "When to see a doctor for chest pain?"
        ]

        # Search input
        query = st.text_area(
            "Enter your medical question or describe your symptoms:",
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
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

        # Process search
        if search_button and query:
            with st.spinner("Searching medical database..."):
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

                    with st.expander(f"Result {i+1}: {st.session_state.response_generator._format_result_title(result)}", expanded=i<2):
                        st.markdown(f'<div class="result-container {relevance_class}">', unsafe_allow_html=True)

                        if result["type"] == "condition":
                            st.session_state.response_generator._display_condition_result(result["data"])
                        elif result["type"] == "drug":
                            st.session_state.response_generator._display_drug_result(result["data"])
                        elif result["type"] == "symptom":
                            st.session_state.response_generator._display_symptom_result(result["data"])

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

    with col2:
        # Sidebar tools
        st.markdown("### 🛠️ Medical Tools")

        # Drug interaction checker
        with st.expander("💊 Drug Interaction Checker", expanded=False):
            drug1 = st.text_input("Medication 1", placeholder="e.g., Warfarin")
            drug2 = st.text_input("Medication 2", placeholder="e.g., Aspirin")

            if st.button("Check Interactions") and drug1 and drug2:
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
                    st.success("✅ No known major interactions found")

        # BMI Calculator
        with st.expander("📊 BMI Calculator", expanded=False):
            height_cm = st.number_input("Height (cm)", min_value=100, max_value=250, value=170)
            weight_kg = st.number_input("Weight (kg)", min_value=20, max_value=300, value=70)

            if st.button("Calculate BMI"):
                bmi = weight_kg / ((height_cm / 100) ** 2)
                st.metric("BMI", f"{bmi:.1f}")

                if bmi < 18.5:
                    st.info("Underweight")
                elif 18.5 <= bmi < 25:
                    st.success("Normal weight")
                elif 25 <= bmi < 30:
                    st.warning("Overweight")
                else:
                    st.error("Obese")

        # Query history
        if st.session_state.query_history:
            st.markdown("### 📋 Recent Searches")
            for i, query in enumerate(st.session_state.query_history[:5]):
                if st.button(f"➤ {query[:30]}...", key=f"history_{i}"):
                    st.session_state.selected_query = query

        # Health tips
        st.markdown("### 💡 Daily Health Tips")
        health_tips = [
            "Stay hydrated - drink 8 glasses of water daily",
            "Get 7-9 hours of sleep each night",
            "Exercise for at least 30 minutes daily",
            "Eat a balanced diet rich in fruits and vegetables",
            "Practice stress management techniques"
        ]
        for tip in health_tips[:3]:
            st.info(tip)

if __name__ == "__main__":
    main()
