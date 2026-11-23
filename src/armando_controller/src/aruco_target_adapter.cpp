#include <cmath>
#include <memory>
#include <string>

#include "aruco_msgs/msg/marker_array.hpp"
#include "geometry_msgs/msg/pose_stamped.hpp"
#include "rclcpp/rclcpp.hpp"
#include "tf2/LinearMath/Quaternion.h"
#include "tf2/LinearMath/Transform.h"
#include "tf2/LinearMath/Vector3.h"
#include "tf2_geometry_msgs/tf2_geometry_msgs.hpp"

class ArucoTargetAdapter : public rclcpp::Node
{
public:
  ArucoTargetAdapter()
  : Node("aruco_target_adapter")
  {
    declare_parameter<int>("target_id", 10);
    declare_parameter<double>("offset_d", 0.15);
    declare_parameter<std::string>("markers_topic", "/aruco_marker_publisher/markers");
    declare_parameter<std::string>("target_pose_topic", "/target_pose");

    target_id_ = get_parameter("target_id").as_int();
    offset_d_ = get_parameter("offset_d").as_double();
    const std::string markers_topic = get_parameter("markers_topic").as_string();
    const std::string target_pose_topic = get_parameter("target_pose_topic").as_string();

    target_pub_ = create_publisher<geometry_msgs::msg::PoseStamped>(target_pose_topic, 10);
    markers_sub_ = create_subscription<aruco_msgs::msg::MarkerArray>(
      markers_topic, rclcpp::QoS(10),
      std::bind(&ArucoTargetAdapter::markers_callback, this, std::placeholders::_1));

    RCLCPP_INFO(
      get_logger(),
      "ArucoTargetAdapter ready (target_id: %d, offset_d: %.3f m, %s -> %s).",
      target_id_, offset_d_, markers_topic.c_str(), target_pose_topic.c_str());
  }

private:
  void markers_callback(const aruco_msgs::msg::MarkerArray::SharedPtr msg)
  {
    for (const auto & marker : msg->markers) {
      if (static_cast<int>(marker.id) != target_id_) {
        continue;
      }

      tf2::Transform t_marker;
      tf2::fromMsg(marker.pose.pose, t_marker);

      // Offset along marker +Z (towards camera), oriented so target +Z points at the marker
      tf2::Quaternion q_offset;
      q_offset.setRPY(M_PI, 0.0, 0.0);
      tf2::Transform t_offset(q_offset, tf2::Vector3(0.0, 0.0, offset_d_));

      tf2::Transform t_target = t_marker * t_offset;

      geometry_msgs::msg::PoseStamped target_pose;
      target_pose.header = marker.header;
      if (target_pose.header.frame_id.empty()) {
        target_pose.header.frame_id = msg->header.frame_id;
      }
      tf2::toMsg(t_target, target_pose.pose);

      target_pub_->publish(target_pose);
      return;
    }
  }

  int target_id_;
  double offset_d_;
  rclcpp::Publisher<geometry_msgs::msg::PoseStamped>::SharedPtr target_pub_;
  rclcpp::Subscription<aruco_msgs::msg::MarkerArray>::SharedPtr markers_sub_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<ArucoTargetAdapter>());
  rclcpp::shutdown();
  return 0;
}
