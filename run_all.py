from sabertooth import Sabertooth
import time

controller_1 = Sabertooth(address=128)

while True:
    time.sleep(0.1)
    controller_1.driveMotor("left", "fwd", 100)
