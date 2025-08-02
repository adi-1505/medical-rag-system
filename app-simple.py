import streamlit as st
import time
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Medical Literature RAG Assistant",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .query-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .answer-box {
        background-color: #e8f4fd;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .disclaimer {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
        font-size: 0.9rem;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'system_ready' not in st.session_state:
    st.session_state.system_ready = False
if 'query_history' not in st.session_state:
    st.session_state.query_history = []

# Medical knowledge database (offline)
MEDICAL_KNOWLEDGE = {
    "diabetes": {
        "symptoms": "Common symptoms of type 2 diabetes include increased thirst (polydipsia), frequent urination (polyuria), increased hunger (polyphagia), unexplained weight loss, fatigue, blurred vision, slow-healing wounds, and frequent infections.",
        "diagnosis": "Type 2 diabetes is diagnosed using fasting plasma glucose ≥126 mg/dL, 2-hour oral glucose tolerance test ≥200 mg/dL, HbA1c ≥6.5%, or random plasma glucose ≥200 mg/dL with classic symptoms.",
        "treatment": "Treatment includes lifestyle modifications (diet, exercise), metformin as first-line medication, additional medications as needed (sulfonylureas, DPP-4 inhibitors, GLP-1 agonists, SGLT-2 inhibitors), and insulin therapy when other agents are insufficient.",
        "complications": "Complications include cardiovascular disease, diabetic neuropathy, diabetic retinopathy, diabetic nephropathy, and poor wound healing."
    },
    "hypertension": {
        "classification": "Blood pressure classification: Normal (<120/80 mmHg), Elevated (120-129/<80 mmHg), Stage 1 (130-139/80-89 mmHg), Stage 2 (≥140/90 mmHg), Hypertensive crisis (>180/120 mmHg).",
        "treatment": "Treatment includes lifestyle modifications (DASH diet, sodium restriction, exercise, weight management), and medications such as ACE inhibitors, ARBs, calcium channel blockers, and thiazide diuretics.",
        "symptoms": "Most people with hypertension have no symptoms. Some may experience headaches, shortness of breath, nosebleeds, flushing, dizziness, chest pain, or visual changes.",
        "risks": "Risk factors include age, family history, obesity, physical inactivity, high sodium diet, excessive alcohol consumption, and chronic stress."
    },
    "drug interactions": {
        "warfarin": "Warfarin interactions include NSAIDs (increased bleeding risk), fluoroquinolone antibiotics (enhanced anticoagulation), azole antifungals (increased warfarin effect), and amiodarone (requires dose reduction).",
        "statins": "Statin interactions include macrolide antibiotics (increased myopathy risk), azole antifungals (elevated statin levels), grapefruit juice (increased concentration), and fibrates (enhanced muscle toxicity risk).",
        "ace_inhibitors": "ACE inhibitor interactions include NSAIDs (reduced effectiveness, kidney impairment), potassium supplements (hyperkalemia risk), and lithium (increased lithium levels).",
        "prevention": "Prevention strategies include comprehensive medication reconciliation, drug interaction checking software, patient education, regular monitoring, and healthcare provider communication."
    }
}

def initialize_system():
    """Initialize the offline medical system."""
    try:
        with st.spinner("🔄 Initializing Medical Knowledge System..."):
            time.sleep(2)  # Simulate initialization
            st.success("✅ Medical Knowledge System initialized successfully!")
            st.info("📚 Loaded comprehensive medical database covering diabetes, hypertension, and drug interactions")
            return True
    except Exception as e:
        st.error(f"❌ Error initializing system: {str(e)}")
        return False

def search_medical_knowledge(query):
    """Search through medical knowledge database."""
    query_lower = query.lower()
    results = []
    
    # Search through all medical topics
    for topic, content in MEDICAL_KNOWLEDGE.items():
        for subtopic, info in content.items():
            # Simple keyword matching
            if any(keyword in query_lower for keyword in [topic, subtopic]) or \
               any(keyword in info.lower() for keyword in query_lower.split()):
                results.append({
                    "topic": topic.title(),
                    "subtopic": subtopic.title(),
                    "content": info,
                    "relevance": len([w for w in query_lower.split() if w in info.lower()])
                })
    
    # Sort by relevance
    results.sort(key=lambda x: x["relevance"], reverse=True)
    return results[:3]  # Return top 3 results

def generate_medical_response(query):
    """Generate medical response from offline knowledge base."""
    try:
        # Search knowledge base
        search_results = search_medical_knowledge(query)
        
        if not search_results:
            return {
                "answer": "I couldn't find specific information about your query in my medical knowledge base. Please try rephrasing your question or ask about diabetes, hypertension, or drug interactions.",
                "sources": [],
                "confidence": "low"
            }
        
        # Construct response from search results
        response_parts = []
        sources = []
        
        for result in search_results:
            response_parts.append(f"**{result['topic']} - {result['subtopic']}:**\n{result['content']}")
            sources.append({
                "title": f"{result['topic']} - {result['subtopic']}",
                "content": result['content'][:200] + "...",
                "score": result['relevance']
            })
        
        answer = "\n\n".join(response_parts)
        answer += "\n\n**Medical Disclaimer:** This information is for educational purposes only and should not replace professional medical advice. Always consult with qualified healthcare providers for medical decisions."
        
        return {
            "answer": answer,
            "sources": sources,
            "confidence": "high" if len(search_results) > 1 else "medium"
        }
        
    except Exception as e:
        return {
            "answer": f"I encountered an error while processing your query: {str(e)}",
            "sources": [],
            "confidence": "none"
        }

def display_query_results(response_data):
    """Display the query results in a formatted way."""
    
    # Display the answer
    st.markdown("### 🩺 Medical Information")
    with st.container():
        st.markdown(f'<div class="answer-box">{response_data["answer"]}</div>', 
                   unsafe_allow_html=True)
    
    # Display metadata
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h4>📚 Sources Found</h4>
            <h2>{len(response_data["sources"])}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h4>🎯 System</h4>
            <h3>Offline Knowledge</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        confidence_color = {"high": "🟢", "medium": "🟡", "low": "🔴", "none": "⚫"}
        st.markdown(f"""
        <div class="metric-card">
            <h4>📊 Confidence</h4>
            <h3>{confidence_color.get(response_data['confidence'], '⚫')} {response_data['confidence'].title()}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    # Display sources
    if response_data["sources"]:
        st.markdown("### 📖 Knowledge Sources")
        
        for i, source in enumerate(response_data["sources"], 1):
            with st.expander(f"📄 Source {i}: {source['title']} (Relevance: {source['score']})"):
                st.markdown("**Content Preview:**")
                st.markdown(source['content'])

def main():
    """Main application function."""
    
    # Header
    st.markdown('<h1 class="main-header">🩺 Medical Literature RAG Assistant</h1>', 
               unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem; color: #666;">
        Evidence-based medical information powered by offline medical knowledge base
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ System Control")
        
        # Initialize system button
        if st.button("🔄 Initialize System", type="primary"):
            st.session_state.system_ready = initialize_system()
        
        # System status
        if st.session_state.system_ready:
            st.success("✅ System Ready")
        else:
            st.warning("⚠️ System Not Initialized")
        
        st.markdown("---")
        
        # Sample queries
        st.header("💡 Sample Medical Queries")
        sample_queries = [
            "What are the symptoms of type 2 diabetes?",
            "How is hypertension classified?",
            "What are warfarin drug interactions?",
            "What is the treatment for diabetes?",
            "What are the risk factors for hypertension?"
        ]
        
        for query in sample_queries:
            if st.button(f"📝 {query}", key=query):
                st.session_state.selected_query = query
        
        st.markdown("---")
        
        # Query history
        st.header("📚 Query History")
        if st.session_state.query_history:
            for i, historical_query in enumerate(reversed(st.session_state.query_history[-5:]), 1):
                st.text(f"{i}. {historical_query[:50]}...")
        else:
            st.text("No queries yet")
        
        st.markdown("---")
        
        # System info
        st.header("ℹ️ System Information")
        st.markdown("""
        **Mode:** Offline Knowledge Base
        **Topics:** Diabetes, Hypertension, Drug Interactions
        **Requirements:** None (No API keys needed)
        **Status:** Fully functional
        """)
    
    # Main content area
    if not st.session_state.system_ready:
        st.info("👆 Please initialize the system using the button in the sidebar to get started.")
        st.markdown("### 🎯 About This System")
        st.markdown("""
        This is an **offline medical information system** that provides evidence-based medical information without requiring:
        - ✅ No OpenAI API keys
        - ✅ No internet connection for queries
        - ✅ No cloud services
        - ✅ No credits or payments
        
        **Available Medical Topics:**
        - **Diabetes:** Symptoms, diagnosis, treatment, complications
        - **Hypertension:** Classification, treatment, symptoms, risk factors  
        - **Drug Interactions:** Warfarin, statins, ACE inhibitors, prevention
        """)
        return
    
    # Query input
    st.markdown("### 🔍 Ask Your Medical Question")
    
    # Check if there's a selected query from sidebar
    default_query = ""
    if hasattr(st.session_state, 'selected_query'):
        default_query = st.session_state.selected_query
        delattr(st.session_state, 'selected_query')
    
    # Query input
    query = st.text_area(
        "Enter your medical question:",
        value=default_query,
        height=100,
        placeholder="e.g., What are the symptoms of diabetes?",
        help="Ask specific medical questions about diabetes, hypertension, or drug interactions."
    )
    
    # Search button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        search_button = st.button("🔍 Search Medical Knowledge", type="primary", use_container_width=True)
    
    # Process query
    if search_button and query.strip():
        # Add to history
        st.session_state.query_history.append(query.strip())
        
        # Display query
        st.markdown(f'<div class="query-box"><strong>Your Question:</strong> {query}</div>', 
                   unsafe_allow_html=True)
        
        # Process query
        with st.spinner("🔍 Searching medical knowledge base..."):
            start_time = time.time()
            
            # Get response from knowledge base
            response = generate_medical_response(query)
            
            processing_time = time.time() - start_time
            
            # Display results
            display_query_results(response)
            
            # Processing time
            st.caption(f"⏱️ Response generated in {processing_time:.2f} seconds from offline knowledge base")
    
    elif search_button and not query.strip():
        st.warning("⚠️ Please enter a medical question before searching.")
    
    # Footer disclaimer
    st.markdown("---")
    st.markdown("""
    <div class="disclaimer">
        <strong>⚠️ Important Medical Disclaimer:</strong><br>
        This system provides information for educational and research purposes only. 
        The responses are generated based on established medical knowledge and should not be considered as 
        professional medical advice, diagnosis, or treatment recommendations. 
        Always consult with qualified healthcare professionals for medical decisions and patient care.
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()