################################################################################
# server.py - Game Server
################################################################################

import asyncio
import websockets
import json
import numpy as np
from dataclasses import dataclass, asdict
from typing import Set
import time

# --- Import Configuration ---
from config import *

@dataclass
class Ship:
    player_id: int
    position: np.ndarray
    velocity: np.ndarray
    angle: float
    alive: bool = True
    score: int = 0

@dataclass
class Bullet:
    owner_id: int
    position: np.ndarray
    velocity: np.ndarray
    birth_time: float

class GameServer:
    def __init__(self):
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.ships = {}
        self.bullets = []
        self.sun_position = np.array([WORLD_WIDTH / 2, WORLD_HEIGHT / 2])
        self.player_inputs = {}
        self.next_player_id = 0
        self.game_time = 0.0
        
    async def register(self, websocket):
        """Register a new client"""
        if len(self.clients) >= 4:
            await websocket.send(json.dumps({"type": "error", "message": "Game full"}))
            return None
            
        player_id = self.next_player_id
        self.next_player_id += 1
        
        self.clients.add(websocket)
        print(f"Player {player_id} connected ({len(self.clients)} total players)")
        
        # Spawn positions (corners)
        spawn_positions = [
            np.array([100.0, 100.0], dtype=float),
            np.array([WORLD_WIDTH - 100, 100.0], dtype=float),
            np.array([100.0, WORLD_HEIGHT - 100], dtype=float),
            np.array([WORLD_WIDTH - 100, WORLD_HEIGHT - 100], dtype=float)
        ]
        
        self.ships[player_id] = Ship(
            player_id=player_id,
            position=spawn_positions[player_id % 4].copy(),
            velocity=np.zeros(2, dtype=float),
            angle=0.0
        )
        
        self.player_inputs[player_id] = {
            "thrust": False,
            "rotate_left": False,
            "rotate_right": False,
            "shoot": False,
            "respawn": False
        }
        
        await websocket.send(json.dumps({
            "type": "player_id",
            "player_id": player_id
        }))
        
        return player_id
        
    async def unregister(self, websocket, player_id):
        """Remove a client"""
        self.clients.discard(websocket)
        if player_id is not None and player_id in self.ships:
            del self.ships[player_id]
            del self.player_inputs[player_id]
    
    async def handle_client(self, websocket):
        """Handle a client connection"""
        player_id = await self.register(websocket)
        if player_id is None:
            return
            
        try:
            async for message in websocket:
                data = json.loads(message)
                if data["type"] == "input":
                    self.player_inputs[player_id] = data["inputs"]
        finally:
            await self.unregister(websocket, player_id)
    
    def apply_gravity(self, dt):
        """Apply gravitational force from sun"""
        for ship in self.ships.values():
            if not ship.alive:
                continue
            delta = self.sun_position - ship.position
            distance = np.linalg.norm(delta)
            if distance > SUN_RADIUS:
                force = GRAVITY_CONSTANT * SUN_MASS * SHIP_MASS / (distance ** 2)
                acceleration = (delta / distance) * (force / SHIP_MASS)
                ship.velocity += acceleration * dt
        
        # Apply gravity to bullets too
        for bullet in self.bullets:
            delta = self.sun_position - bullet.position
            distance = np.linalg.norm(delta)
            if distance > SUN_RADIUS:
                force = GRAVITY_CONSTANT * SUN_MASS / (distance ** 2)
                acceleration = (delta / distance) * force
                bullet.velocity += acceleration * dt
    
    def process_inputs(self, dt):
        """Process player inputs"""
        for player_id, inputs in self.player_inputs.items():
            ship = self.ships.get(player_id)
            if not ship:
                continue
            
            # Respawn
            if inputs.get("respawn") and not ship.alive:
                spawn_positions = [
                    np.array([100.0, 100.0], dtype=float),
                    np.array([WORLD_WIDTH - 100, 100.0], dtype=float),
                    np.array([100.0, WORLD_HEIGHT - 100], dtype=float),
                    np.array([WORLD_WIDTH - 100, WORLD_HEIGHT - 100], dtype=float)
                ]
                ship.position = spawn_positions[player_id % 4].copy()
                ship.velocity = np.zeros(2, dtype=float)
                ship.angle = 0.0
                ship.alive = True
                continue
            
            if not ship.alive:
                continue
            
            # Rotation
            if inputs["rotate_left"]:
                ship.angle += SHIP_ROTATION_SPEED * dt
            if inputs["rotate_right"]:
                ship.angle -= SHIP_ROTATION_SPEED * dt
            
            # Thrust
            if inputs["thrust"]:
                thrust_vector = np.array([
                    np.cos(ship.angle),
                    np.sin(ship.angle)
                ]) * SHIP_THRUST * dt
                ship.velocity += thrust_vector
            
            # Shooting
            if inputs["shoot"]:
                # Simple cooldown: only shoot if no recent bullet from this player
                recent_bullets = [b for b in self.bullets 
                                if b.owner_id == player_id and 
                                self.game_time - b.birth_time < 0.3]
                if not recent_bullets:
                    bullet_vel = np.array([
                        np.cos(ship.angle),
                        np.sin(ship.angle)
                    ]) * BULLET_SPEED + ship.velocity
                    
                    self.bullets.append(Bullet(
                        owner_id=player_id,
                        position=ship.position.copy(),
                        velocity=bullet_vel,
                        birth_time=self.game_time
                    ))
    
    def update_positions(self, dt):
        """Update all positions"""
        for ship in self.ships.values():
            if ship.alive:
                ship.position += ship.velocity * dt
        
        for bullet in self.bullets:
            bullet.position += bullet.velocity * dt
    
    def check_collisions(self):
        """Check for collisions"""
        # Remove old bullets
        self.bullets = [b for b in self.bullets 
                       if self.game_time - b.birth_time < BULLET_LIFETIME]
        
        # Ship-sun collision
        for ship in self.ships.values():
            if ship.alive:
                dist = np.linalg.norm(ship.position - self.sun_position)
                if dist < SUN_RADIUS + SHIP_RADIUS:
                    ship.alive = False
        
        # Bullet-ship collision
        bullets_to_remove = []
        for i, bullet in enumerate(self.bullets):
            for ship in self.ships.values():
                if not ship.alive or ship.player_id == bullet.owner_id:
                    continue
                dist = np.linalg.norm(bullet.position - ship.position)
                if dist < SHIP_RADIUS + BULLET_RADIUS:
                    ship.alive = False
                    if bullet.owner_id in self.ships:
                        self.ships[bullet.owner_id].score += 1
                    bullets_to_remove.append(i)
                    break
        
        # Remove hit bullets (iterate backwards to avoid index issues)
        for i in reversed(bullets_to_remove):
            del self.bullets[i]
        
        # Boundary wrapping
        for ship in self.ships.values():
            ship.position[0] = ship.position[0] % WORLD_WIDTH
            ship.position[1] = ship.position[1] % WORLD_HEIGHT
        
        # Remove out-of-bounds bullets
        self.bullets = [b for b in self.bullets
                       if 0 <= b.position[0] <= WORLD_WIDTH and
                          0 <= b.position[1] <= WORLD_HEIGHT]
    
    def get_game_state(self):
        """Get current game state for broadcasting"""
        return {
            "type": "game_state",
            "time": self.game_time,
            "ships": [
                {
                    "player_id": s.player_id,
                    "x": float(s.position[0]),
                    "y": float(s.position[1]),
                    "vx": float(s.velocity[0]),
                    "vy": float(s.velocity[1]),
                    "angle": float(s.angle),
                    "alive": s.alive,
                    "score": s.score
                }
                for s in self.ships.values()
            ],
            "bullets": [
                {
                    "owner_id": b.owner_id,
                    "x": float(b.position[0]),
                    "y": float(b.position[1])
                }
                for b in self.bullets
            ],
            "sun": {
                "x": float(self.sun_position[0]),
                "y": float(self.sun_position[1]),
                "radius": SUN_RADIUS
            }
        }
    
    async def game_loop(self):
        """Main game loop"""
        dt = 1.0 / TICK_RATE
        while True:
            start_time = time.time()
            
            self.apply_gravity(dt)
            self.process_inputs(dt)
            self.update_positions(dt)
            self.check_collisions()
            
            self.game_time += dt
            
            # Broadcast state
            if self.clients:
                state = self.get_game_state()
                message = json.dumps(state)
                websockets.broadcast(self.clients, message)
            
            # Sleep to maintain tick rate
            elapsed = time.time() - start_time
            sleep_time = max(0, dt - elapsed)
            await asyncio.sleep(sleep_time)
    
    async def start(self, host="localhost", port=8765):
        """Start the server"""
        async with websockets.serve(self.handle_client, host, port):
            print(f"Server started on ws://{host}:{port}")
            await self.game_loop()

if __name__ == "__main__":
    server = GameServer()
    asyncio.run(server.start())
