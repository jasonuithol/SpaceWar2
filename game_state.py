################################################################################
# game_state.py - Client Game State
################################################################################

import numpy as np
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class ClientShip:
    player_id: int
    position: np.ndarray
    velocity: np.ndarray
    angle: float
    alive: bool
    score: int

@dataclass
class ClientBullet:
    owner_id: int
    position: np.ndarray

class GameState:
    def __init__(self):
        self.ships: Dict[int, ClientShip] = {}
        self.bullets: List[ClientBullet] = []
        self.sun_position = np.array([400.0, 300.0])
        self.sun_radius = 30
        self.local_player_id: int = -1
        self.last_update_time = 0.0
        
    def update_from_server(self, state_data: dict):
        """Update state from server data"""
        self.last_update_time = state_data["time"]
        
        # Update ships
        self.ships.clear()
        for ship_data in state_data["ships"]:
            self.ships[ship_data["player_id"]] = ClientShip(
                player_id=ship_data["player_id"],
                position=np.array([ship_data["x"], ship_data["y"]]),
                velocity=np.array([ship_data["vx"], ship_data["vy"]]),
                angle=ship_data["angle"],
                alive=ship_data["alive"],
                score=ship_data["score"]
            )
        
        # Update bullets
        self.bullets.clear()
        for bullet_data in state_data["bullets"]:
            self.bullets.append(ClientBullet(
                owner_id=bullet_data["owner_id"],
                position=np.array([bullet_data["x"], bullet_data["y"]])
            ))
        
        # Update sun
        sun_data = state_data["sun"]
        self.sun_position = np.array([sun_data["x"], sun_data["y"]])
        self.sun_radius = sun_data["radius"]
    
    def set_local_player(self, player_id: int):
        """Set the local player ID"""
        self.local_player_id = player_id
    
    def get_local_ship(self) -> ClientShip:
        """Get the local player's ship"""
        return self.ships.get(self.local_player_id)

