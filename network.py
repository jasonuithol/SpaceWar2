################################################################################
# network.py - Client Network Layer
################################################################################

import asyncio
import websockets
import json
from typing import Callable, Optional

class NetworkClient:
    def __init__(self, on_state_update: Callable, on_player_id: Callable):
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.on_state_update = on_state_update
        self.on_player_id = on_player_id
        self.connected = False
        
    async def connect(self, uri="ws://localhost:8765"):
        """Connect to the game server"""
        try:
            self.websocket = await websockets.connect(uri)
            self.connected = True
            print(f"Connected to {uri}")
        except Exception as e:
            print(f"Connection failed: {e}")
            self.connected = False
    
    async def send_inputs(self, inputs: dict):
        """Send player inputs to server"""
        if self.websocket and self.connected:
            try:
                await self.websocket.send(json.dumps({
                    "type": "input",
                    "inputs": inputs
                }))
            except Exception as e:
                print(f"Send error: {e}")
                self.connected = False
    
    async def receive_loop(self):
        """Receive game state updates"""
        if not self.websocket:
            return
            
        try:
            async for message in self.websocket:
                data = json.loads(message)
                
                if data["type"] == "player_id":
                    self.on_player_id(data["player_id"])
                elif data["type"] == "game_state":
                    self.on_state_update(data)
                elif data["type"] == "error":
                    print(f"Server error: {data['message']}")
        except websockets.exceptions.ConnectionClosed:
            print("Connection closed")
            self.connected = False
        except Exception as e:
            print(f"Receive error: {e}")
            self.connected = False
    
    async def close(self):
        """Close the connection"""
        if self.websocket:
            await self.websocket.close()
        self.connected = False

