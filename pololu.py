import serial
import Adafruit_BBIO.UART as UART


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

    def _send_command(self, command, message):
        """
            Sends a packetised serial command to the Sabertooth controller
            valid commands are (as strings):
                fwd_left, fwd_right, rev_left, rev_right, ramp
            message - speed to send with command 0-100 in % percent
        """
        data = (170).to_bytes(1, byteorder='little') + self.address.to_bytes(1, byteorder='little') + command.to_bytes(1, byteorder='little') + message.to_bytes(1, byteorder='little')
        self.pololu.write(data)
        self.pololu.flush()

    def set(self, value):
        value = max(-1, min(value, 1))
        dir = "fwd" if value > 0 else "rev"
        power = abs(value) * 127
        self._send_command(self.cmds[dir], int(power))