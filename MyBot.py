#!/usr/bin/env python3
# Python 3.6

import hlt
import numpy as np

from hlt import constants, Position, Direction

import random
import logging

game = hlt.Game()



game.ready("KoncsiBot")

logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))

directions = {}
mode = {}

while True:
    game.update_frame()
    me = game.me
    game_map = game.game_map

    command_queue = []

    for ship in me.get_ships():
       pass

    game.end_turn(command_queue)
