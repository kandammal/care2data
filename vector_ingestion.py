"""
MongoDB Atlas Vector Ingestion Pipeline
Chunks drug and syndrome knowledge files and creates vector embeddings
"""

import os
import re
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass
from pymongo import MongoClient
from fastembed import TextEmbedding
import tiktoken


@dataclass
class DocumentChunk:
    """Represents a semantic chunk of medical knowledge"""
    document_type: str  # "drug" or "syndrome"
    name: str
    section: str
    chunk_text: str
    embedding: List[float]
    metadata: Dict


class MedicalKnowledgeVectorizer:
    """
    Chunks medical knowledge and creates vector embeddings for MongoDB Atlas using FastEmbed
    """
    
    def __init__(
        self, 
        mongo_uri: str,
        db_name: str = "clinical_rag",
        collection_name: str = "medical_knowledge"
    ):
        """
        Initialize vectorizer with FastEmbed and MongoDB credentials
        
        Args:
            mongo_uri: MongoDB Atlas connection string
            db_name: Database name
            collection_name: Collection name
        """
        self.embedding_model = TextEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.model_name = "all-MiniLM-L6-v2"
        
        # MongoDB setup
        self.mongo_client = MongoClient(mongo_uri)
        self.db = self.mongo_client[db_name]
        self.collection = self.db[collection_name]
        
        # Tokenizer for chunking
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        
        # Section headers to detect
        self.drug_sections = [
            "MECHANISM OF ACTION",
            "COMMON ADVERSE EFFECTS",
            "SERIOUS ADVERSE EFFECTS",
            "RISK FACTORS",
            "CONTRAINDICATIONS",
            "MONITORING",
            "DRUG INTERACTIONS"
        ]
        
        self.syndrome_sections = [
            "KEY SYMPTOMS",
            "PATHOPHYSIOLOGY",
            "RISK FACTORS",
            "DIAGNOSTIC MARKERS",
            "CLINICAL ACTION",
            "COMPLICATIONS",
            "SEVERITY"
        ]
    
    def chunk_markdown_file(self, file_path: str, document_type: str) -> List[Dict]:
        """
        Parse markdown file and chunk by semantic sections
        
        Args:
            file_path: Path to markdown file
            document_type: "drug" or "syndrome"
            
        Returns:
            List of chunk dictionaries
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract document name
        name_match = re.search(r'(DRUG NAME|SYNDROME):\s*(.+)', content)
        doc_name = name_match.group(2).strip() if name_match else Path(file_path).stem
        
        chunks = []
        
        if document_type == "drug":
            sections = self.drug_sections
        else:
            sections = self.syndrome_sections
        
        # Add full document as context chunk
        full_text = f"Document: {doc_name}\n\n{content}"
        chunks.append({
            "section": "FULL_DOCUMENT",
            "text": full_text,
            "name": doc_name
        })
        
        # Extract each section
        for section in sections:
            pattern = rf'{section}:\s*\n(.*?)(?=\n[A-Z\s]+:|$)'
            match = re.search(pattern, content, re.DOTALL)
            
            if match:
                section_text = match.group(1).strip()
                
                # Create chunk with context
                chunk_text = f"""Document: {doc_name}
Section: {section}

{section_text}"""
                
                chunks.append({
                    "section": section,
                    "text": chunk_text,
                    "name": doc_name
                })
        
        return chunks
    
    def create_embedding(self, text: str) -> List[float]:
        """
        Generate embedding using FastEmbed with all-MiniLM-L6-v2
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        embedding = list(self.embedding_model.embed([text]))[0]
        return embedding.tolist()
    
    def ingest_directory(self, directory: str, document_type: str):
        """
        Process all markdown files in a directory
        
        Args:
            directory: Path to directory containing .md files
            document_type: "drug" or "syndrome"
        """
        directory_path = Path(directory)
        md_files = list(directory_path.glob("*.md"))
        
        print(f"\n📂 Processing {len(md_files)} {document_type} files from {directory}")
        
        all_documents = []
        
        for md_file in md_files:
            print(f"  📄 Chunking: {md_file.name}")
            chunks = self.chunk_markdown_file(str(md_file), document_type)
            
            for chunk in chunks:
                print(f"    🔹 Embedding section: {chunk['section']}")
                embedding = self.create_embedding(chunk['text'])
                
                document = {
                    "document_type": document_type,
                    "name": chunk['name'],
                    "section": chunk['section'],
                    "chunk_text": chunk['text'],
                    "embedding": embedding,
                    "metadata": {
                        "file_name": md_file.name,
                        "token_count": len(self.tokenizer.encode(chunk['text']))
                    }
                }
                
                all_documents.append(document)
        
        # Insert into MongoDB
        if all_documents:
            print(f"\n💾 Inserting {len(all_documents)} chunks into MongoDB...")
            self.collection.insert_many(all_documents)
            print("✅ Insertion complete!")
        
        return len(all_documents)
    
    def create_vector_index(self):
        """
        Create MongoDB Atlas Vector Search index
        
        Note: This generates the JSON definition. You must create the index
        in Atlas UI or via Atlas CLI.
        """
        index_definition = {
            "name": "vector_index",
            "type": "vectorSearch",
            "definition": {
                "fields": [
                    {
                        "type": "vector",
                        "path": "embedding",
                        "numDimensions": 384,  # all-MiniLM-L6-v2
                        "similarity": "cosine"
                    },
                    {
                        "type": "filter",
                        "path": "document_type"
                    },
                    {
                        "type": "filter",
                        "path": "name"
                    }
                ]
            }
        }
        
        print("\n🔍 Vector Search Index Definition:")
        print("=" * 60)
        import json
        print(json.dumps(index_definition, indent=2))
        print("=" * 60)
        print("\n⚠️  Create this index in MongoDB Atlas UI:")
        print("   1. Go to Atlas Cluster → Search → Create Search Index")
        print("   2. Choose 'JSON Editor'")
        print("   3. Paste the definition above")
        print("   4. Name it 'vector_index'\n")
        
        return index_definition
    
    def reset_collection(self):
        """Drop and recreate collection"""
        self.collection.drop()
        print("🗑️  Collection reset")
    
    def get_stats(self):
        """Get collection statistics"""
        total = self.collection.count_documents({})
        drug_count = self.collection.count_documents({"document_type": "drug"})
        syndrome_count = self.collection.count_documents({"document_type": "syndrome"})
        
        print("\n📊 Collection Statistics:")
        print(f"  Total chunks: {total}")
        print(f"  Drug chunks: {drug_count}")
        print(f"  Syndrome chunks: {syndrome_count}")


def main():
    """Main ingestion pipeline"""
    
    print("=" * 70)
    print("🧬 MEDICAL KNOWLEDGE VECTOR INGESTION PIPELINE")
    print("=" * 70)
    
    # Configuration (replace with your credentials)
    MONGO_URI = os.getenv("MONGO_URI", "your-mongodb-atlas-uri")
    
    if MONGO_URI == "your-mongodb-atlas-uri":
        print("\n⚠️  Please set MONGO_URI environment variable")
        print("   export MONGO_URI='mongodb+srv://...'")
        return
    
    # Initialize vectorizer
    print("\n🤖 Loading FastEmbed model...")
    vectorizer = MedicalKnowledgeVectorizer(
        mongo_uri=MONGO_URI
    )
    
    # Reset collection (optional)
    reset = input("\n❓ Reset collection? (y/n): ").lower()
    if reset == 'y':
        vectorizer.reset_collection()
    
    # Ingest drug knowledge
    drug_count = vectorizer.ingest_directory("drug_knowledge", "drug")
    
    # Ingest syndrome knowledge
    syndrome_count = vectorizer.ingest_directory("syndrome_knowledge", "syndrome")
    
    # Show statistics
    vectorizer.get_stats()
    
    # Generate vector index definition
    vectorizer.create_vector_index()
    
    print("\n✅ Vector ingestion complete!")
    print(f"   Total documents: {drug_count + syndrome_count}")


if __name__ == "__main__":
    main()
