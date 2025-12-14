
import pyglet
from pyglet.gl import *
from pyglet.graphics import shader
from pyglet.math import Mat4, Vec3
import random
import os

from . import geometry
from .spacecraft_renderer import SpacecraftManager

class Renderer:
    def __init__(self):
        # Config must be imported from pyglet.gl
        config = Config(sample_buffers=1, samples=4,
                        depth_size=24, double_buffer=True)
        self.window = pyglet.window.Window(fullscreen=True, config=config, caption="Space Game")
        self.width = self.window.width
        self.height = self.window.height
        
        # Colors for players
        self.player_colors = [
            (0.4, 0.6, 1.0),   # Blue
            (1.0, 0.4, 0.4),   # Red
            (0.4, 1.0, 0.4),   # Green
            (1.0, 1.0, 0.4),   # Yellow
        ]
        
        self.setup_opengl()
        self.create_shader()
        
        # Initialize geometry once (Performance fix)
        self.init_geometry()
        self.init_stars()

        self.spacecraft_manager = SpacecraftManager()
        self.spacecraft_manager.init_geometry(self.shader_program, self.pyramid)

    def setup_opengl(self):
        """Initialize OpenGL state"""
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self.window.clear()
    
    def create_shader(self):
        """Create shader program"""

        with open(os.path.join("shaders", "main.vert"), "r") as f:
            VERTEX_SHADER = f.read()

        with open(os.path.join("shaders", "main.frag"), "r") as f:
            FRAGMENT_SHADER = f.read()

        self.shader_program = shader.ShaderProgram(
            shader.Shader(VERTEX_SHADER, 'vertex'),
            shader.Shader(FRAGMENT_SHADER, 'fragment')
        )
        
        # Create a simple shader for stars (points) to avoid lighting calculations
        # or just reuse the main shader with emissive=True
        
    def init_geometry(self):
        """Initialize geometry by loading assets and generating sphere mesh"""
        
        # --- Pyramid (Ship) ---
        self.pyramid = geometry.init_pyramid_geometry() # <-- Load from OBJ

        # --- Sphere (Sun/Bullets) ---
        sphere = geometry.init_sphere_geometry() # <-- Programmatic generation
        s_vertices, s_normals, s_indices = sphere.vertices, sphere.normals, sphere.indices
        
        self.sphere_data = (s_vertices, s_normals, s_indices)

        # Create the reusable VertexList for the sphere (White default)
        white_colors = (1.0, 1.0, 1.0) * (len(s_vertices) // 3)
        self.sphere_vlist = self.shader_program.vertex_list_indexed(
            len(s_vertices) // 3, GL_TRIANGLES, s_indices,
            position=('f', s_vertices),
            normal=('f', s_normals),
            colors=('f', white_colors)
        )

    def init_stars(self):
        """Create star geometry"""
        star_points = []
        star_colors = []
        
        for _ in range(300):
            x = random.uniform(-500, 1300)
            y = random.uniform(-300, 900)
            z = random.uniform(-200, -50)
            brightness = random.uniform(0.4, 1.0)
            star_points.extend([x, y, z])
            star_colors.extend([brightness, brightness, brightness])
            
        # Create a VertexList for stars using GL_POINTS
        self.star_vlist = self.shader_program.vertex_list(
            len(star_points) // 3, GL_POINTS,
            position=('f', star_points),
            normal=('f', star_points), # Dummy normals
            colors=('f', star_colors)
        )

    def draw_mesh(self, vlist, model_matrix, is_emissive=False):
        """Helper to draw a vertex list"""
        self.shader_program['model'] = model_matrix
        self.shader_program['isEmissive'] = is_emissive
        self.shader_program['sunPosition'] = self.sun_pos
        vlist.draw(GL_TRIANGLES)

    def draw(self, game_state):
        """Main Draw Loop"""
        self.window.clear()
        
        # Update Sun Position Uniform
        self.sun_pos = (game_state.sun_position[0], game_state.sun_position[1], 0.0)
        
        # 1. 3D PASS
        # ---------------------------------------------------------
        # Set Window Projection and View for 3D
        # Pyglet's WindowBlock will automatically update the UBO
        self.window.projection = Mat4.perspective_projection(
            self.window.aspect_ratio, z_near=1.0, z_far=1000.0, fov=45.0
        )
        self.window.view = Mat4.look_at(
            position=Vec3(400, 300, 600),
            target=Vec3(400, 300, 0),
            up=Vec3(0, 1, 0)
        )
        
        self.shader_program.use()

        # Draw Stars
        # We use Identity model matrix for stars
        self.shader_program['model'] = Mat4()
        self.shader_program['isEmissive'] = True # Stars glow
        self.star_vlist.draw(GL_POINTS)

        # Draw Sun
        sun_model = (Mat4()
                     .translate(Vec3(*self.sun_pos))
                     .scale(Vec3(game_state.sun_radius, game_state.sun_radius, game_state.sun_radius)))
        # For the sun, we want a yellowish color. 
        # Since our reusable sphere is white, the fragment shader handles lighting,
        # but for an emissive object, it just returns vertex_color.
        # Ideally, we'd use a color uniform, but let's stick to the vlist for now.
        self.draw_mesh(self.sphere_vlist, sun_model, is_emissive=True)

        # Draw Bullets
        for bullet in game_state.bullets:
            bullet_model = (Mat4()
                           .translate(Vec3(bullet.position[0], bullet.position[1], 0))
                           .scale(Vec3(3, 3, 3)))
            self.draw_mesh(self.sphere_vlist, bullet_model, is_emissive=True)

        # Draw Ships
        self.shader_program['useTexture'] = True  # Enable textures
        self.spacecraft_manager.render_spacecraft(game_state)
        self.shader_program['useTexture'] = False  # Disable for other objects     

        # 2. 2D HUD PASS
        # ---------------------------------------------------------
        # Switch to Orthographic projection for UI
        self.window.projection = Mat4.orthogonal_projection(
            0, self.width, 0, self.height, -1, 1
        )
        self.window.view = Mat4() # Identity
        
        # Pyglet Labels use their own shaders, so we stop using ours
        self.shader_program.stop()
        
        # Using a Batch is best practice for UI
        batch = pyglet.graphics.Batch()
        
        if game_state.local_player_id >= 0:
            local_ship = game_state.get_local_ship()
            if local_ship:
                status = "ALIVE" if local_ship.alive else "DEAD - Press R"
                p_color = self.player_colors[local_ship.player_id % len(self.player_colors)]
                text_color = (int(p_color[0]*255), int(p_color[1]*255), int(p_color[2]*255), 255)
                
                pyglet.text.Label(
                    f"P{game_state.local_player_id} - {status} | ESC=Quit",
                    font_size=16, x=10, y=self.height - 30,
                    color=text_color, batch=batch
                )
                
                pyglet.text.Label(
                    f"Score: {local_ship.score}",
                    font_size=20, x=self.width - 10, y=self.height - 30,
                    anchor_x='right', color=(255, 255, 255, 255), batch=batch
                )
        
        # Draw all UI elements
        batch.draw()
    