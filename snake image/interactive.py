# BRAINY BODIES SNAKE IMAGE INTERACTIVE
# Oliver Norred, 2024
# olivernorred@gmail.com

import serial
import serial.tools.list_ports
import pygame
import psutil
import os
import sys
from threading import Timer

# quits program if there is an instance already running. Useful for the auto start process, which runs the script every 1 minute.
def check_if_already_running():
    current_process = psutil.Process(os.getpid())
    script_name = os.path.basename(__file__)
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if(
                proc.info['pid'] != current_process.pid and
                'python' in proc.info['name'].lower() and
                script_name in proc.info['cmdline']
            ):
                print("Another instance of this script is already running. Exiting.")
                sys.exit()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
# call this method immediately
check_if_already_running()

# This method finds which port the arduino is plugged into, so it can be plugged into any port
def get_arduino_port():
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        print(p, p.device)
        if "arduino" in p.description.lower() or "usb" in p.description.lower() or "ch340" in p.description.lower() or "acm0" in p.description.lower():
            print("This is an Arduino: ", p.device)
            return p.device
    raise Exception("Arduino not found")

# A method to return the serial message sent by the arduino
def read_serial(arduino):
    if arduino.in_waiting:
        data = arduino.readline().decode('utf-8').rstrip()
        return data if data != None else None
    return None

# A method to "blit" an image and update the pygame screen
def show_image(game_display, image):
    game_display.blit(image, (0, 0))  # "blit" is a term that comes from an old computer graphics operation called BitBLT
    pygame.display.update()

def set_neutral_image(game_display, neutral_snake_image, state):
    # "neutral snake" is case-sensitive and space-sensitive. Probably not the best programming practice, but it reads clearly.
    state["image_state"] = "neutral snake"
    # show_image(game_display, neutral_snake_image)
    print("neutral timer went off")
    state["neutral_timer_counting"] = False

def main():
    # find the port the arduino is plugged into
    selected_port = get_arduino_port()
    arduino = serial.Serial(port=selected_port, baudrate=9600)

    # initialize pygame
    pygame.init()
    window_width, window_height = 640, 480
    game_display = pygame.display.set_mode((window_width, window_height), flags=pygame.FULLSCREEN)
    pygame.mouse.set_visible(False)

    # Load up the image files
    blue_snake_image = pygame.image.load('/home/pi/Desktop/interactive/1.jpg')
    white_snake_image = pygame.image.load('/home/pi/Desktop/interactive/2.jpg')
    neutral_snake_image = pygame.image.load('/home/pi/Desktop/interactive/3.jpg')

    # initialize the button states (neither pressed)
    button_states = [0, 0]
    # initialize the state machine for the back-to-neutral-image timer
    state = {
        "image_state": "neutral snake",
        "neutral_timer": None,
        "neutral_timer_counting": False
    }

    # infinite loop codeblock
    running = True
    while running:
        # quit on ESC
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # if button pressed or unpressed (therefore serial message sent)...
        detected_serial_message = read_serial(arduino)
        if detected_serial_message:
            # ... set button_changed to the first part of the serial message, and set the new button state to the second part of the serial message.
            button_changed, changed_button_state = detected_serial_message.split(":")
            changed_button_state = int(changed_button_state)
            # if the first button was changed (pressed or unpressed)
            if button_changed == "switch1":
                # update button_states
                button_states[0] = changed_button_state
                # if pressed, change image state to "blue snake"
                if changed_button_state == 1:
                    state["image_state"] = "blue snake"
                # if released, change image state to "white snake" if second button is pressed
                else:
                    state["image_state"] = "white snake" if button_states[1] == 1 else "blue snake"
            
            # if the second button was changed (pressed or unpressed)
            elif button_changed == "switch2":
                # update button_states
                button_states[1] = changed_button_state
                # if pressed, change image state to "white snake"
                if changed_button_state == 1:
                    state["image_state"] = "white snake"
                # if released, change image state to "blue snake" if first button is pressed
                else:
                    state["image_state"] = "blue snake" if button_states[0] == 1 else "white snake"

            # Setting up the back-to-neutral countdown timer (currently set to 0 seconds)
            # This functionality exists for if it is decided that this interactive should be more accessible for those who cannot hold a button down long enough or steadily enough to use it.
            
            # 1. Cancel any existing timer if the state is not neutral
            if state["neutral_timer_counting"] and state["image_state"] != "neutral snake":
                state["neutral_timer"].cancel()
                state["neutral_timer_counting"] = False

            # 2. Start a 0-second timer to change to the neutral image if both switches are off
            if button_states == [0,0] and not state["neutral_timer_counting"]:
                state["neutral_timer"] = Timer(1, set_neutral_image, [game_display, neutral_snake_image, state])
                state["neutral_timer"].start()
                state["neutral_timer_counting"] = True
        
            print(button_states)
        
        # Show the corresponding image based on the current image_state string value
        if state["image_state"] == "neutral snake":
            show_image(game_display, neutral_snake_image)
        elif state["image_state"] == "blue snake":
            show_image(game_display, blue_snake_image)
        elif state["image_state"] == "white snake":
            show_image(game_display, white_snake_image)

    # quit if `running` is false
    pygame.quit()

if __name__ == "__main__":
    main()
