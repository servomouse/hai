import * as THREE from 'three';
import RAPIER from '@dimforge/rapier3d-compat';
import URDFLoader from 'urdf-loader';

const ROBOT_URDF = `<?xml version="1.0"?>
<robot name="binocular_robot">
  <link name="chassis_link">
    <visual>
      <geometry>
        <box size="1.4 0.4 1.8" />
      </geometry>
      <material name="chassis_dark">
        <color rgba="0.08 0.1 0.14 1" />
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="1.4 0.4 1.8" />
      </geometry>
    </collision>
  </link>
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
  <link name="left_flashlight_link">
    <visual>
      <geometry>
        <box size="0.18 0.18 0.18" />
      </geometry>
      <material name="left_flashlight_blue">
        <color rgba="0.1 0.25 0.7 1" />
      </material>
    </visual>
  </link>
  <link name="right_distance_sensor_link">
    <visual>
      <geometry>
        <box size="0.18 0.18 0.18" />
      </geometry>
      <material name="right_distance_sensor_blue">
        <color rgba="0.1 0.25 0.7 1" />
      </material>
    </visual>
  </link>
  <link name="led_matrix_link" />
  <link name="front_left_wheel_link">
    <visual>
      <geometry>
        <cylinder radius="0.22" length="0.16" />
      </geometry>
      <material name="wheel_rubber">
        <color rgba="0.02 0.02 0.025 1" />
      </material>
    </visual>
  </link>
  <link name="front_right_wheel_link">
    <visual>
      <geometry>
        <cylinder radius="0.22" length="0.16" />
      </geometry>
      <material name="wheel_rubber">
        <color rgba="0.02 0.02 0.025 1" />
      </material>
    </visual>
  </link>
  <link name="rear_left_wheel_link">
    <visual>
      <geometry>
        <cylinder radius="0.22" length="0.16" />
      </geometry>
      <material name="wheel_rubber">
        <color rgba="0.02 0.02 0.025 1" />
      </material>
    </visual>
  </link>
  <link name="rear_right_wheel_link">
    <visual>
      <geometry>
        <cylinder radius="0.22" length="0.16" />
      </geometry>
      <material name="wheel_rubber">
        <color rgba="0.02 0.02 0.025 1" />
      </material>
    </visual>
  </link>
  <joint name="head_mount" type="fixed">
    <parent link="chassis_link" />
    <child link="base_link" />
    <origin xyz="0 0.72 0" rpy="0 0 0" />
  </joint>
  <joint name="left_camera_mount" type="fixed">
    <parent link="base_link" />
    <child link="left_camera_link" />
    <origin xyz="0.59 0.3 0.41" rpy="0 0 0" />
  </joint>
  <joint name="right_camera_mount" type="fixed">
    <parent link="base_link" />
    <child link="right_camera_link" />
    <origin xyz="-0.59 0.3 0.41" rpy="0 0 0" />
  </joint>
  <joint name="left_flashlight_mount" type="fixed">
    <parent link="base_link" />
    <child link="left_flashlight_link" />
    <origin xyz="0.59 -0.3 0.41" rpy="0 0 0" />
  </joint>
  <joint name="right_distance_sensor_mount" type="fixed">
    <parent link="base_link" />
    <child link="right_distance_sensor_link" />
    <origin xyz="-0.59 -0.3 0.41" rpy="0 0 0" />
  </joint>
  <joint name="led_matrix_mount" type="fixed">
    <parent link="base_link" />
    <child link="led_matrix_link" />
    <origin xyz="0 0 0.51" rpy="0 0 0" />
  </joint>
  <joint name="front_left_wheel_mount" type="fixed">
    <parent link="chassis_link" />
    <child link="front_left_wheel_link" />
    <origin xyz="0.72 -0.28 0.58" rpy="0 1.5708 0" />
  </joint>
  <joint name="front_right_wheel_mount" type="fixed">
    <parent link="chassis_link" />
    <child link="front_right_wheel_link" />
    <origin xyz="-0.72 -0.28 0.58" rpy="0 1.5708 0" />
  </joint>
  <joint name="rear_left_wheel_mount" type="fixed">
    <parent link="chassis_link" />
    <child link="rear_left_wheel_link" />
    <origin xyz="0.72 -0.28 -0.58" rpy="0 1.5708 0" />
  </joint>
  <joint name="rear_right_wheel_mount" type="fixed">
    <parent link="chassis_link" />
    <child link="rear_right_wheel_link" />
    <origin xyz="-0.72 -0.28 -0.58" rpy="0 1.5708 0" />
  </joint>
</robot>`;

export class Robot {
  constructor(world, scene, initialPos = { x: 0, y: 0.6, z: 0 }) {
    this.world = world;
    this.scene = scene;
    this.visualHeightOffset = 0.3;

    this.prevVelocity = { x: 0, y: 0, z: 0 };
    this.moveSpeed = 4.0;
    this.turnSpeed = 2.5;
    this.headMoveSpeed = 1.5;
    this.headYaw = 0;
    this.headPitch = 0;

    // Smoothing factor for Exponential Moving Average (EMA) [0.0 = max smooth/slow, 1.0 = raw/no filter]
    this.smoothingFactor = 0.5;

    // Filtered state stores
    this.filteredGyro = { x: 0, y: 0, z: 0 };
    this.filteredAccel = { x: 0, y: 0, z: 0 };
    this.filteredDistance = 8.0;
    this.maxSensorDistance = 20.0;

    this.keys = {
      forward: false,
      backward: false,
      left: false,
      right: false,
      headUp: false,
      headDown: false,
      headLeft: false,
      headRight: false
    };

    this.initPhysicsAndVisuals(initialPos);
    this.initOnboardCameras();
    this.initFlashlight();
    this.initLedMatrix();
    this.initRaycastVisual();
    this.initInputListeners();
  }

  initPhysicsAndVisuals(pos) {
    const bodyDesc = RAPIER.RigidBodyDesc.dynamic()
      .setTranslation(pos.x, pos.y, pos.z)
      .setLinearDamping(0.5)
      .setAngularDamping(1.0);
      
    this.body = this.world.createRigidBody(bodyDesc);

    const colliderDesc = RAPIER.ColliderDesc.cuboid(0.7, 0.2, 0.9);
    this.collider = this.world.createCollider(colliderDesc, this.body);

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

  initFlashlight() {
    this.flashlightFrame = this.mesh.frames.left_flashlight_link;
    this.flashlight = new THREE.SpotLight(0xffffff, 5, this.maxSensorDistance, Math.PI / 7, 0.35, 1.5);
    this.flashlight.castShadow = true;
    this.flashlight.shadow.mapSize.width = 512;
    this.flashlight.shadow.mapSize.height = 512;
    this.flashlight.shadow.bias = -0.0005;
    this.flashlight.position.set(0, 0, 0);
    this.flashlight.target.position.set(0, 0, 1);
    this.flashlightFrame.add(this.flashlight);
    this.flashlightFrame.add(this.flashlight.target);

    this.flashlightLensMaterials = [];
    this.flashlightFrame.traverse((object) => {
      if (!object.isMesh || this.flashlightLensMaterials.length > 0) return;

      const baseMaterial = object.material;
      const materials = Array.from({ length: 6 }, () => baseMaterial.clone());
      materials[4] = new THREE.MeshStandardMaterial({
        color: 0x222222,
        emissive: 0x000000,
        roughness: 0.25
      });
      object.material = materials;
      this.flashlightLensMaterials = [object, materials[4]];
    });
    this.setFlashlightEnabled(true);
  }

  setFlashlightEnabled(enabled) {
    this.flashlight.visible = enabled;
    if (this.flashlightLensMaterials.length > 0) {
      this.flashlightLensMaterials[1].color.setHex(enabled ? 0xffffff : 0x222222);
      this.flashlightLensMaterials[1].emissive.setHex(enabled ? 0xffffff : 0x000000);
      this.flashlightLensMaterials[1].emissiveIntensity = enabled ? 2 : 0;
    }
  }

  initLedMatrix() {
    this.ledMatrixFrame = this.mesh.frames.led_matrix_link;
    this.leds = [];

    const ledGeometry = new THREE.CylinderGeometry(0.035, 0.035, 0.025, 12);
    const spacing = 0.095;
    const matrixSize = spacing * 7;

    for (let row = 0; row < 8; row += 1) {
      for (let column = 0; column < 8; column += 1) {
        const ledMaterial = new THREE.MeshStandardMaterial({
          color: 0x180000,
          emissive: 0x000000,
          roughness: 0.35
        });
        const led = new THREE.Mesh(ledGeometry, ledMaterial);
        led.rotation.x = Math.PI / 2;
        led.position.set(
          column * spacing - matrixSize / 2,
          matrixSize / 2 - row * spacing,
          0.015
        );
        led.castShadow = true;
        led.receiveShadow = true;
        this.ledMatrixFrame.add(led);
        this.leds.push({ led, material: ledMaterial });
      }
    }

    this.setLedMatrix(new Array(8).fill(0));
  }

  setLedMatrix(rows) {
    if (!Array.isArray(rows) || rows.length !== 8) {
      throw new TypeError('LED matrix requires an array of 8 byte values.');
    }

    for (let row = 0; row < 8; row += 1) {
      const value = Number(rows[row]);
      if (!Number.isInteger(value) || value < 0 || value > 255) {
        throw new TypeError('LED matrix rows must be bytes from 0 to 255.');
      }

      for (let column = 0; column < 8; column += 1) {
        const isOn = (value & (1 << (7 - column))) !== 0;
        const led = this.leds[row * 8 + column];
        led.material.color.setHex(isOn ? 0xff2020 : 0x180000);
        led.material.emissive.setHex(isOn ? 0xff0000 : 0x000000);
        led.material.emissiveIntensity = isOn ? 3 : 0;
      }
    }
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
      case 'ArrowUp': this.keys.forward = isPressed; break;
      case 'ArrowDown': this.keys.backward = isPressed; break;
      case 'ArrowLeft': this.keys.left = isPressed; break;
      case 'ArrowRight': this.keys.right = isPressed; break;
      case 'KeyW': this.keys.headUp = isPressed; break;
      case 'KeyS': this.keys.headDown = isPressed; break;
      case 'KeyA': this.keys.headLeft = isPressed; break;
      case 'KeyD': this.keys.headRight = isPressed; break;
    }
  }

  updatePhysics(dt = 1 / 60) {
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

    if (this.keys.headUp) this.headPitch += this.headMoveSpeed * dt;
    if (this.keys.headDown) this.headPitch -= this.headMoveSpeed * dt;
    if (this.keys.headLeft) this.headYaw += this.headMoveSpeed * dt;
    if (this.keys.headRight) this.headYaw -= this.headMoveSpeed * dt;

    const maxHeadRotation = Math.PI / 2;
    this.headPitch = THREE.MathUtils.clamp(this.headPitch, -maxHeadRotation, maxHeadRotation);
    this.headYaw = THREE.MathUtils.clamp(this.headYaw, -maxHeadRotation, maxHeadRotation);
  }

  syncVisuals() {
    const pos = this.body.translation();
    const rot = this.body.rotation();
    this.mesh.position.set(pos.x, pos.y + this.visualHeightOffset, pos.z);
    this.mesh.quaternion.set(rot.x, rot.y, rot.z, rot.w);
    this.mesh.frames.base_link.rotation.set(this.headPitch, this.headYaw, 0);
    this.mesh.updateMatrixWorld(true);

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

    this.mesh.updateMatrixWorld(true);
    const sensorFrame = this.mesh.frames.right_distance_sensor_link;
    const rayOriginVector = sensorFrame.getWorldPosition(new THREE.Vector3());
    const rayEnd = sensorFrame.localToWorld(new THREE.Vector3(0, 0, 1));
    const forward = rayEnd.sub(rayOriginVector).normalize();

    const rayOrigin = new RAPIER.Vector3(rayOriginVector.x, rayOriginVector.y, rayOriginVector.z);
    const rayDir = new RAPIER.Vector3(forward.x, forward.y, forward.z);

    const ray = new RAPIER.Ray(rayOrigin, rayDir);
    const hit = this.world.castRay(ray, this.maxSensorDistance, true);
    const rawDistance = hit && hit.toi !== undefined ? hit.toi : Infinity;
    const visualDistance = Number.isFinite(rawDistance) ? rawDistance : this.maxSensorDistance;

    this.sensorRayVisual.position.copy(rayOriginVector);
    this.sensorRayVisual.lookAt(
      rayOriginVector.x + forward.x * visualDistance,
      rayOriginVector.y + forward.y * visualDistance,
      rayOriginVector.z + forward.z * visualDistance
    );
    this.sensorRayVisual.scale.set(1, 1, visualDistance);

    // Apply Exponential Moving Average (EMA) filtering
    const alpha = this.smoothingFactor;

    this.filteredGyro.x += alpha * (rawGyroObj.x - this.filteredGyro.x);
    this.filteredGyro.y += alpha * (rawGyroObj.y - this.filteredGyro.y);
    this.filteredGyro.z += alpha * (rawGyroObj.z - this.filteredGyro.z);

    this.filteredAccel.x += alpha * (rawAccelObj.x - this.filteredAccel.x);
    this.filteredAccel.y += alpha * (rawAccelObj.y - this.filteredAccel.y);
    this.filteredAccel.z += alpha * (rawAccelObj.z - this.filteredAccel.z);

    this.filteredDistance = Number.isFinite(rawDistance)
      ? (Number.isFinite(this.filteredDistance)
        ? this.filteredDistance + alpha * (rawDistance - this.filteredDistance)
        : rawDistance)
      : Infinity;

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