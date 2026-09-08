import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { Reflector } from 'three/addons/objects/Reflector.js';
import RAPIER from '@dimforge/rapier3d-compat';

export class Arena {
  constructor(containerId) {
    this.container = document.getElementById(containerId);

    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x1a1a1a);

    this.camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 100);
    this.camera.position.set(5, 6, 8);

    // Main Canvas Renderer
    this.renderer = new THREE.WebGLRenderer({ antialias: true });
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.renderer.shadowMap.enabled = true;
    this.container.appendChild(this.renderer.domElement);

    // Secondary Renderer for PIP Canvas
    const pipCanvas = document.getElementById('pip-canvas');
    this.pipRenderer = new THREE.WebGLRenderer({ canvas: pipCanvas, antialias: true });
    this.pipRenderer.setSize(240, 160);

    // OrbitControls Setup
    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    this.controls.target.set(0, 0.5, 0);
    this.controls.enableZoom = true;
    this.controls.enablePan = true;
    this.controls.enableRotate = true;
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.05;

    this.controls.mouseButtons = {
      LEFT: THREE.MOUSE.ROTATE,
      MIDDLE: THREE.MOUSE.DOLLY,
      RIGHT: THREE.MOUSE.PAN
    };

    this.controls.minDistance = 1.0;
    this.controls.maxDistance = 20.0;
    this.controls.update();

    this.dynamicObjects = [];

    this.setupLighting();
    this.setupVisualGrid();

    window.addEventListener('resize', () => this.onResize());
  }

  setupLighting() {
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    this.scene.add(ambientLight);

    const dirLight = new THREE.DirectionalLight(0xffffff, 0.9);
    dirLight.position.set(10, 15, 10);
    dirLight.castShadow = true;
    dirLight.shadow.mapSize.width = 1024;
    dirLight.shadow.mapSize.height = 1024;
    this.scene.add(dirLight);
  }

  setupVisualGrid() {
    const grid = new THREE.GridHelper(20, 20, 0x00ffcc, 0x444444);
    this.scene.add(grid);
  }

  buildPhysicsEnvironment(world) {
    this.world = world;

    // 1. Static Ground Plane
    const groundDesc = RAPIER.RigidBodyDesc.fixed();
    const groundBody = world.createRigidBody(groundDesc);
    const groundCollider = RAPIER.ColliderDesc.cuboid(10, 0.1, 10);
    world.createCollider(groundCollider, groundBody);

    // --- OBSTACLES DEFINITION ---

    // 2. Mirror Pillar (Replaces the Large Red Pillar)
    this.addMirrorPillar({ x: -3, y: 1.0, z: 2 }, { x: 1.5, y: 2.0, z: 1.5 });

    // Fixed (Unmovable) Cubes
    this.addCube({ x: 3, y: 0.5, z: -2 }, { x: 1.0, y: 1.0, z: 1.0 }, 0xaa00ff, false); // Medium Purple Block
    this.addCube({ x: 0, y: 0.75, z: 4 }, { x: 3.0, y: 1.5, z: 0.5 }, 0x333333, false); // Long Dark Wall

    // Movable (Pushable) Cubes
    this.addCube({ x: 1.5, y: 0.4, z: 2 }, { x: 0.8, y: 0.8, z: 0.8 }, 0xffaa00, true);  // Small Orange Box
    this.addCube({ x: -1.5, y: 0.3, z: -1 }, { x: 0.6, y: 0.6, z: 0.6 }, 0x00ffaa, true); // Teal Crate

    // Movable (Rollable) Balls / Spheres
    this.addSphere({ x: 0, y: 0.5, z: 2.5 }, 0.5, 0xff0077, true);   // Medium Pink Ball
    this.addSphere({ x: -2, y: 0.75, z: -3 }, 0.75, 0x00aaff, true); // Large Blue Beach Ball
    this.addSphere({ x: 2, y: 0.3, z: -3 }, 0.3, 0xffff00, true);    // Small Yellow Ball
    this.addSphere({ x: 1, y: 0.4, z: 0 }, 0.4, 0xff8800, true);     // Orange Ball
  }

  addMirrorPillar(pos, size) {
    // 1. Static Physics Collider in Rapier
    const bodyDesc = RAPIER.RigidBodyDesc.fixed().setTranslation(pos.x, pos.y, pos.z);
    const body = this.world.createRigidBody(bodyDesc);
    const collider = RAPIER.ColliderDesc.cuboid(size.x / 2, size.y / 2, size.z / 2);
    this.world.createCollider(collider, body);

    // 2. Base Box Geometry Mesh with Dark Red Tint
    const pillarGroup = new THREE.Group();
    pillarGroup.position.set(pos.x, pos.y, pos.z);

    const baseMesh = new THREE.Mesh(
      new THREE.BoxGeometry(size.x, size.y, size.z),
      new THREE.MeshStandardMaterial({ color: 0x330000, roughness: 0.2 })
    );
    pillarGroup.add(baseMesh);

    // 3. Attach Mirror Reflectors to front and side faces
    const mirrorOptions = {
      clipBias: 0.003,
      textureWidth: window.innerWidth * window.devicePixelRatio,
      textureHeight: window.innerHeight * window.devicePixelRatio,
      color: 0xffaaaa // Subtitle red tint on reflection
    };

    // Front Face Mirror (+Z side)
    const frontMirrorGeo = new THREE.PlaneGeometry(size.x, size.y);
    const frontMirror = new Reflector(frontMirrorGeo, mirrorOptions);
    frontMirror.position.set(0, 0, size.z / 2 + 0.01);
    pillarGroup.add(frontMirror);

    // Right Face Mirror (+X side)
    const rightMirrorGeo = new THREE.PlaneGeometry(size.z, size.y);
    const rightMirror = new Reflector(rightMirrorGeo, mirrorOptions);
    rightMirror.position.set(size.x / 2 + 0.01, 0, 0);
    rightMirror.rotation.y = Math.PI / 2;
    pillarGroup.add(rightMirror);

    this.scene.add(pillarGroup);
  }

  addCube(pos, size, color, isDynamic = false) {
    const bodyDesc = isDynamic
      ? RAPIER.RigidBodyDesc.dynamic().setTranslation(pos.x, pos.y, pos.z).setLinearDamping(0.8).setAngularDamping(0.8)
      : RAPIER.RigidBodyDesc.fixed().setTranslation(pos.x, pos.y, pos.z);

    const body = this.world.createRigidBody(bodyDesc);
    const collider = RAPIER.ColliderDesc.cuboid(size.x / 2, size.y / 2, size.z / 2);
    this.world.createCollider(collider, body);

    const mesh = new THREE.Mesh(
      new THREE.BoxGeometry(size.x, size.y, size.z),
      new THREE.MeshStandardMaterial({ color, roughness: 0.4 })
    );
    mesh.position.set(pos.x, pos.y, pos.z);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    this.scene.add(mesh);

    if (isDynamic) {
      this.dynamicObjects.push({ body, mesh });
    }
  }

  addSphere(pos, radius, color, isDynamic = true) {
    const bodyDesc = isDynamic
      ? RAPIER.RigidBodyDesc.dynamic().setTranslation(pos.x, pos.y, pos.z).setLinearDamping(0.3).setAngularDamping(0.3)
      : RAPIER.RigidBodyDesc.fixed().setTranslation(pos.x, pos.y, pos.z);

    const body = this.world.createRigidBody(bodyDesc);
    const collider = RAPIER.ColliderDesc.ball(radius);
    this.world.createCollider(collider, body);

    const mesh = new THREE.Mesh(
      new THREE.SphereGeometry(radius, 32, 32),
      new THREE.MeshStandardMaterial({ color, roughness: 0.2 })
    );
    mesh.position.set(pos.x, pos.y, pos.z);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    this.scene.add(mesh);

    if (isDynamic) {
      this.dynamicObjects.push({ body, mesh });
    }
  }

  syncDynamicObjects() {
    for (const obj of this.dynamicObjects) {
      const pos = obj.body.translation();
      const rot = obj.body.rotation();
      obj.mesh.position.set(pos.x, pos.y, pos.z);
      obj.mesh.quaternion.set(rot.x, rot.y, rot.z, rot.w);
    }
  }

  render(robotCamera) {
    this.syncDynamicObjects();

    this.controls.update();
    this.renderer.render(this.scene, this.camera);

    if (robotCamera) {
      this.pipRenderer.render(this.scene, robotCamera);
    }
  }

  onResize() {
    this.camera.aspect = window.innerWidth / window.innerHeight;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(window.innerWidth, window.innerHeight);
  }
}