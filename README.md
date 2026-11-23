# Armando_Simulation — Classwork 2 (Robotics Lab 2026)

ROS 2 Humble pipeline for ArUco marker detection and KDL inverse kinematics on the Armando manipulator.

## Marker & Target Configuration
- **ArUco dictionary:** `DICT_ARUCO_ORIGINAL`
- **Marker ID:** `10`
- **Black square size (`marker_size`):** `0.10 m` (10 cm)
- **Total plane size including white border (`L` in `model.sdf`):** `0.15 m` (15 cm)
- **Target offset along marker `+Z` normal (`offset_d`):** `0.15 m` (15 cm), with target `+Z` oriented toward the marker (`RPY = [pi, 0, 0]` relative to marker frame).

## 1. Build and Start the Docker Container
```bash
git clone https://github.com/checco03na/Armando_Simulation.git
cd Armando_Simulation/docker_scripts
chmod +x *.sh
./docker_build_image.sh
./docker_run_container.sh
```

## 2. Launch the Gazebo Simulation (Terminal 1 inside container)
```bash
ros2 launch armando_description armando_gazebo.launch.py
```

## 3. Launch the ArUco + Adapter + KDL IK Pipeline (Terminal 2 inside container)
Attach a second terminal on the host with `./docker_connect.sh`, then run:
```bash
source install/setup.bash
ros2 launch armando_controller aruco_kdl_pipeline.launch.py target_id:=10 offset_d:=0.15
```
`aruco_marker_publisher` publishes `/aruco_marker_publisher/markers`, `aruco_target_adapter` converts the selected marker pose (with offset `d`) into `/target_pose`, and `armando_ik_kdl_node` moves Armando to reach it.
