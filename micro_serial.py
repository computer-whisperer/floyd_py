import serial
import Adafruit_BBIO.UART as UART


class MicroSerial:

    cmds = {
        "set speed": 1,
        "set pos": 2,
        "set pos abs": 4
        }

    def __init__(self, Beagle_UART="UART3", port="ttyO4", address=1):
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
        self.isOpen = self.serial.isOpen()

    def _send_commmand(self, command, servo_num, message, data_bytes=1):
        """
            Sends a packetised serial command to the Sabertooth controller
            valid commands are (as strings):
                fwd_left, fwd_right, rev_left, rev_right, ramp
            message - speed to send with command 0-100 in % percent
        """

        if data_bytes > 1:
            data = (message - 128).to_bytes(1, byteorder='little') + (message//128).to_bytes(1, byteorder='little')
        else:
            data = message.to_bytes(1, byteorder='little')
        data = (128).to_bytes(1, byteorder='little') + self.address.to_bytes(1, byteorder='little') + command.to_bytes(1, byteorder='little') + servo_num.to_bytes(1, byteorder='little') + data
        self.serial.write(data)
        self.serial.flush()

    def set(self, values):
        for i in range(len(values)):
            value = max(0, min(values[i], 1)) * 127
            self._send_commmand(self.cmds["set pos abs"], i, value)
