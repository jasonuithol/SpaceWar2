#version 330 core
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
