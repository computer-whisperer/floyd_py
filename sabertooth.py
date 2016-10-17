import serial
import logging
import Adafruit_BBIO.UART as UART

class Sabertooth():

    cmds = {
            "fwd_left": 0x00,
            "rev_left": 0x01,
            "fwd_right": 0x04,
            "rev_right": 0x05,
            "ramp": 0x10
            }

    def __init__(self, Beagle_UART="UART1", port="ttyO1", address=128):
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
        self.serial = serial.Serial()
        self.serial.baudrate = 9600
        self.serial.port = '/dev/%s' % (self.port)
        self.serial.open()

    def _send_command(self, command, message):
        chk_dat = self.address + command + message
        checksum = bytearray([a & b for a, b in zip(chk_dat.to_bytes(2, byteorder='little'), (127).to_bytes(1, byteorder='little'))][0:8])
        data = self.address.to_bytes(1, byteorder='little') + command.to_bytes(1, byteorder='little') + message.to_bytes(1, byteorder='little') + checksum
        self.serial.write(data)
        self.serial.flush()

    def set(self, motor, value):
        value = max(-1, min(value, 1))
        dir = "fwd" if value > 0 else "rev"
        power = abs(value) * 127
        self._send_command(self.cmds[dir + "_" + motor], int(power))

    def setRamp(self, value):
        """
            Set acceleration ramp for controller
            value - ramp value to use
               1-10: Fast Ramp
              11-20: Slow Ramp
              21-80: Intermediate Ramp
        """
        if 0 < value < 81:
            self._send_command(self.cmds["ramp"], value)
