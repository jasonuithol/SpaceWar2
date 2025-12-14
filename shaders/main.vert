#version 330 core
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
