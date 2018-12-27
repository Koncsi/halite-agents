#!/usr/bin/env python3
# Python 3.6

# Import the Halite SDK, which will let you interact with the game.
import hlt

# This library contains constant values.
from hlt import constants, Position, Direction
# This library contains direction metadata to better interface with the game.
from hlt.positionals import Direction

# This library allows you to generate random numbers.
import random

# Logging allows you to save messages for yourself. This is required because the regular STDOUT
#   (print statements) are reserved for the engine-bot communication.
import logging

""" <<<Game Begin>>> """

# This game object contains the initial game state.
game = hlt.Game()


# At this point "game" variable is populated with initial map data.
# This is a good place to do computationally expensive start-up pre-processing.
# As soon as you call "ready" function below, the 2 second per turn timer will start.
def set_direction(map):
    pos = Position(random.randint(0, game_map.width - 1), random.randint(0, game_map.height - 1))
    while (map[pos].halite_amount < 600):
        pos = Position(random.randint(0, game_map.width - 1), random.randint(0, game_map.height - 1))
    return pos


def better_around(map, pos, dir):
    x = pos.x
    y = pos.y

    best_pos = dir
    best_val = 400
    for x_i in range(-2, 2):
        for y_i in range(-2, 2):
            cur_pos = Position(x + x_i, y + y_i)
            cur_amount = map[cur_pos].halite_amount
            if (cur_amount > best_val):
                best_val = cur_amount
                best_pos = cur_pos

    return (best_val > 400), best_pos


game.ready("FROZEN")

# Now that your bot is initialized, save a message to yourself in the log file with some important information.
#   Here, you log here your id, which you can always fetch from the game object by using my_id.
logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))

""" <<<Game Loop>>> """
directions = {}
while True:
    # This loop handles each turn of the game. The game object changes every turn, and you refresh that state by
    #   running update_frame().
    game.update_frame()
    # You extract player metadata and the updated map metadata here for convenience.
    me = game.me
    game_map = game.game_map

    # A command queue holds all the commands you will run this turn. You build this list up and submit it at the
    #   end of the turn.
    command_queue = []

    for ship in me.get_ships():
        if ship.id not in directions:
            directions[ship.id] = set_direction(game_map)
        # For each of your ships, move randomly if the ship is on a low halite location or the ship is full.
        #   Else, collect halite.
        if ship.is_full:
            directions[ship.id] = me.shipyard.position

        # better, bet_pos = better_around(game_map,ship.position,directions[ship.id])
        # if better:
        #     directions[ship.id] = bet_pos

        if ship.position == me.shipyard.position:
            directions[ship.id] = set_direction(game_map)

        if ship.position == directions[ship.id]:
            directions[ship.id] = me.shipyard.position

        command_queue.append(ship.move(game_map.naive_navigate(ship, directions[ship.id])))

    # If the game is in the first 200 turns and you have enough halite, spawn a ship.
    # Don't spawn a ship if you currently have a ship at port, though - the ships will collide.
    if len(me.get_ships()) < 1:
        command_queue.append(me.shipyard.spawn())
    else:
        if me.halite_amount >= 4500 and len(me.get_ships()) < 6 and not game_map[me.shipyard].is_occupied:
            command_queue.append(me.shipyard.spawn())

    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)
