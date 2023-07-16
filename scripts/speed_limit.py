#!/usr/bin/env python3
import rospy
from std_msgs.msg import Int32
from time import sleep

velocity_pub = rospy.Publisher('/speed_limit', Int32, queue_size=10)

rospy.init_node('speed_limit', anonymous=False)

#speed=rospy.get_param('~speed')
SPEED = 3

while not rospy.is_shutdown():
    data=Int32()
    data.data=SPEED
    if type(SPEED) is int:
       velocity_pub.publish(data)
    sleep(0.05)
