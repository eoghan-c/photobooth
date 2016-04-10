#!/usr/bin/env python
# Classes used to handle Photo Booth files

import string
import random

class StringOperations(object):
    
    def __init__(self):
        pass

    def get_random_string(self, str_len):
        # Miss out easy-to-confuse characters 'lI1O0'
        chars = 'abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789_-'
        #chars = string.ascii_letters + string.digits + '_-'
        result = ''.join(random.choice(chars) for i in range(str_len))
        return result
