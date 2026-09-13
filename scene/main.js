import * as THREE from 'three';
import RAPIER from '@dimforge/rapier3d-compat';
import { Arena } from './arena.js';
import { Robot } from './robot.js';

// UI Elements
const gyroEl = document.getElementById('gyro');
const accelEl = document.getElementById('accel');
const distEl = document.getElementById('dist');
const globalLightingToggle = document.getElementById('global-lighting-toggle');
const flashlightToggle = document.getElementById('flashlight-toggle');

let world, arena, robot;
const clock = new THREE.Clock();

async function init() {
  await RAPIER.init();
  world = new RAPIER.World({ x: 0.0, y: -9.81, z: 0.0 });

  arena = new Arena('canvas-container');
  arena.buildPhysicsEnvironment(world);

  robot = new Robot(world, arena.scene);
  globalLightingToggle.addEventListener('change', () => {
    arena.setGlobalLightingEnabled(globalLightingToggle.checked);
  });
  flashlightToggle.addEventListener('change', () => {
    robot.setFlashlightEnabled(flashlightToggle.checked);
  });

  animate();
}

function animate() {
  requestAnimationFrame(animate);

  const dt = clock.getDelta();

  if (world && dt > 0) {
    robot.updatePhysics();
    world.step();
    robot.syncVisuals();

    const sensors = robot.getSensorReadings(dt);

    gyroEl.innerText = `X: ${sensors.gyro.x.toFixed(2)} | Y: ${sensors.gyro.y.toFixed(2)} | Z: ${sensors.gyro.z.toFixed(2)}`;
    accelEl.innerText = `X: ${sensors.accel.x.toFixed(2)} | Y: ${sensors.accel.y.toFixed(2)} | Z: ${sensors.accel.z.toFixed(2)}`;
    distEl.innerText = Number.isFinite(sensors.distance)
      ? `${sensors.distance.toFixed(2)} m`
      : 'Infinity m';
  }

  // Render main viewport & pass onboard binocular cameras to PIP canvases
  arena.render(robot?.cameras);
}

init();