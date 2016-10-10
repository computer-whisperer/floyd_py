from sabertooth import Sabertooth
from pololu import Pololu
from micro_serial import MicroSerial
import Adafruit_BBIO.GPIO as GPIO
import simplestreamer
import time

streamer = simplestreamer.SimpleStreamer(5201)
streamer.subscribe("192.168.7.1", 5200, "surface", updates_per_sec=20)

controller_1 = Sabertooth(address=128)
controller_2 = Sabertooth(address=129)
vert_controller_1 = Pololu(address=13)
vert_controller_2 = Pololu(address=14)
panopticon_servo = MicroSerial(address=1)
claw_close_io = "P8_17"
claw_open_io = "P8_18"
GPIO.setup(claw_close_io, GPIO.OUT)
GPIO.setup(claw_open_io, GPIO.OUT)

trim = 0
claw_closed = False
toggle_time = time.time()
last_trigger = False
pan_state = [0.5, 0.5, 0.5]

last_time = time.time()
while True:
    # Time delta calculations
    curr_time = time.time()
    dt = curr_time - last_time
    last_time = curr_time

    # Control signals in
    data = streamer.get_data("surface")
    axes = data.get("axes", [0, 0, 0])
    axes = [abs(v)*v for v in axes]
    buttons = data.get("buttons", [0 for _ in range(20)])
    povs = data.get("povs", [(0, 0)])

    # Quit?
    if buttons[6]:
        controller_1.set("left", 0)
        controller_1.set("right", 0)
        controller_2.set("left", 0)
        controller_2.set("right", 0)
        vert_controller_1.set(0)
        vert_controller_2.set(0)
        panopticon_servo.set([0, 0, 0])
        quit()

    # Trim
    if buttons[5]: # Up trim
        trim += 0.2 * dt
    elif buttons[3]: # Down trim
        trim -= 0.2 * dt

    # Drive
    trans_vector = [-axes[0], axes[1], 0]
    rot_value = axes[2]
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

    # Panopticon
    x, y = povs[0]
    pan_state[0] = max(0, min(pan_state[0] + x*dt*0.2, 1))
    pan_state[1] = max(0, min(pan_state[1] + y*dt*0.2, 1))
    panopticon_servo.set(pan_state)

    # CLAW
    trigger = buttons[0]
    if trigger and not last_trigger:
        claw_closed = not claw_closed
        toggle_time = curr_time
    last_trigger = trigger

    if curr_time - toggle_time > 1:
        GPIO.output(claw_close_io, claw_closed)
        GPIO.output(claw_open_io, not claw_closed)
    else:
        GPIO.output(claw_open_io, False)
        GPIO.output(claw_close_io, False)

    time.sleep(0.05)

