#version 330 core
// ============================================================================
// main.frag - Updated Fragment Shader with Texture Support
// ============================================================================

in vec3 FragPos;
in vec3 Normal;
in vec3 VertexColor;
in vec2 TexCoord;  // NEW: Receive texture coordinates

uniform vec3 sunPosition;
uniform bool isEmissive;
uniform sampler2D textureSampler;  // NEW: Texture sampler
uniform bool useTexture;           // NEW: Flag to enable/disable texture

out vec4 FragColor;

void main() {
    if (isEmissive) {
        // Emissive objects glow
        FragColor = vec4(VertexColor, 1.0);
    } else {
        // Calculate lighting
        vec3 norm = normalize(Normal);
        vec3 lightDir = normalize(sunPosition - FragPos);
        float diff = max(dot(norm, lightDir), 0.0);
        
        vec3 ambient = vec3(0.3);
        vec3 diffuse = vec3(0.7) * diff;
        
        // NEW: Sample texture if enabled
        vec3 baseColor;
        if (useTexture) {
            baseColor = texture(textureSampler, TexCoord).rgb;
        } else {
            baseColor = VertexColor;
        }
        
        vec3 result = (ambient + diffuse) * baseColor;
        FragColor = vec4(result, 1.0);
    }
}
