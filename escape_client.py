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
sounds.append(pygame.mixer.Sound("/home/pi/Desktop/esc-button/sounds/ReconnectingAudio.wav"))
sounds.append(pygame.mixer.Sound("/home/pi/Desktop/esc-button/sounds/ConnectedAudio.wav"))
sounds[2].set_volume(0.25)

dictionary = {'SL':'a', 'LSSS':'b', 'LSLS':'c', 'LSS':'d', 'S':'e',\
              'SSLS':'f', 'LLS':'g', 'SSSS':'h', 'SS':'i', 'SLLL':'j',\
              'LSL':'k', 'SLSS':'l', 'LL':'m', 'LS':'n', 'LLL':'o',\
              'SLLS':'p', 'LLSL':'q', 'SLS':'r', 'SSS':'s', 'L':'t',\
              'SSL':'u', 'SSSL':'v', 'SLL':'w', 'LSSL':'x', 'LSLL':'y',\
              'LLSS':'z',\
              'SLSLSL':'.', 'LLSSLL':',', 'SSLLSS':'?', 'SSLL':' ',\
              'SLLLL':'1', 'SSLLL':'2', 'SSSLL':'3', 'SSSSL':'4', 'SSSSS':'5',\
              'LSSSS':'6', 'LLSSS':'7', 'LLLSS':'8', 'LLLLS':'9', 'LLLLL':'0',\
              'SSSSLL':'CAPS', 'SSSSSL':'\\enter\\', 'SSSSSS':'\\delete\\'}

mouse_inputs = {'SS':'\\up\\', 'LL':'\\down\\', 'SL':'\\left\\', 'LS':'\\right\\'}

UDP_IP = '10.6.1.30'
UDP_PORT = 9980
ESC = '\\escape\\'
CAPS = False
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)

pressed_time = int(round(time.time()*1000))
released_time = int(round(time.time()*1000))
curr_time = int(round(time.time()*1000))
just_changed = False
current_mode = "esc"

while True:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((UDP_IP, UDP_PORT))
        print('connected!')
        sounds[4].play()
        pressed = False
        curr_buffer = ""
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
                if current_mode != "esc" and not just_changed and difference > 60:
                    if difference < 250:
                        curr_buffer += "S"
                        print("short")
                    elif difference < 1000:
                        curr_buffer += "L"
                        print("long")
                just_changed = False
            elif not pressed and curr_buffer != "":
                curr_time = int(round(time.time()*1000))
                difference = curr_time - released_time
                if difference > 500:
                    pressed_time = curr_time
                    released_time = curr_time
                    if curr_buffer in dictionary and current_mode == "keyboard":
                        letter = dictionary[curr_buffer]
                        if letter == "CAPS":
                            CAPS = not CAPS
                            print("CAPS LOCK " + str(CAPS))
                        else:
                            if CAPS and len(letter) < 2:
                                letter = letter.upper()
                            print("<<<<< sending " + letter + " <<<<<")
                            s.sendto(letter, (UDP_IP, UDP_PORT))
                    elif curr_buffer in mouse_inputs and current_mode == 'mouse':
                        direction = mouse_inputs[curr_buffer]
                        print("<<<<< sending " + direction + " <<<<<")
                        s.sendto(direction, (UDP_IP, UDP_PORT))
                    else:
                        print("<<<<< ERROR " + curr_buffer + " is invalid for "\
                              + current_mode + " <<<<<")
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
                    elif current_mode == "esc":
                        current_mode = "mouse"
                        print("changing to mouse")
                    else:
                        current_mode = "keyboard"
                        print("changing to keyboard")
                        sounds[1].play()
                    
                time.sleep(0.05)
    except IOError, e:
        print('reconnecting...')
        sounds[3].play()
        time.sleep(1) 


p.terminate()

