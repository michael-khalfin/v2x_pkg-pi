#!/usr/bin/env python3

import rospy
import pymysql
import sys
from datetime import datetime

#sys.path.insert(0, '/home/catkin_ws/src/tpn_pkg') 
from tpn_pkg.msg import Position
from yolov8ros_pkg.msg import BBoxes

rospy.init_node('v2x', anonymous=True)

#conn = pymysql.connect(db='example', user='root', password='teach', host='localhost')
#c = conn.cursor()

count = 0

def callback1(msg):
    conn = pymysql.connect(db='example', user='root', password='teach', host='localhost')
    c = conn.cursor()

    values = (msg.lat, msg.lon, msg.heading, msg.velocity, msg.angZ)

    sql_check = "SELECT COUNT(*) FROM `Client Vehicle Table` WHERE `index`=1"
    c.execute(sql_check)
    row_count = c.fetchone()[0]
    if row_count > 0:
        sql_update = """
            UPDATE `Client Vehicle Table`
            SET latitude = %s, longitude = %s, heading = %s, speed = %s, angular_z = %s
            WHERE `index` = 1
        """
        c.execute(sql_update, values)
    else:
        sql_insert = """
            INSERT INTO `Client Vehicle Table` (`index`, latitude, longitude, heading, speed, angular_z)
            VALUES (1, %s, %s, %s, %s, %s)
        """
        c.execute(sql_insert, values)
    conn.commit()

def callback2(msg):
    conn = pymysql.connect(db='example', user='root', password='teach', host='localhost')
    c = conn.cursor()
    values = (msg.lat, msg.lon, msg.heading, msg.velocity, msg.angZ)

    sql_check = "SELECT COUNT(*) FROM `Client Vehicle Table` WHERE `index`=2"
    c.execute(sql_check)
    row_count = c.fetchone()[0]
    if row_count > 0:
        sql_update = """
            UPDATE `Client Vehicle Table`
            SET latitude = %s, longitude = %s, heading = %s, speed = %s, angular_z = %s
            WHERE `index` = 2
        """
        c.execute(sql_update, values)
    else:
        sql_insert = """
            INSERT INTO `Client Vehicle Table` (`index`, latitude, longitude, heading, speed, angular_z)
            VALUES (2, %s, %s, %s, %s, %s)
        """
        c.execute(sql_insert, values)
    conn.commit()

def cone_callback1(msg):
    conn = pymysql.connect(db='example', user='root', password='teach', host='localhost')
    c = conn.cursor()
    global count
    if not msg.boxes or msg.boxes[0].confidence <= .5:
        return
    if count >= 5:
        sql_lat = "SELECT latitude FROM `Client Vehicle Table` WHERE `index`=1"
        c.execute(sql_lat)
        result = c.fetchone()
        if result:
            lat = result[0]
        sql_lon = "SELECT longitude FROM `Client Vehicle Table` WHERE `index`=1"
        c.execute(sql_lon)
        result = c.fetchone()
        if result:
            lon = result[0]
    
        time = datetime.now().strftime("%H:%M:%S")
        values = (lat, lon, "Cone", time) 
        sql_insert = """
            INSERT INTO `Identified Objects Table` (latitude, longitude, type, time)
            VALUES (%s, %s, %s, %s)
        """
        c.execute(sql_insert, values)

        conn.commit()
        count = 0
    else:
        count += 1
    check_size()

def cone_callback2(msg):
    conn = pymysql.connect(db='example', user='root', password='teach', host='localhost')
    c = conn.cursor()
    global count
    if not msg.boxes or msg.boxes[0].confidence <= .5:
        return
    if count >= 5:
        sql_lat = "SELECT latitude FROM `Client Vehicle Table` WHERE `index`=2"
        c.execute(sql_lat)
        result = c.fetchone()
        if result:
            lat = result[0]
        sql_lon = "SELECT longitude FROM `Client Vehicle Table` WHERE `index`=2"
        c.execute(sql_lon)
        result = c.fetchone()
        if result:
            lon = result[0]
    
        time = datetime.now().strftime("%H:%M:%S")
        values = (lat, lon, "Cone", time) 
        sql_insert = """
            INSERT INTO `Identified Objects Table` (latitude, longitude, type, time)
            VALUES (%s, %s, %s, %s)
        """
        c.execute(sql_insert, values)

        conn.commit()
        count = 0
    else:
        count += 1
    check_size()

def check_size():
    conn = pymysql.connect(db='example', user='root', password='teach', host='localhost')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM `Identified Objects Table`")
    row_count = c.fetchone()[0]

    if row_count > 20:
        rows_to_delete = row_count - 20
        delete_query = f"DELETE FROM `Identified Objects Table` ORDER BY `index` LIMIT {rows_to_delete}"
        c.execute(delete_query)
        conn.commit()

while not rospy.is_shutdown():
    rospy.Subscriber('/actor1/tpn_node/gps_chatter', Position, callback1)
    rospy.Subscriber('/actor2/tpn_node/gps_chatter', Position, callback2)
    rospy.Subscriber('/actor1/predictions', BBoxes, cone_callback1)
    rospy.Subscriber('/actor2/predictions', BBoxes, cone_callback2)
    rospy.spin()
