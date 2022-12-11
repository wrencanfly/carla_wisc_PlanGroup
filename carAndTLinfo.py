import glob
import os
import sys
try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass
import carla

import random
import time
import numpy as np
import math
import pandas as pd
VEH_NUM = 5
actor_list = []
df = pd.DataFrame()
def destroy():
    for actor in actor_list:
        actor.destroy()


try:
    # 0. Set the cilent and the world
    client = carla.Client('localhost', 2000) # https://carla.readthedocs.io/en/latest/core_world/#client-creation
    client.set_timeout(50.0)

    world = client.get_world()

    # 1. Spawn two example vehicles
    # Get the blueprint library
    blueprint_library = world.get_blueprint_library() # https://carla.readthedocs.io/en/latest/core_actors/#blueprints

    # Get all the spawn points
    spawn_points = world.get_map().get_spawn_points()
    # for i, spawn_point in enumerate(spawn_points):
    #     # Draw in the spectator window the spawn point index
    #     world.debug.draw_string(spawn_point.location, str(i), life_time=100)
    #     # We can also draw an arrow to see the orientation of the spawn point
    #     # (i.e. which way the vehicle will be facing when spawned)
    #     world.debug.draw_arrow(spawn_point.location, spawn_point.location + spawn_point.get_forward_vector(),
    #                            life_time=100)
    # Spawn the vehicles
    vehicle_1_bp = blueprint_library.filter('model3')[0]
    spawn_point_1 = spawn_points[0]
    vehicle_1 = world.spawn_actor(vehicle_1_bp, spawn_point_1)
    vehicle_1.set_autopilot(True)
    actor_list.append(vehicle_1)

    vehicle_2_bp = blueprint_library.filter('cybertruck')[0]
    # spawn_point_2 = spawn_points[1]
    spawn_point_2 = carla.Transform(spawn_point_1.location-carla.Location(x=6), spawn_point_1.rotation)
    vehicle_2 = world.spawn_actor(vehicle_2_bp, spawn_point_2)
    vehicle_2.set_autopilot(True)
    actor_list.append(vehicle_2)

    # for i in range(VEH_NUM):
    #     # Choose random blueprint and choose the i-th default spawn points
    #     vehicle_bp_i = random.choice(blueprint_library.filter('vehicle.*.*'))
    #     spawn_point_i = spawn_points[i]
    #
    #     # Spawn the actor
    #     vehicle_i = world.spawn_actor(vehicle_bp_i, spawn_point_i)
    #
    #     # Set control mode for v_i. https://carla.readthedocs.io/en/latest/python_api/#carla.Vehicle
    #     vehicle_i.set_autopilot(True)
    #
    #     # Append to the actor_list
    #     actor_list.append(vehicle_i)


    # 2. Set autopilot behavior.
    # Get the traffic manager.  https://carla.readthedocs.io/en/latest/python_api/#carla.TrafficManager.
    tm = client.get_trafficmanager(8000)

    # Set the autopilot behavior. https://carla.readthedocs.io/en/latest/adv_traffic_manager/#configuring-autopilot-behavior.
    # Set vehicle_1 as a general automated vehicle, which keeps at least 2 meters from other vehicles, and drives 20% faster than the current speed limit.
    current_veh = vehicle_1
    tm.distance_to_leading_vehicle(current_veh,2)
    tm.vehicle_percentage_speed_difference(current_veh,-20)

    # Set vehicle_2 as a dangerous vehicle, which ignores all traffic lights, keeps no safety distance from other vehicles, and drive 40% faster than the current speed limit.
    danger_car = vehicle_2
    tm.ignore_lights_percentage(danger_car,100)
    tm.distance_to_leading_vehicle(danger_car,0)
    tm.vehicle_percentage_speed_difference(danger_car,-40)


    # 3. Set the spectator.
    # Get the spectator. https://carla.readthedocs.io/en/latest/tuto_G_getting_started/#the-spectator
    spectator = world.get_spectator()
    last_red = time.time()
    last_red_update = True

    # Use the while loop to update the location and rotation of the spectator.
    while True:
        offset = 0
        # transform = vehicle_1.get_transform()
        #
        # loc = vehicle_1.get_location()
        # vel = vehicle_1.get_velocity()
        # acc = vehicle_1.get_acceleration()
        #
        # loc2 = vehicle_2.get_location()
        # vel2 = vehicle_2.get_velocity()
        # acc2 = vehicle_2.get_acceleration()
        #
        # vehicle_1_status = 'Vehicle_ID:{%s}, Location_X:{%.3f}, Location_Y:{%.3f}, \nVelocity_X:{%.3f}, Velocity_Y:{%.3f}, \nAcceleration_X:{%.3f}, Acceleration_Y:{%.3f}.' % (
        # i, loc.x, loc.y, vel.x, vel.y, acc.x, acc.y)
        #
        # vehicle_2_status = 'Vehicle_ID:{%s}, Location_X:{%.3f}, Location_Y:{%.3f}, \nVelocity_X:{%.3f}, Velocity_Y:{%.3f}, \nAcceleration_X:{%.3f}, Acceleration_Y:{%.3f}.' % (
        #     i, loc2.x, loc2.y, vel2.x, vel2.y, acc2.x, acc2.y)
        #
        # world.debug.draw_string(vehicle_1.get_location(), vehicle_1_status, draw_shadow = True,  color = carla.Color(255, 0, 0), life_time=0.03)
        # world.debug.draw_string(vehicle_2.get_location(), vehicle_2_status, draw_shadow=True,
        #                         color=carla.Color(255, 0, 0), life_time=0.03)

        transform = vehicle_1.get_transform()
        #for i in range(len(actor_list)):
        for vehicle_i in actor_list:
            # transform = vehicle_1.get_transform()
            loc_i = vehicle_i.get_location()
            vel_i = vehicle_i.get_velocity()
            acc_i = vehicle_i.get_acceleration()
            vehicle_i_status = 'Vehicle_ID:%s, Location_X: %.3f, Location_Y: %.3f, \nVelocity_X: %.3f, Velocity_Y: %.3f, \nAcceleration_X: %.3f, Acceleration_Y: %.3f.' % (
                actor_list.index(vehicle_i), loc_i.x, loc_i.y, vel_i.x, vel_i.y, acc_i.x, acc_i.y)
            world.debug.draw_string(vehicle_i.get_location(), vehicle_i_status, draw_shadow=True,
                                    color=carla.Color(255, 0, 0), life_time=0.03)

        for tl in world.get_actors().filter('traffic.traffic_light*'):
            curr_traffic_light_text = 'NONE'
            next_red = 0
            next_green = 0
            next_yellow = 0
            if tl.state is not None:
                if tl.state == carla.TrafficLightState.Green:
                    curr_traffic_light_text = 'GREEN'
                elif tl.state == carla.TrafficLightState.Yellow:
                    curr_traffic_light_text = 'YELLOW'
                else:
                    curr_traffic_light_text = 'RED'
            #next_red = tl.get_red_time()
            #next_red = tl.get_elapsed_time()
            if curr_traffic_light_text == 'GREEN':
                if last_red_update == True:
                    last_red = time.time()
                    last_red_update = False
                next_red = tl.get_green_time() + tl.get_yellow_time() - tl.get_elapsed_time()
                next_green = tl.get_green_time() +tl.get_yellow_time() + tl.get_red_time() - tl.get_elapsed_time()
                next_yellow =  tl.get_green_time() - tl.get_elapsed_time()
            if curr_traffic_light_text == 'YELLOW':
                if last_red_update == False:
                    last_red_update = True
                next_red = tl.get_yellow_time() - tl.get_elapsed_time()
                next_green = tl.get_yellow_time() +  tl.get_red_time() - tl.get_elapsed_time()
                next_yellow =  tl.get_green_time() +tl.get_yellow_time() + tl.get_red_time() - tl.get_elapsed_time()
            if curr_traffic_light_text == 'RED':
                curr_time = time.time()
                next_red = (tl.get_yellow_time() + tl.get_green_time() + tl.get_red_time() + tl.get_yellow_time() + tl.get_green_time()) - (curr_time - last_red)
                next_green = tl.get_yellow_time() + tl.get_green_time() + tl.get_red_time()  - (curr_time - last_red)
                next_yellow =  tl.get_yellow_time() + tl.get_green_time() + tl.get_red_time() +  tl.get_green_time() - (curr_time - last_red)


            tl_info = "Elapsed time: {:.2f}, Current status:{}, next red:{:.2f}, next green:{:.2f}, next yellow:{:.2f};".format(tl.get_elapsed_time(), curr_traffic_light_text, next_red, next_green, next_yellow)
            world.debug.draw_string(tl.get_location() + carla.Location(z=7,y=10), tl_info, draw_shadow=True,
                                    color=carla.Color(0, 0, 255), life_time=0.03)
            # current_df = pd.DataFrame([[curr_traffic_light_text, next_red, next_green, next_yellow]])
            # df.append(current_df, ignore_index=True)

        # Select one transform and uncomment the other one.
        # spectator transform 1: bird's-eye view
        spectator_location = transform.location + carla.Location(z=20)
        spectator_rotation = carla.Rotation(pitch=-70)

        # spectator transform 2: first-person view
        # spectator_location = transform.location + carla.Location(z=2)
        # spectator_rotation = carla.Rotation(pitch=0, yaw=transform.rotation.yaw)

        # Update the transform
        #spectator.set_transform(carla.Transform(spectator_location, spectator_rotation))
        time.sleep(0.02)

finally:
    print('destroying actors')
    # df.to_csv('tl_info.csv')
    destroy()
    print('done.')
