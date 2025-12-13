import pyglet
from pyglet.gl import *
from pyglet.graphics import shader
from pyglet.math import Mat4, Vec3
import math
import random
import numpy as np
import time

# Vertex shader
# Note: layout(std140) ensures the block matches Pyglet's internal memory layout
VERTEX_SHADER = """#version 330 core
in vec3 position;
in vec3 normal;
in vec3 colors;

out vec3 vertex_colors;
out vec3 fragPosition;
out vec3 fragNormal;

layout(std140) uniform WindowBlock {
    mat4 projection;
    mat4 view;
} window;

uniform mat4 model;

void main() {
    vec4 worldPos = model * vec4(position, 1.0);
    fragPosition = worldPos.xyz;
    fragNormal = mat3(transpose(inverse(model))) * normal;
    vertex_colors = colors;
    
    gl_Position = window.projection * window.view * worldPos;
}
"""

# Fragment shader
FRAGMENT_SHADER = """#version 330 core
in vec3 vertex_colors;
in vec3 fragPosition;
in vec3 fragNormal;

out vec4 finalColor;

uniform vec3 sunPosition;
uniform bool isEmissive;

void main() {
    if (isEmissive) {
        finalColor = vec4(vertex_colors, 1.0);
    } else {
        // Ambient (space glow)
        vec3 ambient = 0.25 * vertex_colors;
        
        // Diffuse from sun
        vec3 lightDir = normalize(sunPosition - fragPosition);
        vec3 norm = normalize(fragNormal);
        float diff = max(dot(norm, lightDir), 0.0);
        
        // Distance attenuation
        float distance = length(sunPosition - fragPosition);
        float attenuation = 1.0 / (1.0 + 0.001 * distance + 0.000005 * distance * distance);
        
        vec3 sunColor = vec3(1.0, 0.85, 0.6);
        vec3 diffuse = diff * sunColor * vertex_colors * attenuation;
        
        finalColor = vec4(ambient + diffuse, 1.0);
    }
}
"""

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
    
    def setup_opengl(self):
        """Initialize OpenGL state"""
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self.window.clear()
    
    def create_shader(self):
        """Create shader program"""
        self.shader_program = shader.ShaderProgram(
            shader.Shader(VERTEX_SHADER, 'vertex'),
            shader.Shader(FRAGMENT_SHADER, 'fragment')
        )
        
        # Create a simple shader for stars (points) to avoid lighting calculations
        # or just reuse the main shader with emissive=True
        
    def init_geometry(self):
        """Create and store VertexLists for objects"""
        
        # --- Pyramid (Ship) ---
        # Centered: Tip is at Y=+0.5, Base is at Y=-0.5
        # This ensures it spins purely in place like a top.
        pyramid_vertices = [
            # Front face
            0.0, 0.5, 0.0,    0.5, -0.5, 0.5,   -0.5, -0.5, 0.5,
            # Left face  
            0.0, 0.5, 0.0,   -0.5, -0.5, 0.5,  -0.5, -0.5, -0.5,
            # Back face
            0.0, 0.5, 0.0,   -0.5, -0.5, -0.5,  0.5, -0.5, -0.5,
            # Right face
            0.0, 0.5, 0.0,    0.5, -0.5, -0.5,  0.5, -0.5, 0.5,
            # Base (Two triangles making a square)
            0.5, -0.5, 0.5,  -0.5, -0.5, 0.5,  -0.5, -0.5, -0.5,
            0.5, -0.5, 0.5,  -0.5, -0.5, -0.5,  0.5, -0.5, -0.5,
        ]
        
        pyramid_normals = []
        for i in range(0, len(pyramid_vertices), 9):
            v1 = np.array(pyramid_vertices[i:i+3])
            v2 = np.array(pyramid_vertices[i+3:i+6])
            v3 = np.array(pyramid_vertices[i+6:i+9])
            edge1 = v2 - v1
            edge2 = v3 - v1
            normal = np.cross(edge1, edge2)
            normal = normal / (np.linalg.norm(normal) + 1e-10)
            pyramid_normals.extend(list(normal) * 3)
            
        # We create the vertex list once. 
        # Note: We will use a white color by default and modulate it or using uniforms if we wanted
        # But since the shader expects 'in vec3 colors', we must provide them.
        # We'll create a generic white ship and recolor in shader or just rebuild for simplicity.
        # For this example, we will store the raw data and build the list on draw if color changes,
        # OR better, pass color as a uniform. But sticking to your shader structure:
        self.pyramid_data = (pyramid_vertices, pyramid_normals)

        # --- Sphere (Sun/Bullets) ---
        slices, stacks = 16, 16
        s_vertices = []
        s_normals = []
        s_indices = []
        
        for i in range(stacks + 1):
            lat = math.pi * (-0.5 + float(i) / stacks)
            y = math.sin(lat)
            r = math.cos(lat)
            for j in range(slices + 1):
                lon = 2 * math.pi * float(j) / slices
                x = r * math.cos(lon)
                z = r * math.sin(lon)
                s_vertices.extend([x, y, z])
                s_normals.extend([x, y, z])
        
        for i in range(stacks):
            for j in range(slices):
                first = i * (slices + 1) + j
                second = first + slices + 1
                s_indices.extend([first, second, first + 1, second, second + 1, first + 1])
                
        self.sphere_data = (s_vertices, s_normals, s_indices)

        # Create the reusable VertexList for the sphere (White default)
        # We can use this for the Sun and Bullets
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
        # Note: Because ships have different colors, we can't easily reuse one static VBO
        # without a 'color' uniform. To keep this robust but simple, we create a
        # temporary VList for the ship if the color differs, or just rebuild it.
        # Optimized approach: Pass color as Uniform, but shader expects attribute.
        # We will rebuild the ship VList for this specific implementation.
        vertices, normals = self.pyramid_data

        # We use time.time() to get a continuous value for the rotation angle
        anim_time = time.time()

        for ship in game_state.ships.values():
            if not ship.alive:
                continue
            
            color_rgb = self.player_colors[ship.player_id % len(self.player_colors)]
            
            # --- MATRICES ---
            
            # 1. Scale (Local)
            scale_mat = Mat4().scale(Vec3(15, 15, 15))
            
            # 2. Roll / Spin Animation (Local)
            # We rotate around Y because our pyramid model "points" up the Y axis.
            # 5.0 is the speed of the spin (radians per second).
            roll_angle = anim_time * 5.0  
            roll_mat = Mat4().rotate(roll_angle, Vec3(0, 1, 0))
            
            # 3. Heading / Direction (World Orientation)
            # This orients the spinning ship to face its travel direction
            heading_mat = Mat4().rotate(ship.angle - math.pi/2, Vec3(0, 0, 1))
            
            # 4. Position (World Space)
            trans_mat = Mat4().translate(Vec3(ship.position[0], ship.position[1], 0))
            
            # Combine: Translate @ Heading @ Roll @ Scale
            # This order is CRITICAL.
            ship_model = trans_mat @ heading_mat @ roll_mat @ scale_mat
            
            # --- RENDER ---
            
            # Create color array (since we aren't using uniforms for color yet)
            colors = color_rgb * (len(vertices) // 3)
            
            self.shader_program['model'] = ship_model
            self.shader_program['isEmissive'] = False
            self.shader_program['sunPosition'] = self.sun_pos
            
            self.shader_program.vertex_list(
                len(vertices) // 3, GL_TRIANGLES,
                position=('f', vertices),
                normal=('f', normals),
                colors=('f', colors)
            ).draw(GL_TRIANGLES)

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
    