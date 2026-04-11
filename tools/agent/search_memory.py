from mem0 import Memory
import sys

def search_memory(query):
    config = {
        "vector_store": { "provider": "qdrant", "config": { "path": "./.mem0_qdrant", "embedding_model_dims": 384 } },
        "embedder": { "provider": "huggingface", "config": { "model": "sentence-transformers/all-MiniLM-L6-v2" } },
        "llm": { "provider": "ollama", "config": { "model": "phi3", "ollama_base_url": "http://localhost:11434" } },
    }
    
    try:
        m = Memory.from_config(config)
        results = m.search(query, user_id="agent")
        
        print(f"\n--- Search results for: '{query}' ---")
        if not results:
            print("No matching memories found.")
        else:
            m_list = results.get('results', []) if isinstance(results, dict) else results
            for i, res in enumerate(m_list):
                text = res.get('memory') or res.get('text')
                print(f"[{i+1}] {text} (Score: {res.get('score', 'N/A')})")
        print("---------------------------------------\n")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        search_memory(sys.argv[1])
    else:
        print("Usage: python search_memory.py '<query>'")
