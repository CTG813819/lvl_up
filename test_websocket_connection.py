#!/usr/bin/env python3
"""
Test script to verify WebSocket connection to the backend server
"""

import asyncio
import websockets
import json
import sys

async def test_websocket_connection():
    """Test WebSocket connection to the backend server"""
    
    # Test URLs
    urls = [
        "ws://34.202.215.209:8000/ws",
        "ws://34.202.215.209:8000/ws/imperium/learning-analytics",
        "ws://34.202.215.209:8000/api/notifications/ws",
        "ws://34.202.215.209:4000/ws",
    ]
    
    for url in urls:
        print(f"\n🔌 Testing WebSocket connection to: {url}")
        try:
            async with websockets.connect(url) as websocket:
                print(f"✅ Successfully connected to {url}")
                
                # Send a test message
                test_message = {
                    "type": "connection",
                    "client": "test_script",
                    "timestamp": "2024-01-01T00:00:00Z"
                }
                
                await websocket.send(json.dumps(test_message))
                print(f"📤 Sent test message: {test_message}")
                
                # Try to receive a response
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5)
                    print(f"📨 Received response: {response}")
                except asyncio.TimeoutError:
                    print("⏰ No response received within 5 seconds")
                
                await websocket.close()
                print(f"🔌 Closed connection to {url}")
                
        except websockets.exceptions.InvalidURI as e:
            print(f"❌ Invalid URI: {e}")
        except websockets.exceptions.ConnectionClosed as e:
            print(f"❌ Connection closed: {e}")
        except websockets.exceptions.InvalidStatusCode as e:
            print(f"❌ Invalid status code: {e}")
        except Exception as e:
            print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket_connection()) 