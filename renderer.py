################################################################################
# renderer.py - Pyglet Renderer
################################################################################

import pyglet
from pyglet import shapes
import math
import random

class Renderer:
    def __init__(self, width=800, height=600):
        self.window = pyglet.window.Window(width, height, "Spacewar!")
        self.batch = pyglet.graphics.Batch()
        self.width = width
        self.height = height
        
        # Colors for different players
        self.player_colors = [
            (100, 150, 255),  # Blue
            (255, 100, 100),  # Red
            (100, 255, 100),  # Green
            (255, 255, 100),  # Yellow
        ]
        
        # Background stars
        self.stars = []
        for _ in range(100):
            x = random.randint(0, width)
            y = random.randint(0, height)
            star = shapes.Circle(x, y, 1, color=(200, 200, 200), batch=self.batch)
            self.stars.append(star)
    
    def draw(self, game_state):
        """Draw the game state"""
        self.window.clear()
        
        # Draw stars
        self.batch.draw()
        
        # Draw sun
        sun_shape = shapes.Circle(
            game_state.sun_position[0],
            game_state.sun_position[1],
            game_state.sun_radius,
            color=(255, 200, 0)
        )
        sun_shape.draw()
        
        # Draw bullets
        for bullet in game_state.bullets:
            bullet_shape = shapes.Circle(
                bullet.position[0],
                bullet.position[1],
                3,
                color=(255, 255, 255)
            )
            bullet_shape.draw()
        
        # Draw ships
        for ship in game_state.ships.values():
            color = self.player_colors[ship.player_id % len(self.player_colors)]
            
            if not ship.alive:
                # Draw dead ship as X
                x, y = ship.position[0], ship.position[1]
                line1 = shapes.Line(x-10, y-10, x+10, y+10, 2, color=color)
                line2 = shapes.Line(x-10, y+10, x+10, y-10, 2, color=color)
                line1.draw()
                line2.draw()
                
                # Show "DEAD" label
                label = pyglet.text.Label(
                    f"P{ship.player_id} DEAD (Press R)",
                    font_size=10,
                    x=ship.position[0],
                    y=ship.position[1] - 25,
                    anchor_x='center',
                    anchor_y='center',
                    color=(*color, 255)
                )
                label.draw()
                continue
            
            # Draw ship as a triangle
            nose_x = ship.position[0] + math.cos(ship.angle) * 15
            nose_y = ship.position[1] + math.sin(ship.angle) * 15
            
            left_x = ship.position[0] + math.cos(ship.angle + 2.5) * 10
            left_y = ship.position[1] + math.sin(ship.angle + 2.5) * 10
            
            right_x = ship.position[0] + math.cos(ship.angle - 2.5) * 10
            right_y = ship.position[1] + math.sin(ship.angle - 2.5) * 10
            
            ship_shape = shapes.Triangle(
                nose_x, nose_y,
                left_x, left_y,
                right_x, right_y,
                color=color
            )
            ship_shape.draw()
            
            # Draw player ID and score
            label = pyglet.text.Label(
                f"P{ship.player_id} ({ship.score})",
                font_size=10,
                x=ship.position[0],
                y=ship.position[1] - 25,
                anchor_x='center',
                anchor_y='center',
                color=(*color, 255)
            )
            label.draw()
        
        # Draw status for local player
        if game_state.local_player_id >= 0:
            local_ship = game_state.get_local_ship()
            if local_ship:
                status = "ALIVE" if local_ship.alive else "DEAD - Press R to respawn"
                status_label = pyglet.text.Label(
                    f"You are Player {game_state.local_player_id} - {status}",
                    font_size=14,
                    x=10,
                    y=self.height - 20,
                    color=(255, 255, 255, 255)
                )
                status_label.draw()
