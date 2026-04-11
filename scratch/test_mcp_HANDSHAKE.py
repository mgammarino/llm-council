import subprocess
import json
import time
import sys
import threading

def read_stream(stream, name):
    for line in iter(stream.readline, ''):
        print(f"[{name}] {line[:1000].strip()}...")

def test_mcp_startup():
    # Start the server
    process = subprocess.Popen(
        [sys.executable, 'src/llm_council/mcp_server.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0
    )

    # Use threads to read stdout and stderr in parallel
    stdout_thread = threading.Thread(target=read_stream, args=(process.stdout, "STDOUT"))
    stderr_thread = threading.Thread(target=read_stream, args=(process.stderr, "STDERR"))
    stdout_thread.daemon = True
    stderr_thread.daemon = True
    stdout_thread.start()
    stderr_thread.start()

    try:
        # Give it a second to start
        print("Waiting for server to start...")
        time.sleep(2)
        
        # 1. Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        time.sleep(1)

        # 2. Send initialized notification
        init_notif = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        process.stdin.write(json.dumps(init_notif) + "\n")
        process.stdin.flush()
        time.sleep(1)

        # 3. Send tools/list request
        print("Sending tools/list request...")
        list_tools_req = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        process.stdin.write(json.dumps(list_tools_req) + "\n")
        process.stdin.flush()
        time.sleep(2)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        process.terminate()

if __name__ == "__main__":
    test_mcp_startup()
