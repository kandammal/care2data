# 📐 System Architecture
# AI-Powered Adverse Drug Reaction Clinical Narrative Generator

## 🏛️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER LAYER                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────┐         ┌─────────────────────────┐          │
│  │   Streamlit Web UI      │         │   REST API Clients      │          │
│  │   (Port 8501)           │         │   (curl, Python, JS)    │          │
│  │                         │         │                         │          │
│  │  • Patient Form         │         │  • Programmatic Access  │          │
│  │  • Narrative Display    │         │  • System Integration   │          │
│  │  • Report Download      │         │  • Batch Processing     │          │
│  └────────────┬────────────┘         └────────────┬────────────┘          │
│               │                                   │                        │
└───────────────┼───────────────────────────────────┼────────────────────────┘
                │                                   │
                ▼                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          APPLICATION LAYER                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    FastAPI Backend Service                          │   │
│  │                        (api_server.py)                              │   │
│  │                                                                     │   │
│  │  Endpoints:                                                         │   │
│  │  • POST /generate-narrative  → Generate clinical narrative          │   │
│  │  • GET  /download-report/:id → Download TXT report                 │   │
│  │  • GET  /health             → System health check                  │   │
│  │  • POST /search-knowledge   → Search medical knowledge             │   │
│  │  • GET  /drugs              → List available drugs                 │   │
│  │  • GET  /syndromes          → List known syndromes                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│               │                                                             │
│               ▼                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                   Business Logic Layer                              │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │                                                                     │   │
│  │  ┌──────────────────────┐        ┌──────────────────────┐         │   │
│  │  │  RAG Retriever       │        │  Narrative Generator │         │   │
│  │  │  (rag_clinical.py)   │        │  (clinical_narrative │         │   │
│  │  │                      │        │   _engine.py)        │         │   │
│  │  │  • Query Builder     │───────▶│  • Prompt Builder    │         │   │
│  │  │  • Embedding Gen     │        │  • Groq LLM Call     │         │   │
│  │  │  • Vector Search     │        │  • Response Parser   │         │   │
│  │  │  • Context Format    │        │  • Report Generator  │         │   │
│  │  └──────────────────────┘        └──────────────────────┘         │   │
│  │               │                              │                     │   │
│  └───────────────┼──────────────────────────────┼─────────────────────┘   │
│                  │                              │                         │
└──────────────────┼──────────────────────────────┼─────────────────────────┘
                   │                              │
                   ▼                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         EXTERNAL SERVICES LAYER                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐         │
│  │  MongoDB Atlas   │  │  OpenAI API      │  │  Groq API        │         │
│  │  Vector Search   │  │  Embeddings      │  │  LLM Inference   │         │
│  │                  │  │                  │  │                  │         │
│  │  • Medical KB    │  │  Model:          │  │  Model:          │         │
│  │  • Drug Chunks   │  │  text-embedding  │  │  Llama3-70B      │         │
│  │  • Syndrome Data │  │  -3-large        │  │  Versatile       │         │
│  │  • 3072-dim      │  │                  │  │                  │         │
│  │    Embeddings    │  │  Dimensions:     │  │  Temperature:    │         │
│  │                  │  │  3072            │  │  0.3 (conservative)         │
│  │  • Cosine        │  │                  │  │                  │         │
│  │    Similarity    │  │  Cost:           │  │  Max Tokens:     │         │
│  │                  │  │  ~$0.13/1M tok   │  │  4000            │         │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Data Flow Diagram

```
STEP 1: USER INPUT
┌─────────────────────────────────────────────┐
│ Patient Case Information                    │
│                                             │
│ • Patient ID: PT-2024-001                   │
│ • Age: 68, Gender: Male                     │
│ • Drug: Atorvastatin                        │
│ • Duration: 45 days                         │
│ • Stop Reason: Muscle pain                  │
└─────────────┬───────────────────────────────┘
              │
              ▼
STEP 2: SEMANTIC QUERY CONSTRUCTION
┌─────────────────────────────────────────────┐
│ RAG Retriever: build_semantic_query()      │
│                                             │
│ Input: drug_name, stop_reason, age, days   │
│ Output: "atorvastatin muscle pain elderly  │
│          adverse effect mechanism toxicity  │
│          rhabdomyolysis pathophysiology"    │
└─────────────┬───────────────────────────────┘
              │
              ▼
STEP 3: EMBEDDING GENERATION
┌─────────────────────────────────────────────┐
│ OpenAI API: create_embedding()              │
│                                             │
│ Model: text-embedding-3-large               │
│ Input: Semantic query string                │
│ Output: [0.021, -0.014, ..., 0.032]         │
│         (3072-dimensional vector)           │
└─────────────┬───────────────────────────────┘
              │
              ▼
STEP 4: VECTOR SEARCH
┌─────────────────────────────────────────────┐
│ MongoDB Atlas: $vectorSearch                │
│                                             │
│ Index: vector_index (cosine similarity)    │
│                                             │
│ Query Vector: [3072 dims]                  │
│ Document Filter: document_type = "drug"    │
│ Limit: 5 chunks                             │
│                                             │
│ Results:                                    │
│ 1. Atorvastatin - MECHANISM (score: 0.89) │
│ 2. Atorvastatin - ADVERSE EFFECTS (0.86)  │
│ 3. Atorvastatin - RISK FACTORS (0.84)     │
│ 4. Atorvastatin - MONITORING (0.81)       │
│ 5. Atorvastatin - FULL_DOCUMENT (0.79)    │
└─────────────┬───────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────┐
│ MongoDB Atlas: $vectorSearch (Syndromes)    │
│                                             │
│ Document Filter: document_type = "syndrome"│
│ Limit: 5 chunks                             │
│                                             │
│ Results:                                    │
│ 1. Statin Rhabdomyolysis - FULL (0.92)    │
│ 2. Statin Rhabdo - PATHOPHYSIOLOGY (0.88) │
│ 3. Statin Rhabdo - RISK FACTORS (0.85)    │
│ 4. Statin Rhabdo - SYMPTOMS (0.83)        │
│ 5. Statin Rhabdo - CLINICAL ACTION (0.80) │
└─────────────┬───────────────────────────────┘
              │
              ▼
STEP 5: CONTEXT FORMATTING
┌─────────────────────────────────────────────┐
│ RAG Retriever: format_context_for_llm()    │
│                                             │
│ === RETRIEVED MEDICAL KNOWLEDGE ===        │
│                                             │
│ --- DRUG INFORMATION ---                   │
│ [Drug Knowledge 1] Atorvastatin - MECHANISM│
│ Competitive inhibition of HMG-CoA...       │
│                                             │
│ [Drug Knowledge 2] Atorvastatin - ADVERSE  │
│ Rhabdomyolysis, myopathy, elevated CK...   │
│                                             │
│ --- SYNDROME INFORMATION ---                │
│ [Syndrome Knowledge 1] Statin Rhabdo...    │
│ Severe muscle pain, CK > 10x ULN...        │
└─────────────┬───────────────────────────────┘
              │
              ▼
STEP 6: PROMPT CONSTRUCTION
┌─────────────────────────────────────────────┐
│ Narrative Generator: build_prompt()        │
│                                             │
│ You are a Senior Pharmacovigilance AI...   │
│                                             │
│ CASE DETAILS:                               │
│ Patient ID: PT-2024-001                     │
│ Age: 68, Gender: Male                       │
│ Drug: Atorvastatin, Duration: 45 days      │
│ Stop Reason: Muscle pain                    │
│                                             │
│ RETRIEVED MEDICAL KNOWLEDGE:                │
│ [Inserted context from Step 5]             │
│                                             │
│ INSTRUCTIONS:                               │
│ Generate structured narrative with...      │
│ 1. Case Summary                             │
│ 2. Mechanistic Explanation                  │
│ 3. Syndrome Correlation                     │
│ [...]                                       │
└─────────────┬───────────────────────────────┘
              │
              ▼
STEP 7: LLM INFERENCE
┌─────────────────────────────────────────────┐
│ Groq API: chat.completions.create()        │
│                                             │
│ Model: llama-3.3-70b-versatile             │
│ Temperature: 0.3 (conservative)             │
│ Max Tokens: 4000                            │
│                                             │
│ System: "You are Senior Pharmacovigilance  │
│          Physician AI..."                   │
│                                             │
│ User: [Prompt from Step 6]                 │
│                                             │
│ Processing: ~15-25 seconds                  │
└─────────────┬───────────────────────────────┘
              │
              ▼
STEP 8: RESPONSE PARSING
┌─────────────────────────────────────────────┐
│ Narrative Generator: Parse LLM Response    │
│                                             │
│ Extract:                                    │
│ • Full narrative text                       │
│ • Probable syndrome                         │
│ • Mechanism                                 │
│ • Seriousness level                         │
│ • Causality category                        │
│ • Clinical advice                           │
└─────────────┬───────────────────────────────┘
              │
              ▼
STEP 9: REPORT GENERATION
┌─────────────────────────────────────────────┐
│ Narrative Generator: format_report()       │
│                                             │
│ Create structured TXT report:              │
│                                             │
│ ╔═══════════════════════════════════════╗  │
│ ║ ADVERSE DRUG REACTION ASSESSMENT      ║  │
│ ╚═══════════════════════════════════════╝  │
│                                             │
│ CASE IDENTIFICATION                         │
│ Patient ID: PT-2024-001                     │
│ Drug: Atorvastatin                          │
│ Duration: 45 days                           │
│                                             │
│ CLINICAL NARRATIVE                          │
│ [Full multi-paragraph narrative]           │
│                                             │
│ SUMMARY ASSESSMENT                          │
│ Probable Syndrome: Statin Rhabdomyolysis   │
│ Seriousness: MODERATE to SEVERE            │
│ Causality: PROBABLE (WHO-UMC)              │
│ [...]                                       │
│                                             │
│ Save to: reports/clinical_report_PT-...txt │
└─────────────┬───────────────────────────────┘
              │
              ▼
STEP 10: USER DELIVERY
┌─────────────────────────────────────────────┐
│ • Display in Streamlit UI                   │
│ • Return via FastAPI JSON response          │
│ • Provide download link for TXT report      │
└─────────────────────────────────────────────┘
```

---

## 🗄️ Database Schema

```
MongoDB Collection: medical_knowledge

Document Structure:
{
  "_id": ObjectId("..."),
  
  "document_type": "drug" | "syndrome",
  
  "name": "Atorvastatin" | "Statin-Induced Rhabdomyolysis",
  
  "section": "MECHANISM OF ACTION" | "PATHOPHYSIOLOGY" | ...,
  
  "chunk_text": "Document: Atorvastatin\nSection: MECHANISM...",
  
  "embedding": [
    0.021543,
    -0.014234,
    0.032156,
    ...
    -0.008923
  ],  // 3072 dimensions
  
  "metadata": {
    "file_name": "atorvastatin.md",
    "token_count": 245
  }
}

Indexes:
1. vector_index (Vector Search):
   - Field: embedding
   - Type: vector
   - Dimensions: 3072
   - Similarity: cosine
   
2. document_type_index (Filter):
   - Field: document_type
   - Type: filter
   
3. name_index (Filter):
   - Field: name
   - Type: filter
```

---

## 🔄 Component Interactions

```
┌────────────────────────────────────────────────────────────────┐
│                    COMPONENT DEPENDENCY GRAPH                  │
└────────────────────────────────────────────────────────────────┘

config.py
  │
  ├──▶ vector_ingestion.py
  │     │
  │     ├──▶ OpenAI (embeddings)
  │     └──▶ MongoDB Atlas (insert)
  │
  ├──▶ rag_clinical.py
  │     │
  │     ├──▶ OpenAI (query embeddings)
  │     └──▶ MongoDB Atlas (vector search)
  │
  ├──▶ clinical_narrative_engine.py
  │     │
  │     └──▶ Groq (LLM generation)
  │
  ├──▶ api_server.py
  │     │
  │     ├──▶ rag_clinical.py
  │     └──▶ clinical_narrative_engine.py
  │
  └──▶ app_streamlit.py
        │
        ├──▶ rag_clinical.py
        └──▶ clinical_narrative_engine.py
```

---

## 📦 File Responsibilities

```
vector_ingestion.py
├─ MedicalKnowledgeVectorizer
│  ├─ chunk_markdown_file()      → Parse .md files
│  ├─ create_embedding()         → Generate vectors
│  ├─ ingest_directory()         → Batch process files
│  └─ create_vector_index()      → Index definition

rag_clinical.py
├─ ClinicalRAGRetriever
│  ├─ build_semantic_query()     → Construct search query
│  ├─ create_query_embedding()   → Vectorize query
│  ├─ vector_search()            → Execute $vectorSearch
│  ├─ retrieve_for_case()        → Get relevant chunks
│  └─ format_context_for_llm()   → Format for prompt

clinical_narrative_engine.py
├─ ClinicalNarrativeGenerator
│  ├─ build_prompt()             → Create LLM prompt
│  ├─ generate_narrative()       → Call Groq API
│  ├─ format_report()            → Create TXT report
│  └─ save_report()              → Write to file

api_server.py
├─ FastAPI Application
│  ├─ /generate-narrative        → Main endpoint
│  ├─ /download-report/:id       → Report download
│  ├─ /health                    → Health check
│  └─ /search-knowledge          → Knowledge search

app_streamlit.py
├─ Streamlit UI
│  ├─ Patient input form
│  ├─ Narrative display
│  └─ Report download

config.py
├─ Configuration Management
│  ├─ DatabaseConfig
│  ├─ OpenAIConfig
│  ├─ GroqConfig
│  └─ ApplicationConfig
```

---

## ⚡ Performance Characteristics

```
LATENCY BREAKDOWN (per case):

1. Semantic Query Construction      <1ms
2. Query Embedding Generation        ~500ms
3. Vector Search (Drug)              ~100ms
4. Vector Search (Syndrome)          ~100ms
5. Context Formatting                <10ms
6. Prompt Construction               <10ms
7. Groq LLM Inference                ~15-25s
8. Response Parsing                  <50ms
9. Report Generation                 <100ms
───────────────────────────────────────────
TOTAL:                               ~16-27s

RESOURCE USAGE:

Memory:
- Application: ~200-300 MB
- MongoDB Client: ~50 MB
- Peak (during LLM): ~400 MB

Network:
- Upload per case: ~5-10 KB
- Download per case: ~10-20 KB (context + response)

API Costs (per case):
- OpenAI Embedding: ~$0.0001
- Groq LLM: Free tier (limited)
- MongoDB: Free M0 tier
```

---

## 🔐 Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      SECURITY LAYERS                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. TRANSPORT LAYER                                         │
│     • HTTPS/TLS for production                              │
│     • Encrypted MongoDB Atlas connection                    │
│     • API key transmission over HTTPS only                  │
│                                                             │
│  2. AUTHENTICATION & AUTHORIZATION                          │
│     • Environment variable isolation                        │
│     • No hardcoded credentials                              │
│     • MongoDB Atlas username/password                       │
│     • IP whitelisting (Atlas)                               │
│                                                             │
│  3. DATA PROTECTION                                         │
│     • No PHI/PII in vector database                         │
│     • Local report storage only                             │
│     • No data retention in LLM providers                    │
│                                                             │
│  4. APPLICATION SECURITY                                    │
│     • Input validation (Pydantic)                           │
│     • SQL injection prevention (NoSQL)                      │
│     • CORS configuration                                    │
│     • Rate limiting (recommended for production)            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

**System designed for:**
✅ Clinical accuracy  
✅ Regulatory compliance  
✅ Scalability  
✅ Maintainability  
✅ Security  
✅ Performance  

**Architecture Status:** Production-Ready ✨
