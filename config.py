#!/usr/bin/env python
# Common global variable configuration file

import os

# Set up variables to reference the GPIO pins we will use
led_pin_select    = 18
button_pin_select = 23
led_pin_left      = 17
button_pin_left   = 27
led_pin_right     = 16
button_pin_right  = 20
button_pin_exit   = 5

# Set up some colour constants
black_colour     = (0, 0, 0)
off_black_colour = (5, 5, 5)
white_colour     = (250, 250, 250)
blue_colour      = (40, 70, 200)

# Set the screen saver constants
screen_saver_seconds = 300

# Set up the file paths of overlay images
images_dir                = 'images'
face_target_overlay_image = os.path.join(images_dir, 'face_overlay_fill.png')
face_target_fit_face_overlay_image = os.path.join(images_dir, 'face_overlay_fit-face.png')
face_target_smile_overlay_image = os.path.join(images_dir, 'face_overlay_smile.png')
accept_overlay_image      = os.path.join(images_dir, 'accept.png')
reject_overlay_image      = os.path.join(images_dir, 'reject.png')
go_up_overlay_image       = os.path.join(images_dir, 'go_up.png')
go_down_overlay_image     = os.path.join(images_dir, 'go_down.png')
select_overlay_image      = os.path.join(images_dir, 'select.png')
exit_overlay_image        = os.path.join(images_dir, 'exit.png')
menu_overlay_image        = os.path.join(images_dir, 'menu.png')
previous_overlay_image    = os.path.join(images_dir, 'previous.png')
next_overlay_image        = os.path.join(images_dir, 'next.png')

exit_side_overlay_image   = os.path.join(images_dir, 'exit_side.png')
exit_side_overlay_image_bk_black = os.path.join(images_dir, 'exit_side_bk-black.png')

menu_side_overlay_image   = os.path.join(images_dir, 'menu_side.png')

start_overlay_image       = os.path.join(images_dir, 'start.png')
start_overlay_image_bk_black = os.path.join(images_dir, 'start_bk-black.png')
