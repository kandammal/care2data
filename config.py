"""
Configuration Management for ADR Clinical Narrative Generator
Environment variables and application settings
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class DatabaseConfig:
    """MongoDB Atlas configuration"""
    uri: str
    database_name: str = "clinical_rag"
    collection_name: str = "medical_knowledge"
    vector_index_name: str = "vector_index"


@dataclass
class OpenAIConfig:
    """OpenAI configuration"""
    api_key: str
    embedding_model: str = "text-embedding-3-large"
    embedding_dimensions: int = 3072


@dataclass
class GroqConfig:
    """Groq LLM configuration"""
    api_key: str
    model: str = "llama-3.3-70b-versatile"
    temperature: float = 0.3
    max_tokens: int = 4000


@dataclass
class ApplicationConfig:
    """Application configuration"""
    report_output_dir: str = "reports"
    drug_knowledge_dir: str = "drug_knowledge"
    syndrome_knowledge_dir: str = "syndrome_knowledge"
    
    # RAG settings
    drug_chunks_to_retrieve: int = 5
    syndrome_chunks_to_retrieve: int = 5
    vector_search_candidates: int = 50
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Streamlit settings
    streamlit_port: int = 8501


class Config:
    """Main configuration class"""
    
    def __init__(self):
        self.database = self._load_database_config()
        self.openai = self._load_openai_config()
        self.groq = self._load_groq_config()
        self.application = self._load_application_config()
    
    def _load_database_config(self) -> DatabaseConfig:
        """Load database configuration from environment"""
        mongo_uri = os.getenv("MONGO_URI")
        if not mongo_uri:
            raise ValueError("MONGO_URI environment variable not set")
        
        return DatabaseConfig(
            uri=mongo_uri,
            database_name=os.getenv("MONGO_DB_NAME", "clinical_rag"),
            collection_name=os.getenv("MONGO_COLLECTION_NAME", "medical_knowledge"),
            vector_index_name=os.getenv("MONGO_VECTOR_INDEX", "vector_index")
        )
    
    def _load_openai_config(self) -> OpenAIConfig:
        """Load OpenAI configuration from environment"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        return OpenAIConfig(
            api_key=api_key,
            embedding_model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-large"),
            embedding_dimensions=int(os.getenv("OPENAI_EMBEDDING_DIMS", "3072"))
        )
    
    def _load_groq_config(self) -> GroqConfig:
        """Load Groq configuration from environment"""
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")
        
        return GroqConfig(
            api_key=api_key,
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            temperature=float(os.getenv("GROQ_TEMPERATURE", "0.3")),
            max_tokens=int(os.getenv("GROQ_MAX_TOKENS", "4000"))
        )
    
    def _load_application_config(self) -> ApplicationConfig:
        """Load application configuration"""
        return ApplicationConfig(
            report_output_dir=os.getenv("REPORT_OUTPUT_DIR", "reports"),
            drug_knowledge_dir=os.getenv("DRUG_KNOWLEDGE_DIR", "drug_knowledge"),
            syndrome_knowledge_dir=os.getenv("SYNDROME_KNOWLEDGE_DIR", "syndrome_knowledge"),
            drug_chunks_to_retrieve=int(os.getenv("DRUG_CHUNKS", "5")),
            syndrome_chunks_to_retrieve=int(os.getenv("SYNDROME_CHUNKS", "5")),
            api_host=os.getenv("API_HOST", "0.0.0.0"),
            api_port=int(os.getenv("API_PORT", "8000")),
            streamlit_port=int(os.getenv("STREAMLIT_PORT", "8501"))
        )
    
    def validate(self) -> bool:
        """Validate all configurations"""
        try:
            assert self.database.uri, "MongoDB URI is required"
            assert self.openai.api_key, "OpenAI API key is required"
            assert self.groq.api_key, "Groq API key is required"
            assert os.path.exists(self.application.drug_knowledge_dir), "Drug knowledge directory not found"
            assert os.path.exists(self.application.syndrome_knowledge_dir), "Syndrome knowledge directory not found"
            return True
        except AssertionError as e:
            print(f"❌ Configuration validation failed: {e}")
            return False
    
    def display(self):
        """Display configuration (safe - no secrets)"""
        print("\n" + "=" * 70)
        print("⚙️  APPLICATION CONFIGURATION")
        print("=" * 70)
        
        print("\n📊 Database:")
        print(f"  Database: {self.database.database_name}")
        print(f"  Collection: {self.database.collection_name}")
        print(f"  Vector Index: {self.database.vector_index_name}")
        print(f"  URI: {'✓ Configured' if self.database.uri else '✗ Missing'}")
        
        print("\n🤖 OpenAI:")
        print(f"  Model: {self.openai.embedding_model}")
        print(f"  Dimensions: {self.openai.embedding_dimensions}")
        print(f"  API Key: {'✓ Configured' if self.openai.api_key else '✗ Missing'}")
        
        print("\n🚀 Groq:")
        print(f"  Model: {self.groq.model}")
        print(f"  Temperature: {self.groq.temperature}")
        print(f"  Max Tokens: {self.groq.max_tokens}")
        print(f"  API Key: {'✓ Configured' if self.groq.api_key else '✗ Missing'}")
        
        print("\n📁 Application:")
        print(f"  Reports Directory: {self.application.report_output_dir}")
        print(f"  Drug Knowledge: {self.application.drug_knowledge_dir}")
        print(f"  Syndrome Knowledge: {self.application.syndrome_knowledge_dir}")
        print(f"  API Endpoint: http://{self.application.api_host}:{self.application.api_port}")
        print(f"  Streamlit Port: {self.application.streamlit_port}")
        
        print("\n" + "=" * 70)


def load_config() -> Config:
    """Load and validate configuration"""
    config = Config()
    if config.validate():
        print("✅ Configuration loaded and validated successfully")
    return config


if __name__ == "__main__":
    # Test configuration loading
    try:
        config = load_config()
        config.display()
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\n💡 Set environment variables:")
        print("   export OPENAI_API_KEY='sk-...'")
        print("   export MONGO_URI='mongodb+srv://...'")
        print("   export GROQ_API_KEY='gsk_...'")
