/**
 * Wind Nowcasting - WebGL2 Animated Background
 * ============================================================================
 * Creates an animated particle field using WebGL2 and curl noise for
 * a flowing, wind-like visual effect.
 */

// Configuration
const CONFIG = {
    noise: {
        frequency: 32,
        thresholdBottom: 0.3,
        thresholdTop: 1,
        speed: 2
    },
    particle: {
        size: 4.0,
        spacing: 16
    },
    fbm: {
        octaves: 10,
        amplitudeDecay: 0.15,
        frequencyGrowth: 15
    }
};

// DOM Elements
const canvas = document.getElementById('index-background');
if (!canvas) {
    console.warn('Background canvas not found');
}

// WebGL2 Context
const gl = canvas.getContext('webgl2');
if (!gl) {
    console.warn('WebGL2 not supported, skipping background animation');
    canvas.style.display = 'none';
}

// Initialize noise
if (typeof noise === 'undefined') {
    console.warn('Perlin noise library not loaded');
}
noise.seed(Math.random());

// Shader Sources
const SHADERS = {
    vertex: `#version 300 es
        in vec2 p;
        in float brightness;
        in float colorType;
        uniform float t;
        uniform float w;
        uniform float h;
        out float v_brightness;
        out float v_colorType;
        void main() {
            vec2 pos = p * 2.0 / vec2(w, h) - 1.0;
            gl_Position = vec4(pos, 0, 1);
            gl_PointSize = ${CONFIG.particle.size.toFixed(1)};
            v_brightness = brightness;
            v_colorType = colorType;
        }`,
    
    fragment: `#version 300 es
        precision mediump float;
        in float v_brightness;
        in float v_colorType;
        out vec4 f;
        void main() { 
            vec3 blue = vec3(0.15, 0.25, 0.45);
            vec3 gray = vec3(0.1, 0.2, 0.3);
            vec3 lightBlue = vec3(0.2, 0.4, 0.8);
            vec3 color;
            if (v_colorType < 0.5) {
                color = blue;
            } else if (v_colorType < 1.5) {
                color = gray;
            } else {
                color = lightBlue;
            }
            f = vec4(color * v_brightness, 1);
        }`
};

// Compile shaders and create program
function createShaderProgram(gl, vertexSource, fragmentSource) {
    const program = gl.createProgram();
    
    [vertexSource, fragmentSource].forEach((source, index) => {
        const type = index === 0 ? gl.VERTEX_SHADER : gl.FRAGMENT_SHADER;
        const shader = gl.createShader(type);
        gl.shaderSource(shader, source);
        gl.compileShader(shader);
        
        if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
            console.error('Shader compilation error:', gl.getShaderInfoLog(shader));
            return null;
        }
        
        gl.attachShader(program, shader);
    });
    
    gl.linkProgram(program);
    
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
        console.error('Program linking error:', gl.getProgramInfoLog(program));
        return null;
    }
    
    return program;
}

// Mathematical functions
const MathUtils = {
    sigmoid: (x) => 1 / (1 + Math.exp(-x)),
    
    scalarPotential: (x, y, t) => {
        const p1 = noise.perlin3(x, y, t);
        const p2 = noise.perlin3(x * 1.7 + 5.123, y * 1.7 + 8.456, t * 0.3);
        return (p1 + p2) * 0.5;
    },
    
    curlNoise: (x, y, time, eps = 0.0001) => {
        const x1 = MathUtils.scalarPotential(x - eps, y, time);
        const x2 = MathUtils.scalarPotential(x + eps, y, time);
        const dy = (x2 - x1) / (2 * eps);
        
        const y1 = MathUtils.scalarPotential(x, y - eps, time);
        const y2 = MathUtils.scalarPotential(x, y + eps, time);
        const dx = (y2 - y1) / (2 * eps);
        
        return Math.sqrt(dy * dy + dx * dx) / (2 * Math.SQRT2);
    },
    
    fbmNoise: (x, y, t) => {
        let n = 0;
        let amp = 1;
        let freq = 1;
        let weight = 0;
        const { octaves, amplitudeDecay, frequencyGrowth } = CONFIG.fbm;
        
        for (let i = 0; i < octaves; i++) {
            n += amp * noise.perlin3(x * freq, y * freq, t * freq);
            weight += amp;
            amp *= amplitudeDecay;
            freq *= frequencyGrowth;
        }
        
        return n / weight;
    }
};

// Initialize WebGL program
const program = createShaderProgram(gl, SHADERS.vertex, SHADERS.fragment);
if (!program) {
    throw new Error('Failed to create shader program');
}
gl.useProgram(program);

// Particle data management
class ParticleSystem {
    constructor() {
        this.data = [];
        this.cols = 0;
        this.rows = 0;
        this.buffer = gl.createBuffer();
        this.generatePoints();
        this.setupAttributes();
    }
    
    generatePoints() {
        const { size, spacing } = CONFIG.particle;
        const length = size + spacing;
        
        this.cols = Math.ceil(innerWidth / length) + 1;
        this.rows = Math.ceil(innerHeight / length) + 1;
        this.data = [];
        
        for (let y = 0; y < this.rows; y++) {
            for (let x = 0; x < this.cols; x++) {
                const rand = Math.random();
                let colorType;
                
                if (rand < 0.3) {
                    colorType = 0.0; // 30% blue
                } else if (rand < 0.98) {
                    colorType = 1.0; // 68% gray
                } else {
                    colorType = 2.0; // 2% light blue
                }
                
                // [x, y, brightness, gridX, gridY, colorType]
                this.data.push(x * length, y * length, 1.0, x, y, colorType);
            }
        }
    }
    
    setupAttributes() {
        const stride = 24; // 6 floats * 4 bytes
        
        gl.bindBuffer(gl.ARRAY_BUFFER, this.buffer);
        gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(this.data), gl.DYNAMIC_DRAW);
        
        // Position attribute
        const positionLoc = gl.getAttribLocation(program, 'p');
        gl.enableVertexAttribArray(positionLoc);
        gl.vertexAttribPointer(positionLoc, 2, gl.FLOAT, false, stride, 0);
        
        // Brightness attribute
        const brightnessLoc = gl.getAttribLocation(program, 'brightness');
        gl.enableVertexAttribArray(brightnessLoc);
        gl.vertexAttribPointer(brightnessLoc, 1, gl.FLOAT, false, stride, 8);
        
        // Color type attribute
        const colorTypeLoc = gl.getAttribLocation(program, 'colorType');
        gl.enableVertexAttribArray(colorTypeLoc);
        gl.vertexAttribPointer(colorTypeLoc, 1, gl.FLOAT, false, stride, 20);
    }
    
    updateBuffer() {
        gl.bindBuffer(gl.ARRAY_BUFFER, this.buffer);
        gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(this.data), gl.DYNAMIC_DRAW);
    }
    
    update(t) {
        const { frequency, speed } = CONFIG.noise;
        const time = t * 0.0001;
        
        for (let i = 0; i < this.cols * this.rows; i++) {
            const baseIndex = i * 6;
            const gridX = this.data[baseIndex + 3];
            const gridY = this.data[baseIndex + 4];
            
            const n = MathUtils.fbmNoise(gridX / frequency, gridY / frequency, time * speed);
            const breakPoint = MathUtils.fbmNoise(gridX, gridY, time);
            
            let brightness = 0;
            if (Math.abs(n - breakPoint) > 0.2) {
                brightness = MathUtils.sigmoid(n * 5);
            }
            
            this.data[baseIndex + 2] = brightness;
        }
        
        this.updateBuffer();
    }
    
    draw() {
        gl.drawArrays(gl.POINTS, 0, this.cols * this.rows);
    }
    
    handleResize() {
        this.generatePoints();
        this.updateBuffer();
    }
}

// Resize handling
function resizeCanvas() {
    const dpr = Math.min(window.devicePixelRatio, 2);
    canvas.width = innerWidth * dpr;
    canvas.height = innerHeight * dpr;
    canvas.style.width = `${innerWidth}px`;
    canvas.style.height = `${innerHeight}px`;
    gl.viewport(0, 0, canvas.width, canvas.height);
}

// Animation loop
function startAnimation() {
    const particleSystem = new ParticleSystem();
    
    resizeCanvas();
    
    const uniforms = {
        t: gl.getUniformLocation(program, 't'),
        w: gl.getUniformLocation(program, 'w'),
        h: gl.getUniformLocation(program, 'h')
    };
    
    function render(timestamp) {
        gl.clearColor(0, 0, 0, 1);
        gl.clear(gl.COLOR_BUFFER_BIT);
        
        gl.uniform1f(uniforms.t, timestamp * 0.0001);
        gl.uniform1f(uniforms.w, canvas.width);
        gl.uniform1f(uniforms.h, canvas.height);
        
        particleSystem.update(timestamp);
        particleSystem.draw();
        
        requestAnimationFrame(render);
    }
    
    requestAnimationFrame(render);
    
    // Handle resize
    let resizeTimeout;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            resizeCanvas();
            particleSystem.handleResize();
        }, 100);
    }, { passive: true });
}

// Start animation when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', startAnimation);
} else {
    startAnimation();
}
