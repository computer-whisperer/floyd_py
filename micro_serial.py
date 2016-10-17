import serial
import Adafruit_BBIO.UART as UART
import Adafruit_BBIO.GPIO as GPIO
import time


class MicroSerial:

    cmds = {
        "set speed": 1,
        "set pos": 2,
        "set pos 8bit": 3,
        "set pos abs": 4
        }

    def __init__(self, Beagle_UART="UART4", port="ttyO4", address=1, reset_pin="P8_8"):
        """
            Beagle_UART - UART0, UART1 or UART2 on BeagleBone Black to use
            port        - /dev/ttyXX device to connect to
            address     - address of Sabertooth controller to send commands to

        """
        self.UART = Beagle_UART
        self.port = port
        self.address = address
        self.reset_pin = reset_pin

        # Setup UART on BeagleBone (loads device tree overlay)
        UART.setup(self.UART)

        # Initialiase serial port
        self.serial = serial.Serial()
        self.serial.baudrate = 9600
        self.serial.port = '/dev/%s' % (self.port)
        self.serial.open()

        GPIO.setup(reset_pin, GPIO.OUT)
        GPIO.output(reset_pin, False)
        time.sleep(1)
        GPIO.output(reset_pin, True)

    def set_reset(self, value):
        GPIO.output(self.reset_pin, not value)


    def _send_commmand(self, command, servo_num, message, data_bytes=1):
        """
            Sends a packetised serial command to the Sabertooth controller
            valid commands are (as strings):
                fwd_left, fwd_right, rev_left, rev_right, ramp
            message - speed to send with command 0-100 in % percent
        """

        if data_bytes > 1:
            byte_message = max(message - 128, 0).to_bytes(1, byteorder='little') + (message//128).to_bytes(1, byteorder='little')
        else:
            byte_message = message.to_bytes(1, 'little')
        components = [self.address, command, servo_num, message]

        #data = (128).to_bytes(1, byteorder='little') + self.address.to_bytes(1, byteorder='little') + command.to_bytes(1, byteorder='little') + servo_num.to_bytes(1, 'little') + message.to_bytes(1, 'little')#+ servo_num.to_bytes(1, byteorder='little') + byte_message
        data = (128).to_bytes(1, 'little')
        for comp in components:
            data += comp.to_bytes(1, 'little')
        #print(data)
        #print(byte_message)
        #print(bytearray(data))
        #exit()
        self.serial.write(data)
        self.serial.flush()
        return data

    def set(self, values):
        for i in range(len(values)):
            value = int((values[i] + 1) * 63)
            result = self._send_commmand(self.cmds["set pos"], i, value, data_bytes=1)
