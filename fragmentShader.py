# GLSL

fragment_shader = '''
#version 330 core

in vec2 fragTexCoords;
in vec3 fragNormal;
in vec4 fragPosition;

out vec4 fragColor;

uniform sampler2D tex0;
uniform vec3 pointLight;
uniform float ambientLight;

void main()
{
    vec3 lightDir = normalize(pointLight - fragPosition.xyz);
    float intensity = max(0.0, dot(fragNormal, lightDir)) + ambientLight;
    fragColor = texture(tex0, fragTexCoords) * intensity;
}

'''

# NEW FRAGMENT SHADER 1: Hologram Effect
hologram_shader = '''
#version 330 core

in vec2 fragTexCoords;
in vec3 fragNormal;
in vec4 fragPosition;

out vec4 fragColor;

uniform sampler2D tex0;
uniform vec3 pointLight;
uniform float ambientLight;
uniform float time;

void main()
{
    vec3 lightDir = normalize(pointLight - fragPosition.xyz);
    float intensity = max(0.0, dot(fragNormal, lightDir)) + ambientLight;
    
    // Holographic color shift
    vec3 hologramColor = vec3(
        0.3 + 0.7 * sin(time + fragPosition.y * 10.0),
        0.5 + 0.5 * sin(time * 1.3 + fragPosition.y * 10.0),
        0.7 + 0.3 * sin(time * 1.7 + fragPosition.y * 10.0)
    );
    
    // Scanline effect
    float scanline = sin(fragPosition.y * 50.0 + time * 5.0) * 0.5 + 0.5;
    scanline = pow(scanline, 3.0);
    
    // Fresnel effect for edge glow
    vec3 viewDir = normalize(-fragPosition.xyz);
    float fresnel = pow(1.0 - abs(dot(viewDir, fragNormal)), 3.0);
    
    vec4 texColor = texture(tex0, fragTexCoords);
    
    // Combine effects
    vec3 finalColor = texColor.rgb * hologramColor * intensity;
    finalColor += hologramColor * fresnel * 0.8;
    finalColor *= (0.7 + scanline * 0.3);
    
    // Add transparency based on fresnel
    float alpha = 0.6 + fresnel * 0.4;
    
    fragColor = vec4(finalColor, alpha);
}

'''

# NEW FRAGMENT SHADER 2: Plasma/Fire Effect
plasma_shader = '''
#version 330 core

in vec2 fragTexCoords;
in vec3 fragNormal;
in vec4 fragPosition;

out vec4 fragColor;

uniform sampler2D tex0;
uniform float time;
uniform vec3 pointLight;
uniform float ambientLight;

void main()
{
    vec3 lightDir = normalize(pointLight - fragPosition.xyz);
    float baseIntensity = max(0.0, dot(fragNormal, lightDir)) + ambientLight;
    
    // Plasma effect using multiple sine waves
    float plasma = 0.0;
    
    plasma += sin(fragTexCoords.x * 10.0 + time);
    plasma += sin(fragTexCoords.y * 10.0 + time * 1.3);
    plasma += sin((fragTexCoords.x + fragTexCoords.y) * 10.0 + time * 0.7);
    plasma += sin(sqrt(fragTexCoords.x * fragTexCoords.x + fragTexCoords.y * fragTexCoords.y) * 10.0 + time * 1.5);
    
    plasma = plasma / 4.0;
    
    // Color mapping for fire/plasma
    vec3 color1 = vec3(1.0, 0.0, 0.0);  // Red
    vec3 color2 = vec3(1.0, 0.5, 0.0);  // Orange
    vec3 color3 = vec3(1.0, 1.0, 0.0);  // Yellow
    vec3 color4 = vec3(1.0, 1.0, 1.0);  // White
    
    vec3 plasmaColor;
    float t = (plasma + 1.0) * 0.5; // Normalize to 0-1
    
    if (t < 0.33) {
        plasmaColor = mix(color1, color2, t * 3.0);
    } else if (t < 0.66) {
        plasmaColor = mix(color2, color3, (t - 0.33) * 3.0);
    } else {
        plasmaColor = mix(color3, color4, (t - 0.66) * 3.0);
    }
    
    vec4 texColor = texture(tex0, fragTexCoords);
    
    // Blend texture with plasma
    vec3 finalColor = mix(texColor.rgb, plasmaColor, 0.6) * baseIntensity;
    
    fragColor = vec4(finalColor, 1.0);
}

'''

# NEW FRAGMENT SHADER 3: Matrix Digital Rain Effect
matrix_shader = '''
#version 330 core

in vec2 fragTexCoords;
in vec3 fragNormal;
in vec4 fragPosition;

out vec4 fragColor;

uniform sampler2D tex0;
uniform float time;
uniform vec3 pointLight;
uniform float ambientLight;

// Pseudo-random function
float random(vec2 st) {
    return fract(sin(dot(st.xy, vec2(12.9898, 78.233))) * 43758.5453123);
}

void main()
{
    vec3 lightDir = normalize(pointLight - fragPosition.xyz);
    float intensity = max(0.0, dot(fragNormal, lightDir)) + ambientLight;
    
    // Create matrix digital rain effect
    vec2 gridUV = fragTexCoords * 20.0; // Create grid
    vec2 gridID = floor(gridUV);
    
    // Animate falling characters
    float speed = 2.0;
    float offset = random(gridID) * 10.0;
    float rain = fract(time * speed + offset);
    
    // Character brightness based on position in rain
    float charBrightness = 0.0;
    float yPos = fract(gridUV.y);
    
    // Brightest at the leading edge
    if (abs(yPos - rain) < 0.1) {
        charBrightness = 1.0;
    } 
    // Fading trail
    else if (yPos < rain && yPos > rain - 0.5) {
        charBrightness = 1.0 - (rain - yPos) * 2.0;
    }
    
    // Matrix green color
    vec3 matrixColor = vec3(0.0, 1.0, 0.3);
    
    // Add some color variation
    float colorVar = random(gridID + vec2(time * 0.1, 0.0));
    matrixColor = mix(matrixColor, vec3(0.0, 1.0, 0.7), colorVar);
    
    vec4 texColor = texture(tex0, fragTexCoords);
    
    // Combine texture with matrix effect
    vec3 finalColor = texColor.rgb * intensity * 0.3;
    finalColor += matrixColor * charBrightness;
    
    // Add scanline effect
    float scanline = sin(fragTexCoords.y * 100.0 + time * 2.0) * 0.05 + 0.95;
    finalColor *= scanline;
    
    fragColor = vec4(finalColor, 1.0);
}

'''
