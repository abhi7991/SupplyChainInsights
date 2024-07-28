# -*- coding: utf-8 -*-
"""
Created on Sun Jul 28 13:50:39 2024

@author: abhis
"""

import os
import sys
file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)
from modules import utils


utils.graph_init()

print(utils.chat_bot("I am looking for products which contain OraQuick Advance ?"))