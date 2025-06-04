attribute vec4 aVertexPosition;
attribute vec3 aVertexNormal;

uniform mat4 uNormalMatrix;
uniform mat4 uViewMatrix;
uniform mat4 uProjectionMatrix;

varying highp vec3 vLighting;

void main(void) {
    gl_Position = uProjectionMatrix * (uViewMatrix * aVertexPosition + vec4(0.0, 0.0, -3.0, 0.0));

    // Apply lighting effect

    highp vec3 ambientLight = vec3(0.3, 0.3, 0.3);
    highp vec3 directionalLightColor = vec3(1, 1, 1);
    highp vec3 directionalVector = normalize(vec3(0.85, 0.8, 0.75));

    highp vec3 transformedNormal = (uNormalMatrix * vec4(aVertexNormal, 0.0)).xyz;

    highp float directional = max(dot(transformedNormal, directionalVector), 0.0);
    vLighting = ambientLight + (directionalLightColor * directional);
}