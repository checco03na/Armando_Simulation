from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    controller_share = FindPackageShare("armando_controller")

    target_id_arg = DeclareLaunchArgument("target_id", default_value="10")
    offset_d_arg = DeclareLaunchArgument("offset_d", default_value="0.15")
    marker_size_arg = DeclareLaunchArgument("marker_size", default_value="0.10")
    reference_frame_arg = DeclareLaunchArgument("reference_frame", default_value="base_link")
    camera_frame_arg = DeclareLaunchArgument("camera_frame", default_value="camera_optical_frame")
    image_topic_arg = DeclareLaunchArgument("image_topic", default_value="/camera/image_raw")
    camera_info_topic_arg = DeclareLaunchArgument("camera_info_topic", default_value="/camera/camera_info")
    markers_topic_arg = DeclareLaunchArgument("markers_topic", default_value="/aruco_marker_publisher/markers")
    target_pose_topic_arg = DeclareLaunchArgument("target_pose_topic", default_value="/target_pose")
    use_sim_time_arg = DeclareLaunchArgument("use_sim_time", default_value="true")

    aruco_marker_publisher = Node(
        package="aruco_ros",
        executable="marker_publisher",
        name="aruco_marker_publisher",
        parameters=[
            {
                "marker_size": LaunchConfiguration("marker_size"),
                "reference_frame": LaunchConfiguration("reference_frame"),
                "camera_frame": LaunchConfiguration("camera_frame"),
                "image_is_rectified": True,
                "use_sim_time": LaunchConfiguration("use_sim_time"),
            }
        ],
        remappings=[
            ("/camera_info", LaunchConfiguration("camera_info_topic")),
            ("/image", LaunchConfiguration("image_topic")),
        ],
        output="screen",
    )

    aruco_target_adapter = Node(
        package="armando_controller",
        executable="aruco_target_adapter",
        name="aruco_target_adapter",
        parameters=[
            {
                "target_id": LaunchConfiguration("target_id"),
                "offset_d": LaunchConfiguration("offset_d"),
                "markers_topic": LaunchConfiguration("markers_topic"),
                "target_pose_topic": LaunchConfiguration("target_pose_topic"),
                "use_sim_time": LaunchConfiguration("use_sim_time"),
            }
        ],
        output="screen",
    )

    kdl_ik_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([controller_share, "launch", "armando_ik_kdl.launch.py"])
        ),
        launch_arguments={
            "target_pose_topic": LaunchConfiguration("target_pose_topic"),
            "use_sim_time": LaunchConfiguration("use_sim_time"),
        }.items(),
    )

    return LaunchDescription(
        [
            target_id_arg,
            offset_d_arg,
            marker_size_arg,
            reference_frame_arg,
            camera_frame_arg,
            image_topic_arg,
            camera_info_topic_arg,
            markers_topic_arg,
            target_pose_topic_arg,
            use_sim_time_arg,
            aruco_marker_publisher,
            aruco_target_adapter,
            kdl_ik_launch,
        ]
    )
