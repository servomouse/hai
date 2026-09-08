import * as THREE from 'three';
import RAPIER from '@dimforge/rapier3d-compat';

export class Robot {
  constructor(world, scene, initialPos = { x: 0, y: 0.6, z: 0 }) {
    this.world = world;
    this.scene = scene;

    this.prevVelocity = { x: 0, y: 0, z: 0 };
    this.moveSpeed = 4.0;
    this.turnSpeed = 2.5;

    this.keys = { forward: false, backward: false, left: false, right: false };

    this.initPhysicsAndVisuals(initialPos);
    this.initOnboardCameras();
    this.initRaycastVisual();
    this.initInputListeners();
  }

  initPhysicsAndVisuals(pos) {
    const bodyDesc = RAPIER.RigidBodyDesc.dynamic()
      .setTranslation(pos.x, pos.y, pos.z)
      .setLinearDamping(0.5)
      .setAngularDamping(1.0);
      
    this.body = this.world.createRigidBody(bodyDesc);

    const colliderDesc = RAPIER.ColliderDesc.cuboid(0.5, 0.5, 0.5);
    this.world.createCollider(colliderDesc, this.body);

    this.mesh = new THREE.Mesh(
      new THREE.BoxGeometry(1, 1, 1),
      new THREE.MeshStandardMaterial({ color: 0x4488ff })
    );
    this.scene.add(this.mesh);
  }

  // Setup dual left & right stereo camera rig
  initOnboardCameras() {
    const aspect = 180 / 120;
    this.leftCamera = new THREE.PerspectiveCamera(70, aspect, 0.01, 50);
    this.rightCamera = new THREE.PerspectiveCamera(70, aspect, 0.01, 50);

    // Baseline separation: 0.2 units apart (0.1 units left/right of center)
    const baselineOffset = 0.5;
    this.leftCameraOffset = new THREE.Vector3(baselineOffset, 0.35, 0.25);
    this.rightCameraOffset = new THREE.Vector3(-baselineOffset, 0.35, 0.25);
  }

  initRaycastVisual() {
    const rayGeo = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(0, 0, 0),
      new THREE.Vector3(0, 0, 1)
    ]);
    this.sensorRayVisual = new THREE.Line(
      rayGeo,
      new THREE.LineBasicMaterial({ color: 0x00ff00 })
    );
    this.scene.add(this.sensorRayVisual);
  }

  initInputListeners() {
    window.addEventListener('keydown', (e) => this.handleKey(e.code, true));
    window.addEventListener('keyup', (e) => this.handleKey(e.code, false));
  }

  handleKey(code, isPressed) {
    switch (code) {
      case 'KeyW': case 'ArrowUp': this.keys.forward = isPressed; break;
      case 'KeyS': case 'ArrowDown': this.keys.backward = isPressed; break;
      case 'KeyA': case 'ArrowLeft': this.keys.left = isPressed; break;
      case 'KeyD': case 'ArrowRight': this.keys.right = isPressed; break;
    }
  }

  updatePhysics() {
    if (!this.body) return;

    let turn = 0;
    if (this.keys.left) turn += this.turnSpeed;
    if (this.keys.right) turn -= this.turnSpeed;
    this.body.setAngvel({ x: 0, y: turn, z: 0 }, true);

    let drive = 0;
    if (this.keys.forward) drive += this.moveSpeed;
    if (this.keys.backward) drive -= this.moveSpeed;

    const rot = this.body.rotation();
    const q = new THREE.Quaternion(rot.x, rot.y, rot.z, rot.w);
    const forward = new THREE.Vector3(0, 0, 1).applyQuaternion(q);

    const currentVel = this.body.linvel();
    this.body.setLinvel(
      { x: forward.x * drive, y: currentVel.y, z: forward.z * drive },
      true
    );
  }

  syncVisuals() {
    const pos = this.body.translation();
    const rot = this.body.rotation();
    this.mesh.position.set(pos.x, pos.y, pos.z);
    this.mesh.quaternion.set(rot.x, rot.y, rot.z, rot.w);

    const q = this.mesh.quaternion.clone();

    // Position and align Left Camera
    const leftLocalPos = this.leftCameraOffset.clone().applyQuaternion(q);
    this.leftCamera.position.copy(this.mesh.position).add(leftLocalPos);
    const leftForward = new THREE.Vector3(-0.25, 0, 10).applyQuaternion(q).add(this.mesh.position);
    this.leftCamera.lookAt(leftForward);

    // Position and align Right Camera
    const rightLocalPos = this.rightCameraOffset.clone().applyQuaternion(q);
    this.rightCamera.position.copy(this.mesh.position).add(rightLocalPos);
    const rightForward = new THREE.Vector3(0.25, 0, 10).applyQuaternion(q).add(this.mesh.position);
    this.rightCamera.lookAt(rightForward);
  }

  getSensorReadings(dt) {
    const rawGyro = this.body ? this.body.angvel() : null;
    const gyro = { x: rawGyro?.x ?? 0, y: rawGyro?.y ?? 0, z: rawGyro?.z ?? 0 };

    const currentVel = this.body ? this.body.linvel() : { x: 0, y: 0, z: 0 };
    const gravY = this.world?.gravity?.y ?? -9.81;

    const accel = {
      x: dt > 0 ? (currentVel.x - this.prevVelocity.x) / dt : 0,
      y: dt > 0 ? (currentVel.y - this.prevVelocity.y) / dt - gravY : 0,
      z: dt > 0 ? (currentVel.z - this.prevVelocity.z) / dt : 0
    };
    this.prevVelocity = { ...currentVel };

    const pos = this.body.translation();
    const rot = this.body.rotation();
    const q = new THREE.Quaternion(rot.x, rot.y, rot.z, rot.w);
    const forward = new THREE.Vector3(0, 0, 1).applyQuaternion(q);

    const rayOrigin = new RAPIER.Vector3(pos.x, pos.y, pos.z);
    const rayDir = new RAPIER.Vector3(forward.x, forward.y, forward.z);

    const ray = new RAPIER.Ray(rayOrigin, rayDir);
    const maxDist = 8.0;
    const hit = this.world.castRay(ray, maxDist, true);
    const distance = (hit && hit.toi !== undefined) ? hit.toi : maxDist;

    this.sensorRayVisual.position.set(pos.x, pos.y, pos.z);
    this.sensorRayVisual.lookAt(
      pos.x + forward.x * distance,
      pos.y + forward.y * distance,
      pos.z + forward.z * distance
    );
    this.sensorRayVisual.scale.set(1, 1, distance);

    return { gyro, accel, distance };
  }

  // Returns both cameras for external rendering
  get cameras() {
    return {
      left: this.leftCamera,
      right: this.rightCamera
    };
  }
}