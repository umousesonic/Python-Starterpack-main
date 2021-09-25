# if your collab is working leave ur name here: Elaine, Tianshu
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
from enum import Enum

logger = Logger()
constants = Constants()


allSeeds = dict()
allPlantedCrops = []
allHarvestableCrops = dict()


class STATE(Enum):
    BUY = 1
    PLANT = 2
    HARVEST = 3
    BANDIT = 4
    SELL = 5



CURRENT_STATE = STATE.BUY

dead_counter = 0
    

def getAllHarvestableTiles(game: Game):
    #format: [[tile(object), x, y], [tile, x, y], [tile, x, y] ....]
    myTiles = getTiles(game)
    result = []
    
    for y, row in enumerate(myTiles):
        for x, ele in enumerate(row):
            if (ele.crop.type != "NONE"):
                temp = [ele, x, y]
                result.append(temp)
    
    return result

def gotoGrocer(my_player: Player):
    tempX = 15
    tempY = 0
    if abs(my_player.position.x - tempX) >= 10:
        tempX = my_player.position.x + 10 if (tempX - my_player.position.x) > 0 else my_player.position.x - 10
        tempY = my_player.position.y
    if abs(my_player.position.y - tempY) >= 10:
        tempX = my_player.position.x
        tempY = my_player.position.y + 10 if (tempY - my_player.position.y) > 0 else my_player.position.y - 10
    decision = MoveDecision(Position(tempX, tempY))
    return decision

def gotoPlot(my_player: Player, game_state: GameState, crop_time):
    yPos = GetOptimalPlantCords(game_state, crop_time)
    if len(allPlantedCrops) == 0:
        xPos = 1
    else:
        xPos = allPlantedCrops[-1][1] + 2

    tempX = xPos
    tempY = yPos
    if abs(my_player.position.x - tempX) >= 10:
        tempX = my_player.position.x + 10 if (tempX - my_player.position.x) > 0 else my_player.position.x - 10
        tempY = my_player.position.y
    if abs(my_player.position.y - tempY) >= 10:
        tempX = my_player.position.x
        tempY = my_player.position.y + 10 if (tempY - my_player.position.y) > 0 else my_player.position.y - 10
    decision = MoveDecision(Position(tempX, tempY))
    return Position(xPos, yPos)
    

def getTiles(game: Game):
    game_state = game.get_game_state()
    myTileMap = game_state.tile_map
    myTiles = myTileMap.tiles
    return myTiles

def IsCanReach(x, y):
    return x+y<=10

def GetOptimalBandCords(game_state: GameState):
    currentTurn = game_state.turn
    return (currentTurn - 13) // 3

def GetOptimalPlantCords(game_state: GameState, crop_time):
    optimalBand = GetOptimalBandCords(game_state)
    return max(constants.GRASS_ROWS + 2, crop_time + optimalBand)

# bandit strate functions
def BanditStrateMovement(my_player: Player, myHarvestableTiles):
    if IsCanReach(myHarvestableTiles[0][1], myHarvestableTiles[0][2]):
        decision = MoveDecision(Position(myHarvestableTiles[0][1], myHarvestableTiles[0][2]))
    else:
        tempX = myHarvestableTiles[0+dead_counter][1]
        tempY = myHarvestableTiles[0+dead_counter][2]
        if abs(my_player.position.x - tempX) >= 10:
            tempX = my_player.position.x + 10 if (tempX - my_player.position.x) > 0 else my_player.position.x - 10
            tempY = my_player.position.y
        if abs(my_player.position.y - tempY) >= 10:
            tempX = my_player.position.x
            tempY = my_player.position.y + 10 if (tempY - my_player.position.y) > 0 else my_player.position.y - 10
        decision = MoveDecision(Position(tempX, tempY))
        if tempX == my_player.position.x and tempY == my_player.position.y:
            dead_counter += 1
    return decision
            


############################### MAIN MOVE DECISION ##########################################
def get_move_decision(game: Game) -> MoveDecision:
    game_state: GameState = game.get_game_state()
    my_player: Player = game_state.get_my_player()
    pos: Position = my_player.position
    decision = MoveDecision(pos)
    # potato strate
    if game_state.turn < 13: 
        if CURRENT_STATE == STATE.BUY:
            decision = MoveDecision(gotoGrocer(my_player))
        elif CURRENT_STATE == STATE.PLANT:
            decision = MoveDecision(gotoPlot(my_player, game_state, 4))
    elif CURRENT_STATE == STATE.SELL:
        decision = MoveDecision(gotoGrocer(my_player))
    else:
        # Bandit mode
        myHarvestableTiles = getAllHarvestableTiles(game)
        if len(myHarvestableTiles) > 0:
            decision = BanditStrateMovement(my_player, myHarvestableTiles)

        # If we have something to sell that we harvested, then try to move towards the green grocer tiles
        elif random.random() < 0.5 and \
                (sum(my_player.seed_inventory.values()) == 0 or len(my_player.harvested_inventory)):
            logger.debug("Moving towards green grocer")
            decision = MoveDecision(Position(constants.BOARD_WIDTH // 2, max(0, pos.y - constants.MAX_MOVEMENT)))
        # If not, then move randomly within the range of locations we can move to
        else:
            pos = random.choice(game_util.within_move_range(game_state, my_player.name))
            logger.debug("Moving randomly")
            decision = MoveDecision(pos)

    logger.debug(CURRENT_STATE)
    return decision


def get_action_decision(game: Game) -> ActionDecision:
    global CURRENT_STATE
    '''
    This is the part 2 of your action, where you plant/use item/harvest
    '''
    
    
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
    logger.debug(f"[Turn {game_state.turn}] Feedback received from engine: {game_state.feedback}")

    # Select your decision here!
    my_player: Player = game_state.get_my_player()
    pos: Position = my_player.position
    # Let the crop of focus be the one we have a seed for, if not just choose a random crop
    crop = max(my_player.seed_inventory, key=my_player.seed_inventory.get) \
        if sum(my_player.seed_inventory.values()) > 0 else random.choice(list(CropType))

    # Get a list of possible harvest locations for our harvest radius
    possible_harvest_locations = []
    harvest_radius = my_player.harvest_radius
    for harvest_pos in game_util.within_harvest_range(game_state, my_player.name):
        if game_state.tile_map.get_tile(harvest_pos.x, harvest_pos.y).crop.value > 0:
            possible_harvest_locations.append(harvest_pos)

    logger.debug(f"Possible harvest locations={possible_harvest_locations}")

    # If we can harvest something, try to harvest it
    if len(possible_harvest_locations) > 0:
        decision = HarvestDecision(possible_harvest_locations)
    # If not but we have that seed, then try to plant it in a fertility band
    elif my_player.seed_inventory[crop] > 0 and \
            game_state.tile_map.get_tile(pos.x, pos.y).type != TileType.GREEN_GROCER and \
            game_state.tile_map.get_tile(pos.x, pos.y).type.value >= TileType.F_BAND_OUTER.value:
        logger.debug(f"Deciding to try to plant at position {pos}")
        decision = PlantDecision([crop], [pos])

    # If we don't have that seed, but we have the money to buy it, then move towards the
    # green grocer to buy it
    # elif my_player.money >= crop.get_seed_price() and \
    #     game_state.tile_map.get_tile(pos.x, pos.y).type == TileType.GREEN_GROCER:
    #     logger.debug(f"Buy 1 of {crop}")
    #     decision = BuyDecision([crop], [1])
    # # If we can't do any of that, then just do nothing (move around some more)
    else:
        logger.debug(f"Couldn't find anything to do, waiting for move step")
        decision = DoNothingDecision()

    logger.debug(f"[Turn {game_state.turn}] Sending ActionDecision: {decision}")
    logger.debug(my_player.harvested_inventory)


    if game_state.turn > 13:
        CURRENT_STATE = STATE.HARVEST

    elif CURRENT_STATE == STATE.BUY:
        if game_state.tile_map.get_tile(pos.x, pos.y).type == TileType.GREEN_GROCER:
            decision = BuyDecision([CropType.POTATO], [10])
            # TODO: if there are harvestable crop change to STATE.HARVEST
            CURRENT_STATE = STATE.PLANT
    elif CURRENT_STATE == STATE.PLANT:
        CURRENT_STATE = STATE.HARVEST
        
    if (game_state.turn % 10 == 0 and len(my_player.harvested_inventory) != 0) or (CURRENT_STATE == STATE.SELL and len(my_player.harvested_inventory) != 0):
        CURRENT_STATE = STATE.SELL
    

    return decision


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
