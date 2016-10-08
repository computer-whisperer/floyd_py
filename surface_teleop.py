# just dumps time data into the streamer at 100 hz
import simplestreamer
import time
import pygame

pygame.init()

# Set the width and height of the screen [width,height]
size = [500, 700]
screen = pygame.display.set_mode(size)
screen.fill((255, 255, 255))

pygame.display.set_caption("My Game")

pygame.joystick.init()
joy1 = pygame.joystick.Joystick(0)
joy1.init()

# Used to manage how fast the screen updates
clock = pygame.time.Clock()



while True:
    axes = [joy1.get_axis(a) for a in range(3)]
    buttons = [joy1.get_button(a) for a in range(joy1.get_numbuttons())]
    streamer.send_data({"buttons": buttons, "axes": axes})
    print(axes)
    # Limit to 20 frames per second
    clock.tick(5)
