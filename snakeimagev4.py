import serial
import serial.tools.list_ports
import pygame
from threading import Timer

def get_arduino_port():
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        print(p)
        if "arduino" in p.description.lower():
            print("This is an Arduino: ", p.name)
            return p.name
    raise Exception("Arduino not found")

def read_serial(arduino):
    if arduino.in_waiting:
        data = arduino.readline().decode('utf-8').rstrip()
        return data if data != None else None
    return None

def show_image(game_display, image):
    game_display.blit(image, (0, 0))
    pygame.display.update()

def set_neutral_image(game_display, neutral_snake_image, state):
    state["image_state"] = "neutral snake"
    # show_image(game_display, neutral_snake_image)
    print("neutral timer went off")
    state["neutral_timer_counting"] = False

def main():
    selected_port = get_arduino_port()
    arduino = serial.Serial(port=selected_port, baudrate=9600)

    pygame.init()
    window_width, window_height = 640, 480
    game_display = pygame.display.set_mode((window_width, window_height))

    blue_snake_image = pygame.image.load('1.jpg')
    white_snake_image = pygame.image.load('2.jpg')
    neutral_snake_image = pygame.image.load('3.jpg')

    button_states = [0, 0]
    state = {
        "image_state": "neutral snake",
        "neutral_timer": None,
        "neutral_timer_counting": False
    }

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        detected_serial_message = read_serial(arduino)
        if detected_serial_message:
            button_changed, changed_button_state = detected_serial_message.split(":")
            changed_button_state = int(changed_button_state)

            if button_changed == "switch1":
                button_states[0] = changed_button_state
                if changed_button_state == 1:
                    state["image_state"] = "blue snake"
                else:
                    state["image_state"] = "white snake" if button_states[1] == 1 else "blue snake"

            elif button_changed == "switch2":
                button_states[1] = changed_button_state
                if changed_button_state == 1:
                    state["image_state"] = "white snake"
                else:
                    state["image_state"] = "blue snake" if button_states[0] == 1 else "white snake"

            # Cancel any existing timer if the state is not neutral
            if state["neutral_timer_counting"] and state["image_state"] != "neutral snake":
                state["neutral_timer"].cancel()
                state["neutral_timer_counting"] = False

            # Start a 3-second timer to change to the neutral image if both switches are off
            if button_states == [0,0] and not state["neutral_timer_counting"]:
                state["neutral_timer"] = Timer(1, set_neutral_image, [game_display, neutral_snake_image, state])
                state["neutral_timer"].start()
                state["neutral_timer_counting"] = True
        
            print(button_states)

        # Show the corresponding image based on the current state
        if state["image_state"] == "neutral snake":
            show_image(game_display, neutral_snake_image)
        elif state["image_state"] == "blue snake":
            show_image(game_display, blue_snake_image)
        elif state["image_state"] == "white snake":
            show_image(game_display, white_snake_image)

    pygame.quit()

if __name__ == "__main__":
    main()
