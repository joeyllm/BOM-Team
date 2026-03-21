/**
 * Wind Nowcasting - WebGL2 Animated Background
 */

const CONFIG = {
    noise: { frequency: 32, thresholdBottom: 0.3, thresholdTop: 1, speed: 2 },
    particle: { size: 4, spacing: 16 },
    fbm: { octaves: 10, amplitudeDecay: 0.15, frequencyGrowth: 15 }
};

const canvas = document.getElementById('index-background');
if (!canvas) console.warn('Background canvas not found');

const gl = canvas?.getContext('webgl2');
if (!gl) {
    console.warn('WebGL2 not supported');
    canvas?.style?.display && (canvas.style.display = 'none');
}

if (typeof noise !== 'undefined') noise.seed(Math.random());

const SHADERS = {
    vertex: `#version 300 es
        in vec2 p; in float brightness; in float colorType;
        uniform float w, h;
        out float v_brightness, v_colorType;
        void main() {
            gl_Position = vec4(p * 2.0 / vec2(w, h) - 1.0, 0, 1);
            gl_PointSize = ${CONFIG.particle.size.toFixed(1)};
            v_brightness = brightness; v_colorType = colorType;
        }`,
    fragment: `#version 300 es
        precision mediump float;
        in float v_brightness, v_colorType; out vec4 f;
        void main() { 
            vec3 c[3] = vec3[](vec3(0,0.48,1), vec3(0.15,0.25,0.4), vec3(0.39,0.4,0.94));
            f = vec4(c[int(v_colorType < 0.5 ? 0.0 : v_colorType < 1.5 ? 1.0 : 2.0)] * v_brightness, 1);
        }`
};

function createShaderProgram(gl, vs, fs) {
    const p = gl.createProgram();
    [vs, fs].forEach((src, i) => {
        const s = gl.createShader(i ? gl.FRAGMENT_SHADER : gl.VERTEX_SHADER);
        gl.shaderSource(s, src); gl.compileShader(s);
        if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) return console.error(gl.getShaderInfoLog(s));
        gl.attachShader(p, s);
    });
    gl.linkProgram(p);
    return gl.getProgramParameter(p, gl.LINK_STATUS) ? p : null;
}

const program = createShaderProgram(gl, SHADERS.vertex, SHADERS.fragment);
if (!program) throw new Error('Failed to create shader');
gl.useProgram(program);

const MathUtils = {
    sigmoid: x => 1 / (1 + Math.exp(-x)),
    scalarPotential: (x, y, t) => (noise.perlin3(x, y, t) + noise.perlin3(x * 1.7 + 5.123, y * 1.7 + 8.456, t * 0.3)) * 0.5,
    curlNoise: (x, y, t, eps = 1e-4) => {
        const dy = (MathUtils.scalarPotential(x + eps, y, t) - MathUtils.scalarPotential(x - eps, y, t)) / (2 * eps);
        const dx = (MathUtils.scalarPotential(x, y + eps, t) - MathUtils.scalarPotential(x, y - eps, t)) / (2 * eps);
        return Math.sqrt(dy * dy + dx * dx) / (2 * Math.SQRT2);
    },
    fbmNoise: (x, y, t) => {
        let n = 0, amp = 1, freq = 1, w = 0;
        for (let i = 0; i < CONFIG.fbm.octaves; i++) {
            n += amp * noise.perlin3(x * freq, y * freq, t * freq);
            w += amp; amp *= CONFIG.fbm.amplitudeDecay; freq *= CONFIG.fbm.frequencyGrowth;
        }
        return n / w;
    }
};

class ParticleSystem {
    constructor() {
        this.data = []; this.cols = 0; this.rows = 0;
        this.buffer = gl.createBuffer();
        this.generatePoints();
        this.setupAttributes();
    }
    
    generatePoints() {
        const len = CONFIG.particle.size + CONFIG.particle.spacing;
        this.cols = Math.ceil(innerWidth / len) + 1;
        this.rows = Math.ceil(innerHeight / len) + 1;
        this.data = [];
        for (let y = 0; y < this.rows; y++) {
            for (let x = 0; x < this.cols; x++) {
                const r = Math.random();
                const colorType = r < 0.3 ? 0.0 : r < 0.98 ? 1.0 : 2.0;
                this.data.push(x * len, y * len, 1.0, x, y, colorType);
            }
        }
    }
    
    setupAttributes() {
        const stride = 24;
        gl.bindBuffer(gl.ARRAY_BUFFER, this.buffer);
        gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(this.data), gl.DYNAMIC_DRAW);
        ['p', 'brightness', 'colorType'].forEach((name, i) => {
            const loc = gl.getAttribLocation(program, name);
            gl.enableVertexAttribArray(loc);
            gl.vertexAttribPointer(loc, i === 0 ? 2 : 1, gl.FLOAT, false, stride, i === 0 ? 0 : i === 1 ? 8 : 20);
        });
    }
    
    update(t) {
        const time = t * 0.0001, { frequency, speed } = CONFIG.noise;
        for (let i = 0; i < this.cols * this.rows; i++) {
            const idx = i * 6, gx = this.data[idx + 3], gy = this.data[idx + 4];
            const n = MathUtils.fbmNoise(gx / frequency, gy / frequency, time * speed);
            const bp = MathUtils.fbmNoise(gx, gy, time);
            this.data[idx + 2] = Math.abs(n - bp) > 0.2 ? MathUtils.sigmoid(n * 5) : 0;
        }
        gl.bindBuffer(gl.ARRAY_BUFFER, this.buffer);
        gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(this.data), gl.DYNAMIC_DRAW);
    }
    
    draw() { gl.drawArrays(gl.POINTS, 0, this.cols * this.rows); }
    handleResize() { this.generatePoints(); }
}

function resizeCanvas() {
    const dpr = Math.min(window.devicePixelRatio, 2);
    canvas.width = innerWidth * dpr; canvas.height = innerHeight * dpr;
    canvas.style.width = `${innerWidth}px`; canvas.style.height = `${innerHeight}px`;
    gl.viewport(0, 0, canvas.width, canvas.height);
}

function startAnimation() {
    const ps = new ParticleSystem();
    resizeCanvas();
    const uniforms = { t: gl.getUniformLocation(program, 't'), w: gl.getUniformLocation(program, 'w'), h: gl.getUniformLocation(program, 'h') };
    
    function render(ts) {
        gl.clearColor(0, 0, 0, 1); gl.clear(gl.COLOR_BUFFER_BIT);
        gl.uniform1f(uniforms.t, ts * 0.0001);
        gl.uniform1f(uniforms.w, canvas.clientWidth);
        gl.uniform1f(uniforms.h, canvas.clientHeight);
        ps.update(ts); ps.draw();
        requestAnimationFrame(render);
    }
    requestAnimationFrame(render);
    
    let timeout;
    window.addEventListener('resize', () => {
        clearTimeout(timeout);
        timeout = setTimeout(() => { resizeCanvas(); ps.handleResize(); }, 100);
    }, { passive: true });
}

if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', startAnimation);
else startAnimation();
