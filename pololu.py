try:
    import serial
    import logging
    import Adafruit_BBIO.UART as UART

    #https://github.com/tdack/BBB-Bot/blob/master/server/Sabertooth/Sabertooth.py

    class Pololu():

        cmds = {
                "fwd": 10,
                "rev": 9,
                }

        def __init__(self, Beagle_UART="UART2", port="ttyO2", address=13):
            """
                Beagle_UART - UART0, UART1 or UART2 on BeagleBone Black to use
                port        - /dev/ttyXX device to connect to
                address     - address of Sabertooth controller to send commands to

            """
            self.UART = Beagle_UART
            self.port = port
            self.address = address

            # Setup UART on BeagleBone (loads device tree overlay)
            UART.setup(self.UART)

            # Initialiase serial port
            self.pololu = serial.Serial()
            self.pololu.baudrate = 9600
            self.pololu.port = '/dev/%s' % (self.port)
            self.pololu.open()
            self.isOpen = self.pololu.isOpen()

        def __del__(self):
            self.stop()
            return

        def sendCommand(self, command, message):
            """
                Sends a packetised serial command to the Sabertooth controller
                valid commands are (as strings):
                    fwd_left, fwd_right, rev_left, rev_right, ramp
                message - speed to send with command 0-100 in % percent
            """
            data = (170).to_bytes(1, byteorder='little') + self.address.to_bytes(1, byteorder='little') + command.to_bytes(1, byteorder='little') + message.to_bytes(1, byteorder='little')
            sentBytes = self.pololu.write(data)
            self.pololu.flush()
            return sentBytes

        def driveMotor(self, direction="fwd", speed=0):
            """
                Simple motor control
                motor     - "left", "right" or "both"
                direction - "fwd" or "rev"
                speed     - 0 to 100 in percent
            """


            if  speed < 0:
                speed = 0
            elif speed > 100:
                speed = 100

            speed = int((float(speed)* 127)//100)
            self.sendCommand(self.cmds[direction], speed)

        def set(self, value):
            value = max(-1, min(value, 1))
            dir = "fwd" if value > 0 else "rev"
            power = abs(value) * 100
            self.driveMotor(dir, power)

        def stop(self):
            """
                Stops both motors
            """
            sentBytes = 0
            sentBytes = self.driveMotor("fwd", 0)
            return sentBytes

        def setRamp(self, value):
            """
                Set acceleration ramp for controller
                value - ramp value to use
                   1-10: Fast Ramp
                  11-20: Slow Ramp
                  21-80: Intermediate Ramp
            """
            sentBytes = 0
            if (value > 0 and value < 81):
                sentBytes = self.sendCommand(self.cmds["ramp"], value)
            return sentBytes
except ImportError:
    print("WARNING: Using fake sabertooth!")
    class Pololu():

        def __init__(self, Beagle_UART="UART1", port="/dev/ttyO1", address=128):
            pass

        def driveMotor(self, motor="both", direction="fwd", speed=0):
            """
                Simple motor control
                motor     - "left", "right" or "both"
                direction - "fwd" or "rev"
                speed     - 0 to 100 in percent
            """
            pass

        def stop(self):
            pass

        def set(self, motor, value):
            pass