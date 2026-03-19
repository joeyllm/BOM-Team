const C = document.getElementById('index-background');

// create a new Two.js instance
const two = new Two({
    width: C.clientWidth,
    height: C.clientHeight
}).appendTo(C);

// calculate coordinates
const ITEM_SIZE = 10;
const THRESHOLD = 0;
const FREQ = 200;
noise.seed(8715)

// function: createParticles
function createParticles() {
    // Clear existing particles
    two.clear();
    
    // Get current size
    const width = C.clientWidth;
    const height = C.clientHeight;
    
    // Update Two.js instance size
    two.width = width;
    two.height = height;
    
    // create a circle
    for (let i = 0; i + ITEM_SIZE / 2 < width; i += ITEM_SIZE) {
        for (let j = 0; j + ITEM_SIZE / 2 < height; j += ITEM_SIZE) {
            var n = noise.perlin3(i/FREQ, j/FREQ, 0);
            if (n > THRESHOLD) {
                const circle = two.makeCircle(i + ITEM_SIZE / 2, j + ITEM_SIZE / 2, 2);
                circle.fill = 'cyan';
                circle.stroke = 'black';
                circle.linewidth = 0;
            }
        }
    }
    
    two.update();
}

// Initial creation of particles
createParticles();

// Add window resize event listener
window.addEventListener('resize', function() {
    createParticles();
});

two.play();