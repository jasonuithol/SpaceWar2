################################################################################
# renderer.py - Pyglet Renderer
################################################################################

import pyglet
from pyglet import shapes
import math
import random

class Renderer:
    def __init__(self, width=800, height=600):
        self.window = pyglet.window.Window(fullscreen=True)
        self.width = self.window.width
        self.height = self.window.height
        self.batch = pyglet.graphics.Batch()
        
        # Colors for different players
        self.player_colors = [
            (100, 150, 255),  # Blue
            (255, 100, 100),  # Red
            (100, 255, 100),  # Green
            (255, 255, 100),  # Yellow
        ]
        
        # Background stars
        self.stars = []
        for _ in range(200):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            star = shapes.Circle(x, y, 1, color=(200, 200, 200), batch=self.batch)
            self.stars.append(star)
    
    def draw(self, game_state):
        """Draw the game state"""
        self.window.clear()
        
        # Calculate scaling to fit game world in window
        scale_x = self.width / 800  # Game world is 800x600
        scale_y = self.height / 600
        scale = min(scale_x, scale_y)  # Maintain aspect ratio
        
        offset_x = (self.width - 800 * scale) / 2
        offset_y = (self.height - 600 * scale) / 2
        
        # Draw stars
        self.batch.draw()
        
        # Draw sun
        sun_x = game_state.sun_position[0] * scale + offset_x
        sun_y = game_state.sun_position[1] * scale + offset_y
        sun_shape = shapes.Circle(
            sun_x, sun_y,
            game_state.sun_radius * scale,
            color=(255, 200, 0)
        )
        sun_shape.draw()
        
        # Draw bullets
        for bullet in game_state.bullets:
            bx = bullet.position[0] * scale + offset_x
            by = bullet.position[1] * scale + offset_y
            bullet_shape = shapes.Circle(bx, by, 3 * scale, color=(255, 255, 255))
            bullet_shape.draw()
        
        # Draw ships
        for ship in game_state.ships.values():
            color = self.player_colors[ship.player_id % len(self.player_colors)]
            
            sx = ship.position[0] * scale + offset_x
            sy = ship.position[1] * scale + offset_y
            
            if not ship.alive:
                # Draw dead ship as X
                size = 10 * scale
                line1 = shapes.Line(sx-size, sy-size, sx+size, sy+size, 2, color=color)
                line2 = shapes.Line(sx-size, sy+size, sx+size, sy-size, 2, color=color)
                line1.draw()
                line2.draw()
                
                # Show "DEAD" label
                label = pyglet.text.Label(
                    f"P{ship.player_id} DEAD (Press R)",
                    font_size=int(10 * scale),
                    x=sx,
                    y=sy - 25 * scale,
                    anchor_x='center',
                    anchor_y='center',
                    color=(*color, 255)
                )
                label.draw()
                continue
            
            # Draw ship as a triangle
            nose_x = sx + math.cos(ship.angle) * 15 * scale
            nose_y = sy + math.sin(ship.angle) * 15 * scale
            
            left_x = sx + math.cos(ship.angle + 2.5) * 10 * scale
            left_y = sy + math.sin(ship.angle + 2.5) * 10 * scale
            
            right_x = sx + math.cos(ship.angle - 2.5) * 10 * scale
            right_y = sy + math.sin(ship.angle - 2.5) * 10 * scale
            
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
                font_size=int(10 * scale),
                x=sx,
                y=sy - 25 * scale,
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
                    f"You are Player {game_state.local_player_id} - {status} | ESC to quit",
                    font_size=int(14 * scale),
                    x=10,
                    y=self.height - 20,
                    color=(255, 255, 255, 255)
                )
                status_label.draw()

