"""
RAG Retrieval Engine for Clinical ADR Narrative Generation
Performs semantic search across drug and syndrome knowledge base
"""

import os
from typing import List, Dict, Tuple
from dataclasses import dataclass
from pymongo import MongoClient
from fastembed import TextEmbedding


@dataclass
class RetrievedChunk:
    """Represents a retrieved knowledge chunk"""
    document_type: str
    name: str
    section: str
    chunk_text: str
    score: float


class ClinicalRAGRetriever:
    """
    Retrieval-Augmented Generation engine for clinical knowledge
    """
    
    def __init__(
        self,
        mongo_uri: str,
        db_name: str = "clinical_rag",
        collection_name: str = "medical_knowledge"
    ):
        """
        Initialize RAG retriever
        
        Args:
            mongo_uri: MongoDB Atlas URI
            db_name: Database name
            collection_name: Collection name
        """
        self.embedding_model = TextEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.model_name = "all-MiniLM-L6-v2"
        
        # MongoDB connection
        self.mongo_client = MongoClient(mongo_uri)
        self.db = self.mongo_client[db_name]
        self.collection = self.db[collection_name]
    
    def create_query_embedding(self, query: str) -> List[float]:
        """
        Create embedding for query text using FastEmbed
        
        Args:
            query: Query string
            
        Returns:
            Embedding vector
        """
        embedding = list(self.embedding_model.embed([query]))[0]
        return embedding.tolist()
    
    def build_semantic_query(
        self,
        drug_name: str,
        stop_reason: str,
        age: int,
        days: int,
        gender: str = ""
    ) -> str:
        """
        Construct optimized semantic query for vector search
        
        Args:
            drug_name: Drug name
            stop_reason: Symptom/reason for stopping
            age: Patient age
            days: Duration in days
            gender: Patient gender
            
        Returns:
            Semantic query string
        """
        # Age risk modifier
        age_risk = "elderly" if age >= 65 else "adult"
        
        # Duration modifier
        if days <= 7:
            duration = "short-term"
        elif days <= 30:
            duration = "acute"
        else:
            duration = "chronic prolonged"
        
        # Build comprehensive query
        query = f"""{drug_name} {stop_reason} adverse effect mechanism toxicity 
        {age_risk} age risk {duration} duration pathophysiology 
        clinical manifestation syndrome complication serious"""
        
        return " ".join(query.split())  # Clean whitespace
    
    def vector_search(
        self,
        query_embedding: List[float],
        document_type: str = None,
        top_k: int = 5
    ) -> List[RetrievedChunk]:
        """
        Perform MongoDB Atlas Vector Search
        
        Args:
            query_embedding: Query vector
            document_type: Filter by "drug" or "syndrome" (optional)
            top_k: Number of results to return
            
        Returns:
            List of retrieved chunks
        """
        # Build aggregation pipeline
        pipeline = [
            {
                "$vectorSearch": {
                    "index": "vector_index",
                    "path": "embedding",
                    "queryVector": query_embedding,
                    "numCandidates": top_k * 10,
                    "limit": top_k
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "document_type": 1,
                    "name": 1,
                    "section": 1,
                    "chunk_text": 1,
                    "score": {"$meta": "vectorSearchScore"}
                }
            }
        ]
        
        # Add filter if specified
        if document_type:
            pipeline.insert(1, {
                "$match": {"document_type": document_type}
            })
        
        # Execute search
        results = list(self.collection.aggregate(pipeline))
        
        # Convert to dataclass
        chunks = [
            RetrievedChunk(
                document_type=r['document_type'],
                name=r['name'],
                section=r['section'],
                chunk_text=r['chunk_text'],
                score=r['score']
            )
            for r in results
        ]
        
        return chunks
    
    def retrieve_for_case(
        self,
        patient_id: str,
        drug_name: str,
        stop_reason: str,
        age: int,
        days: int,
        gender: str = "",
        drug_chunks: int = 5,
        syndrome_chunks: int = 5
    ) -> Dict:
        """
        Retrieve relevant knowledge for a clinical case
        
        Args:
            patient_id: Patient identifier
            drug_name: Drug name
            stop_reason: Reason for stopping
            age: Patient age
            days: Duration of treatment
            gender: Patient gender
            drug_chunks: Number of drug chunks to retrieve
            syndrome_chunks: Number of syndrome chunks to retrieve
            
        Returns:
            Dictionary with retrieved context
        """
        print(f"\n🔍 Retrieving knowledge for Patient {patient_id}")
        print(f"   Drug: {drug_name}")
        print(f"   Stop Reason: {stop_reason}")
        print(f"   Age: {age}, Duration: {days} days\n")
        
        # Build semantic query
        query = self.build_semantic_query(drug_name, stop_reason, age, days, gender)
        print(f"📝 Semantic Query: {query}\n")
        
        # Create query embedding
        query_embedding = self.create_query_embedding(query)
        
        # Retrieve drug knowledge
        print(f"🔬 Retrieving top {drug_chunks} drug chunks...")
        drug_results = self.vector_search(
            query_embedding,
            document_type="drug",
            top_k=drug_chunks
        )
        
        # Retrieve syndrome knowledge
        print(f"🧬 Retrieving top {syndrome_chunks} syndrome chunks...")
        syndrome_results = self.vector_search(
            query_embedding,
            document_type="syndrome",
            top_k=syndrome_chunks
        )
        
        # Display results
        print("\n📊 Retrieved Drug Chunks:")
        for i, chunk in enumerate(drug_results, 1):
            print(f"  {i}. {chunk.name} - {chunk.section} (score: {chunk.score:.4f})")
        
        print("\n📊 Retrieved Syndrome Chunks:")
        for i, chunk in enumerate(syndrome_results, 1):
            print(f"  {i}. {chunk.name} - {chunk.section} (score: {chunk.score:.4f})")
        
        # Compile context
        context = {
            "patient_id": patient_id,
            "drug_name": drug_name,
            "stop_reason": stop_reason,
            "age": age,
            "days": days,
            "gender": gender,
            "query": query,
            "drug_context": [
                {
                    "name": c.name,
                    "section": c.section,
                    "text": c.chunk_text,
                    "score": c.score
                }
                for c in drug_results
            ],
            "syndrome_context": [
                {
                    "name": c.name,
                    "section": c.section,
                    "text": c.chunk_text,
                    "score": c.score
                }
                for c in syndrome_results
            ]
        }
        
        return context
    
    def format_context_for_llm(self, context: Dict) -> str:
        """
        Format retrieved context into a prompt for LLM
        
        Args:
            context: Retrieved context dictionary
            
        Returns:
            Formatted context string
        """
        formatted = "=== RETRIEVED MEDICAL KNOWLEDGE ===\n\n"
        
        formatted += "--- DRUG INFORMATION ---\n\n"
        for i, drug_chunk in enumerate(context['drug_context'], 1):
            formatted += f"[Drug Knowledge {i}] {drug_chunk['name']} - {drug_chunk['section']}\n"
            formatted += f"{drug_chunk['text']}\n\n"
        
        formatted += "\n--- SYNDROME INFORMATION ---\n\n"
        for i, syndrome_chunk in enumerate(context['syndrome_context'], 1):
            formatted += f"[Syndrome Knowledge {i}] {syndrome_chunk['name']} - {syndrome_chunk['section']}\n"
            formatted += f"{syndrome_chunk['text']}\n\n"
        
        return formatted


def test_retriever():
    """Test the RAG retriever"""
    
    print("=" * 70)
    print("🧪 TESTING RAG RETRIEVAL ENGINE")
    print("=" * 70)
    
    # Configuration
    MONGO_URI = os.getenv("MONGO_URI", "your-mongodb-atlas-uri")
    
    if MONGO_URI == "your-mongodb-atlas-uri":
        print("\n⚠️  Set MONGO_URI environment variable")
        return
    
    # Initialize retriever
    retriever = ClinicalRAGRetriever(
        mongo_uri=MONGO_URI
    )
    
    # Test case
    context = retriever.retrieve_for_case(
        patient_id="PT-2024-001",
        drug_name="atorvastatin",
        stop_reason="muscle pain",
        age=68,
        days=45,
        gender="Male"
    )
    
    # Format for LLM
    print("\n" + "=" * 70)
    print("📄 FORMATTED CONTEXT FOR LLM")
    print("=" * 70)
    formatted = retriever.format_context_for_llm(context)
    print(formatted[:1500] + "..." if len(formatted) > 1500 else formatted)
    
    print("\n✅ Retrieval test complete!")


if __name__ == "__main__":
    test_retriever()
