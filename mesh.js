function arrangeBuffers(buffers) {
  // buffers is an object of name to size

  let length = 0;
  const offsetsizes = {};
  for (const [name, size] of Object.entries(buffers)) {
    offsetsizes[name] = [length, size]; // size is a number of components
    length += size;
  }

  const stride = length;

  return {offsetsizes, stride};
}

function initBuffers(gl, data) {
  const {offsetsizes, stride} = arrangeBuffers({aVertexPosition: 3, aVertexNormal: 3});
  
  const buffer = gl.createBuffer();

  setBuffers(gl, {buffer, offsetsizes, stride}, data);
  
  return {buffer, offsetsizes, stride};
}

function setBuffers(gl, bufferdata, buffers) {
  // bufferdata is returned from initBuffers
  const {buffer, offsetsizes, stride} = bufferdata;

  //Object.values(buffers).map(data => data.length).every((l, _, ls) => l == l[0]); // all of the arrays are the same length
  //Object.values(buffers).every(data => data.map(point => point.length).every((l, _, ls) => l == l[0])); // each array has consistent tuple sizes

  const data = Object.values(buffers)[0].map(_ => Array(stride));

  for (const [name, points] of Object.entries(buffers)) {
    //points[0].length = offsetsizes[name][1] // the points are of the expected sizes
    points.map((point, i) => point.map((e, j) => data[i][offsetsizes[name][0] + j] = e)); // add each point to the corresponding data element
  }

  gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([].concat(...data)), gl.STATIC_DRAW);

  return {buffer, offsetsizes, stride};
}

function setMatrix(gl, shaderInfo, viewMatrix, scale) {
  // Set the shader uniforms
  const scaledViewMatrix = mat4.create();
  
  mat4.scale(
    scaledViewMatrix,
    viewMatrix,
    [scale, scale, scale],
  );
  
  gl.uniformMatrix4fv(
    shaderInfo.uniforms.uViewMatrix,
    false,
    scaledViewMatrix,
  );

  const normalMatrix = mat4.create();
  mat4.invert(normalMatrix, viewMatrix);
  mat4.transpose(normalMatrix, normalMatrix);
  
  gl.uniformMatrix4fv(
    shaderInfo.uniforms.uNormalMatrix,
    false,
    normalMatrix,
  );
}

function drawShape(gl, shape) {
  gl.drawArrays(gl.TRIANGLES, shape.offset, shape.size);
  //printGlError(gl);
}

function printGlError(gl) {
  const e = gl.getError();
  //if (e == gl.NO_ERROR) console.log("gl.NO_ERROR	No error has been recorded. The value of this constant is 0.");
  if (e == gl.INVALID_ENUM) console.log("gl.INVALID_ENUM	An unacceptable value has been specified for an enumerated argument. The command is ignored and the error flag is set.");
  if (e == gl.INVALID_VALUE) console.log("gl.INVALID_VALUE	A numeric argument is out of range. The command is ignored and the error flag is set.");
  if (e == gl.INVALID_OPERATION) console.log("gl.INVALID_OPERATION	The specified command is not allowed for the current state. The command is ignored and the error flag is set.");
  if (e == gl.INVALID_FRAMEBUFFER_OPERATION) console.log("gl.INVALID_FRAMEBUFFER_OPERATION	The currently bound framebuffer is not framebuffer complete when trying to render to or to read from it.");
  if (e == gl.OUT_OF_MEMORY) console.log("gl.OUT_OF_MEMORY	Not enough memory is left to execute the command.");
  if (e == gl.CONTEXT_LOST_WEBGL) console.log("gl.CONTEXT_LOST_WEBGL	If the WebGL context is lost, this error is returned on the first call to getError. Afterwards and until the context has been restored, it returns gl.NO_ERROR.");
}

function setAttributeLocations(gl, buffers, shaderInfo) {
  const {buffer, offsetsizes, stride} = buffers;
  gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
  
  const type = gl.FLOAT; // the data in the buffer is 32bit floats
  const normalize = false; // don't normalize
  
  for (const [name, [offset, size]] of Object.entries(offsetsizes)) {
    gl.vertexAttribPointer(
      shaderInfo.attributes[name],
      size,
      type,
      normalize,
      stride * 4,
      offset * 4, // 4 bytes per float
    );
    gl.enableVertexAttribArray(shaderInfo.attributes[name]);
  }
}

function getShaderVars(gl, shader, vars) {
  // vars is an object with two keys - attributes and uniforms
  // which are lists of names
  const {attributes, uniforms} = vars;
  
  return {
    shader,
    attributes: Object.fromEntries(attributes.map(name => [name, gl.getAttribLocation(shader, name)])),
    uniforms: Object.fromEntries(uniforms.map(name => [name, gl.getUniformLocation(shader, name)])),
  }
}

const keysPressed = {};

addEventListener("keydown", e => keysPressed[event.code] = true);
addEventListener("keyup", e => keysPressed[event.code] = false);

function keyPressed(key) {
  return keysPressed[key] === true;
}

function compileShader(gl, vertSource, fragSource) {
  const vertexShader = loadShader(gl, gl.VERTEX_SHADER, vertSource);
  const fragmentShader = loadShader(gl, gl.FRAGMENT_SHADER, fragSource);
  const shaderProgram = gl.createProgram();

  gl.attachShader(shaderProgram, vertexShader);
  gl.attachShader(shaderProgram, fragmentShader);
  gl.linkProgram(shaderProgram);

  if (!gl.getProgramParameter(shaderProgram, gl.LINK_STATUS)) {
    console.log(`Unable to initialize the shader program ): ${gl.getshaderInfoLog(shaderProgram)}`,);
    return null;
  }

  return shaderProgram;
}

function loadShader(gl, type, source) {
  const shader = gl.createShader(type);
  gl.shaderSource(shader, source);
  gl.compileShader(shader);

  if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
    console.log(`An error occurred compiling the shaders ): ${gl.getShaderInfoLog(shader)}`,);
    gl.deleteShader(shader);
    return null;
  }

  return shader;
}

function initScene(gl, shaderInfo, shape, data) {
  gl.clearColor(0.0, 0.0, 0.0, 1.0); // Clear to black, fully opaque
  gl.clearDepth(1.0); // Clear everything
  gl.enable(gl.DEPTH_TEST); // Enable depth testing
  gl.depthFunc(gl.LEQUAL); // Near things obscure far things

  // Create a perspective matrix, a special matrix that is
  // used to simulate the distortion of perspective in a camera.
  // Our field of view is 45 degrees, or pi/4, with a width/height
  // ratio that matches the display size of the canvas
  // and we only want to see objects between 0.1 units
  // and 100 units away from the camera.

  const fieldOfView = Math.PI / 4; // in radians
  const aspect = gl.canvas.clientWidth / gl.canvas.clientHeight;
  const zNear = 0.1;
  const zFar = 100.0;
  const projectionMatrix = mat4.create();

  mat4.perspective(projectionMatrix, fieldOfView, aspect, zNear, zFar);

  data.viewMatrix = mat4.create();
  data.scale = 1;

  const buffers = initBuffers(gl, shape.attributes);

  setAttributeLocations(gl, buffers, shaderInfo);

  gl.useProgram(shaderInfo.shader);

  // Set the projection matrix
  gl.uniformMatrix4fv(
    shaderInfo.uniforms.uProjectionMatrix,
    false,
    projectionMatrix,
  );
}

function drawScene(gl, shaderInfo, shape, data) {
  // clear the canvas
  gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
  
  setMatrix(gl, shaderInfo, data.viewMatrix, data.scale);
  drawShape(gl, shape);
}

function toShape(mesh) {
  console.log(mesh);
  let offset = 0;
  let shapes = []
  for (const m of mesh.meshes) {
    const size = [].concat(...m).length;
    shapes.push({offset, size});
    offset += size;
  }
  const idxs = [].concat(...[].concat(...mesh.meshes));
  const size = idxs.length;
  const aVertexPosition_ = idxs.map(i => mesh.vertices[i]);
  const aVertexNormal = idxs.map(i => 'normals' in mesh ? mesh.normals[i] : [0, 0, 0]);
  const maxcoords = aVertexPosition_.reduce((p1, p2) => p1.map((_, i) => Math.max(p1[i], p2[i])));
  const mincoords = aVertexPosition_.reduce((p1, p2) => p1.map((_, i) => Math.min(p1[i], p2[i])));
  const largestdim = Math.max(...maxcoords.map((_, i) => maxcoords[i] - mincoords[i]));
  const center = maxcoords.map((_, i) => (maxcoords[i] + mincoords[i]) / 2);
  const aVertexPosition = aVertexPosition_.map(p => p.map((c, i) => (c - center[i]) / largestdim));
  return {size, offset: 0, shapes, attributes: {aVertexPosition, aVertexNormal}};
}

function main(vertSource, fragSource, mesh, canvas, callback) {
  const gl = canvas.getContext("webgl");
  
  let mouseX, mouseY, hasMouse;
  canvas.addEventListener("mousemove", (e) => {
    const rect = canvas.getBoundingClientRect();
    mouseX = e.offsetX * 2 / rect.width - 1;
    mouseY = 1 - e.offsetY * 2 / rect.height;
    //console.log(e.movementX, e.movementY, e.buttons)
    
    if (e.buttons == 1) {
    const rotMatrix = mat4.create();

    mat4.rotate(
      rotMatrix,
      rotMatrix,
      0.01 * e.movementX,
      [0.0, 1.0, 0.0]
    );

    mat4.rotate(
      rotMatrix,
      rotMatrix,
      0.01 * e.movementY,
      [1.0, 0.0, 0.0]
    );
    
    mat4.mul(
      data.viewMatrix,
      rotMatrix,
      data.viewMatrix,
    );
    } else if (e.buttons == 2) {
      data.scale *= 1 + 0.01 * e.movementY;
    }
  });
  canvas.addEventListener("mouseenter", () => hasMouse = true);
  canvas.addEventListener("mouseleave", () => hasMouse = false);

  addEventListener("keydown", e => {if (hasMouse) {e.preventDefault();}});

  if (gl === null) {
    console.log("no webgl :(");
    return;
  }
  
  const shader = compileShader(gl, vertSource, fragSource);
  
  const shaderInfo = getShaderVars(gl, shader, {
    attributes: ["aVertexPosition", "aVertexNormal"],
    uniforms: ["uViewMatrix", "uProjectionMatrix", "uNormalMatrix"],
  });
  
  const shape = toShape(mesh);
  
  console.log(shape);
  
  const data = {};
  
  initScene(gl, shaderInfo, shape, data);
  
  const shapes = [shape, ...shape.shapes];
  let idx = 0;

  function render() {
    if (keyPressed("KeyJ")) {
      console.log(mouseX, mouseY, hasMouse);
      keysPressed["KeyJ"] = false;
    }
    
    if (keyPressed("Space") && hasMouse) {
      idx++;
      if (idx >= shapes.length) {
        idx = 0;
      }
      keysPressed["Space"] = false;
    }

    drawScene(gl, shaderInfo, shapes[idx], data);

    requestAnimationFrame(render);
  }

  requestAnimationFrame(_ => {render(); callback();});
}

const vertload = fetch("shader.vert").then(res => res.text());

const fragload = fetch("shader.frag").then(res => res.text());

function meshrender(mesh, canvas, callback) {
  Promise.all([vertload, fragload]).then(([vertSource, fragSource]) => main(vertSource, fragSource, mesh, canvas, callback));
}