import argparse
import sys
import os

from src.llm_config import generate_config
from src.collector import run_collector
from src.validator import run_validation
from src.rag_builder import build_rag

def main():
    parser = argparse.ArgumentParser(description="API Document Collector to FastAPI Agent Builder")
    parser.add_argument("url", help="Target API documentation URL")
    parser.add_argument("--llm", default="local", help="LLM string. e.g., local:ollama/llama3, api:openai:gpt-4o")
    parser.add_argument("--rag", action="store_true", help="Enable RAG DB build")
    
    args = parser.parse_args()
    
    # 1. Generate Config using LLM
    print(f"Generating configuration for {args.url} using {args.llm}...")
    config = generate_config(args.url, args.llm)
    if not config:
        print("Failed to generate configuration. Exiting.")
        sys.exit(1)
        
    # 2. Run Collector
    print(f"Running collector with config...")
    docs_dir = run_collector(config)
    
    # 3. Validate
    print(f"Validating collected documents in {docs_dir}...")
    is_valid = run_validation(docs_dir, args.llm)
    
    # 4. Optional RAG DB Generation
    if args.rag and is_valid:
        print(f"Building RAG Database...")
        build_rag(docs_dir)

    print("\nPipeline finished successfully!")

if __name__ == "__main__":
    main()
