varying highp vec3 vLighting;

void main(void) {
    highp vec3 color = vec3(1.0);
    
    gl_FragColor = vec4(color * vLighting, 1.0);
}