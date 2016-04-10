#!/usr/bin/env python
# Classes used to display text and images on pygame screen

import pygame
from PIL import Image, ImageDraw

import config

class PrintOnScreen(object):
    screen        = None
    screen_width  = None
    screen_height = None
    centerx       = None
    centery       = None

    def __init__(self, screen):
        self.screen = screen
        self.screen_width  = pygame.display.Info().current_w
        self.screen_height = pygame.display.Info().current_h
        self.centerx = screen.get_rect().centerx
        self.centery = screen.get_rect().centery

    # TODO: Factor out common code from TextPrinter and ImagePrinter

class TextPrinter(PrintOnScreen):
    'Class to print text on a pygame screen'

    # print_text()
    # text_defs is a matrix of the form:
    #    [["text", size, (colour), "alignment", position], ["text", size, (colour), "alignment", position]]
    # alignment can be combination of 'lcrtmb' (left, centre, right; top, middle, bottom)
    def print_text(self, text_defs, line_spacing, clear_screen):
        # If called for, clear previous text from screen
        if clear_screen:
            screen_colour_fill(self.screen, config.white_colour)

        # Define a list to collect the Surfaces of each line of text
        screen_text  = []
        text_rect_list = []

        for curr_text_def in text_defs:
            print_text, font_size, font_colour, alignment, position = curr_text_def

            font = pygame.font.Font(None, font_size)
            screen_text.append([font.render(print_text, True, font_colour), alignment, position])

        # Get the combined height of all the lines of text
        combined_height = 0
        for curr_text in screen_text:
            text_surface, alignment, position = curr_text
            text_rect = text_surface.get_rect()
            combined_height += text_rect[3] + line_spacing
        combined_height -= line_spacing

        multiline_curr_line_y = (self.screen_height - combined_height) // 2
        
        # Now we have rendered all the lines of text onto different Surfaced, work out where to place them
        for curr_text in screen_text:
            text_surface, alignment, position = curr_text

            text_rect = text_surface.get_rect()
            text_x, text_y, text_width, text_height = text_rect
            
            # Deal centreing first: horizontally or vertically
            if 'c' in alignment:
                text_rect.centerx = self.centerx
            if 'm' in alignment:
                text_rect.centery = self.centery

            # Now deal with horizontal position
            if 'l' in alignment:
                pos_shift = int(float(self.screen_width) / float(100) * float(position))
                text_rect.move_ip(pos_shift, 0)
            if 'r' in alignment:
                pos_shift = self.screen_width - int(float(self.screen_width) / float(100) * float(position))
                text_rect.move_ip(pos_shift - text_width, 0)

            # Finally deal with vertical postion
            if len(screen_text) > 1:
                # We need to space the lines out vertically
                # TODO: Currently lines will be spaced out from mid-point of screen, 
                #       could improve function to allow lines to be spaced from top or bottom of screen
                text_rect[1] = multiline_curr_line_y
                multiline_curr_line_y += text_height + line_spacing
            else:
                # Only one line, so 
                if 't' in alignment:
                    pos_shift = int(float(self.screen_height) / float(100) * float(position))
                    text_rect.move_ip(0, pos_shift)
                if 'b' in alignment:
                    pos_shift = self.screen_height - int(float(self.screen_height) / float(100) * float(position))
                    text_rect.move_ip(0, pos_shift - text_height)

            text_rect_list.append(text_rect)

            self.screen.blit(text_surface, text_rect)
        
        # Blit everything to the screen
        pygame.display.flip()

        return text_rect_list

class ImagePrinter(PrintOnScreen):
    'Class to print text on a pygame screen'

    # print_images()
    # image_defs is a matrix of the form:
    #     [["image path", "alignment", postion, height_scale]]
    # alignment can include characters 'lcrtmb' (left, centre, right; top, middle, bottom)
    #     e.g. pin image to bottom left = 'lb'
    # height_scale a percentage of the display height that image should be scaled to (0 is ignored)
    def print_images(self, image_defs, clear_screen):
        # If called for, clear previous text from screen
        if clear_screen:
            screen_colour_fill(self.screen, config.white_colour)

        for curr_image_def in image_defs:
            image_file, alignment, position, height_scale = curr_image_def

            # Load the image
            img = pygame.image.load(image_file)
            img.convert_alpha()

            orig_width, orig_height = img.get_size()
            if height_scale > 0:
                # Work out the new size for the image
                new_height   = int(float(self.screen_height) / float(100) * float(height_scale))
                scale_factor = float(new_height) / float(orig_height)
                new_width    = int(float(orig_width) * float(scale_factor))

                # Resize the image
                img = pygame.transform.scale(img, (new_width, new_height))

            image_rect = img.get_rect()
            image_x, image_y, image_width, image_height = image_rect

            # Deal with centreing first
            if 'c' in alignment:
                image_rect.centerx = self.centerx
            if 'm' in alignment:
                image_rect.centery = self.centery

            # Then deal with horizontal positioning
            if 'l' in alignment:
                pos_shift = int(float(self.screen_width) / float(100) * float(position))
                image_rect.move_ip(pos_shift, 0)
            if 'r' in alignment:
                pos_shift = self.screen_width - int(float(self.screen_width) / float(100) * float(position))
                image_rect.move_ip(pos_shift - image_width, 0)

            # Finally deal with vertical positioning
            if 't' in alignment:
                pos_shift = int(float(self.screen_height) / float(100) * float(position))
                image_rect.move_ip(0, pos_shift)
            if 'b' in alignment:
                pos_shift = self.screen_height - int(float(self.screen_height) / float(100) * float(position))
                image_rect.move_ip(0, pos_shift - image_height)
           
            self.screen.blit(img, image_rect)

        pygame.display.flip()

class CursorPrinter(PrintOnScreen):
    'Class to print a single character cursor on a pygame screen'

    font_size   = 64
    font_colour = config.blue_colour
    cursor_char = '>'
    margin      = 10

    def __init__(self, screen, font_size=None, font_colour=None):
        self.screen      = screen
        self.font_size   = font_size if font_size is not None else self.font_size
        self.font_colour = font_colour if font_colour is not None else self.font_colour

    def print_cursor(self, option_rect_list, chosen_index):
        self.num_options  = len(option_rect_list)

        if chosen_index < 0:
            chosen_index = 0
        elif chosen_index > self.num_options - 1:
            chosen_index = self.num_options - 1

        self.option_rect = option_rect_list[chosen_index]

        self.font   = pygame.font.Font(None, self.font_size)
        self.cursor = self.font.render(self.cursor_char, True, self.font_colour)

        self.cursor_rect = self.cursor.get_rect()

        self.cursor_rect[0] = self.option_rect[0] - self.margin - self.cursor_rect[2]
        self.cursor_rect[1] = self.option_rect[1]

        # Before we draw the cursor, erase all previous cursors
        self.cursor_mask_rect    = self.cursor.get_rect()
        self.cursor_mask_rect[0] = self.cursor_rect[0]
        self.cursor_mask_rect[1] = option_rect_list[0][1] # Set to the y value of first menu option
        self.cursor_mask_rect[2] = self.cursor_rect[2]
        self.cursor_mask_rect[3] = (option_rect_list[self.num_options-1][1] - 
                                    self.cursor_mask_rect[1] + 
                                    option_rect_list[self.num_options-1][3])

        self.cursor_mask = pygame.draw.rect( self.screen, 
                                             config.white_colour, 
                                             self.cursor_mask_rect, 
                                             0)

        # Draw the current cursor on the screen
        self.screen.blit(self.cursor, self.cursor_rect)

        # Blit everything to the screen
        pygame.display.flip()

class OverlayOnCamera(object):
    'Print overlays on top of PiCamera preview'
    camera            = None
    overlay           = None
    prev_overlay_size = None

    def __init__(self, camera):
        self.camera = camera

    def camera_overlay(self, image_file):
        img = Image.open(image_file)

        # Create an image padded to the required size with
        # mode 'RGB'
        pad = Image.new('RGB', (
            ((img.size[0] + 31) // 32) * 32,
            ((img.size[1] + 15) // 16) * 16,
            ))

        # Paste the original image into the padded one
        pad.paste(img, (0, 0))
        
        # Add the overlay with the padded image as the source,
        # but the original image's dimensions
        if self.overlay:
            # If we previously added an overlay, was it the same padded size?
            if (self.prev_overlay_size[0] == img.size[0] and self.prev_overlay_size[1] == img.size[1]):
                # If it was the same size, simply update the overlay
                self.overlay.update(pad.tostring())
            else:
                # If it was a different size, we will have to remove the previous overlay first
                camera.remove_overlay(self.overlay)
                self.overlay = self.camera.add_overlay(pad.tostring(), layer=3, size=img.size, alpha=128)
        else:
            self.overlay = self.camera.add_overlay(pad.tostring(), layer=3, size=img.size, alpha=128)

        self.prev_overlay_size = img.size

    def remove_camera_overlay(self):
        self.camera.remove_overlay(self.overlay)
        self.overlay = None

# HACK: Don't really need a whole class that only uses __init__() do we?
class screen_colour_fill(object):
    'Base class to fill the pygame screen with solid colours'

    def __init__(self, screen, colour, rectangle=None):
        # If 'rectangle' is set, only fill in that rectangle of the screen
        if rectangle is None:
            # If it is not set, fill in the whole screen
            rectangle = screen.get_rect()

        screen.fill(colour, rectangle)

        screen.blit( screen, (0,0) )
        pygame.display.flip()

