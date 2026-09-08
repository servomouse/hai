import pybullet as p
import pybullet_data
import time
import numpy as np
import cv2

class ExponentialFilter:
    """Low-pass filter to eliminate discrete physics solver jitter."""
    def __init__(self, alpha=0.05, initial_value=0.0):
        self.alpha = alpha
        self.value = np.array(initial_value, dtype=np.float64)

    def update(self, new_value):
        self.value = self.alpha * np.array(new_value) + (1.0 - self.alpha) * self.value
        return self.value

def normalize(value, min_val, max_val):
    """Scales a scalar or numpy array from [min_val, max_val] to [-1, 1]."""
    clipped = np.clip(value, min_val, max_val)
    return 2.0 * (clipped - min_val) / (max_val - min_val) - 1.0

# -----------------------------------------------------------------------------
# 1. Initialize PyBullet Environment
# -----------------------------------------------------------------------------
physicsClient = p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.setGravity(0, 0, -9.81)
p.configureDebugVisualizer(p.COV_ENABLE_GUI, 0)

# Stabilize solver
p.setPhysicsEngineParameter(
    fixedTimeStep=1.0/240.0,
    numSubSteps=4,
    numSolverIterations=20
)

plane_id = p.loadURDF("plane.urdf")

# -----------------------------------------------------------------------------
# 2. Build Expanded Arena & Obstacles
# -----------------------------------------------------------------------------
def create_wall(position, half_extents):
    col_shape = p.createCollisionShape(p.GEOM_BOX, halfExtents=half_extents)
    vis_shape = p.createVisualShape(p.GEOM_BOX, halfExtents=half_extents, rgbaColor=[0.5, 0.5, 0.5, 1])
    return p.createMultiBody(baseMass=0, baseCollisionShapeIndex=col_shape, baseVisualShapeIndex=vis_shape, basePosition=position)

# Expanded arena dimensions (20m x 20m)
length, width, height, thickness = 20.0, 20.0, 1.5, 0.3
create_wall([0,  width / 2, height / 2], [length / 2, thickness / 2, height / 2])
create_wall([0, -width / 2, height / 2], [length / 2, thickness / 2, height / 2])
create_wall([ length / 2, 0, height / 2], [thickness / 2, width / 2, height / 2])
create_wall([-length / 2, 0, height / 2], [thickness / 2, width / 2, height / 2])

# Helper function to spawn obstacles
def spawn_obstacle(shape_type, pos, radius_or_extents, color, mass=0.0):
    if shape_type == "box":
        col = p.createCollisionShape(p.GEOM_BOX, halfExtents=radius_or_extents)
        vis = p.createVisualShape(p.GEOM_BOX, halfExtents=radius_or_extents, rgbaColor=color)
    elif shape_type == "sphere":
        col = p.createCollisionShape(p.GEOM_SPHERE, radius=radius_or_extents[0])
        vis = p.createVisualShape(p.GEOM_SPHERE, radius=radius_or_extents[0], rgbaColor=color)
    elif shape_type == "cylinder":  # Used as triangular-like cylindrical obstacles
        col = p.createCollisionShape(p.GEOM_CYLINDER, radius=radius_or_extents[0], height=radius_or_extents[1])
        vis = p.createVisualShape(p.GEOM_CYLINDER, radius=radius_or_extents[0], length=radius_or_extents[1], rgbaColor=color)
    
    return p.createMultiBody(baseMass=mass, baseCollisionShapeIndex=col, baseVisualShapeIndex=vis, basePosition=pos)

# --- Add Colored Spheres ---
spawn_obstacle("sphere", [3.0, 2.0, 0.5], [0.5], [1.0, 0.2, 0.2, 1.0])   # Red sphere
spawn_obstacle("sphere", [-4.0, 3.0, 0.7], [0.7], [0.2, 0.8, 0.2, 1.0])  # Green sphere
spawn_obstacle("sphere", [2.0, -5.0, 0.4], [0.4], [0.9, 0.8, 0.1, 1.0])  # Yellow sphere

# --- Add Colored Cubes ---
spawn_obstacle("box", [-2.0, -3.0, 0.5], [0.5, 0.5, 0.5], [0.8, 0.2, 0.8, 1.0])  # Purple box
spawn_obstacle("box", [5.0, -2.0, 0.6], [0.6, 0.6, 0.6], [0.1, 0.8, 0.9, 1.0])   # Cyan box

# --- Add Triangular/Cylindrical Pillars ---
spawn_obstacle("cylinder", [-5.0, -5.0, 0.75], [0.4, 1.5], [0.9, 0.5, 0.1, 1.0])
spawn_obstacle("cylinder", [4.0, 5.0, 0.75], [0.5, 1.5], [0.3, 0.3, 0.9, 1.0])

# --- Add Mirrored Cube ---
# Highly reflective material settings (silver/metallic specular highlights)
mirror_col = p.createCollisionShape(p.GEOM_BOX, halfExtents=[0.8, 0.8, 0.8])
mirror_vis = p.createVisualShape(
    p.GEOM_BOX,
    halfExtents=[0.8, 0.8, 0.8],
    rgbaColor=[0.95, 0.95, 0.95, 1.0],
    specularColor=[1.0, 1.0, 1.0]
)
mirror_cube_id = p.createMultiBody(baseMass=0, baseCollisionShapeIndex=mirror_col, baseVisualShapeIndex=mirror_vis, basePosition=[0.0, 4.0, 0.8])

# -----------------------------------------------------------------------------
# 3. Load Robot
# -----------------------------------------------------------------------------
robot_id = p.loadURDF("robot.urdf", basePosition=[0, 0, 0.3])
left_wheels = [2, 4]
right_wheels = [3, 5]

for j in left_wheels + right_wheels:
    p.changeDynamics(
        bodyUniqueId=robot_id,
        linkIndex=j,
        lateralFriction=0.9,
        spinningFriction=0.05,
        rollingFriction=0.01,
        contactStiffness=10000,
        contactDamping=100
    )

# Filters with strong smoothing
accel_filter = ExponentialFilter(alpha=0.05, initial_value=[0.0, 0.0, 9.81])
fl_torque_filter = ExponentialFilter(alpha=0.05)
fr_torque_filter = ExponentialFilter(alpha=0.05)
rl_torque_filter = ExponentialFilter(alpha=0.05)
rr_torque_filter = ExponentialFilter(alpha=0.05)

# Camera configuration
IMG_W, IMG_H = 320, 240
proj_matrix = p.computeProjectionMatrixFOV(fov=60, aspect=float(IMG_W)/IMG_H, nearVal=0.1, farVal=20.0)

def capture_eye_view_fast(robot_id, eye_offset_y):
    pos, ori = p.getBasePositionAndOrientation(robot_id)
    rot_matrix = np.array(p.getMatrixFromQuaternion(ori)).reshape(3, 3)

    local_eye_pos = np.array([0.34, eye_offset_y, 0.1])
    local_target = np.array([2.0, eye_offset_y, 0.1])
    up_vector = np.array([0, 0, 1])

    world_eye_pos = np.array(pos) + rot_matrix.dot(local_eye_pos)
    world_target = np.array(pos) + rot_matrix.dot(local_target)
    world_up = rot_matrix.dot(up_vector)

    view_matrix = p.computeViewMatrix(world_eye_pos, world_target, world_up)

    # Note: For true mirror raytracing, use renderer=p.ER_TINY_RENDERER
    _, _, rgb_img, _, _ = p.getCameraImage(
        width=IMG_W,
        height=IMG_H,
        viewMatrix=view_matrix,
        projectionMatrix=proj_matrix,
        flags=p.ER_NO_SEGMENTATION_MASK,
        renderer=p.ER_BULLET_HARDWARE_OPENGL
    )
    rgb_arr = np.ascontiguousarray(rgb_img, dtype=np.uint8).reshape((IMG_H, IMG_W, 4))
    return cv2.cvtColor(rgb_arr, cv2.COLOR_RGBA2BGR)

# -----------------------------------------------------------------------------
# 4. Main Simulation Loop
# -----------------------------------------------------------------------------
speed = 15.0
step_counter = 0
RENDER_EVERY_N_STEPS = 12
dt = 1.0 / 240.0
prev_lin_vel = np.array([0.0, 0.0, 0.0])

MAX_ACCEL = 30.0  
MAX_TORQUE = 15.0 

try:
    while p.isConnected():
        keys = p.getKeyboardEvents()

        left_speed, right_speed = 0.0, 0.0
        forward = p.B3G_UP_ARROW in keys and (keys[p.B3G_UP_ARROW] & p.KEY_WAS_TRIGGERED or keys[p.B3G_UP_ARROW] & p.KEY_IS_DOWN)
        backward = p.B3G_DOWN_ARROW in keys and (keys[p.B3G_DOWN_ARROW] & p.KEY_WAS_TRIGGERED or keys[p.B3G_DOWN_ARROW] & p.KEY_IS_DOWN)
        left = p.B3G_LEFT_ARROW in keys and (keys[p.B3G_LEFT_ARROW] & p.KEY_WAS_TRIGGERED or keys[p.B3G_LEFT_ARROW] & p.KEY_IS_DOWN)
        right = p.B3G_RIGHT_ARROW in keys and (keys[p.B3G_RIGHT_ARROW] & p.KEY_WAS_TRIGGERED or keys[p.B3G_RIGHT_ARROW] & p.KEY_IS_DOWN)

        if forward:
            left_speed, right_speed = speed, speed
        elif backward:
            left_speed, right_speed = -speed, -speed

        if left:
            left_speed -= speed * 0.6
            right_speed += speed * 0.6
        elif right:
            left_speed += speed * 0.6
            right_speed -= speed * 0.6

        for j in left_wheels:
            p.setJointMotorControl2(robot_id, j, p.VELOCITY_CONTROL, targetVelocity=left_speed, force=15)
        for j in right_wheels:
            p.setJointMotorControl2(robot_id, j, p.VELOCITY_CONTROL, targetVelocity=right_speed, force=15)

        p.stepSimulation()
        step_counter += 1

        # Accelerometer
        pos, ori = p.getBasePositionAndOrientation(robot_id)
        current_lin_vel = np.array(p.getBaseVelocity(robot_id)[0])
        raw_world_accel = (current_lin_vel - prev_lin_vel) / dt - np.array([0.0, 0.0, -9.81])
        prev_lin_vel = current_lin_vel

        rot_matrix = np.array(p.getMatrixFromQuaternion(ori)).reshape(3, 3)
        raw_local_accel = rot_matrix.T.dot(raw_world_accel)

        accel = accel_filter.update(raw_local_accel)
        norm_accel = normalize(accel, -MAX_ACCEL, MAX_ACCEL)

        # Torque sensors
        raw_fl = p.getJointState(robot_id, left_wheels[0])[3]
        raw_rl = p.getJointState(robot_id, left_wheels[1])[3]
        raw_fr = p.getJointState(robot_id, right_wheels[0])[3]
        raw_rr = p.getJointState(robot_id, right_wheels[1])[3]

        fl_torque = normalize(fl_torque_filter.update(raw_fl), -MAX_TORQUE, MAX_TORQUE)
        rl_torque = normalize(rl_torque_filter.update(raw_rl), -MAX_TORQUE, MAX_TORQUE)
        fr_torque = normalize(fr_torque_filter.update(raw_fr), -MAX_TORQUE, MAX_TORQUE)
        rr_torque = normalize(rr_torque_filter.update(raw_rr), -MAX_TORQUE, MAX_TORQUE)

        # Render cameras and HUD
        if step_counter % RENDER_EVERY_N_STEPS == 0:
            left_frame = capture_eye_view_fast(robot_id, eye_offset_y=0.1)
            right_frame = capture_eye_view_fast(robot_id, eye_offset_y=-0.1)

            stereo_view = np.hstack((left_frame, right_frame))
            
            cv2.putText(stereo_view, "LEFT EYE", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(stereo_view, "RIGHT EYE", (IMG_W + 20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            accel_text = f"Norm IMU [-1,1] X:{norm_accel[0]:.2f} Y:{norm_accel[1]:.2f} Z:{norm_accel[2]:.2f}"
            torque_text_L = f"Norm Torque L [-1,1] F:{fl_torque:.2f} R:{rl_torque:.2f}"
            torque_text_R = f"Norm Torque R [-1,1] F:{fr_torque:.2f} R:{rr_torque:.2f}"

            cv2.putText(stereo_view, accel_text, (20, IMG_H - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1)
            cv2.putText(stereo_view, torque_text_L, (20, IMG_H - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1)
            cv2.putText(stereo_view, torque_text_R, (IMG_W + 20, IMG_H - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1)

            cv2.imshow("Robot Binocular Sight", stereo_view)
            cv2.waitKey(1)

        time.sleep(1.0 / 240.0)

except KeyboardInterrupt:
    pass

p.disconnect()
cv2.destroyAllWindows()