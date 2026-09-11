import * as THREE from 'three';
import RAPIER from '@dimforge/rapier3d-compat';
import URDFLoader from 'urdf-loader';

const ROBOT_URDF = `<?xml version="1.0"?>
<robot name="binocular_robot">
  <link name="base_link">
    <visual>
      <geometry>
        <box size="1 1 1" />
      </geometry>
      <material name="robot_blue">
        <color rgba="0.267 0.533 1 1" />
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="1 1 1" />
      </geometry>
    </collision>
  </link>
  <link name="left_camera_link">
    <visual>
      <geometry>
        <box size="0.18 0.18 0.18" />
      </geometry>
      <material name="left_camera_blue">
        <color rgba="0.1 0.25 0.7 1" />
      </material>
    </visual>
  </link>
  <link name="right_camera_link">
    <visual>
      <geometry>
        <box size="0.18 0.18 0.18" />
      </geometry>
      <material name="right_camera_blue">
        <color rgba="0.1 0.25 0.7 1" />
      </material>
    </visual>
  </link>
  <joint name="left_camera_mount" type="fixed">
    <parent link="base_link" />
    <child link="left_camera_link" />
    <origin xyz="0.58 0.3 0.3" rpy="0 0 0" />
  </joint>
  <joint name="right_camera_mount" type="fixed">
    <parent link="base_link" />
    <child link="right_camera_link" />
    <origin xyz="-0.58 0.3 0.3" rpy="0 0 0" />
  </joint>
</robot>`;

export class Robot {
  constructor(world, scene, initialPos = { x: 0, y: 0.6, z: 0 }) {
    this.world = world;
    this.scene = scene;

    this.prevVelocity = { x: 0, y: 0, z: 0 };
    this.moveSpeed = 4.0;
    this.turnSpeed = 2.5;

    // Smoothing factor for Exponential Moving Average (EMA) [0.0 = max smooth/slow, 1.0 = raw/no filter]
    this.smoothingFactor = 0.5;

    // Filtered state stores
    this.filteredGyro = { x: 0, y: 0, z: 0 };
    this.filteredAccel = { x: 0, y: 0, z: 0 };
    this.filteredDistance = 8.0;

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

    const urdfLoader = new URDFLoader();
    this.mesh = urdfLoader.parse(ROBOT_URDF);
    this.mesh.name = 'robot-urdf';
    this.mesh.traverse((object) => {
      if (object.isMesh) {
        object.castShadow = true;
        object.receiveShadow = true;
      }
    });
    this.scene.add(this.mesh);
  }

  initOnboardCameras() {
    const aspect = 180 / 120;
    this.leftCamera = new THREE.PerspectiveCamera(70, aspect, 0.01, 50);
    this.rightCamera = new THREE.PerspectiveCamera(70, aspect, 0.01, 50);

    this.leftCameraFrame = this.mesh.frames.left_camera_link;
    this.rightCameraFrame = this.mesh.frames.right_camera_link;
    this.leftCameraFrame.add(this.leftCamera);
    this.rightCameraFrame.add(this.rightCamera);
    this.leftCamera.position.set(0, 0, 0);
    this.rightCamera.position.set(0, 0, 0);
    this.leftCamera.rotation.set(0, Math.PI, 0);
    this.rightCamera.rotation.set(0, Math.PI, 0);
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

  }

  getSensorReadings(dt) {
    const rawGyro = this.body ? this.body.angvel() : null;
    const rawGyroObj = { x: rawGyro?.x ?? 0, y: rawGyro?.y ?? 0, z: rawGyro?.z ?? 0 };

    const currentVel = this.body ? this.body.linvel() : { x: 0, y: 0, z: 0 };
    const gravY = this.world?.gravity?.y ?? -9.81;

    const rawAccelObj = {
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
    const rawDistance = (hit && hit.toi !== undefined) ? hit.toi : maxDist;

    this.sensorRayVisual.position.set(pos.x, pos.y, pos.z);
    this.sensorRayVisual.lookAt(
      pos.x + forward.x * rawDistance,
      pos.y + forward.y * rawDistance,
      pos.z + forward.z * rawDistance
    );
    this.sensorRayVisual.scale.set(1, 1, rawDistance);

    // Apply Exponential Moving Average (EMA) filtering
    const alpha = this.smoothingFactor;

    this.filteredGyro.x += alpha * (rawGyroObj.x - this.filteredGyro.x);
    this.filteredGyro.y += alpha * (rawGyroObj.y - this.filteredGyro.y);
    this.filteredGyro.z += alpha * (rawGyroObj.z - this.filteredGyro.z);

    this.filteredAccel.x += alpha * (rawAccelObj.x - this.filteredAccel.x);
    this.filteredAccel.y += alpha * (rawAccelObj.y - this.filteredAccel.y);
    this.filteredAccel.z += alpha * (rawAccelObj.z - this.filteredAccel.z);

    this.filteredDistance += alpha * (rawDistance - this.filteredDistance);

    return {
      gyro: this.filteredGyro,
      accel: this.filteredAccel,
      distance: this.filteredDistance
    };
  }

  get cameras() {
    return {
      left: this.leftCamera,
      right: this.rightCamera
    };
  }
}