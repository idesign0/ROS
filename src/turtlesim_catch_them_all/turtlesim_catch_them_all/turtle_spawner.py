#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from random import uniform
from turtlesim.srv import Spawn
from turtlesim.srv import Kill
from my_robot_interfaces.msg import Turtle
from my_robot_interfaces.msg import TurtleArray
from functools import partial
 
class turtle_spawner(Node):
    def __init__(self):
        super().__init__("turtle_spawner")
        self.aliveTurtles = TurtleArray()
        self.pub_turtleList = self.create_publisher(TurtleArray,"alive_turtles",10)
        timer_1 = self.create_timer(0.5,self.call_spawn_srv)
        timer_2 = self.create_timer(1,self.call_kill_srv)

    def call_spawn_srv(self):

        x = uniform(0,11)
        y = uniform(0,11)
        thta = uniform(0,1)

        new_turtle_client = self.create_client(Spawn,"/spawn")

        while(not new_turtle_client.wait_for_service(1.0)):
            self.get_logger().warn("Waiting for Service: Spawn to start..")
        
        request = Spawn.Request()
        request.x = x
        request.y = y
        request.theta = thta
    
        future = new_turtle_client.call_async(request)
        future.add_done_callback(partial(self.callback_add_turtles,request = request))

    def callback_add_turtles(self,future,request):
        try:
            request.name = future.result().name
            turtle = Turtle()
            turtle.x = request.x
            turtle.y = request.y
            turtle.theta = request.theta
            turtle.name = request.name

            self.aliveTurtles.turtlearray.append(turtle)
            self.pub_turtleList.publish(self.aliveTurtles)

        except Exception as e:
            self.get_logger().error("Service call Failed %r" %(e,))

    def call_kill_srv(self):

        if not self.aliveTurtles or len(self.aliveTurtles.turtlearray) == 0:
            self.get_logger().warning("No turtles in the array.")
            return

        kill_turtle_client = self.create_client(Kill,"/kill")
        
        while(not kill_turtle_client.wait_for_service(1.0)):
            self.get_logger().warn("Waiting for Service: Kill to start..")
        
        request = Kill.Request()
        request.name = self.aliveTurtles.turtlearray[0].name
        future = kill_turtle_client.call_async(request)

        self.aliveTurtles.turtlearray = self.aliveTurtles.turtlearray[1:]

def main(args=None):
    rclpy.init(args=args)
    node = turtle_spawner()
    rclpy.spin(node)
    rclpy.shutdown()
 
 
if __name__ == "__main__":
    main()
