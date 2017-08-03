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
sounds.append(pygame.mixer.Sound("/home/pi/Desktop/esc-button/sounds/MouseModeAudio.wav"))
sounds.append(pygame.mixer.Sound("/home/pi/Desktop/esc-button/sounds/capslockon.wav"))
sounds.append(pygame.mixer.Sound("/home/pi/Desktop/esc-button/sounds/capslockoff.wav"))
sounds[2].set_volume(0.25)

dictionary = {'SL':'a', 'LSSS':'b', 'LSLS':'c', 'LSS':'d', 'S':'e',\
              'SSLS':'f', 'LLS':'g', 'SSSS':'h', 'SS':'i', 'SLLL':'j',\
              'LSL':'k', 'SLSS':'l', 'LL':'m', 'LS':'n', 'LLL':'o',\
              'SLLS':'p', 'LLSL':'q', 'SLS':'r', 'SSS':'s', 'L':'t',\
              'SSL':'u', 'SSSL':'v', 'SLL':'w', 'LSSL':'x', 'LSLL':'y',\
              'LLSS':'z',\
              'SLSLSL':'.', 'LLSSLL':',', 'SSLLSS':'/', 'SSLL':' ',\
              'SLLLL':'1', 'SSLLL':'2', 'SSSLL':'3', 'SSSSL':'4', 'SSSSS':'5',\
              'LSSSS':'6', 'LLSSS':'7', 'LLLSS':'8', 'LLLLS':'9', 'LLLLL':'0',\
              'SSSSLL':'CAPS', 'SSSSSL':'\\enter\\', 'SSSSSS':'\\delete\\', 'SLSL':'\\shift',\
              'SLSSS':'\\aup\\', 'SLSLL':'\\adown\\', 'SLSSL':'\\aleft\\', 'SLSLS':'\\aright\\',\
              'LSLSS':'-', 'LSLSL':'=', 'LSSLS':'[', 'LSSLL':']', 'LSLLS':';', 'LSLLL':'\'',\
              'LLSSL':'\\', 'LLSLL':'`'}

mouse_inputs = {'SS':'\\up', 'LL':'\\down', 'SL':'\\left', 'LS':'\\right',\
                'S':'\\left_click\\', 'L':'\\right_click\\', 'SSS':'\\double_click\\'}

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
shift = False

mouse_dir = ''
move_mouse = False
just_moved = False
mouse_speed = 1
mouse_max_speed = 10
mouse_acc = 0.25

sleep_delay = 0.05
long_cut_off = 250
buffer_time = 400
multiplyer = 1

speed_change = {'LLLLLLLL':1.25, 'SSSSSSSS':0.8, 'SLSLSLSL':None}

while True:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((UDP_IP, UDP_PORT))
        print('connected!')
        sounds[4].play()
        time.sleep(1)
        if current_mode == 'esc':
            sounds[0].play()
        elif current_mode == 'keyboard':
            sounds[1].play()
        else:
            sounds[5].play()
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
                elif just_moved:
                    mouse_dir = ''
                    just_moved = False
                elif mouse_dir and move_mouse:
                    move_mouse = False
                    just_moved = True
                    print("<<<<< STOP >>>>>")
            elif input_state == True and pressed:
                pressed = False
                released_time = int(round(time.time()*1000))
                difference = released_time - pressed_time
                sounds[2].stop()
                if current_mode != "esc" and not move_mouse and not just_changed and not just_moved and difference > 20:
                    if difference < long_cut_off * multiplyer:
                        curr_buffer += "S"
                        print("short")
                    elif difference < 2000:
                        curr_buffer += "L"
                        print("long")
                just_changed = False
            elif not pressed and curr_buffer != "":
                curr_time = int(round(time.time()*1000))
                difference = curr_time - released_time
                if difference > buffer_time * multiplyer:
                    pressed_time = curr_time
                    released_time = curr_time
                    if curr_buffer in dictionary and current_mode == "keyboard":
                        letter = dictionary[curr_buffer]
                        if letter == "CAPS":
                            CAPS = not CAPS
                            if CAPS:
                                sounds[6].play()
                            else:
                                sounds[7].play()
                            print("CAPS LOCK " + str(CAPS))
                        elif letter == '\\shift':
                            shift = True
                            print('<<<<< shift >>>>>')
                        else:
                            if CAPS and len(letter) < 2:
                                letter = letter.upper()
                            if shift:
                                shift = False
                                letter = '\\shift ' + letter + '\\'
                            print("<<<<< sending " + letter + " <<<<<")
                            s.sendto(letter, (UDP_IP, UDP_PORT))
                    elif curr_buffer in mouse_inputs and current_mode == 'mouse' and not move_mouse:
                        mouse_mode = mouse_inputs[curr_buffer]
                        if not mouse_dir and not 'click' in mouse_mode:
                            mouse_speed = 1
                            mouse_dir = mouse_mode
                            move_mouse = True
                            print("<<<<< moving " + mouse_dir + " <<<<<")
                        elif 'click' in mouse_mode:
                            print("<<<<< sending " + mouse_mode + " <<<<<")
                            s.sendto(mouse_mode, (UDP_IP, UDP_PORT))
                    elif curr_buffer in speed_change:
                        if speed_change[curr_buffer]:
                            multiplyer *= speed_change[curr_buffer]
                        else:
                            multiplyer = 1
                        print("multiplyer = " + str(multiplyer))
                    else:
                        print("<<<<< ERROR " + curr_buffer + " is invalid for "\
                              + current_mode + " <<<<<")
                        s.sendto("<<<<< ERROR " + curr_buffer + " is invalid for "\
                              + current_mode + " <<<<<", (UDP_IP, UDP_PORT))
                    curr_buffer = ""
            elif pressed:
                curr_time = int(round(time.time()*1000))
                difference = curr_time - pressed_time
                if difference > 2000:
                    pressed_time = curr_time
                    just_changed = True
                    if current_mode == "keyboard":
                        current_mode = "esc"
                        print("changing to esc")
                        s.sendto("changing to esc", (UDP_IP, UDP_PORT))
                        sounds[0].play()
                    elif current_mode == "esc":
                        current_mode = "mouse"
                        print("changing to mouse")
                        s.sendto("changing to mouse", (UDP_IP, UDP_PORT))
                        sounds[5].play()
                    else:
                        current_mode = "keyboard"
                        mouse_dir = ''
                        move_mouse = False
                        just_moved = False
                        mouse_speed = 1
                        print("changing to keyboard")
                        s.sendto("changing to keyboard", (UDP_IP, UDP_PORT))
                        sounds[1].play()
            elif mouse_dir and move_mouse:
                if mouse_speed < mouse_max_speed:
                    mouse_speed += mouse_acc
                s.sendto(mouse_dir + ' ' + str(int(mouse_speed)) + '\\', (UDP_IP, UDP_PORT))
            time.sleep(sleep_delay * multiplyer)
    except IOError, e:
        print('reconnecting...')
        sounds[3].play()
        time.sleep(2) 
