from mem0 import Memory
import sys

def add_memory(text):
    config = {
        "vector_store": { "provider": "qdrant", "config": { "path": "./.mem0_qdrant", "embedding_model_dims": 384 } },
        "embedder": { "provider": "huggingface", "config": { "model": "sentence-transformers/all-MiniLM-L6-v2" } },
        "llm": { "provider": "ollama", "config": { "model": "phi3", "ollama_base_url": "http://localhost:11434" } },
    }
    
    try:
        m = Memory.from_config(config)
        m.add(text, user_id="agent", infer=False)
        print(f"Successfully recorded memory: {text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        add_memory(" ".join(sys.argv[1:]))
    else:
        print("Usage: python add_memory.py '<text>'")
