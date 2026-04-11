import subprocess
import json
import time
import sys

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

    try:
        # Give it a second to start
        time.sleep(2)
        
        # Check if it died immediately
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            print(f"Server died on startup with code {process.returncode}")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return

        print("Server started. Sending initialize request...")
        
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

        # Wait for initialize response
        print("Waiting for initialize response...")
        line = process.stdout.readline()
        if line:
            print(f"Received: {line}")
            # 2. Send initialized notification
            init_notif = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            }
            process.stdin.write(json.dumps(init_notif) + "\n")
            process.stdin.flush()
            print("Sent notifications/initialized")

            # 3. Send list_tools request
            list_tools_req = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "list_tools",
                "params": {}
            }
            process.stdin.write(json.dumps(list_tools_req) + "\n")
            process.stdin.flush()
            print("Sent list_tools")

            line = process.stdout.readline()
            if line:
                print(f"Received tools: {line[:200]}...")
            else:
                print("No tools response.")
        else:
            print("No initialize response.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        process.terminate()

if __name__ == "__main__":
    test_mcp_startup()
