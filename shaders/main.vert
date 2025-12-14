#version 330 core
// ============================================================================
// main.vert - Updated Vertex Shader with Texture Coordinate Support
// ============================================================================

in vec3 position;
in vec3 normal;
in vec3 colors;
in vec2 tex_coords;  // NEW: Texture coordinates input

uniform WindowBlock {
    mat4 projection;
    mat4 view;
} window;

uniform mat4 model;

out vec3 FragPos;
out vec3 Normal;
out vec3 VertexColor;
out vec2 TexCoord;  // NEW: Pass to fragment shader

void main() {
    gl_Position = window.projection * window.view * model * vec4(position, 1.0);
    FragPos = vec3(model * vec4(position, 1.0));
    Normal = mat3(transpose(inverse(model))) * normal;
    VertexColor = colors;
    TexCoord = tex_coords;  // NEW: Pass texture coordinates
}
