# BRAINY BODIES AUDIO INTERACTIVE
# Oliver Norred, 2024
# olivernorred@gmail.com

import serial
import serial.tools.list_ports
import pygame
import sys
import vlc
import time
import math
import os
import psutil

# quits program if there is an instance already running. Useful for the auto start process, which runs the script every 1 minute.
def check_if_already_running():
    current_process = psutil.Process(os.getpid())
    script_name = os.path.basename(__file__)
    for proc in psutil.process_iter(['pid','name','cmdline']):
        try:
            if(proc.info['pid'] != current_process.pid and 'python' in proc.info['name'].lower() and script_name in proc.info['cmdline']):
                print("Another instance of this script is already running. Exiting.")
                sys.exit()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
# call this method immediately
check_if_already_running()


# This method finds which port belongs to the arduino
def get_arduino_port():
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        print(p)
        if "arduino" in p.description.lower() or "ch340" in p.description.lower() or "usb" in p.description.lower():
            print("This is an Arduino: ", p.device)
            return p.device
    raise Exception("Arduino not found")

def read_serial(arduino):
    if arduino.in_waiting:
        data = arduino.readline().decode('utf-8').rstrip()
        return data if data != None else None
    return None

def write_serial(arduino, volumes):
    message = f"{volumes[0]},{volumes[1]},{volumes[2]},{volumes[3]}"
    print(message.encode('utf-8'))
    arduino.write(message.encode('utf-8'))
    arduino.write(b'\n')

# Initialize pygame
pygame.init()

# Set up display
screen_width, screen_height = 600, 400
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Audio Interactive")

# Set up fonts
font = pygame.font.SysFont(None, 24)

# Set up colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
GREEN = (0, 180, 0)

# Slider parameters
slider_x = 150
slider_y = [50, 120, 190, 260]

# Reset button parameters
button_width = 250
button_height = 50
button_x = (screen_width - button_width) // 2
button_y = 320
button_color = GREEN

# Set initial volumes for the 4 channels (0.5 for 50%)
volumes = [0.5, 0.5, 0.5, 0.5]

# Method to draw sliders (for when connecting a display for testing)
def draw_slider(screen, x, y, volume):
    pygame.draw.rect(screen, GRAY, (x, y, 300, 20))
    pygame.draw.rect(screen, BLACK, (x, y, int(volume * 300), 20))

# Method to draw reset button (for when connecting a display for testing)
def draw_button(screen, text, x, y, w, h, color):
    pygame.draw.rect(screen, color, (x, y, w, h))
    text_surface = font.render(text, True, WHITE)
    screen.blit(text_surface, (x + (w - text_surface.get_width()) // 2, y + (h - text_surface.get_height()) // 2))

# Set up sound channels (only 3 audio files because the radio comes from an online stream url)
channels = [pygame.mixer.Channel(i) for i in range(3)]
sounds = [
    pygame.mixer.Sound('audio/audio1.wav'),
    pygame.mixer.Sound('audio/audio2.wav'),
    pygame.mixer.Sound('audio/audio4.wav'), # File is named audio4 because it is the 4th knob. The 3rd knob is the KEXP radio stream.
]

# Play each sound on a separate channel in a loop
for i in range(3):
    channels[i].play(sounds[i], loops=-1)
    channels[i].set_volume(volumes[i])

# Method to start VLC instance for streaming radio audio
def play_stream(url):
    global player
    instance = vlc.Instance()
    player = instance.media_player_new()
    media = instance.media_new(url)
    player.set_media(media)
    player.play()
    print(f"Playing stream: {url}")

# Play the KEXP stream (If radio is not working, try opening the url in a browser.)
# If KEXP changes their stream url, this will no longer work. We found this url by doing the following:
# 1. Navigate to kexp.org
# 2. Press the now playing / play button / whatever it becomes in the future.
# 3. Press F12 to show the developer tools
# 4. Go to the "Network" tab, and look at the list of sources for something ending in .mp3 (in 2024 it was called `kexp128.mp3`)
# 5. Right click that source and open it in a new tab. The URL it opens should work for this interactive.
stream_url = 'https://kexp-mp3-128.streamguys1.com/kexp128.mp3'
play_stream(stream_url)

# Main loop, run over and over
selected_port = get_arduino_port()
arduino = serial.Serial(port=selected_port, baudrate=115200)
running = True
while running:
    # Read serial
    detected_serial_message = read_serial(arduino)
    if detected_serial_message is not None:
        print("Arduino message:", detected_serial_message)
        for i in range(4):
            volumes[i] = int(detected_serial_message.split(',')[i])/100
            if i == 2:  # radio volume
                player.audio_set_volume(int(volumes[i] * 100))
            elif i == 3: # kids convo volume
                channels[2].set_volume(volumes[i])
            else:
                channels[i].set_volume(volumes[i])

    screen.fill(WHITE)

    # Draw sliders (for testing with display connected)
    for i in range(4):
        draw_slider(screen, slider_x, slider_y[i], volumes[i])

    
    # Quit on escape key
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()

    # This method updates the display (for testing with display connected)
    pygame.display.flip()

# Quit pygame
pygame.quit()
