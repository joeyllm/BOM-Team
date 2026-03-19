const gl = document.getElementById('index-background').getContext('webgl2');
gl.canvas.width = innerWidth;
gl.canvas.height = innerHeight;
gl.viewport(0, 0, gl.canvas.width, gl.canvas.height);

// perlin noise settings
const freq = 64;
const thresh = 0.6;
const speed = 3;

noise.seed(8715);

// render function
const vs = `#version 300 es
in vec2 p; in float size; uniform float t; uniform float w; uniform float h; out vec3 c;
void main() {
    vec2 pos = p*2.0/vec2(w,h)-1.0;
    gl_Position = vec4(pos,0,1);
    gl_PointSize = size;
}`;

const fs = `#version 300 es
precision mediump float; in vec3 c; out vec4 f;
void main() { 
    vec2 coord = gl_PointCoord-0.5;
    f = vec4(0.15,0.25,0.45,1);
}`;

// Compile shaders
const p = gl.createProgram();
[vs,fs].forEach((src,i)=>{
    const s = gl.createShader(i?gl.FRAGMENT_SHADER:gl.VERTEX_SHADER);
    gl.shaderSource(s,src); gl.compileShader(s); gl.attachShader(p,s);
});
gl.linkProgram(p); gl.useProgram(p);

// Generate point data (fixed spacing)
const size = 3.0; // change size here
const spacing = 8; // change spacing here
let d = [], cols = 0, rows = 0;

function generatePoints() {
    var length = size + spacing;
    cols = Math.ceil(innerWidth / length) + 1;
    rows = Math.ceil(innerHeight / length) + 1;
    d = [];
    var thisSize = size;
    for(let y=0;y<rows;y++) for(let x=0;x<cols;x++) {
        d.push(x*length,y*length,thisSize,x,y);
    }
}

generatePoints();

// Setup buffer
const b = gl.createBuffer();
gl.bindBuffer(gl.ARRAY_BUFFER,b);
gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(d),gl.STATIC_DRAW);
const a = gl.getAttribLocation(p,'p');
gl.enableVertexAttribArray(a);
gl.vertexAttribPointer(a,2,gl.FLOAT,false,20,0);

const sizeLoc = gl.getAttribLocation(p, 'size');
gl.enableVertexAttribArray(sizeLoc);
gl.vertexAttribPointer(sizeLoc, 1, gl.FLOAT, false, 20, 8);

function updateBuffer() {
    gl.bindBuffer(gl.ARRAY_BUFFER,b);
    gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(d),gl.STATIC_DRAW);
}

// Sigmoid function
function sigmoid(x) {
    return 1 / (1 + Math.exp(-x));
}

// Scalar potential
function scalarPotential(x, y, t) {
    let p1 = noise.perlin3(x, y, t);
    let p2 = noise.perlin3(x * 1.7 + 5.123, y * 1.7 + 8.456, t * 0.3);
    return (p1 + p2) * 0.5;
}

// curlNoise
function curlNoise(x, y, time, eps = 0.0001) {

    let x1 = scalarPotential(x - eps, y, time);
    let x2 = scalarPotential(x + eps, y, time);
    let dy = (x2 - x1) / (2 * eps);

    let y1 = scalarPotential(x, y - eps, time);
    let y2 = scalarPotential(x, y + eps, time);
    let dx = (y2 - y1) / (2 * eps);

    return Math.sqrt(dy * dy + dx * dx) / (2 * Math.sqrt(2));
}

// Render loop
function render(t) {
    t*=0.0001;
    gl.clearColor(0,0,0,1);
    gl.clear(gl.COLOR_BUFFER_BIT);
    gl.uniform1f(gl.getUniformLocation(p,'t'),t);
    gl.uniform1f(gl.getUniformLocation(p,'w'),innerWidth);
    gl.uniform1f(gl.getUniformLocation(p,'h'),innerHeight);
    
    for(let i=0;i<cols*rows;i++) {
        let gridX = d[i*5+3];
        let gridY = d[i*5+4];
        let n = scalarPotential(gridX/freq, gridY/freq, t * speed);
        let n2 = curlNoise(gridX/freq, gridY/freq, t * 0.7);
        let scaledN = (n + 0.2 * n2) * 4;
        let prob = sigmoid(scaledN);
        let value = 0;
        if (n2 > thresh) {
            value = size * prob;
        } else {
            value = size * prob * 0.5;
        };
        d[i*5+2] = prob * size; 
    }
    updateBuffer();
    
    gl.drawArrays(gl.POINTS,0,cols*rows);
    requestAnimationFrame(render);
}
requestAnimationFrame(render);

// Window resize
addEventListener('resize',()=>{
    gl.canvas.width=innerWidth;
    gl.canvas.height=innerHeight;
    gl.viewport(0,0,innerWidth,innerHeight);
    generatePoints();
    updateBuffer();
});