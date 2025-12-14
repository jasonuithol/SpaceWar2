"""
Textured spacecraft renderer for SpaceWar2
Works with existing geometry and shader system
"""
import math
import time
import pyglet
from pyglet.gl import (
    GL_TRIANGLES, GL_TEXTURE_2D, 
    glEnable, glDisable, glBindTexture
)
from pyglet.math import Mat4, Vec3

class SpacecraftManager:
    """Manages textured spacecraft rendering"""
    
    # Map player IDs to colors
    PLAYER_COLORS = ['blue', 'red', 'yellow', 'green']
    
    # Player color to texture mapping
    TEXTURE_MAP = {
        'blue': 'assets/textures/spacecraft_blue_ice.png',
        'red': 'assets/textures/spacecraft_red_watermelon.png',
        'yellow': 'assets/textures/spacecraft_yellow_pyramid.png',
        'green': 'assets/textures/spacecraft_green_leaf.png',
    }
    
    def __init__(self):
        self.textures = {}
        self.vertex_lists = {}
        self.load_textures()
    
    def load_textures(self):
        """Load all spacecraft textures"""
        for color, path in self.TEXTURE_MAP.items():
            try:
                img = pyglet.image.load(path)
                texture = img.get_texture()
                self.textures[color] = texture
                print(f"Loaded texture for {color} spacecraft")
            except Exception as e:
                print(f"Warning: Could not load texture for {color}: {e}")
                self.textures[color] = None
    
    def init_geometry(self, shader_program, pyramid_geometry):
        """
        Initialize spacecraft geometry with textures
        
        Args:
            shader_program: The shader program to use
            pyramid_geometry: GeometryData with vertices, normals, tex_coords
        """
        self.shader_program = shader_program
        vertex_count = len(pyramid_geometry.vertices) // 3
        
        # Create vertex lists for each color
        for color in self.PLAYER_COLORS:
            # Use white base color so texture shows through
            white_colors = [1.0, 1.0, 1.0] * vertex_count
            
            self.vertex_lists[color] = shader_program.vertex_list(
                vertex_count,
                GL_TRIANGLES,
                position=('f', pyramid_geometry.vertices),
                normal=('f', pyramid_geometry.normals),
                colors=('f', white_colors),
                tex_coords=('f', pyramid_geometry.tex_coords)
            )
    
    def render_spacecraft(self, game_state):
        """
        Render all spacecraft from game state
        
        Args:
            game_state: GameState object with ships dict
        """

        spin_speed = 2.0                                        # radians per second (adjust to taste)
        spin_angle = (time.time() * spin_speed) % (2 * math.pi) # continuous roll

        # Render each ship
        for player_id, ship in game_state.ships.items():
            if not ship.alive:
                continue
            
            # Map player ID to color
            color = self.PLAYER_COLORS[player_id % len(self.PLAYER_COLORS)]
            
            # Create model matrix
            T        = Mat4.from_translation(Vec3(ship.position[0], ship.position[1], 0))
            R_facing = Mat4.from_rotation(ship.angle - math.pi/2, Vec3(0, 0, 1))  # angle in radians
            R_spin   = Mat4.from_rotation(spin_angle, Vec3(0, 1, 0))
            S        = Mat4.from_scale(Vec3(20, 20, 20))

            model = T @ R_facing @ R_spin @ S

            # Set shader uniforms
            self.shader_program['model'] = model
            self.shader_program['isEmissive'] = False
            
            # Bind texture if available
            texture = self.textures.get(color)
            if texture:
                glEnable(GL_TEXTURE_2D)
                glBindTexture(GL_TEXTURE_2D, texture.id)
            
            # Draw the spacecraft
            vertex_list = self.vertex_lists.get(color)
            if vertex_list:
                vertex_list.draw(GL_TRIANGLES)
            
            if texture:
                glDisable(GL_TEXTURE_2D)
