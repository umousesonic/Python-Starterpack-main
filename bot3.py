from networking.io import Logger
from game import Game
from api import game_util
from model.position import Position
from model.decisions.move_decision import MoveDecision
from model.decisions.action_decision import ActionDecision
from model.decisions.buy_decision import BuyDecision
from model.decisions.harvest_decision import HarvestDecision
from model.decisions.plant_decision import PlantDecision
from model.decisions.do_nothing_decision import DoNothingDecision
from model.tile_type import TileType
from model.item_type import ItemType
from model.crop_type import CropType
from model.upgrade_type import UpgradeType
from model.game_state import GameState
from model.player import Player
from api.constants import Constants

import random

logger = Logger()
constants = Constants()

global targetPosition

def move_to_index(my_player, x, y):
    x_diff = abs(my_player.position.x - x)
    y_diff = abs(my_player.position.y - y)
    if x_diff > 10:
        if x > my_player.position.x:
            decision = Position(my_player.position.x + 10, my_player.position.y)
        else:
            decision = Position(my_player.position.x - 10, my_player.position.y)
    elif y_diff > 10:
        if y > my_player.position.y:
            decision = Position(my_player.position.x, my_player.position.y + 10)
        else:
            decision = Position(my_player.position.x, my_player.position.y - 10)
    else:
        if x > my_player.position.x:
            decision = Position(my_player.position.x + x_diff, my_player.position.y)
        else:
            decision = Position(my_player.position.x - x_diff, my_player.position.y)

        y_diff = 10 - x_diff
        if y > my_player.position.y:
            decision = Position(my_player.position.x, my_player.position.y + y_diff)
        else:
            decision = Position(my_player.position.x, my_player.position.y - y_diff)

    return MoveDecision(decision)

def get_move_decision(game: Game) -> MoveDecision:
    global targetPosition
    game_state: GameState = game.get_game_state()
    my_player: Player = game_state.get_my_player()
    current_turn = game_state.turn

    if current_turn >= 1 and current_turn <= 3:
        global targetPosition
        targetPosition = Position(15, 0)
        return move_to_index(my_player, targetPosition.x, targetPosition.y)
    elif current_turn >= 4 and current_turn <= 5:
        global targetPosition
        opp_player = game_state.get_opponent_player()
        if opp_player.x <= 15:
            x = 4
        else:
            x = 25
        targetPosition = Position(x, 5)
        return move_to_index(my_player, targetPosition.x, targetPosition.y)
    elif current_turn >= 6 and current_turn <= 12:
        global targetPosition
        targetPosition = Position(my_player.position.x, my_player.position.y)
        return move_to_index(my_player, my_player.position.x, my_player.position.y)
    elif current_turn >= 13 and current_turn <= 15:
        global targetPosition
        targetPosition = Position(15, 0)
        return move_to_index(my_player, targetPosition.x, targetPosition.y)

    
    return MoveDecision(Position(0, 0))


def get_action_decision(game: Game) -> ActionDecision:
    """
    Returns an action decision for the turn given the current game state.
    This is part 2 of 2 of the turn.

    There are multiple action decisions that you can return here: BuyDecision,
    HarvestDecision, PlantDecision, or UseItemDecision.

    After this action, the next turn will begin.

    :param: game The object that contains the game state and other related information
    :returns: ActionDecision A decision for the bot to make this turn
    """
    game_state: GameState = game.get_game_state()
    #logger.debug(f"[Turn {game_state.turn}] Feedback received from engine: {game_state.feedback}")

    # Select your decision here!
    my_player: Player = game_state.get_my_player()
    pos: Position = my_player.position
    # Let the crop of focus be the one we have a seed for, if not just choose a random crop
    crop = max(my_player.seed_inventory, key=my_player.seed_inventory.get) \
        if sum(my_player.seed_inventory.values()) > 0 else random.choice(list(CropType))

    # # Get a list of possible harvest locations for our harvest radius
    # possible_harvest_locations = []
    # harvest_radius = my_player.harvest_radius
    # for harvest_pos in game_util.within_harvest_range(game_state, my_player.name):
    #     if game_state.tile_map.get_tile(harvest_pos.x, harvest_pos.y).crop.value > 0:
    #         possible_harvest_locations.append(harvest_pos)

    # #logger.debug(f"Possible harvest locations={possible_harvest_locations}")

    # # If we can harvest something, try to harvest it
    # if len(possible_harvest_locations) > 0:
    #     decision = HarvestDecision(possible_harvest_locations)
    # If not but we have that seed, then try to plant it in a fertility band
    if my_player.seed_inventory[crop] > 0 and \
            game_state.tile_map.get_tile(pos.x, pos.y).type != TileType.GREEN_GROCER and \
            game_state.tile_map.get_tile(pos.x, pos.y).type.value >= TileType.F_BAND_OUTER.value:
        #logger.debug(f"Deciding to try to plant at position {pos}")
        decision = PlantDecision([crop], [pos])
    # If we don't have that seed, but we have the money to buy it, then move towards the
    # green grocer to buy it
    elif my_player.money >= crop.get_seed_price() and \
        game_state.tile_map.get_tile(pos.x, pos.y).type == TileType.GREEN_GROCER:
        #logger.debug(f"Buy 1 of {crop}")
        decision = BuyDecision([crop], [1])
    # If we can't do any of that, then just do nothing (move around some more)
    else:
        #logger.debug(f"Couldn't find anything to do, waiting for move step")
        decision = DoNothingDecision()

    #logger.debug(f"[Turn {game_state.turn}] Sending ActionDecision: {decision}")


    global targetPosition
    game_state: GameState = game.get_game_state()
    my_player: Player = game_state.get_my_player()
    current_turn = game_state.turn

    if current_turn >= 1 and current_turn <= 3:
        global targetPosition
        if targetPosition.x == my_player.position.x and targetPosition.y == my_player.position.y:
            return BuyDecision([CropType.POTATO], [5])
    elif current_turn >= 4 and current_turn <= 5:
        global targetPosition
        if targetPosition.x == my_player.position.x and targetPosition.y == my_player.position.y:
            return PlantDecision([CropType.POTATO, CropType.POTATO, CropType.POTATO, CropType.POTATO, CropType.POTATO], 
                                 [])
        opp_player = game_state.get_opponent_player()
        if opp_player.x <= 15:
            x = 4
        else:
            x = 25
        targetPosition = Position(x, 5)
        return move_to_index(my_player, targetPosition.x, targetPosition.y)
    elif current_turn >= 6 and current_turn <= 12:
        return move_to_index(my_player, my_player.position.x, my_player.position.y)
    elif current_turn >= 13 and current_turn <= 15:
        global targetPosition
        targetPosition = Position(15, 0)
        return move_to_index(my_player, targetPosition.x, targetPosition.y)

    return DoNothingDecision()


def main():
    """
    Competitor TODO: choose an item and upgrade for your bot
    """
    game = Game(ItemType.COFFEE_THERMOS, UpgradeType.SCYTHE)

    while (True):
        try:
            game.update_game()
        except IOError:
            exit(-1)
        game.send_move_decision(get_move_decision(game))

        try:
            game.update_game()
        except IOError:
            exit(-1)
        game.send_action_decision(get_action_decision(game))


if __name__ == "__main__":
    main()
