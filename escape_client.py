import RPi.GPIO as GPIO
import time
import threading
from datetime import datetime
import socket
import pygame

sounds = []
pygame.mixer.init(buffer=512)
sounds.append(pygame.mixer.Sound("/home/pi/Desktop/esc-button/sounds/EscapeModeAudio.wav"))
sounds.append(pygame.mixer.Sound("/home/pi/Desktop/esc-button/sounds/KeyboardModeAudio.wav"))
sounds.append(pygame.mixer.Sound("/home/pi/Desktop/esc-button/sounds/magic.wav"))
sounds[2].set_volume(0.25)

dictionary = {'SL':'a', 'LSSS':'b', 'LSLS':'c', 'LSS':'d', 'S':'e', 'SSLS':'f', 'LLS':'g', 'SSSS':'h', 'SS':'i', 'SLLL':'j', 'LSL':'k', 'SLSS':'l', 'LL':'m', 'LS':'n', 'LLL':'o', 'SLLS':'p', 'LLSL':'q', 'SLS':'r', 'SSS':'s', 'L':'t', 'SSL':'u', 'SSSL':'v', 'SLL':'w', 'LSSL':'x', 'LSLL':'y', 'LLSS':'z'}
UDP_IP = '10.6.1.30'
UDP_PORT = 9980
ESC = '\\escape\\'
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)

pressed_time = int(round(time.time()*1000))
released_time = int(round(time.time()*1000))
curr_time = int(round(time.time()*1000))
just_changed = False

while True:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((UDP_IP, UDP_PORT))
        print('connected!')
        pressed = False
        curr_buffer = ""
        current_mode = "keyboard"
        while True:
            input_state = GPIO.input(18)
            if input_state == False and not pressed:
                pressed_time = int(round(time.time()*1000))
                pressed = True
                if current_mode == "esc":
                    s.sendto(ESC, (UDP_IP, UDP_PORT))
                    print("ESC")
                elif current_mode == "keyboard":
                    sounds[2].play()
            elif input_state == True and pressed:
                pressed = False
                released_time = int(round(time.time()*1000))
                difference = released_time - pressed_time
                sounds[2].stop()
                if current_mode == "keyboard" and not just_changed and difference > 60:
                    if difference < 250:
                        curr_buffer += "S"
                        print("short")
                    elif difference < 1000:
                        curr_buffer += "L"
                        print("long")
                just_changed = False
            elif not pressed and curr_buffer != "" and current_mode == "keyboard":
                curr_time = int(round(time.time()*1000))
                difference = curr_time - released_time
                if difference > 500:
                    pressed_time = curr_time
                    released_time = curr_time
                    if curr_buffer in dictionary:
                        letter = dictionary[curr_buffer]
                        print("<<<<< sending " + letter + " <<<<<")
                        s.sendto(letter, (UDP_IP, UDP_PORT))
                    else:
                        print("<<<<< ERROR " + curr_buffer + " is invalid <<<<<")
                    curr_buffer = ""
            elif pressed and not just_changed:
                curr_time = int(round(time.time()*1000))
                difference = curr_time - pressed_time
                if difference > 2000:
                    pressed_time = curr_time
                    just_changed = True
                    if current_mode == "keyboard":
                        current_mode = "esc"
                        print("changing to esc mode")
                        sounds[0].play()
                    else:
                        current_mode = "keyboard"
                        print("changing to keyboard")
                        sounds[1].play()
                    
                time.sleep(0.05)
    except IOError, e:
        print('reconnecting...')
        time.sleep(1) 


p.terminate()

