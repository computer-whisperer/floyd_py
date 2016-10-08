from sabertooth import Sabertooth
from pololu import Pololu
import simplestreamer
import time

streamer = simplestreamer.SimpleStreamer(5201)
streamer.subscribe("192.168.7.1", 5200, "surface", updates_per_sec=20)
#streamer.subscribe("127.0.0.1", 5200, "surface")

controller_1 = Sabertooth(address=128)
controller_2 = Sabertooth(address=129)
vert_controller_1 = Pololu(address=13)
vert_controller_2 = Pololu(address=14)

trim = 0
up_last = False
down_last = False

while True:
    data = streamer.get_data("surface")
    axes = data.get("axes", [0, 0, 0])
    axes = [abs(v)*v for v in axes]
    buttons = data.get("buttons", [0 for _ in range(20)])

    up_pressed = buttons[5]
    down_pressed = buttons[3]

    if up_pressed and not up_last:
        trim += 0.1
    elif down_pressed and not down_last:
        trim -= 0.1

    up_last = up_pressed
    down_last = down_pressed

    trans_vector = [-axes[0], axes[1], 0]
    rot_value = axes[2]

    if buttons[7]:
        quit()

    if buttons[4]:
        trans_vector[2] = -(axes[3]-1)/2
    elif buttons[2]:
        trans_vector[2] = (axes[3]-1)/2

    controller_1.set("left",   -trans_vector[0] + trans_vector[1] - rot_value)
    controller_1.set("right",  -trans_vector[0] + trans_vector[1] + rot_value)
    controller_2.set("left",   -trans_vector[0] - trans_vector[1] + rot_value)
    controller_2.set("right",  -trans_vector[0] - trans_vector[1] - rot_value)
    vert_controller_1.set(trans_vector[2] + trim)
    vert_controller_2.set(trans_vector[2] + trim)
    time.sleep(0.05)

