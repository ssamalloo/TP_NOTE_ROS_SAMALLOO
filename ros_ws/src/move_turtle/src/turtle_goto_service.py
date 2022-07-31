#!/usr/bin/env python3
import rospy
from turtlesim.msg import Pose
from geometry_msgs.msg import Twist
from math import pow, atan2, sqrt, pi


class Waypoint:

    def __init__(self):

        self.__pose_sub = rospy.Subscriber('/turtle1/pose', Pose,
                                           self.pose_callback)
        self.__turtle_vel_pub = rospy.Publisher('/turtle1/cmd_vel',
                                                Twist, queue_size=10)
        self.__teleport_abs = rospy.ServiceProxy('/turtle1/teleport_absolute',
                                                 TeleportAbsolute)
        self.__set_pen = rospy.ServiceProxy('/turtle1/set_pen', SetPen)


        self.__rate = rospy.Rate(10)
        self.__pose = Pose()
        self.__counter = 0  

        # Parameters:
        self.__waypoints = rospy.get_param('waypoints')

    def euclidean_distance(self, goal_pose):
      
        return sqrt(pow((goal_pose.x - self.__pose.x), 2) +
                    pow((goal_pose.y - self.__pose.y), 2))

    def linear_vel(self, goal_pose, constant=1):
       return constant * self.euclidean_distance(goal_pose)

    def steering_angle(self, goal_pose):

        return atan2(goal_pose.y - self.__pose.y, goal_pose.x - self.__pose.x)

    def angular_vel(self, goal_pose, constant=11):

        return constant * (self.steering_angle(goal_pose) - self.__pose.theta)


    def go_to_goal_waypoints(self):
          self.__set_pen(off=1)
          self.__teleport_abs(x=self.__waypoints[0][0], y=self.__waypoints[0][1],
                            theta=0)
          rospy.loginfo("%d %d", self.__waypoints[0][0],self.__waypoints[0][1])
          self.__set_pen(r=255, g=0, b=0, width=2)
          self.__set_pen(off=0)
          self.__set_pen(r=255, g=0, b=0, width=2)
          goal_pose = Pose()
          #Enter tolerance value less than 1 slightly greater than zero eg: 0.5
          distance_tolerance = float(input("Set your tolerance: "))
          vel_msg = Twist()
          for waypoint in self.__waypoints:
           goal_pose.x=self.__waypoints[self.__counter][0]
           goal_pose.y=self.__waypoints[self.__counter][1]
           self.__counter += 1
           rospy.loginfo("%d %d",goal_pose.x, goal_pose.y)
           
           while self.euclidean_distance(goal_pose) >= distance_tolerance:
                    
            vel_msg.linear.x = self.linear_vel(goal_pose)
            vel_msg.linear.y = 0
            vel_msg.linear.z = 0

            # Angular velocity in the z-axis.
            vel_msg.angular.x = 0
            vel_msg.angular.y = 0
            vel_msg.angular.z = self.angular_vel(goal_pose)
            # Publishing our vel_msg
            self.__turtle_vel_pub.publish(vel_msg)

            # Publish at the desired rate.
            self.__rate.sleep()
                 
          rospy.spin()



def main():
    rospy.init_node('waypoint')
    my_waypoint = Waypoint()
    my_waypoint.go_to_goal_waypoints()
    rospy.spin()


if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass
