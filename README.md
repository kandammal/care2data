# 🏥 AI-Powered Adverse Drug Reaction Clinical Narrative Generator

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green.svg)](https://www.mongodb.com/atlas)
[![Groq](https://img.shields.io/badge/LLM-Groq-orange.svg)](https://groq.com/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-teal.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-red.svg)](https://streamlit.io/)

## 📋 Overview

A comprehensive **Clinical Decision Support System** that generates pharmacovigilance-grade adverse drug reaction (ADR) narratives using **Retrieval-Augmented Generation (RAG)**. The system combines vector-based medical knowledge retrieval from MongoDB Atlas with advanced LLM reasoning via Groq to produce regulatory-compliant clinical safety reports.

### 🎯 Key Features

- **🔬 RAG-Powered Knowledge Retrieval**: Semantic search across drug and syndrome knowledge bases
- **🤖 Groq LLM Integration**: Llama3-70B for medical reasoning and narrative generation
- **📊 Vector Database**: MongoDB Atlas with text-embedding-3-large embeddings
- **🏥 Pharmacovigilance Standards**: ICH E2B-compliant narratives with WHO-UMC causality assessment
- **🖥️ Dual Interface**: Streamlit UI + FastAPI REST API
- **📄 Automated Reporting**: Downloadable TXT reports with structured assessments

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                              │
│  ┌──────────────────────┐        ┌──────────────────────┐          │
│  │   Streamlit Web UI   │        │   FastAPI REST API    │          │
│  └──────────┬───────────┘        └───────────┬──────────┘          │
└─────────────┼──────────────────────────────────┼──────────────────┘
              │                                  │
              ▼                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      RAG RETRIEVAL ENGINE                           │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  1. Build Semantic Query (drug + symptom + context)        │    │
│  │  2. Generate Query Embedding (text-embedding-3-large)      │    │
│  │  3. Vector Search MongoDB Atlas                            │    │
│  │  4. Retrieve Top-K Drug + Syndrome Chunks                  │    │
│  └────────────────────────────────────────────────────────────┘    │
└─────────────┬───────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    CLINICAL NARRATIVE GENERATOR                     │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  1. Format Retrieved Context for LLM                       │    │
│  │  2. Build Pharmacovigilance Prompt                         │    │
│  │  3. Generate Narrative via Groq Llama3-70B                 │    │
│  │  4. Extract Structured Fields                              │    │
│  │  5. Create Downloadable Report                             │    │
│  └────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     KNOWLEDGE BASE (MongoDB Atlas)                  │
│  ┌──────────────────────┐      ┌──────────────────────┐            │
│  │   Drug Knowledge     │      │  Syndrome Knowledge  │            │
│  │  • Mechanism         │      │  • Pathophysiology   │            │
│  │  • Adverse Effects   │      │  • Risk Factors      │            │
│  │  • Risk Factors      │      │  • Clinical Signs    │            │
│  │  • Monitoring        │      │  • Diagnostic Markers│            │
│  └──────────────────────┘      └──────────────────────┘            │
│             3072-dimensional vector embeddings                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📦 Project Structure

```
caredata/
├── vector_ingestion.py          # MongoDB vector ingestion pipeline
├── rag_clinical.py              # RAG retrieval engine
├── clinical_narrative_engine.py # Groq LLM narrative generator
├── app_streamlit.py             # Streamlit frontend UI
├── api_server.py                # FastAPI backend service
├── config.py                    # Configuration management
├── requirements.txt             # Python dependencies
├── .env.template                # Environment variables template
├── README.md                    # This file
│
├── drug_knowledge/              # Drug markdown files
│   ├── atorvastatin.md
│   ├── lisinopril.md
│   ├── metformin.md
│   ├── sertraline.md
│   └── warfarin.md
│
├── syndrome_knowledge/          # Syndrome markdown files
│   ├── anticoagulant_bleeding.md
│   ├── drug_accumulation_ckd.md
│   ├── drug_induced_cardiac_event.md
│   ├── drug_induced_hepatotoxicity.md
│   ├── metformin_lactic_acidosis.md
│   ├── neurotoxicity.md
│   ├── serotonin_syndrome.md
│   └── statin_rhabdomyolysis.md
│
└── reports/                     # Generated clinical reports (auto-created)
```

---

## 🚀 Quick Start

### 1️⃣ Prerequisites

- **Python 3.9+**
- **MongoDB Atlas Account** (free tier works)
- **OpenAI API Key** (for embeddings)
- **Groq API Key** (for LLM - free tier available)

### 2️⃣ Installation

```bash
# Clone or navigate to project directory
cd d:\VKS\caredata

# Install dependencies
pip install -r requirements.txt
```

### 3️⃣ Configuration

```bash
# Copy environment template
cp .env.template .env

# Edit .env with your credentials
# Required:
#   OPENAI_API_KEY=sk-...
#   MONGO_URI=mongodb+srv://...
#   GROQ_API_KEY=gsk_...
```

Or set environment variables:

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="sk-your-key"
$env:MONGO_URI="mongodb+srv://your-connection-string"
$env:GROQ_API_KEY="gsk_your-key"
```

**Linux/Mac:**
```bash
export OPENAI_API_KEY="sk-your-key"
export MONGO_URI="mongodb+srv://your-connection-string"
export GROQ_API_KEY="gsk_your-key"
```

### 4️⃣ Setup Vector Database

```bash
# Step 1: Ingest medical knowledge into MongoDB Atlas
python vector_ingestion.py

# This will:
# - Chunk all drug and syndrome markdown files
# - Generate embeddings using text-embedding-3-large
# - Insert into MongoDB Atlas
# - Display vector index JSON definition
```

**Step 2: Create Vector Index in MongoDB Atlas**

1. Go to MongoDB Atlas → Your Cluster → **Search** → **Create Search Index**
2. Choose **JSON Editor**
3. Paste the JSON definition from the output above
4. Name it: `vector_index`
5. Click **Create**

---

## 🖥️ Usage

### Option A: Streamlit Web Interface (Recommended)

```bash
streamlit run app_streamlit.py
```

Access at: **http://localhost:8501**

**Features:**
- ✅ User-friendly form interface
- ✅ Real-time narrative generation
- ✅ Downloadable TXT reports
- ✅ Visual summary dashboard

### Option B: FastAPI REST API

```bash
python api_server.py
```

Access API at: **http://localhost:8000**  
Documentation: **http://localhost:8000/docs**

**Sample API Call:**

```bash
curl -X POST "http://localhost:8000/generate-narrative" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "PT-2024-001",
    "age": 68,
    "gender": "Male",
    "drug_name": "Atorvastatin",
    "start_date": "2024-10-01",
    "stop_date": "2024-11-15",
    "duration_days": 45,
    "stop_reason": "Muscle pain"
  }'
```

---

## 📊 System Workflow

### Input
```
Patient Case:
  - Patient ID: PT-2024-001
  - Age: 68, Gender: Male
  - Drug: Atorvastatin
  - Duration: 45 days
  - Stop Reason: Muscle pain
```

### Processing

1. **Semantic Query Construction**
   ```
   "atorvastatin muscle pain elderly 68 adverse effect 
    mechanism rhabdomyolysis toxicity pathophysiology"
   ```

2. **Vector Search**
   - Generate query embedding (3072 dimensions)
   - Search MongoDB Atlas vector index
   - Retrieve top 5 drug chunks + top 5 syndrome chunks

3. **LLM Prompt Construction**
   - Format retrieved medical knowledge
   - Add patient context
   - Include pharmacovigilance instructions

4. **Groq LLM Generation**
   - Model: Llama3-70B
   - Temperature: 0.3 (conservative)
   - Generate structured narrative

5. **Report Generation**
   - Parse narrative into structured fields
   - Format as TXT report
   - Save to reports/ directory

### Output

```
╔════════════════════════════════════════════════════════╗
║   ADVERSE DRUG REACTION CLINICAL ASSESSMENT REPORT     ║
╚════════════════════════════════════════════════════════╝

CASE SUMMARY:
A 68-year-old male patient received atorvastatin for 45 days 
and developed muscle pain, leading to drug discontinuation...

MECHANISTIC EXPLANATION:
Atorvastatin depletes coenzyme Q10 and impairs mitochondrial 
ATP synthesis in myocytes, resulting in myopathy...

SYNDROME CORRELATION:
Probable Syndrome: Statin-Induced Rhabdomyolysis
Justification: Temporal association, elderly age, muscle pain...

RISK STRATIFICATION:
- Age-related risk: HIGH (elderly ≥65 years)
- Organ function: Monitor renal function for myoglobin clearance
- Drug accumulation: Possible with prolonged therapy

SERIOUSNESS ASSESSMENT:
Severity: MODERATE to SEVERE
Hospitalization: May be required for CK monitoring
Mortality Risk: Low if detected early

REGULATORY CAUSALITY:
Category: PROBABLE (WHO-UMC Scale)
Justification: Strong temporal relationship, known adverse effect...

CLINICAL RECOMMENDATIONS:
1. Discontinue atorvastatin immediately
2. Monitor CK levels, renal function
3. Consider alternative lipid-lowering therapy (ezetimibe)
4. Follow-up in 2 weeks
```

---

## 🔧 Configuration Options

### Vector Search Parameters

```python
# In rag_clinical.py
drug_chunks_to_retrieve = 5      # Top-K drug knowledge chunks
syndrome_chunks_to_retrieve = 5  # Top-K syndrome knowledge chunks
vector_search_candidates = 50    # Candidates to evaluate
```

### LLM Parameters

```python
# In clinical_narrative_engine.py
model = "llama-3.3-70b-versatile"  # Groq model
temperature = 0.3                   # Conservative (0.0-1.0)
max_tokens = 4000                   # Max response length
```

---

## 📚 Knowledge Base Structure

### Drug Knowledge Files

Each drug markdown includes:
- **Drug Name & Class**
- **Mechanism of Action**
- **Common Adverse Effects**
- **Serious Adverse Effects**
- **Risk Factors**
- **Monitoring Requirements**

### Syndrome Knowledge Files

Each syndrome markdown includes:
- **Syndrome Name**
- **Associated Drugs**
- **Key Symptoms**
- **Pathophysiology**
- **Risk Factors**
- **Diagnostic Markers**
- **Clinical Actions**
- **Severity Classification**

---

## 🧪 Testing

### Test Vector Ingestion
```bash
python vector_ingestion.py
```

### Test RAG Retrieval
```bash
python rag_clinical.py
```

### Test Narrative Generation
```bash
python clinical_narrative_engine.py
```

### Test Complete Workflow
```bash
streamlit run app_streamlit.py
# Submit a test case through UI
```

---

## 🔒 Security & Compliance

### Data Privacy
- ✅ No patient data stored in vector database
- ✅ Reports saved locally only
- ✅ API keys stored in environment variables
- ✅ No external data transmission except to configured APIs

### Medical Compliance
- ✅ ICH E2B pharmacovigilance standards
- ✅ WHO-UMC causality assessment
- ✅ Conservative medical language
- ✅ Explicit disclaimer: AI tool, not medical diagnosis

### Important Disclaimers

⚠️ **THIS SYSTEM:**
- Does NOT provide medical diagnosis
- Does NOT replace clinical judgment
- Does NOT constitute medical advice
- MUST be reviewed by qualified healthcare professionals

All generated narratives are **clinical decision support** tools only.

---

## 🛠️ Troubleshooting

### Issue: "MongoDB connection failed"
**Solution:**
- Verify `MONGO_URI` is correct
- Check MongoDB Atlas network access (whitelist your IP)
- Ensure cluster is running

### Issue: "Vector index not found"
**Solution:**
- Create vector index in MongoDB Atlas UI (see Setup section)
- Verify index name is `vector_index`
- Wait 1-2 minutes for index to build

### Issue: "OpenAI API rate limit"
**Solution:**
- Use a paid OpenAI tier (free tier has low limits)
- Add delays between embedding calls
- Reduce batch size in ingestion

### Issue: "Groq API quota exceeded"
**Solution:**
- Groq free tier has limits
- Wait for quota reset
- Upgrade to paid plan
- Reduce temperature/max_tokens

---

## 📈 Performance Metrics

- **Embedding Generation**: ~0.5-1 sec per chunk
- **Vector Search**: ~100-200 ms per query
- **LLM Narrative Generation**: ~10-30 sec (Groq Llama3-70B)
- **Total Pipeline**: ~15-40 sec per case

---

## 🔄 Future Enhancements

- [ ] Multi-drug interaction analysis
- [ ] Time-to-event analysis
- [ ] Integration with EHR systems
- [ ] Multi-language support
- [ ] Advanced causality algorithms (Naranjo, Liverpool)
- [ ] Historical case comparison
- [ ] Regulatory submission formatting (FDA MedWatch, EudraVigilance)

---

## 📄 License

This project is for educational and research purposes.  
**NOT approved for clinical use without proper validation and regulatory approval.**

---

## 👥 Contributors

- **Senior AI Architect & Clinical NLP Engineer**
- Specialized in Pharmacovigilance AI Systems

---

## 📞 Support

For issues or questions:
1. Check troubleshooting section above
2. Review API documentation at `/docs` endpoint
3. Verify environment variables are set correctly
4. Ensure MongoDB Atlas vector index is created

---

## 🎓 Educational Purpose

This system demonstrates:
- ✅ RAG architecture for medical applications
- ✅ Vector database integration (MongoDB Atlas)
- ✅ LLM prompt engineering for medical reasoning
- ✅ Pharmacovigilance narrative generation
- ✅ Full-stack deployment (FastAPI + Streamlit)

**Perfect for:**
- Clinical informatics research
- AI/ML in healthcare education
- Pharmacovigilance automation studies
- RAG system implementation learning

---

**Built with ❤️ for advancing clinical AI and patient safety**
