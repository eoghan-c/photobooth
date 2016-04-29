#!/usr/bin/env python
# original scripts created by chris@drumminhands.com (http://www.drumminhands.com/2014/06/15/raspberry-pi-photo-booth/)
# adapted and expanded by eoghan_clarkson@yahoo.com
# See details at http://eoghan.me.uk/notes/2016/03/28/photo-booth/

import os
import time
#from time import sleep

from photobooth_main import PhotoBooth, Menus
from photobooth_functions import OfficialPhoto, AccompaniedPhoto, AnimatedPhoto, ContinuousPhotos

menus       = None
photobooth  = None
menu_choice = 0

try:
    # Create our main photobooth object
    photobooth = PhotoBooth()

    # Configure the Main Menu
    menus = Menus(photobooth)

    # Add each Photo Booth function to the Main Menu
    menus.add_main_menu_item( OfficialPhoto(photobooth) )
    menus.add_main_menu_item( AccompaniedPhoto(photobooth) )
    menus.add_main_menu_item( AnimatedPhoto(photobooth) )
    menus.add_main_menu_item( ContinuousPhotos(photobooth) )
    
    while True:
        menus.display_main_menu()
        
        # Get the menu option selected by the user
        menu_choice = menus.get_main_menu_selection()

        # If the user pressed the exit button, end the program
        if menu_choice < 0:
            break

        # User didn't exit, so deal with their selection
        chosen_photobooth_function_object = menus.get_menu_object_at_index(menu_choice)
        chosen_photobooth_function_object.start()

finally:
    # Cleanly dispose of our menus object
    if menus is not None:
        del menus
        menus = None

    # Cleanly dispose of our photobooth object
    if photobooth is not None:
        photobooth.tidy_up()
        del photobooth
        photobooth = None

    # A long Exit button press (-2) means exit to console
    # A short Exit button press (-1) means shutdown
    if menu_choice == -1:
        os.system("sudo halt")
