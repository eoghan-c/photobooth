#!/usr/bin/env python
# Classes to handle button presses

import time
import RPi.GPIO as GPIO

import config

class ButtonHandler(object):
    
    def __init__(self):
        pass

    # wait_for_buttons()
    # Argument 'buttons' can be one or more of these characters:
    #    'l' - left button
    #    'r' - right button
    #    's' - select button
    # If arg 'turn_off_after' is True, then all button LEDs will be switched off after button press
    def wait_for_buttons(self, buttons, turn_off_after=True):
            # Turn on the button LEDs
            self.light_button_leds(buttons, True)

            time.sleep(0.2) # Debounce

            # Keep track of how long we have been waiting for a button press
            self.start_time = time.time()

            while True:
                # Check the button states
                if 's' in buttons and self.button_is_down(config.button_pin_select):
                    if turn_off_after:
                        self.light_button_leds(buttons, False)
                    return 's'
                elif 'l' in buttons and self.button_is_down(config.button_pin_left):
                    if turn_off_after:
                        self.light_button_leds(buttons, False)
                    return 'l'
                elif 'r' in buttons and self.button_is_down(config.button_pin_right):
                    if turn_off_after:
                        self.light_button_leds(buttons, False)
                    return 'r'
                elif self.button_is_down(config.button_pin_exit):
                    return 'exit'

                # If we've been waiting for a button press for longer than screen_saver_seconds secs
                # then go into screen_saver mode.
                if time.time() - self.start_time > config.screen_saver_seconds:
                    return 'screensaver'

    def button_is_down(self, button_pin):
        is_up = GPIO.input(button_pin)
        return not is_up

    def light_button_leds(self, buttons, turn_on):
        if 's' in buttons:
            GPIO.output(config.led_pin_select,turn_on)
        if 'l' in buttons:
            GPIO.output(config.led_pin_left,turn_on)
        if 'r' in buttons:
            GPIO.output(config.led_pin_right,turn_on)

    def flash_button_leds(self, buttons, interval_secs, stop_event):
        while not stop_event.is_set():
            self.light_button_leds(buttons, False)
            time.sleep(interval_secs)
            self.light_button_leds(buttons, True)
            time.sleep(interval_secs)
