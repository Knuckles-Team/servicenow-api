#!/usr/bin/env python3
import asyncio
import httpx
import json
import uuid
import time

__version__ = "0.1.0"

print("Starting A2A Agent Validation and waiting for server initialization...")
time.sleep(30)

# Configuration
A2A_URL = "http://localhost:9004/a2a/"


async def main():
    print(f"Validating A2A Agent at {A2A_URL}...")

    questions = [
        "Can you get me the incident: INC0010004?"
        # "Can you create an incident with the short description: 'Test Incident from AI', description: 'Test Again from AI'"
        # "Get the incidents",
        # "Can you create an change request with the short description: 'Test Change from AI', description: 'Test Again from AI', justification: 'We need this upgrade', test plan: 'Test the AI Agent'",
        # "Fetch the change requests",
    ]

    async with httpx.AsyncClient(timeout=10000.0) as client:
        # First, let's verify connectivity and maybe infer output schema

        for q in questions:
            print(f"\n\n\nUser: {q}")
            print("--- Sending Request ---")

            # Construct JSON-RPC payload
            payload = {
                "jsonrpc": "2.0",
                "method": "message/send",
                "params": {
                    "message": {
                        "kind": "message",
                        "role": "user",
                        "parts": [{"kind": "text", "text": q}],
                        "messageId": str(uuid.uuid4()),
                    }
                },
                "id": 1,
            }

            try:
                # Attempt POST to root
                url = A2A_URL
                print(f"Trying POST {url} with JSON-RPC (message/send)...")
                resp = await client.post(
                    url, json=payload, headers={"Content-Type": "application/json"}
                )

                print(f"Status Code: {resp.status_code}")
                if resp.status_code == 200:
                    try:
                        data = resp.json()
                        print(f"Response (JSON):\n{json.dumps(data, indent=2)}")

                        if "result" in data and "id" in data["result"]:
                            task_id = data["result"]["id"]
                            print(
                                f"\nTask Submitted with ID: {task_id}. Polling for result..."
                            )

                            # Poll tasks/get
                            while True:
                                await asyncio.sleep(2)  # Wait a bit
                                poll_payload = {
                                    "jsonrpc": "2.0",
                                    "method": "tasks/get",
                                    "params": {"id": task_id},
                                    "id": 2,
                                }
                                poll_resp = await client.post(
                                    url,
                                    json=poll_payload,
                                    headers={"Content-Type": "application/json"},
                                )
                                if poll_resp.status_code == 200:
                                    poll_data = poll_resp.json()
                                    if "result" in poll_data:
                                        state = poll_data["result"]["status"]["state"]
                                        print(f"Task State: {state}")
                                        if state not in [
                                            "submitted",
                                            "running",
                                            "working",
                                        ]:  # Assuming terminal states
                                            print(
                                                f"\nTask Finished with state: {state}"
                                            )

                                            # Extract final result
                                            if "history" in poll_data["result"]:
                                                history = poll_data["result"]["history"]
                                                if history:
                                                    # Find last non-user message
                                                    last_msg = None
                                                    for msg in reversed(history):
                                                        if msg.get("role") != "user":
                                                            last_msg = msg
                                                            break

                                                    if last_msg and "parts" in last_msg:
                                                        print(
                                                            "\n--- Agent Response ---"
                                                        )
                                                        for part in last_msg["parts"]:
                                                            if "text" in part:
                                                                print(part["text"])
                                                            elif "content" in part:
                                                                print(part["content"])
                                                    elif last_msg:
                                                        print(
                                                            f"Final Message (No parts): {last_msg}"
                                                        )
                                                    else:
                                                        print(
                                                            "\n--- No Agent Response Found in History ---"
                                                        )

                                            print(
                                                f"Full Result Debug:\n{json.dumps(poll_data, indent=2)}"
                                            )
                                            break
                                    else:
                                        print("Starting polling error key check...")
                                        if "error" in poll_data:
                                            print(
                                                f"Polling Error: {poll_data['error']}"
                                            )
                                        break
                                else:
                                    print(f"Polling Failed: {poll_resp.status_code}")
                                    print(f"Polling Error Details: {poll_resp.text}")
                                    break

                        if "error" in data:
                            print(f"JSON-RPC Error: {data['error']}")
                    except json.JSONDecodeError:
                        print(f"Response (Text):\n{resp.text}")
                else:
                    print(f"Error: {resp.status_code}")
                    print(resp.text)

            except httpx.RequestError as e:
                print(f"Connection failed to {url}: {e}")


if __name__ == "__main__":
    asyncio.run(main())
