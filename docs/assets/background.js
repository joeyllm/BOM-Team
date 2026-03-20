const gl = document.getElementById('index-background').getContext('webgl2');
gl.canvas.width = innerWidth;
gl.canvas.height = innerHeight;
gl.viewport(0, 0, gl.canvas.width, gl.canvas.height);

// perlin noise settings
const freq = 20;
const threshB = 0.3;
const threshT = 1;
const speed = 3;

const size = 4.0; // change size here
const spacing = 12; // change spacing here

noise.seed(Math.random());

// render function
const vs = `#version 300 es
in vec2 p; in float brightness; in float colorType; uniform float t; uniform float w; uniform float h; out float v_brightness; out float v_colorType;
void main() {
    vec2 pos = p*2.0/vec2(w,h)-1.0;
    gl_Position = vec4(pos,0,1);
    gl_PointSize = ${size.toFixed(1)};
    v_brightness = brightness;
    v_colorType = colorType;
}`;

const fs = `#version 300 es
precision mediump float; in float v_brightness; in float v_colorType; out vec4 f;
void main() { 
    vec2 coord = gl_PointCoord-0.5;
    vec3 blue = vec3(0.15, 0.25, 0.45);
    vec3 gray = vec3(0.1, 0.2, 0.3);
    vec3 color = mix(blue, gray, v_colorType);
    f = vec4(color * v_brightness, 1);
}`;

// Compile shaders
const p = gl.createProgram();
[vs,fs].forEach((src,i)=>{
    const s = gl.createShader(i?gl.FRAGMENT_SHADER:gl.VERTEX_SHADER);
    gl.shaderSource(s,src); gl.compileShader(s); gl.attachShader(p,s);
});
gl.linkProgram(p); gl.useProgram(p);

// Generate point data (fixed spacing)
let d = [], cols = 0, rows = 0;

function generatePoints() {
    var length = size + spacing;
    cols = Math.ceil(innerWidth / length) + 1;
    rows = Math.ceil(innerHeight / length) + 1;
    d = [];
    for(let y=0;y<rows;y++) for(let x=0;x<cols;x++) {
        let colorType = Math.random() < 0.6 ? 1.0 : 0.0; // 60% probability of gray
        d.push(x*length,y*length,1.0,x,y,colorType);
    }
}

generatePoints();

// Setup buffer
const b = gl.createBuffer();
gl.bindBuffer(gl.ARRAY_BUFFER,b);
gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(d),gl.STATIC_DRAW);
const a = gl.getAttribLocation(p,'p');
gl.enableVertexAttribArray(a);
gl.vertexAttribPointer(a,2,gl.FLOAT,false,24,0);

const brightnessLoc = gl.getAttribLocation(p, 'brightness');
gl.enableVertexAttribArray(brightnessLoc);
gl.vertexAttribPointer(brightnessLoc, 1, gl.FLOAT, false, 24, 8);

const colorTypeLoc = gl.getAttribLocation(p, 'colorType');
gl.enableVertexAttribArray(colorTypeLoc);
gl.vertexAttribPointer(colorTypeLoc, 1, gl.FLOAT, false, 24, 20);

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

// FBM -1 to 1
function fbmNoise(x, y, t) {
    let n = 0;
    let amp = 1;
    let freq = 1;
    let num = 4;
    for(let i=0;i<num;i++) {
        n += amp * noise.perlin3(x * freq, y * freq, t * freq);
        n += amp * 0.3 * curlNoise(x * freq, y * freq, t * freq);
        amp *= 0.15;
        freq *= 15;
    }
    return n / num;
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
        let gridX = d[i*6+3];
        let gridY = d[i*6+4];
        let n = fbmNoise(gridX/freq, gridY/freq, t * speed);
        let prob = sigmoid(n * 10);
        let brightness = 0;
        let breakPoint = fbmNoise(gridX, gridY, t);
        if (Math.abs(n - breakPoint) > 0.14) {
            brightness = 1;
        } else {
            brightness = 0;
        }
        d[i*6+2] = brightness;
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