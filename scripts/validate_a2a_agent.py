#!/usr/bin/env python3
import asyncio
import json
import os
import time
import uuid

import httpx

__version__ = "0.1.0"

print("Starting A2A Agent Validation and waiting for server initialization...")
time.sleep(30)

A2A_URL = os.environ.get("A2A_URL", "http://127.0.0.1:9016/a2a/")


async def main():
    print("Validating the configured A2A agent...")

    questions = [
        os.environ.get(
            "A2A_VALIDATION_QUERY", "Describe your available capabilities."
        )
    ]

    async with httpx.AsyncClient(timeout=10000.0) as client:
        for q in questions:
            print("\nSubmitting the configured validation query.")
            print("--- Sending Request ---")

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
                url = A2A_URL
                print("Trying the configured endpoint with JSON-RPC (message/send)...")
                resp = await client.post(
                    url, json=payload, headers={"Content-Type": "application/json"}
                )

                print(f"Status Code: {resp.status_code}")
                if resp.status_code == 200:
                    try:
                        data = resp.json()
                        print("JSON response received.")

                        if "result" in data and "id" in data["result"]:
                            task_id = data["result"]["id"]
                            print("\nTask submitted; polling for result...")

                            while True:
                                await asyncio.sleep(2)
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
                                        ]:
                                            print(
                                                f"\nTask Finished with state: {state}"
                                            )

                                            if "history" in poll_data["result"]:
                                                history = poll_data["result"]["history"]
                                                if history:
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
                                                                print("Agent response content omitted.")
                                                            elif "content" in part:
                                                                print("Agent response content omitted.")
                                                    elif last_msg:
                                                        print("Final response received without structured parts.")
                                                    else:
                                                        print(
                                                            "\n--- No Agent Response Found in History ---"
                                                        )

                                            print("Validation result received; body omitted.")
                                            break
                                    else:
                                        print("Starting polling error key check...")
                                        if "error" in poll_data:
                                            print(f"Polling JSON-RPC error code: {poll_data['error'].get('code', 'unknown')}")
                                        break
                                else:
                                    print(f"Polling Failed: {poll_resp.status_code}")
                                    print(f"Polling failed with HTTP {poll_resp.status_code}.")
                                    break

                        if "error" in data:
                            print(f"JSON-RPC error code: {data['error'].get('code', 'unknown')}")
                    except json.JSONDecodeError:
                        print(f"Response body omitted (HTTP {resp.status_code}).")
                else:
                    print(f"Error: {resp.status_code}")
                    print(f"Response body omitted (HTTP {resp.status_code}).")

            except httpx.RequestError as e:
                print(f"Operation failed: {type(e).__name__}")


if __name__ == "__main__":
    asyncio.run(main())
