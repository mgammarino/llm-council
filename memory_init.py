import os
from mem0 import Memory

def init_memory():
    # Configuration for local-first execution
    config = {
        "vector_store": {
            "provider": "qdrant",
            "config": {
                "path": "./.mem0_qdrant", # Local directory storage
                "embedding_model_dims": 384, # Match HuggingFace all-MiniLM-L6-v2
            }
        },
        "embedder": {
            "provider": "huggingface",
            "config": {
                "model": "sentence-transformers/all-MiniLM-L6-v2",
            }
        },
        "llm": {
            "provider": "ollama",
            "config": {
                "model": "phi3",
                "ollama_base_url": "http://localhost:11434",
            }
        },
    }
    
    try:
        # Initialize memory with local config
        m = Memory.from_config(config)
        
        # Add core project context
        project_context = "This project, llm-council, is a Python-based orchestration framework for multi-stage LLM reasoning and adversarial critique. Phase 1: Orchestration; Phase 2: Adversarial Critique; Phase 3: Consensus/Reporting. It uses FastAPI for the API layer and Pytest for testing."
        m.add(project_context, user_id="agent", infer=False)
        
        # Add technical stack details
        tech_context = "Tech stack: Python 3.14+, FastAPI, PostgreSQL, and now Mem0 for persistent memory and Repomix for context packing."
        m.add(tech_context, user_id="agent", infer=False)
        
        # Add naming decision
        naming_context = "Decision: Named Stage 1B 'ADVERSARIAL CRITIQUE' instead of 'Devil's Advocate' for a formal corporate tone."
        m.add(naming_context, user_id="agent", infer=False)
        
        print("Mem0 initialized with project context (Local HuggingFace + Qdrant, infer=False).")
        
    except Exception as e:
        print(f"Error initializing Mem0: {e}")

if __name__ == "__main__":
    init_memory()
