#!/usr/bin/env python
# Classes to handle photograph manipulation

import os
import pygame
import time
from PIL import Image, ImageDraw
import ImageChops
import math
import threading

from print_on_screen import ImagePrinter

import config

class PhotoHandler(object):
    'Base class for image transformation code'

    screen        = None
    filehandler   = None
    imageprinter  = None
    
    def __init__(self, screen, filehandler):
        self.screen       = screen
        self.filehandler  = filehandler
        self.imageprinter = ImagePrinter(self.screen)

    # Given a width, find the corresponding height that would fit the screen's aspect ratio
    def get_aspect_ratio_height(self, pixel_width):
        return pygame.display.Info().current_h * pixel_width // pygame.display.Info().current_w

    # Resize an image keeping the same aspect ratio
    def resize_image(self, img_filename, new_width, new_height):
        img = Image.open(img_filename)
        img_width, img_height = img.size

        # First, resize the image
        if new_width > new_height:
            # Required image is Landscape
            scale_factor = float(new_width) / float(img_width)
            temp_width   = new_width
            temp_height  = int(float(img_height) * float(scale_factor))
        else:
            # Required image is Portrait (or Square)
            scale_factor = float(new_height) / float(img_height)
            temp_width   = int(float(img_width) * float(scale_factor))
            temp_height  = new_height

        img = img.resize((temp_width, temp_height), Image.ANTIALIAS)

        return img

    # Thanks Charlie Clark: http://code.activestate.com/recipes/577630-comparing-two-images/
    def rms_difference(self, im1, im2):
        "Calculate the root-mean-square difference between two images"
        diff = ImageChops.difference(im1, im2)
        h = diff.histogram()
        #sq = (value*(idx**2) for idx, value in enumerate(h))
        sq = (value*((idx%256)**2) for idx, value in enumerate(h))
        sum_of_squares = sum(sq)
        rms = math.sqrt(sum_of_squares / float(im1.size[0] * im1.size[1]))
        return rms

    # Convert all captured images into the formats defined in image_defs
    def prepare_images(self, image_extension, image_defs, copy_origs):
        # Get directories
        image_dir  = self.filehandler.get_local_file_dir()

        # PiCamera captures images at 72 pixels/inch.

        # Collect a list of the original PiCamera-saved files
        file_pattern = os.path.join(image_dir, "photobooth*" + image_extension)
        files = self.filehandler.get_sorted_file_list(file_pattern)

        # Process the images in separate threads - in an attempt to speed the process up ...
        # (TODO: Threading doesn't seem to process the images any quicker)
        processing_thread_list = []

        self.imageprinter.print_images([[files[0], "ct", 10, 50]], False)

        for curr_img in files:
            processing_thread_list.append(threading.Thread(target=self.prepare_one_image, 
                                                           args=(curr_img, image_defs, copy_origs)))
            processing_thread_list[len(processing_thread_list)-1].start()

        # Wait for all processing threads to finish
        for curr_thread in processing_thread_list:
            curr_thread.join()

    def prepare_one_image(self, image_file, image_defs, copy_origs):
        upload_dir = self.filehandler.get_upload_file_dir()

        if copy_origs:
            filename        = os.path.basename(image_file)
            name, extension = os.path.splitext(filename)
            new_filepath    = os.path.join(upload_dir, 'original-' + name + extension)

            self.filehandler.copy_file(image_file, new_filepath)
            # Do a straight copy of the image_file file
            # Tip from http://learnpythonthehardway.org/book/ex17.html
            #in_file  = open(image_file)
            #img_data = in_file.read()

            #out_file = open(new_filepath, 'w')
            #out_file.write(img_data)

            #out_file.close()
            #in_file.close()

        for curr_img_def in image_defs:
            # Unpack the curr_img_def array into variables
            def_prefix, def_width, def_height, def_dpi = curr_img_def

            filename        = os.path.basename(image_file)
            name, extension = os.path.splitext(filename)
            new_filepath    = os.path.join(upload_dir, def_prefix + '-' + name + extension)
            
            img = self.resize_image(image_file, def_width, def_height)
            img_width, img_height = img.size

            # Second, if the current image def is a different aspect ratio, crop the image
            image_x = (img_width - def_width) // 2
            image_y = (img_height - def_height) // 2

            img = img.crop((image_x, image_y, image_x + def_width, image_y + def_height))
            img_width, img_height = img.size

            # Finally save the current image, at the requested DPI
            img.save(new_filepath, dpi=(def_dpi, def_dpi))

    # *** Display the captured images on the PyGame screen ***
    def show_photos_tiled(self, image_extension):
        # Get directories
        image_dir = self.filehandler.get_local_file_dir()

        file_pattern = os.path.join(image_dir, "*" + image_extension)
        files = self.filehandler.get_sorted_file_list(file_pattern)

        num_images = len(files)
        if num_images < 1:
            return

        # Find the aspect ratio of the images, for later use
        img = Image.open(files[0])
        image_width, image_height = img.size
        
        num_row_1  = num_images // 2 # Note: given an odd number of images, fewer will appear on top row
        num_row_2  = num_images - num_row_1

        screen_width  = pygame.display.Info().current_w
        screen_height = pygame.display.Info().current_h

        # display_* is the size that we want to display the image at
        display_height = screen_height // 2
        display_width  = int(float(display_height) / float(image_height) * float(image_width))

        row_1_x      = (screen_width - (num_row_1 * display_width)) // 2
        row_2_x      = (screen_width - (num_row_2 * display_width)) // 2

        image_num = 0
        for f in files:
            image_num = image_num + 1

            if image_num <= num_row_1:
                image_x = row_1_x + display_width * (image_num - 1)
                image_y = 0
            else:
                image_x = row_2_x + display_width * (image_num - num_row_1 - 1)
                image_y = display_height

            try:
                img = pygame.image.load(f) 
                img = pygame.transform.scale(img, (display_width, display_height))
                self.screen.blit(img,(image_x,image_y))
            except pygame.error, message:
                print "ERROR: Image " + os.path.basename(f) + " failed to load: " + message

        pygame.display.flip()

    def show_photos_animated(self, image_extension, stop_event):
        image_dir = self.filehandler.get_local_file_dir()

        file_pattern = os.path.join(image_dir, "*" + image_extension)
        files = self.filehandler.get_sorted_file_list(file_pattern)

        num_images = len(files)
        if num_images < 1:
            return

        # Find the aspect ratio of the images, for later use
        img = Image.open(files[0])
        image_width, image_height = img.size
        
        screen_width   = pygame.display.Info().current_w
        screen_height  = pygame.display.Info().current_h

        # display_* is the size that we want to display the image at
        display_height = screen_height // 3 * 2
        display_width  = int(float(display_height) / float(image_height) * float(image_width))

        image_x        = (screen_width // 2) - (display_width // 2)
        image_y        = screen_height // 20

        # Create a list of scaled images to display
        image_list = []
        for f in files:
            try:
                img = pygame.image.load(f) 
                image_list.append(pygame.transform.scale(img, (display_width, display_height)))
            except pygame.error, message:
                print ("ERROR: Image " + os.path.basename(f) + 
                       " failed to load: " + message)

        # In case not all the images were loaded and scaled
        num_images = len(image_list)
        if num_images < 1:
            return

        image_num = 0
        while not stop_event.is_set():
            self.screen.blit(image_list[image_num],(image_x,image_y))
            pygame.display.flip()
       
            stop_event.wait(1)

            # Advance to the next image
            image_num = image_num + 1
            if image_num >= num_images:
                image_num = 0

