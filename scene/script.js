// Scene setup
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// Create a square platform
const platformSize = 5;
const platformGeometry = new THREE.BoxGeometry(platformSize, platformSize, 1);
const platformMaterial = new THREE.MeshBasicMaterial({ color: 0x202020 });
const platform = new THREE.Mesh(platformGeometry, platformMaterial);
scene.add(platform);
platform.position.z -= 0.5;


// Add lines
function createLine(coordsA, coordsB, color) {
    const points = [];
    points.push(
        coordsA,
        coordsB
    );
    const geometry = new THREE.BufferGeometry().setFromPoints(points);
    const line = new THREE.Line(
        geometry,
        new THREE.LineBasicMaterial({color: color})
    );
    scene.add(line);
}

const lineStep = 0.25;
const maxCoord = platformSize/2;
const colorStep = 32;
console.log("Color step = ", colorStep);
for(let i=0; i<platformSize+lineStep; i+=lineStep) {
    const newColor = colorStep * i;
    // Horizontal:
    const hRedColor = 0x100000;
    const hGreenColor = newColor << 8;
    const hBlueColor = 0xa0 - newColor;
    console.log("Horizontal colors = 0x", hGreenColor.toString(16), ", 0x", hBlueColor.toString(16));
    createLine(new THREE.Vector3(-maxCoord, i-maxCoord, 0), new THREE.Vector3(maxCoord, i-maxCoord, 0), hRedColor+hGreenColor+hBlueColor);

    // Vertical:
    const vRedColor = 0xa00000;
    const vGreenColor = newColor << 8;
    const vBlueColor = 0x100000;
    createLine(new THREE.Vector3(i-maxCoord, -maxCoord, 0), new THREE.Vector3(i-maxCoord, maxCoord, 0), vRedColor+vGreenColor+vBlueColor);
}

// Create cubes
const cubeGeometry = new THREE.BoxGeometry(0.5, 0.5, 0.5);

// God cube
const godCubeMaterial = new THREE.MeshBasicMaterial({ color: 0xff0000, opacity:0.6, transparent:true });
const godCube = new THREE.Mesh(cubeGeometry, godCubeMaterial);
godCube.position.set(-2, 2, 0.25);
scene.add(godCube);
const _wireframe = new THREE.EdgesGeometry( cubeGeometry ); // or WireframeGeometry( geometry )
const wireframe = new THREE.LineSegments( _wireframe);
// wireframe.material.color = 0x800080;
wireframe.position.set(-2, 2, 0.25);
scene.add( wireframe );

// Control cube
const controlCubeMaterial = new THREE.MeshBasicMaterial({ color: 0xff0000 });
const controlCube = new THREE.Mesh(cubeGeometry, controlCubeMaterial);
controlCube.position.set(-1, -1, 0.25);
scene.add(controlCube);
console.log("controlCube coords: [", controlCube.position.x, controlCube.position.y, "]");

// Create balls
const numBalls = 3;
let balls = [];
const ballGeometry = new THREE.SphereGeometry(0.25, 32, 32);
const ballMaterial = new THREE.MeshBasicMaterial({ color: 0x0000ff });
let usedCoords = [];

function getDistance(coordsA, coordsB) {
    let distanceX = coordsA[0] - coordsB[0];
    let distanceY = coordsA[1] - coordsB[1];
    console.log("Coords: [", coordsA, coordsB, "]");
    console.log("Distances: [", distanceX, distanceY, "]");
    return Math.sqrt((distanceX * distanceX) + (distanceY * distanceY));
}

function getCoords() {
    let positionx, positiony, minDistance;
    for(let i=0; i<100; i++) {
        positionx = (Math.floor(Math.random() * (4/0.25)) * 0.25) - 2;
        positiony = (Math.floor(Math.random() * (4/0.25)) * 0.25) - 2;
        minDistance = getDistance([positionx, positiony], [controlCube.position.x, controlCube.position.y]);
        const godCubeDistance = getDistance([positionx, positiony], [godCube.position.x, godCube.position.y]);
        if(godCubeDistance < minDistance) {
            minDistance = godCubeDistance;
        }
        for(let idx=0; idx<balls.length; idx++) {
            const distance = getDistance([positionx, positiony], [balls[idx].position.x, balls[idx].position.y]);
            if (distance < minDistance) {
                minDistance = distance;
            }
        }
        if(minDistance > 1) {
            break;
        }
    }
    console.log("MinDistance = ", minDistance);
    return [positionx, positiony];
}

for(let i=0; i<numBalls; i++) {
    const ball = new THREE.Mesh(ballGeometry, ballMaterial);
    const coords = getCoords();
    ball.position.set(coords[0], coords[1], 0.25);
    scene.add(ball);
    balls.push(ball);
}

// Position the camera
camera.position.set(0, 0, 5);
camera.lookAt(0, 0, 0);

// Animation loop
function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}
animate();

// Handle window resize
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});

// Control buttons
const moveDistance = 0.25; // Distance to move the cube and camera

// Cube controls
document.getElementById('moveForward').addEventListener('click', () => {
    controlCube.position.y += moveDistance;
});

document.getElementById('moveBackward').addEventListener('click', () => {
    controlCube.position.y -= moveDistance;
});

document.getElementById('moveLeft').addEventListener('click', () => {
    controlCube.position.x -= moveDistance;
});

document.getElementById('moveRight').addEventListener('click', () => {
    controlCube.position.x += moveDistance;
});

// Camera controls
document.getElementById('cameraForward').addEventListener('click', () => {
    camera.position.y += moveDistance;
});

document.getElementById('cameraBackward').addEventListener('click', () => {
    camera.position.y -= moveDistance;
});

document.getElementById('cameraLeft').addEventListener('click', () => {
    camera.position.x -= moveDistance;
});

document.getElementById('cameraRight').addEventListener('click', () => {
    camera.position.x += moveDistance;
});

document.getElementById('cameraUp').addEventListener('click', () => {
    camera.position.z += moveDistance;
});

document.getElementById('cameraDown').addEventListener('click', () => {
    camera.position.z -= moveDistance;
});

document.getElementById('rotateClockwise').addEventListener('click', () => {
    camera.rotation.z -= Math.PI / 18; // Rotate 10 degrees clockwise
});

document.getElementById('rotateCounterclockwise').addEventListener('click', () => {
    camera.rotation.z += Math.PI / 18; // Rotate 10 degrees counterclockwise
});