#!/usr/bin/env python3
# Python 3.6

# Import the Halite SDK, which will let you interact with the game.
import hlt
import numpy as np

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
def find_destination(game_map):
    halite_map = []

    for y in range(game_map.height):
        for x in range(game_map.width):
            pos = Position(x, y)
            halite_map.append(game_map[pos].halite_amount)

    halite_map = np.array(halite_map)
    num = np.array(game_map.height * game_map.width * 0.1).astype(int)
    indices = np.argpartition(halite_map, -num)[-num:]

    indices = indices[np.random.randint(0, len(indices), len(indices//2))]

    positions = []
    for idx in indices:
        positions.append(Position(idx % game_map.width, idx // game_map.height))

    dist = 999
    best_pos = positions[0]
    for pos in positions:
        d = game_map.calculate_distance(pos, ship.position)
        if d < dist:
            dist = d
            best_pos = pos

    return best_pos

def far_enough(game_map, me, ship):
    for dropoff in me.get_dropoffs():
        if game_map.calculate_distance(ship.position, dropoff.position) < 10:
            return False
    if game_map.calculate_distance(ship.position, me.shipyard.position) < 10:
        return False
    return True


def good_for_depo(game_map, me, ship):
    if not far_enough(game_map,me,ship):
        return False

    if me.halite_amount < 4100:
        return False

    x = ship.position.x
    y = ship.position.y
    halites = []
    for x_i in range(-3, 3):
        for y_i in range(-3, 3):
            pos = Position(x + x_i, y + y_i)
            halites.append(game_map[pos].halite_amount)

    if np.mean(halites) > 250:
        return True
    return False

def set_direction(map):
    positions = []
    halite = []

    for i in range(10):
        pos = Position(random.randint(0, game_map.width - 1), random.randint(0, game_map.height - 1))
        positions.append(pos)
        halite.append(map[pos].halite_amount)

    return positions[np.argmax(halite)]


def closest_depo(game_map,me,ship):
    min_distance = game_map.calculate_distance(me.shipyard.position, ship.position)
    closest = me.shipyard.position
    for depo in me.get_dropoffs():
        other_dist = game_map.calculate_distance(depo.position, ship.position)
        if other_dist < min_distance:
            min_distance = other_dist
            closest = depo.position

    return closest

def better_around(map, pos, dir):
    x = pos.x
    y = pos.y

    best_pos = dir
    best_val = 300
    for x_i in range(-2, 2):
        for y_i in range(-2, 2):
            cur_pos = Position(x + x_i, y + y_i)
            cur_amount = map[cur_pos].halite_amount
            if (cur_amount > best_val):
                best_val = cur_amount
                best_pos = cur_pos

    return (best_val > 400), best_pos


game.ready("DepoBot")

# Now that your bot is initialized, save a message to yourself in the log file with some important information.
#   Here, you log here your id, which you can always fetch from the game object by using my_id.
logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))

""" <<<Game Loop>>> """
directions = {}
mode = {}

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
            directions[ship.id] = find_destination(game_map)

        if ship.id not in mode:
            mode[ship.id] = "collect"
        # END OF SETUP

        if good_for_depo(game_map,me,ship) and game.turn_number < 300:
            command_queue.append(ship.make_dropoff())
            break

        if mode[ship.id] == "collect":
            if game_map[ship.position].halite_amount < 450:
                if ship.is_full:
                    directions[ship.id] = closest_depo(game_map,me,ship)
                    mode[ship.id] = "return"
                    break

                if ship.halite_amount > 400:
                    directions[ship.id] = closest_depo(game_map,me,ship)
                    mode[ship.id] = "return"
                else:
                    better, bet_pos = better_around(game_map, ship.position, directions[ship.id])
                    if better:
                        directions[ship.id] = bet_pos

                dir = game_map.naive_navigate(ship, directions[ship.id])
                if dir == Direction.Still:
                    directions[ship.id] = find_destination(game_map)
                    mode[ship.id] = "collect"

                command_queue.append(ship.move(dir))

            # elif ship.position == directions[ship.id]:
            #     directions[ship.id] = closest_depo(game_map,me,ship)
            #     mode[ship.id] = "return"
            #     command_queue.append(ship.move(game_map.naive_navigate(ship, directions[ship.id])))

            else:
                command_queue.append(ship.stay_still())

        elif mode[ship.id] == "return":
            if ship.position == closest_depo(game_map,me,ship):
                directions[ship.id] = find_destination(game_map)
                mode[ship.id] = "collect"

            command_queue.append(ship.move(game_map.naive_navigate(ship, directions[ship.id])))



    # If the game is in the first 200 turns and you have enough halite, spawn a ship.
    # Don't spawn a ship if you currently have a ship at port, though - the ships will collide.
    if len(me.get_ships()) < 1:
        command_queue.append(me.shipyard.spawn())
    else:
        if me.halite_amount >= 2500 and len(me.get_ships()) < 6 and not game_map[me.shipyard].is_occupied and game.turn_number < 200:
            command_queue.append(me.shipyard.spawn())

    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)
