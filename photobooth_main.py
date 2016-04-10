#!/usr/bin/env python
# This module contains the over arching Photo Booth class, and the Main Menu class

import os
import subprocess
import RPi.GPIO as GPIO
import pygame
import time
import datetime
import threading

from file_handling import FileHandler
from button_handling import ButtonHandler
from print_on_screen import TextPrinter, ImagePrinter, CursorPrinter, screen_colour_fill
#from photobooth_functions import OfficialPhoto, UnofficialPhoto

import config

class PhotoBooth(object):
    'PhotoBooth is the base class that each photobooth feature inherits from'

    # Set up a variable to hold our pygame 'screen'
    screen           = None
    filehandler      = None
    buttonhandler    = None
    size             = None
    local_dirs_ready = True

    # For photobooth functions that upload photos into a dated folder,
    #    we should prefix the date URL with an ID number,
    #    and each hardware (that uploads to the same server) should change the following booth_id
    # TODO: Don't need to use it until we have more than one booth set up.
    booth_id = ""

    def __init__(self):
        self.set_up_gpio()
        self.init_pygame()
        self.buttonhandler = ButtonHandler()

        try:
            self.filehandler = FileHandler()
        except subprocess.CalledProcessError as e:
            self.local_dirs_ready = False

        # Stop the monitor blanking after inactivity
        os.system("setterm -blank 0 -powerdown 0")

    def __del__(self):
        print "Destructing PhotoBooth instance"

    def tidy_up(self):
        # NOTE: This was the __del__ method, but seems more reliable to call explicitly
        print "Tidying up PhotoBooth instance"
        ButtonHandler().light_button_leds('slr', False) # Turn off all LEDs
        pygame.quit()  # End our pygame session
        GPIO.cleanup() # Make sure we properly reset the GPIO ports we've used before exiting

        # Restore monitor blanking (TODO can we store previous values?)
        os.system("setterm -blank 30 -powerdown 30")

    def set_up_gpio(self):
        GPIO.setmode(GPIO.BCM)
        #GPIO.setup(camera_led_pin, GPIO.OUT, initial=False) # Set GPIO to output
        GPIO.setup(config.led_pin_select,GPIO.OUT) # The 'Select' button LED
        GPIO.setup(config.led_pin_left,GPIO.OUT) # The 'Left' button LED
        GPIO.setup(config.led_pin_right,GPIO.OUT) # The 'Right' button LED

        # Detect falling edge on all buttons
        GPIO.setup(config.button_pin_select, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(config.button_pin_left, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(config.button_pin_right, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(config.button_pin_exit, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # Drumminhands found it necessary to switch off LEDs initially
        GPIO.output(config.led_pin_select, False)
        GPIO.output(config.led_pin_left, False)
        GPIO.output(config.led_pin_right, False)

    def init_pygame(self):
        pygame.init()
        self.size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        print "Initialised PyGame: Screen Width " + str(self.size[0]) + " x Height " + str(self.size[1])

        pygame.display.set_caption('Photo Booth')
        pygame.mouse.set_visible(False) # Hide the mouse cursor
        self.screen = pygame.display.set_mode(self.size, pygame.FULLSCREEN)

    def get_booth_id(self):
        return self.booth_id

    def get_pygame_screen(self):
        return self.screen

    def get_button_handler(self):
        return self.buttonhandler

    def get_file_handler(self):
        return self.filehandler

    def screen_saver(self):
        # If we have been waiting at the Main Menu for too long  
        # then blank the screen, and pulse the Select button

        # Turn off the Left and Right button LEDs
        self.buttonhandler.light_button_leds('lr', False)

        # Make a copy of what is currently displayed on the screen
        screen_copy = pygame.Surface.copy(self.screen)

        # Turn off the screen
        screen_colour_fill(self.screen, config.black_colour)
        #os.system("sudo ./support/rpi-hdmi.sh off")

        # Start a separate thread to flash the Select LED
        flash_led_stop = threading.Event()
        flash_led = threading.Thread(target=self.buttonhandler.flash_button_leds,
                                     args=('s', 1, flash_led_stop))
        flash_led.start()


        # Wait until the Select button is pressed
        while not self.buttonhandler.button_is_down(config.button_pin_select):
            time.sleep(0.2)

        # Come out of screen saver
        # Turn on the button LEDs
        self.buttonhandler.light_button_leds('lsr', True)

        # Show the copy of the display that we made before going into screensaver
        self.screen.blit(screen_copy, (0,0))
        pygame.display.flip()
        #os.system("sudo ./support/rpi-hdmi.sh on")

        # Stop the thread which has been flashing the Select LED
        flash_led_stop.set()
        flash_led.join()

        # In case the thread was still running and turned off the Select LED,
        #    make sure all the buttons are lit
        self.buttonhandler.light_button_leds('lsr', True)

class Menus(object):
    'A class to handle the Main Menu'

    photobooth    = None
    buttonhandler = None

    # Set the text attributes for the main menu heading
    heading_font_colour = config.blue_colour

    # Set the text attributes for the menu item display
    menu_font_size      = 64
    menu_font_colour    = config.black_colour
    menu_item_alignment = "lm"
    menu_item_position  = 20 

    menu_cursor_font_size   = 64
    menu_cursor_font_colour = config.blue_colour

    menu_item_line_spacing = 20
    menu_option_rects      = None

    # menu_objects holds instances of each Photo Booth function class that 
    #    is added to the Main Menu
    menu_objects = []
    
    def __init__(self, photobooth):
        self.photobooth    = photobooth
        self.screen        = photobooth.get_pygame_screen()
        self.buttonhandler = photobooth.get_button_handler()
        self.textprinter   = TextPrinter(self.screen)
        self.imageprinter  = ImagePrinter(self.screen)
        
        screen_colour_fill(self.screen, config.white_colour)

    def __del__(self):
        print "Destructing Menus instance"
        self.photobooth = None

    def add_main_menu_item(self, item_class):
        self.menu_objects.append(item_class)

    def display_main_menu(self):
        self.text_defs  = []
        self.image_defs = []

        # Print the heading on the screen
        self.textprinter.print_text( [["Welcome to the Photo Booth", 
                                      120, 
                                      self.heading_font_colour, 
                                      "ct", 
                                      5]],
                                     0,
                                     True )

        # Print the main menu items
        for item_class in self.menu_objects:
            self.text_defs.append( [item_class.get_menu_text(), 
                                    self.menu_font_size,
                                    self.menu_font_colour,
                                    self.menu_item_alignment,
                                    self.menu_item_position] )

        self.menu_option_rects = self.textprinter.print_text( self.text_defs, 
                                                             self.menu_item_line_spacing,
                                                             False )

        # Print the image overlays onto the screen
        self.image_defs = [
            [config.go_up_overlay_image,   'lb', 0, 0],
            [config.go_down_overlay_image, 'rb', 0, 0],
            [config.select_overlay_image,  'cb', 0, 0]
        ]

        self.imageprinter.print_images(self.image_defs, False)

    def get_main_menu_selection(self):
        self.cursorprinter = CursorPrinter(self.screen, self.menu_cursor_font_size, 
                                           self.menu_cursor_font_colour) 

        self.menu_choice   = 0

        # Print the initial cursor at the first menu option
        self.cursorprinter.print_cursor(self.menu_option_rects, self.menu_choice)

        while True:
            self.button = self.buttonhandler.wait_for_buttons('lsr', False)
            if self.button == 'l':
                if self.menu_choice > 0:
                    self.menu_choice -= 1
                    self.cursorprinter.print_cursor( self.menu_option_rects, self.menu_choice)
            if self.button == 'r':
                if self.menu_choice < len(self.menu_option_rects) - 1:
                    self.menu_choice += 1
                    self.cursorprinter.print_cursor( self.menu_option_rects, self.menu_choice)
            if self.button == 's':
                self.buttonhandler.light_button_leds('lsr', False)
                break

            if self.button == 'exit':
                # The user pressed the exit button - how long did they keep it pressed for?
                self.start_time = time.time()
                time.sleep(0.2)

                self.menu_choice = -1 # -1 indicates a short exit button
                while self.buttonhandler.button_is_down(config.button_pin_exit):
                    time.sleep(0.2)
                    # If the exit button is held down for longer than 3 seconds
                    # then record a 'long exit button press'
                    if time.time() - self.start_time > 3:
                        self.menu_choice = -2 # -2 indicates a long exit button press
                        break
                    
                break

            # If we have been sitting at the Main Menu for longer than screen_saver_seconds secs
            # then go into screen_saver mode.
            if self.button == 'screensaver':
                print "Monitor going into screen saver mode."
                self.photobooth.screen_saver() # HACK
                pass

        return self.menu_choice

    def get_menu_object_at_index(self, object_index):
        return self.menu_objects[object_index]

