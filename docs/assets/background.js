const gl = document.getElementById('index-background').getContext('webgl2');
gl.canvas.width = innerWidth;
gl.canvas.height = innerHeight;
gl.viewport(0, 0, gl.canvas.width, gl.canvas.height);

// perlin noise settings
const freq = 200;
const thresh = 0;

noise.seed(8715);

// render function
const vs = `#version 300 es
in vec2 p; uniform float t; uniform float w; uniform float h; out vec3 c;
void main() {
    vec2 pos = p*2.0/vec2(w,h)-1.0;
    gl_Position = vec4(pos,0,1);
    gl_PointSize = 5.0;
}`;

const fs = `#version 300 es
precision mediump float; in vec3 c; out vec4 f;
void main() { 
    vec2 coord = gl_PointCoord-0.5;
    f = vec4(1,1,1,1);
}`;

// 编译着色器
const p = gl.createProgram();
[vs,fs].forEach((src,i)=>{
    const s = gl.createShader(i?gl.FRAGMENT_SHADER:gl.VERTEX_SHADER);
    gl.shaderSource(s,src); gl.compileShader(s); gl.attachShader(p,s);
});
gl.linkProgram(p); gl.useProgram(p);

// 生成点数据（固定间距）
const spacing = 10;
let d = [], cols = 0, rows = 0;

function generatePoints() {
    cols = Math.ceil(innerWidth / spacing) + 1;
    rows = Math.ceil(innerHeight / spacing) + 1;
    d = [];
    for(let y=0;y<rows;y++) for(let x=0;x<cols;x++) d.push(x*spacing,y*spacing);
}

generatePoints();

// 设置缓冲区
const b = gl.createBuffer();
gl.bindBuffer(gl.ARRAY_BUFFER,b);
gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(d),gl.STATIC_DRAW);
const a = gl.getAttribLocation(p,'p');
gl.enableVertexAttribArray(a);
gl.vertexAttribPointer(a,2,gl.FLOAT,false,0,0);

function updateBuffer() {
    gl.bindBuffer(gl.ARRAY_BUFFER,b);
    gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(d),gl.STATIC_DRAW);
}

// 渲染循环
function render(t) {
    t*=0.001;
    gl.clearColor(0,0,0,1);
    gl.clear(gl.COLOR_BUFFER_BIT);
    gl.uniform1f(gl.getUniformLocation(p,'t'),t);
    gl.uniform1f(gl.getUniformLocation(p,'w'),innerWidth);
    gl.uniform1f(gl.getUniformLocation(p,'h'),innerHeight);
    gl.drawArrays(gl.POINTS,0,cols*rows);
    requestAnimationFrame(render);
}
requestAnimationFrame(render);

// 窗口大小调整
addEventListener('resize',()=>{
    gl.canvas.width=innerWidth;
    gl.canvas.height=innerHeight;
    gl.viewport(0,0,innerWidth,innerHeight);
    generatePoints();
    updateBuffer();
});