# -*- coding: utf-8 -*-
"""
Created on Tue Jul  2 10:19:05 2024

@author: abhis
"""
import os
import sys

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir) 
from modules import utils


utils.graph_init()

utils.chat_bot("Give me a movie about toys?")