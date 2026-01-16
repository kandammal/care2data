"""
FastAPI Backend Service for ADR Clinical Narrative Generator
RESTful API for programmatic access to the RAG system
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional
import os
from datetime import datetime
import uvicorn

from rag_clinical import ClinicalRAGRetriever
from clinical_narrative_engine import ClinicalNarrativeGenerator


# Pydantic models
class PatientCase(BaseModel):
    """Patient case input model"""
    patient_id: str = Field(..., description="Unique patient identifier")
    age: int = Field(..., ge=18, le=120, description="Patient age in years")
    gender: str = Field(..., description="Patient gender")
    drug_name: str = Field(..., description="Drug associated with adverse event")
    start_date: str = Field(..., description="Drug start date (YYYY-MM-DD)")
    stop_date: str = Field(..., description="Drug stop date (YYYY-MM-DD)")
    duration_days: int = Field(..., ge=1, description="Treatment duration in days")
    stop_reason: str = Field(..., description="Adverse event/symptom")
    
    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": "PT-2024-001",
                "age": 68,
                "gender": "Male",
                "drug_name": "Atorvastatin",
                "start_date": "2024-10-01",
                "stop_date": "2024-11-15",
                "duration_days": 45,
                "stop_reason": "Muscle pain"
            }
        }


class NarrativeResponse(BaseModel):
    """Clinical narrative response model"""
    patient_id: str
    drug_name: str
    duration_days: int
    stop_reason: str
    narrative: str
    probable_syndrome: str
    mechanism: str
    seriousness_level: str
    causality_category: str
    clinical_advice: str
    generated_at: str
    report_url: Optional[str] = None


class HealthCheck(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    version: str
    components: dict


# Initialize FastAPI app
app = FastAPI(
    title="ADR Clinical Narrative Generator API",
    description="AI-Powered Adverse Drug Reaction Clinical Narrative Generator using RAG",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize components
def get_retriever():
    """Get RAG retriever instance"""
    return ClinicalRAGRetriever(
        mongo_uri=os.getenv("MONGO_URI")
    )


def get_generator():
    """Get narrative generator instance"""
    return ClinicalNarrativeGenerator(
        groq_api_key=os.getenv("GROQ_API_KEY")
    )


# API Endpoints

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "AI-Powered ADR Clinical Narrative Generator API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthCheck, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    
    # Check component availability
    components = {
        "fastembed": True,
        "mongodb_atlas": bool(os.getenv("MONGO_URI")),
        "groq_api": bool(os.getenv("GROQ_API_KEY"))
    }
    
    all_healthy = all(components.values())
    
    return HealthCheck(
        status="healthy" if all_healthy else "degraded",
        timestamp=datetime.now().isoformat(),
        version="1.0.0",
        components=components
    )


@app.post("/generate-narrative", response_model=NarrativeResponse, tags=["Narrative"])
async def generate_narrative(case: PatientCase, background_tasks: BackgroundTasks):
    """
    Generate clinical narrative for adverse drug reaction case
    
    This endpoint:
    1. Retrieves relevant medical knowledge using vector search
    2. Generates clinical narrative using Groq LLM
    3. Returns structured response with downloadable report
    """
    
    try:
        # Validate API keys
        if not os.getenv("MONGO_URI"):
            raise HTTPException(status_code=500, detail="MongoDB URI not configured")
        if not os.getenv("GROQ_API_KEY"):
            raise HTTPException(status_code=500, detail="Groq API key not configured")
        
        # Step 1: Retrieve medical knowledge
        retriever = get_retriever()
        context = retriever.retrieve_for_case(
            patient_id=case.patient_id,
            drug_name=case.drug_name.lower(),
            stop_reason=case.stop_reason,
            age=case.age,
            days=case.duration_days,
            gender=case.gender
        )
        
        formatted_context = retriever.format_context_for_llm(context)
        
        # Step 2: Generate narrative
        generator = get_generator()
        narrative = generator.generate_narrative(
            patient_id=case.patient_id,
            age=case.age,
            gender=case.gender,
            drug_name=case.drug_name,
            days=case.duration_days,
            stop_reason=case.stop_reason,
            retrieved_context=formatted_context
        )
        
        # Step 3: Save report
        report_path = generator.save_report(narrative, output_dir="reports")
        report_url = f"/download-report/{case.patient_id}"
        
        # Return response
        return NarrativeResponse(
            patient_id=narrative.patient_id,
            drug_name=narrative.drug_name,
            duration_days=narrative.duration_days,
            stop_reason=narrative.stop_reason,
            narrative=narrative.narrative,
            probable_syndrome=narrative.probable_syndrome,
            mechanism=narrative.mechanism,
            seriousness_level=narrative.seriousness_level,
            causality_category=narrative.causality_category,
            clinical_advice=narrative.clinical_advice,
            generated_at=narrative.generated_at,
            report_url=report_url
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating narrative: {str(e)}")


@app.get("/download-report/{patient_id}", tags=["Reports"])
async def download_report(patient_id: str):
    """
    Download clinical report as text file
    """
    
    report_path = f"reports/clinical_report_{patient_id}.txt"
    
    if not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail="Report not found")
    
    return FileResponse(
        path=report_path,
        filename=f"clinical_report_{patient_id}.txt",
        media_type="text/plain"
    )


@app.get("/drugs", tags=["Reference"])
async def list_drugs():
    """List available drugs in knowledge base"""
    return {
        "drugs": [
            "Atorvastatin",
            "Lisinopril",
            "Metformin",
            "Sertraline",
            "Warfarin"
        ]
    }


@app.get("/symptoms", tags=["Reference"])
async def list_symptoms():
    """List common adverse event symptoms"""
    return {
        "symptoms": [
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
        ]
    }


@app.get("/syndromes", tags=["Reference"])
async def list_syndromes():
    """List known adverse drug reaction syndromes"""
    return {
        "syndromes": [
            "Anticoagulant Bleeding",
            "Drug Accumulation in CKD",
            "Drug-Induced Cardiac Event",
            "Drug-Induced Hepatotoxicity",
            "Metformin Lactic Acidosis",
            "Neurotoxicity",
            "Serotonin Syndrome",
            "Statin Rhabdomyolysis"
        ]
    }


@app.post("/search-knowledge", tags=["Knowledge"])
async def search_knowledge(query: str, document_type: Optional[str] = None, top_k: int = 5):
    """
    Search medical knowledge base using semantic search
    
    Args:
        query: Search query
        document_type: Filter by "drug" or "syndrome" (optional)
        top_k: Number of results to return
    """
    
    try:
        retriever = get_retriever()
        query_embedding = retriever.create_query_embedding(query)
        results = retriever.vector_search(query_embedding, document_type, top_k)
        
        return {
            "query": query,
            "document_type": document_type,
            "results": [
                {
                    "name": r.name,
                    "section": r.section,
                    "text": r.chunk_text[:500] + "..." if len(r.chunk_text) > 500 else r.chunk_text,
                    "score": r.score
                }
                for r in results
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching knowledge: {str(e)}")


# Run server
def start_server(host: str = "0.0.0.0", port: int = 8000):
    """Start FastAPI server"""
    print("=" * 70)
    print("🚀 STARTING ADR CLINICAL NARRATIVE GENERATOR API")
    print("=" * 70)
    print(f"📡 Server: http://{host}:{port}")
    print(f"📚 Documentation: http://{host}:{port}/docs")
    print(f"🔬 ReDoc: http://{host}:{port}/redoc")
    print("=" * 70)
    
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    start_server()
