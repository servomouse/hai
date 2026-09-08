import * as THREE from 'three';
import RAPIER from '@dimforge/rapier3d-compat';
import { Arena } from './arena.js';
import { Robot } from './robot.js';

// UI Elements
const gyroEl = document.getElementById('gyro');
const accelEl = document.getElementById('accel');
const distEl = document.getElementById('dist');

let world, arena, robot;
const clock = new THREE.Clock();

async function init() {
  await RAPIER.init();
  world = new RAPIER.World({ x: 0.0, y: -9.81, z: 0.0 });

  arena = new Arena('canvas-container');
  arena.buildPhysicsEnvironment(world);

  robot = new Robot(world, arena.scene);

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
    distEl.innerText = `${sensors.distance.toFixed(2)} m`;
  }

  // Render main viewport & pass onboard robot camera to PIP canvas
  arena.render(robot?.camera, robot?.mesh);
}

init();