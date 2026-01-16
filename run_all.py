#!/usr/bin/env python
"""
Run All - Convenience Script
Execute the complete ADR Clinical Narrative Generator workflow
"""

import os
import sys
import argparse
from pathlib import Path


def print_banner(text):
    """Print a formatted banner"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def check_environment():
    """Check if environment variables are set"""
    print_banner("STEP 1: Checking Environment")
    
    required_vars = {
        "OPENAI_API_KEY": "OpenAI API key for embeddings",
        "MONGO_URI": "MongoDB Atlas connection string",
        "GROQ_API_KEY": "Groq API key for LLM"
    }
    
    missing = []
    for var, desc in required_vars.items():
        if not os.getenv(var):
            missing.append(f"{var} ({desc})")
            print(f"❌ {var}: NOT SET")
        else:
            print(f"✅ {var}: Configured")
    
    if missing:
        print("\n⚠️  Missing environment variables:")
        for m in missing:
            print(f"   - {m}")
        print("\nSet them using:")
        print("  Windows: $env:VARIABLE_NAME='value'")
        print("  Linux/Mac: export VARIABLE_NAME='value'")
        return False
    
    print("\n✅ All environment variables configured!")
    return True


def run_tests():
    """Run the test suite"""
    print_banner("STEP 2: Running Test Suite")
    
    try:
        import subprocess
        result = subprocess.run([sys.executable, "test_suite.py"], 
                               capture_output=True, text=True)
        print(result.stdout)
        
        if result.returncode == 0:
            print("✅ All tests passed!")
            return True
        else:
            print("❌ Some tests failed")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False


def run_ingestion(skip_reset=True):
    """Run vector ingestion"""
    print_banner("STEP 3: Vector Ingestion (Optional)")
    
    if skip_reset:
        print("⏭️  Skipping ingestion (assuming already done)")
        print("   To run ingestion: python run_all.py --ingest")
        return True
    
    try:
        from vector_ingestion import main as ingest_main
        ingest_main()
        return True
    except Exception as e:
        print(f"❌ Ingestion failed: {e}")
        return False


def start_services(service="streamlit"):
    """Start the application services"""
    print_banner(f"STEP 4: Starting {service.upper()} Service")
    
    if service == "streamlit":
        print("🚀 Launching Streamlit UI...")
        print("   URL: http://localhost:8501")
        print("   Press Ctrl+C to stop\n")
        
        import subprocess
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app_streamlit.py"])
        
    elif service == "api":
        print("🚀 Launching FastAPI Server...")
        print("   API: http://localhost:8000")
        print("   Docs: http://localhost:8000/docs")
        print("   Press Ctrl+C to stop\n")
        
        from api_server import start_server
        start_server()
    
    else:
        print(f"❌ Unknown service: {service}")
        return False
    
    return True


def main():
    """Main execution"""
    parser = argparse.ArgumentParser(
        description="ADR Clinical Narrative Generator - Run All Script"
    )
    parser.add_argument(
        "--service", 
        choices=["streamlit", "api"], 
        default="streamlit",
        help="Which service to start (default: streamlit)"
    )
    parser.add_argument(
        "--skip-tests", 
        action="store_true",
        help="Skip running tests"
    )
    parser.add_argument(
        "--ingest", 
        action="store_true",
        help="Run vector ingestion (warning: may reset database)"
    )
    
    args = parser.parse_args()
    
    print("\n" + "╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  AI-Powered Adverse Drug Reaction Narrative Generator".center(68) + "║")
    print("║" + "  Complete Workflow Automation".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")
    
    # Step 1: Check environment
    if not check_environment():
        print("\n❌ Environment check failed. Please configure environment variables.")
        sys.exit(1)
    
    # Step 2: Run tests (optional)
    if not args.skip_tests:
        if not run_tests():
            print("\n⚠️  Tests failed. Continue anyway? (y/n): ", end="")
            if input().lower() != 'y':
                sys.exit(1)
    else:
        print_banner("STEP 2: Skipping Tests")
        print("⏭️  Tests skipped (use --skip-tests to skip)")
    
    # Step 3: Ingestion (optional)
    if not run_ingestion(skip_reset=not args.ingest):
        print("\n⚠️  Ingestion failed. Continue anyway? (y/n): ", end="")
        if input().lower() != 'y':
            sys.exit(1)
    
    # Step 4: Start service
    try:
        start_services(args.service)
    except KeyboardInterrupt:
        print("\n\n👋 Service stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting service: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
