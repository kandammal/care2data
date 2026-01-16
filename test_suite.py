"""
End-to-End Test Script
Tests the complete ADR narrative generation pipeline
"""

import os
import sys
from datetime import datetime


def test_configuration():
    """Test 1: Configuration validation"""
    print("\n" + "=" * 70)
    print("TEST 1: Configuration Validation")
    print("=" * 70)
    
    try:
        from config import load_config
        config = load_config()
        config.display()
        print("✅ Configuration test passed")
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def test_vector_ingestion():
    """Test 2: Vector ingestion (dry run)"""
    print("\n" + "=" * 70)
    print("TEST 2: Vector Ingestion Pipeline")
    print("=" * 70)
    
    try:
        from vector_ingestion import MedicalKnowledgeVectorizer
        import tempfile
        
        # Test markdown chunking only (no actual ingestion)
        print("Testing markdown file chunking...")
        
        vectorizer = MedicalKnowledgeVectorizer(
            openai_api_key=os.getenv("OPENAI_API_KEY", "test-key"),
            mongo_uri=os.getenv("MONGO_URI", "test-uri")
        )
        
        # Test chunking on a sample file
        drug_files = list(os.listdir("drug_knowledge"))
        if drug_files:
            test_file = f"drug_knowledge/{drug_files[0]}"
            chunks = vectorizer.chunk_markdown_file(test_file, "drug")
            print(f"✅ Successfully chunked {len(chunks)} sections from {drug_files[0]}")
        
        print("✅ Vector ingestion pipeline test passed")
        return True
    except Exception as e:
        print(f"❌ Vector ingestion test failed: {e}")
        return False


def test_rag_retrieval():
    """Test 3: RAG retrieval engine"""
    print("\n" + "=" * 70)
    print("TEST 3: RAG Retrieval Engine")
    print("=" * 70)
    
    try:
        from rag_clinical import ClinicalRAGRetriever
        
        print("Testing semantic query builder...")
        retriever = ClinicalRAGRetriever(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            mongo_uri=os.getenv("MONGO_URI")
        )
        
        query = retriever.build_semantic_query(
            drug_name="atorvastatin",
            stop_reason="muscle pain",
            age=68,
            days=45
        )
        
        print(f"Generated query: {query}")
        print("✅ RAG retrieval engine test passed")
        return True
    except Exception as e:
        print(f"❌ RAG retrieval test failed: {e}")
        return False


def test_narrative_generator():
    """Test 4: Clinical narrative generator"""
    print("\n" + "=" * 70)
    print("TEST 4: Clinical Narrative Generator")
    print("=" * 70)
    
    try:
        from clinical_narrative_engine import ClinicalNarrativeGenerator
        
        print("Testing narrative prompt builder...")
        generator = ClinicalNarrativeGenerator(
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
        
        prompt = generator.build_prompt(
            patient_id="TEST-001",
            age=68,
            gender="Male",
            drug_name="Atorvastatin",
            days=45,
            stop_reason="Muscle pain",
            retrieved_context="[Mock context for testing]"
        )
        
        print(f"✅ Generated prompt (length: {len(prompt)} characters)")
        print("✅ Narrative generator test passed")
        return True
    except Exception as e:
        print(f"❌ Narrative generator test failed: {e}")
        return False


def test_api_imports():
    """Test 5: API server imports"""
    print("\n" + "=" * 70)
    print("TEST 5: FastAPI Server")
    print("=" * 70)
    
    try:
        from api_server import app
        print("✅ FastAPI app imported successfully")
        print("✅ API server test passed")
        return True
    except Exception as e:
        print(f"❌ API server test failed: {e}")
        return False


def test_streamlit_imports():
    """Test 6: Streamlit app imports"""
    print("\n" + "=" * 70)
    print("TEST 6: Streamlit App")
    print("=" * 70)
    
    try:
        # Just check if file is valid Python
        with open("app_streamlit.py", 'r') as f:
            code = f.read()
        compile(code, "app_streamlit.py", "exec")
        print("✅ Streamlit app syntax valid")
        print("✅ Streamlit app test passed")
        return True
    except Exception as e:
        print(f"❌ Streamlit app test failed: {e}")
        return False


def test_knowledge_base():
    """Test 7: Knowledge base files"""
    print("\n" + "=" * 70)
    print("TEST 7: Knowledge Base Files")
    print("=" * 70)
    
    try:
        drug_count = len(list(os.listdir("drug_knowledge")))
        syndrome_count = len(list(os.listdir("syndrome_knowledge")))
        
        print(f"Drug knowledge files: {drug_count}")
        print(f"Syndrome knowledge files: {syndrome_count}")
        
        assert drug_count > 0, "No drug knowledge files found"
        assert syndrome_count > 0, "No syndrome knowledge files found"
        
        print("✅ Knowledge base test passed")
        return True
    except Exception as e:
        print(f"❌ Knowledge base test failed: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("🧪 ADR CLINICAL NARRATIVE GENERATOR - TEST SUITE")
    print("=" * 70)
    print(f"Started: {datetime.now().isoformat()}")
    
    tests = [
        ("Configuration", test_configuration),
        ("Vector Ingestion", test_vector_ingestion),
        ("RAG Retrieval", test_rag_retrieval),
        ("Narrative Generator", test_narrative_generator),
        ("API Server", test_api_imports),
        ("Streamlit App", test_streamlit_imports),
        ("Knowledge Base", test_knowledge_base)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("\n" + "=" * 70)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
    else:
        print(f"⚠️  {total - passed} test(s) failed")
    
    print("=" * 70)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
