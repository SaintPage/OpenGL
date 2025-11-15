vertex_shader = '''
#version 330 core

layout (location = 0) in vec3 inPosition;
layout (location = 1) in vec2 inTexCoords;
layout (location = 2) in vec3 inNormals;

out vec2 fragTexCoords;
out vec3 fragNormal;
out vec4 fragPosition;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;

void main()
{
    gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(inPosition, 1.0);
    fragPosition = modelMatrix * vec4(inPosition, 1.0);
    fragNormal = normalize(vec3(modelMatrix * vec4(inNormals, 0.0)));
    fragTexCoords = inTexCoords;
}

'''

# NEW VERTEX SHADER 1: Spiral/Twist Effect
spiral_shader = '''
#version 330 core

layout (location = 0) in vec3 inPosition;
layout (location = 1) in vec2 inTexCoords;
layout (location = 2) in vec3 inNormals;

out vec2 fragTexCoords;
out vec3 fragNormal;
out vec4 fragPosition;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;
uniform float time;
uniform float value;

void main()
{
    // Create a spiral/twist effect based on height
    float height = inPosition.y;
    float angle = height * 3.14159 * value + time;
    
    float cosA = cos(angle);
    float sinA = sin(angle);
    
    // Rotation matrix around Y axis
    mat3 rotation = mat3(
        cosA, 0.0, sinA,
        0.0, 1.0, 0.0,
        -sinA, 0.0, cosA
    );
    
    vec3 twistedPos = rotation * inPosition;
    
    fragPosition = modelMatrix * vec4(twistedPos, 1.0);
    gl_Position = projectionMatrix * viewMatrix * fragPosition;
    fragNormal = normalize(vec3(modelMatrix * vec4(rotation * inNormals, 0.0)));
    fragTexCoords = inTexCoords;
}

'''

# NEW VERTEX SHADER 2: Pulse/Heartbeat Effect
pulse_shader = '''
#version 330 core

layout (location = 0) in vec3 inPosition;
layout (location = 1) in vec2 inTexCoords;
layout (location = 2) in vec3 inNormals;

out vec2 fragTexCoords;
out vec3 fragNormal;
out vec4 fragPosition;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;
uniform float time;
uniform float value;

void main()
{
    // Pulsating heartbeat effect from center
    vec3 center = vec3(0.0, 0.0, 0.0);
    float dist = length(inPosition - center);
    
    // Create pulse waves emanating from center
    float pulse = sin(dist * 10.0 - time * 5.0) * 0.5 + 0.5;
    float scale = 1.0 + pulse * value * 0.3;
    
    vec3 pulsedPos = inPosition * scale;
    
    fragPosition = modelMatrix * vec4(pulsedPos, 1.0);
    gl_Position = projectionMatrix * viewMatrix * fragPosition;
    fragNormal = normalize(vec3(modelMatrix * vec4(inNormals, 0.0)));
    fragTexCoords = inTexCoords;
}

'''

# NEW VERTEX SHADER 3: Glitch/Displacement Effect
glitch_shader = '''
#version 330 core

layout (location = 0) in vec3 inPosition;
layout (location = 1) in vec2 inTexCoords;
layout (location = 2) in vec3 inNormals;

out vec2 fragTexCoords;
out vec3 fragNormal;
out vec4 fragPosition;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;
uniform float time;
uniform float value;

void main()
{
    // Glitch effect with random displacement
    float glitchAmount = value * 0.3;
    
    // Use pseudo-random function based on position and time
    float random = fract(sin(dot(inPosition.xy + time * 0.1, vec2(12.9898, 78.233))) * 43758.5453);
    
    // Create glitch blocks
    float blockY = floor(inPosition.y * 5.0) / 5.0;
    float blockRandom = fract(sin(blockY * 127.1 + time) * 43758.5453);
    
    vec3 glitchOffset = vec3(0.0);
    
    // Random horizontal displacement for certain blocks
    if (blockRandom > 0.7) {
        glitchOffset.x = (blockRandom - 0.7) * glitchAmount * sin(time * 10.0);
    }
    
    // Add some vertical jitter
    glitchOffset.y = random * glitchAmount * 0.3 * sin(time * 15.0);
    
    vec3 glitchedPos = inPosition + glitchOffset;
    
    fragPosition = modelMatrix * vec4(glitchedPos, 1.0);
    gl_Position = projectionMatrix * viewMatrix * fragPosition;
    fragNormal = normalize(vec3(modelMatrix * vec4(inNormals, 0.0)));
    fragTexCoords = inTexCoords;
}

'''
