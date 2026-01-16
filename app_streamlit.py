"""
Streamlit Frontend for AI-Powered Adverse Drug Reaction Narrative Generator
Professional UI for clinical case submission and report generation
"""

import streamlit as st
import os
from datetime import datetime, timedelta
import sys

# Import backend components
from rag_clinical import ClinicalRAGRetriever
from clinical_narrative_engine import ClinicalNarrativeGenerator


# Page configuration
st.set_page_config(
    page_title="ADR Clinical Narrative Generator",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f4788;
        text-align: center;
        padding: 1rem 0;
        border-bottom: 3px solid #1f4788;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1f4788;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-left: 4px solid #1f4788;
        padding-left: 1rem;
    }
    .info-box {
        background-color: #f0f8ff;
        border-left: 4px solid #4169e1;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f4788;
        color: white;
        font-weight: 600;
        padding: 0.75rem;
        font-size: 1.1rem;
    }
    .stButton>button:hover {
        background-color: #163861;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'narrative' not in st.session_state:
        st.session_state.narrative = None
    if 'report_path' not in st.session_state:
        st.session_state.report_path = None
    if 'processing' not in st.session_state:
        st.session_state.processing = False


def validate_api_keys():
    """Validate required API keys"""
    mongo_uri = os.getenv("MONGO_URI")
    groq_key = os.getenv("GROQ_API_KEY")
    
    missing = []
    if not mongo_uri or mongo_uri == "your-mongodb-atlas-uri":
        missing.append("MONGO_URI")
    if not groq_key or groq_key == "your-groq-api-key":
        missing.append("GROQ_API_KEY")
    
    return missing


def main():
    """Main application"""
    
    initialize_session_state()
    
    # Header
    st.markdown('<div class="main-header">🏥 AI-Powered Adverse Drug Reaction<br/>Clinical Narrative Generator</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Pharmacovigilance Decision Support System using RAG & Groq LLM</div>', unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.markdown("### ⚙️ System Configuration")
        
        # Check API keys
        missing_keys = validate_api_keys()
        
        if missing_keys:
            st.markdown('<div class="warning-box">', unsafe_allow_html=True)
            st.warning("⚠️ Missing API Keys")
            for key in missing_keys:
                st.code(f"export {key}='your-key-here'")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("### 📋 Setup Instructions")
            st.markdown("""
            1. Set environment variables for:
               - MONGO_URI
               - GROQ_API_KEY
            
            2. Run vector ingestion:
               ```bash
               python vector_ingestion.py
               ```
            
            3. Create vector index in MongoDB Atlas
            
            4. Launch application:
               ```bash
               streamlit run app_streamlit.py
               ```
            """)
        else:
            st.success("✅ All API keys configured")
        
        st.markdown("---")
        st.markdown("### 📊 System Info")
        st.info("""
        **Embedding Model:**  
        FastEmbed (all-MiniLM-L6-v2)
        
        **LLM:**  
        Groq Llama3-70B
        
        **Vector DB:**  
        MongoDB Atlas
        
        **Standards:**  
        ICH E2B Pharmacovigilance
        """)
        
        st.markdown("---")
        st.markdown("### ⚖️ Disclaimer")
        st.warning("""
        This AI system is a **clinical decision support tool** and does NOT:
        - Provide medical diagnosis
        - Replace physician judgment
        - Constitute treatment advice
        
        All cases must be reviewed by qualified healthcare professionals.
        """)
    
    # Main content
    if missing_keys:
        st.error("⚠️ Please configure API keys to use the system (see sidebar)")
        return
    
    # Input Form
    st.markdown('<div class="section-header">📝 Patient Case Information</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        patient_id = st.text_input(
            "Patient ID *",
            placeholder="PT-2024-001",
            help="Unique patient identifier"
        )
        
        age = st.number_input(
            "Age (years) *",
            min_value=18,
            max_value=120,
            value=65,
            help="Patient age in years"
        )
        
        gender = st.selectbox(
            "Gender *",
            options=["Male", "Female", "Other"],
            help="Patient gender"
        )
        
        drug_name = st.selectbox(
            "Drug Name *",
            options=[
                "Atorvastatin",
                "Lisinopril",
                "Metformin",
                "Sertraline",
                "Warfarin"
            ],
            help="Select the drug associated with adverse event"
        )
    
    with col2:
        start_date = st.date_input(
            "Drug Start Date *",
            value=datetime.now() - timedelta(days=60),
            max_value=datetime.now(),
            help="Date when drug was initiated"
        )
        
        stop_date = st.date_input(
            "Drug Stop Date *",
            value=datetime.now(),
            max_value=datetime.now(),
            help="Date when drug was discontinued"
        )
        
        # Calculate duration
        if stop_date >= start_date:
            duration_days = (stop_date - start_date).days
            st.info(f"📅 Treatment Duration: **{duration_days} days**")
        else:
            st.error("Stop date must be after start date")
            duration_days = 0
        
        stop_reason = st.selectbox(
            "Stop Reason (Adverse Event) *",
            options=[
                "Muscle pain",
                "Bleeding",
                "Confusion",
                "Palpitations",
                "Liver enzyme elevation",
                "Seizure",
                "Severe nausea",
                "Tremor",
                "Hypotension",
                "Arrhythmia",
                "Dark urine",
                "Weakness",
                "Dizziness",
                "Rash",
                "Headache"
            ],
            help="Symptom or event that led to drug discontinuation"
        )
    
    st.markdown("---")
    
    # Generate button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate_button = st.button(
            "🚀 Generate Clinical Narrative",
            disabled=st.session_state.processing or not patient_id or duration_days <= 0,
            type="primary"
        )
    
    # Process case
    if generate_button:
        st.session_state.processing = True
        
        with st.spinner("🔍 Retrieving medical knowledge from vector database..."):
            try:
                # Initialize RAG retriever
                retriever = ClinicalRAGRetriever(
                    mongo_uri=os.getenv("MONGO_URI")
                )
                
                # Retrieve context
                context = retriever.retrieve_for_case(
                    patient_id=patient_id,
                    drug_name=drug_name.lower(),
                    stop_reason=stop_reason,
                    age=age,
                    days=duration_days,
                    gender=gender
                )
                
                # Format context
                formatted_context = retriever.format_context_for_llm(context)
                
                st.success("✅ Medical knowledge retrieved successfully!")
                
            except Exception as e:
                st.error(f"❌ Error retrieving knowledge: {str(e)}")
                st.session_state.processing = False
                return
        
        with st.spinner("🤖 Generating clinical narrative with Groq LLM..."):
            try:
                # Initialize narrative generator
                generator = ClinicalNarrativeGenerator(
                    groq_api_key=os.getenv("GROQ_API_KEY")
                )
                
                # Generate narrative
                narrative = generator.generate_narrative(
                    patient_id=patient_id,
                    age=age,
                    gender=gender,
                    drug_name=drug_name,
                    days=duration_days,
                    stop_reason=stop_reason,
                    retrieved_context=formatted_context
                )
                
                # Save report
                report_path = generator.save_report(narrative, output_dir="reports")
                
                st.session_state.narrative = narrative
                st.session_state.report_path = report_path
                st.session_state.processing = False
                
                st.success("✅ Clinical narrative generated successfully!")
                
            except Exception as e:
                st.error(f"❌ Error generating narrative: {str(e)}")
                st.session_state.processing = False
                return
    
    # Display narrative
    if st.session_state.narrative:
        st.markdown("---")
        st.markdown('<div class="section-header">📄 Generated Clinical Narrative</div>', unsafe_allow_html=True)
        
        narrative = st.session_state.narrative
        
        # Summary cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Patient ID", narrative.patient_id)
        with col2:
            st.metric("Drug", narrative.drug_name)
        with col3:
            st.metric("Duration", f"{narrative.duration_days} days")
        with col4:
            st.metric("Adverse Event", narrative.stop_reason)
        
        st.markdown("---")
        
        # Full narrative in expandable section
        with st.expander("📋 **Full Clinical Narrative**", expanded=True):
            st.markdown(narrative.narrative)
        
        st.markdown("---")
        
        # Summary assessment
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🧬 Probable Syndrome")
            st.info(narrative.probable_syndrome)
            
            st.markdown("#### ⚠️ Seriousness Level")
            st.warning(narrative.seriousness_level)
        
        with col2:
            st.markdown("#### 🔬 Mechanistic Pathway")
            st.info(narrative.mechanism)
            
            st.markdown("#### ⚖️ Causality Category")
            st.success(narrative.causality_category)
        
        st.markdown("---")
        
        st.markdown("#### 💊 Clinical Recommendations")
        st.info(narrative.clinical_advice)
        
        st.markdown("---")
        
        # Download button
        if st.session_state.report_path and os.path.exists(st.session_state.report_path):
            with open(st.session_state.report_path, 'r', encoding='utf-8') as f:
                report_content = f.read()
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.download_button(
                    label="📥 Download Full Report (TXT)",
                    data=report_content,
                    file_name=f"clinical_report_{narrative.patient_id}.txt",
                    mime="text/plain",
                    type="primary"
                )
        
        # Reset button
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔄 Generate New Case"):
                st.session_state.narrative = None
                st.session_state.report_path = None
                st.rerun()


if __name__ == "__main__":
    main()
