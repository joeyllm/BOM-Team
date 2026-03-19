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
in vec2 p; uniform float t; out vec3 c;
void main() {
    vec2 pos = p*2.0-1.0;
    gl_Position = vec4(pos,0,1);
    gl_PointSize = 3.0;
    c = vec3(0.5+0.5*sin(t+p.x),0.5+0.5*sin(t+1.0+p.y),0.5+0.5*sin(t+2.0+p.x+p.y));
}`;

const fs = `#version 300 es
precision mediump float; in vec3 c; out vec4 f;
void main() { 
    vec2 coord = gl_PointCoord-0.5;
    if(length(coord)>0.5) discard;
    f = vec4(c,1.0-smoothstep(0.3,0.5,length(coord)));
}`;

// 编译着色器
const p = gl.createProgram();
[vs,fs].forEach((src,i)=>{
    const s = gl.createShader(i?gl.FRAGMENT_SHADER:gl.VERTEX_SHADER);
    gl.shaderSource(s,src); gl.compileShader(s); gl.attachShader(p,s);
});
gl.linkProgram(p); gl.useProgram(p);

// 生成点数据
const d = [], s = 30;
for(let y=0;y<s;y++) for(let x=0;x<s;x++) d.push(x/(s-1),y/(s-1));

// 设置缓冲区
const b = gl.createBuffer();
gl.bindBuffer(gl.ARRAY_BUFFER,b);
gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(d),gl.STATIC_DRAW);
const a = gl.getAttribLocation(p,'p');
gl.enableVertexAttribArray(a);
gl.vertexAttribPointer(a,2,gl.FLOAT,false,0,0);

// 渲染循环
function render(t) {
    t*=0.001;
    gl.clearColor(0,0,0,1);
    gl.clear(gl.COLOR_BUFFER_BIT);
    gl.uniform1f(gl.getUniformLocation(p,'t'),t);
    gl.drawArrays(gl.POINTS,0,s*s);
    requestAnimationFrame(render);
}
requestAnimationFrame(render);

// 窗口大小调整
addEventListener('resize',()=>{
    gl.canvas.width=innerWidth;
    gl.canvas.height=innerHeight;
    gl.viewport(0,0,innerWidth,innerHeight);
});