import time
import random
from sys import modules

import externals.robotNames


class FunctionFailedError(Exception):
    """Exception for an undefined error occurring in a function."""

    def __init__(self, function):
        self.function = function
        Exception.__init__(self, "Unspecified Error Occurred In {}".format(function))


class tile(object):
    """Object for all tiles."""

    def __init__(self, _map, location):
        """Create blank entity and save location and map data"""
        self.entity = ""
        self.map = _map
        self.location = location

    def getImage(self):
        """
        Return image to display in terminal.
        :return: Char.
        """
        if self.entity == "":
            return "□"
        if self.entity == "ship":
            return "○"
        if self.entity == "destroyedShip":
            return "⊛"
        if self.entity == "targeted":
            return "■"

    def attack(self):
        """
        Return True if hit ship and store new cell data.
        :return: Bool.
        """
        if self.entity == "ship":
            self.entity = "destroyedShip"
            return True
        elif self.entity == "destroyedShip":
            return True
        else:
            self.entity = "targeted"
            return False

    def hasAdjacentShip(self):
        """
        Return True if any ships adjacent to location.
        :return: Bool.
        """
        cardinals = [-1, -self.map.length, +1, +self.map.length]
        for index, item in enumerate(cardinals):
            if self.validOffset(item):
                if self.map.array[self.location + item].entity == "ship":
                    return True
        return False

    def availableSpace(self, orientation, offset):
        """
        Return available space for a ship
        :param orientation: Char.
        :param offset: Int.
        :return:
        """
        count = 0
        if orientation == "H":
            while int(self.location / self.map.length) == int((self.location + count) / self.map.length):
                count += 1
        else:
            while (self.location + count * offset >= 0) and (self.location + count * offset < self.map.length ** 2):
                count += 1
        return count

    def validOffset(self, offset):
        """
        Return True if the offset given is valid.
        :param offset: Int.
        :return: Bool.
        """
        if (self.location + offset < self.map.length ** 2) and (self.location + offset >= 0):
            if abs(offset) == 1:
                if int(self.location / self.map.length) == int((self.location + offset) / self.map.length):
                    return True
            if abs(offset) == self.map.length:
                if (self.location + offset >= 0) and (self.location + offset < self.map.length ** 2):
                    return True
        return False


class knowledgeTile(tile):
    """Object for holding AI knowledge regarding a tile"""

    def __init__(self, _map, location):
        """Initialize as a possible location for a ship and save location and map data"""
        self.entity = "possible"
        self.map = _map
        self.location = location

    def getImage(self):
        """
        Return image to display in terminal (debugging).
        :return: Char.
        """
        if self.entity == "possible":
            return "□"
        if self.entity == "hit":
            return "⊛"
        if self.entity == "completedShip":
            return "⊛"
        if self.entity == "impossible":
            return "■"

    def hasAdjacentShip(self):
        """
        Return True if any completeShips adjacent to location.
        :return: Bool.
        """
        cardinals = [-1, -self.map.length, +1, +self.map.length]
        for index, item in enumerate(cardinals):
            if self.validOffset(item):
                if self.map.array[self.location + item].entity == "completedShip":
                    return True
        return False

    def hasVerticalShip(self):
        """
        Return True if any hits north or south of location.
        :return: Bool.
        """
        verticals = [-self.map.length, +self.map.length]
        for index, item in enumerate(verticals):
            if self.validOffset(item):
                if self.map.array[self.location + item].entity == "hit":
                    return True
        return False

    def hasHorizontalShip(self):
        """
        Return True if any hits east or west of location.
        :return: Bool.
        """
        horizontals = [-1, +1]
        for index, item in enumerate(horizontals):
            if self.validOffset(item):
                if self.map.array[self.location + item].entity == "hit":
                    return True
        return False


class ship(object):
    """Object for ships, used only for ship creation, discarded afterwards."""

    def __init__(self, homeMap):
        """
        Assign homemap, length, location and orientation.
        :param homeMap: _Map class
        """
        self.homeMap = homeMap
        self.length = None
        self.location = None
        self.orientation = None
        self.offset = None

    def __chooseLocation(self):
        """Choose a location based on length and orientation"""
        fails = 0
        while True:
            self.location = random.choice(self.homeMap.array)
            if self.validShipLocation()[0] is True:
                break
            if fails > 10:
                raise FunctionFailedError(__name__)
            fails += 1

    def __chooseOrientation(self):
        """Choose an orientation randomly"""
        self.offset = random.choice([+1, -self.homeMap.length])
        if self.offset == +1:
            self.orientation = "H"
        else:
            self.orientation = "V"

    def __chooseLength(self, maxLength):
        """
        Choose a length for the ship randomly
        :param maxLength: Int, maximum length of ship
        """
        valid = False
        while valid is False:
            self.length = random.randint(2, maxLength)
            if self.length <= self.homeMap.length:
                valid = True

    def validShipLocation(self):
        if self.location.availableSpace(self.orientation, self.offset) < self.length:
            return False, "Inadequate space to place ship"
        for i in range(0, self.length):
            if self.homeMap.array[self.location.location + self.offset * i].hasAdjacentShip():
                return False, "Ship adjacent to chosen location"
        return True, "This shouldn't EVER print"

    def place(self, maxLength=0):
        """Calculate any missing values and then place itself onto map"""
        while True:
            try:
                if self.orientation is None:
                    self.__chooseOrientation()
                if self.length is None:
                    self.__chooseLength(maxLength)
                if self.location is None:
                    self.__chooseLocation()
                self.homeMap.placeShip(self.location.location, self.length, self.offset)
                break
            except FunctionFailedError:
                self.__init__(self.homeMap)


class map_(object):
    """Object for each player's map."""

    def __init__(self, length):
        """
        Create array and save length.
        :param length: Int, length of map array to create
        """
        self.array = []
        self.length = length
        for x in range(0, length ** 2):
            self.array.append(tile(self, x))

    def placeShip(self, startingPos, length, offset):
        """
        Place ship onto map array.
        :param startingPos: Int, position for ship to start.
        :param length: Int, length of ship.
        :param offset: Int, whether horizontal or vertical.
        """
        for i in range(0, length):
            self.array[startingPos + (offset * i)].entity = "ship"

    def displayMap(self, shipVis):
        """
        Print map onto the screen.
        :param shipVis: Bool, whether to show unhit ships
        """
        print(" ", end="")
        for i in range(0, self.length):
            print(i, end="")
        for i in range(0, len(self.array)):
            if i % self.length == 0:
                print("\n" + str(i / self.length)[0], end="")
            if (self.array[i].entity == "ship") and (shipVis is False):
                print("□", end="")
            else:
                print(self.array[i].getImage(), end="")
        print("\n", end="")

    def hasShips(self):
        """
        return True if this map has sips.
        :return: Bool.
        """
        for index, item in enumerate(self.array):
            if item.entity == "ship":
                return True
        return False


class knowledgeMap(map_):
    """Object used for tracking AI knowledge"""

    def __init__(self, length):
        """
        Create array and save length.
        :param length:
        """
        self.array = []
        self.length = length
        for x in range(0, length ** 2):
            self.array.append(knowledgeTile(self, x))

    def sunkShip(self):
        """Update knowledge to reflect ship being sunk."""
        for index, item in enumerate(self.array):
            if item.entity == "hit":
                item.entity = "completedShip"
            if item.hasAdjacentShip() is True:
                item.entity = "impossible"

    def shipLocated(self, location):
        """
        Mark four cardinals as "cardinalCheck".
        :param location: Index.
        """
        cardinals = [-1, -self.length, +1, +self.length]
        for index, item in enumerate(cardinals):
            if self.array[location].validOffset(item):
                self.array[location + item].entity = "cardinalCheck"

    def horizontalShip(self):
        """Remove "cardinalCheck" markers and place "shipCheck" markers for horizontal locations."""
        for index, item in enumerate(self.array):
            if item.entity == "cardinalCheck":
                item.entity = "impossible"
            if item.hasVerticalShip() and (item.entity != "hit"):
                item.entity = "impossible"
            if item.hasHorizontalShip() and (item.entity != "hit"):
                item.entity = "shipCheck"

    def verticalShip(self):
        """Remove "cardinalCheck" markers and place "shipCheck" markers for vertical locations."""
        for index, item in enumerate(self.array):
            if item.entity == "cardinalCheck":
                item.entity = "impossible"
            if item.hasHorizontalShip() and (item.entity != "hit"):
                item.entity = "impossible"
            elif item.hasVerticalShip() and (item.entity != "hit"):
                item.entity = "shipCheck"

    def cardinalConfirmed(self, location):
        """
        Call appropriate ship direction function.
        :param location: Index.
        """
        if self.array[location].hasHorizontalShip() is True:
            self.horizontalShip()
        else:
            self.verticalShip()

    def horizontalChecked(self):
        """Replace vertical "cardinalCheck" with "likelyCardinal" markers."""
        for index, item in enumerate(self.array):
            if item.hasVerticalShip() is True:
                item.entity = "likelyCardinal"

    def verticalChecked(self):
        """Replace horizontal "cardinalCheck" with "likelyCardinal" markers."""
        for index, item in enumerate(self.array):
            if item.hasHorizontalShip() is True:
                item.entity = "likelyCardinal"

    def cardinalChecked(self, location):
        """
        Call appropriate ship direction checked function.
        :param location: Index.
        """
        if self.array[location].hasHorizontalShip() is True:
            self.horizontalChecked()
        else:
            self.verticalChecked()

    def resetCardinalPriorities(self):
        """Reset all "likelyCardinal"s to "cardinalCheck"."""
        for index, item in enumerate(self.array):
            if item.entity == "likelyCardinal":
                item.entity = "cardinalCheck"

    def shipCheckHit(self, location):
        """
        Mark next cardinal as "shipCheck"
        :param location: Index.
        """
        horizontals = [-1, +1]
        verticals = [-self.length, +self.length]
        if self.array[location].hasHorizontalShip():
            directionToCheck = horizontals
        elif self.array[location].hasVerticalShip():
            directionToCheck = verticals
        for index, item in enumerate(directionToCheck):
            if self.array[location].validOffset(item):
                if self.array[location + item].entity != "hit":
                    self.array[location + item].entity = "shipCheck"

    def highestPriority(self):
        """
        Return highest priority attack.
        :return: String.
        """
        if any(item.entity == "likelyCardinal" for index, item in enumerate(self.array)):
            return "likelyCardinal"
        if any(item.entity == "cardinalCheck" for index, item in enumerate(self.array)):
            return "cardinalCheck"
        if any(item.entity == "shipCheck" for index, item in enumerate(self.array)):
            return "shipCheck"
        return "possible"


class player(object):
    """Base class for all players."""

    def __init__(self, lengthOfMap):
        """
        Create map class for all child classes.
        :param lengthOfMap: Int.
        """
        self.map = map_(lengthOfMap)
        self.targetMap = None


class AI(player):
    """Object for AI player, derived from player base class."""

    def __init__(self, lengthOfMap):
        """
        Assign name, place ship, and create knowledgeMap to track knowns.
        :param lengthOfMap: Int.
        """
        super().__init__(lengthOfMap)
        self.__assignName()
        self.__placeShip()
        self.knowledge = knowledgeMap(lengthOfMap)

    def __assignName(self):
        """Assign a name for the AI"""
        self.name = externals.robotNames.newName()

    def __placeShip(self):
        """place own ships with a total length equal to totalLength"""
        fails = 0
        while self.shipsLeft > 1:
            tempShip = ship(self.map)
            tempShip.place(self.shipsLeft)
            self.shipsLeft -= tempShip.length
            del tempShip

    def __callAttack(self, location):
        """
        call attack and update the knowledgeMap.
        :param location: Index.
        """
        if self.targetMap.array[location].attack() is True:
            self.knowledge.array[location].entity = "hit"
            return True
        else:
            self.knowledge.array[location].entity = "impossible"
            return False

    def __updateKnowledge(self, location, attackInfo):
        """
        Update knowledgeMap appropriately.
        :param location: Index.
        :param attackInfo: String.
        """
        if (attackInfo == "shipCheck") and (self.knowledge.array[location].entity == "hit"):
            self.knowledge.shipCheckHit(location)
            return "{} shipCheck hit {}".format(self.__class__, location)
        if (attackInfo == "shipCheck") and (
                not any(item.entity == "shipCheck" for index, item in enumerate(self.knowledge.array))):
            self.knowledge.sunkShip()
            return "{} Ship sunk {}".format(self.__class__, location)
        elif (attackInfo == "possible") and (self.knowledge.array[location].entity == "hit"):
            self.knowledge.shipLocated(location)
            return "{} Ship Located {}".format(self.__class__, location)
        elif (attackInfo == "cardinalCheck") and (self.knowledge.array[location].entity == "hit"):
            self.knowledge.resetCardinalPriorities()
            self.knowledge.cardinalConfirmed(location)
            return "{} cardinalCheck hit {}".format(self.__class__, location)
        elif (attackInfo == "cardinalCheck") and (self.knowledge.array[location].entity != "hit"):
            self.knowledge.resetCardinalPriorities()
            self.knowledge.cardinalChecked(location)
            return "{} cardinalCheck miss {}".format(self.__class__, location)
        elif (attackInfo == "likelyCardinal") and (self.knowledge.array[location].entity == "hit"):
            self.knowledge.resetCardinalPriorities()
            self.knowledge.cardinalConfirmed(location)
            return "{} cardinalCheck hit {}".format(self.__class__, location)
        elif (attackInfo == "likelyCardinal") and (self.knowledge.array[location].entity != "hit"):
            self.knowledge.resetCardinalPriorities()
            self.knowledge.cardinalChecked(location)
            return "{} cardinalCheck miss {}".format(self.__class__, location)
        else:
            return "{} {} {}".format(self.__class__, attackInfo, location)

    def attack(self):
        """Call attack on appropriate location"""
        highestPriority = self.knowledge.highestPriority()
        locationsToRandomise = []
        for index, item in enumerate(self.knowledge.array):
            if item.entity == highestPriority:
                locationsToRandomise.append(index)
        try:
            locationToAttack = random.choice(locationsToRandomise)
        except IndexError:
            self.targetMap.displayMap(True)
            return False
        hit = self.__callAttack(locationToAttack)
        logic = self.__updateKnowledge(locationToAttack, highestPriority)
        return hit, logic


class easyAI(AI):
    """Easy difficulty AI, designed to make obvious errors in judgement and play worse than a normal human."""

    def __init__(self, lengthOfMap):
        """
        Initialize easyAI with fewer ships than standard.
        :param lengthOfMap: Int
        """
        self.shipsLeft = 8
        super().__init__(lengthOfMap)


class mediumAI(AI):
    """Medium difficulty AI, designed to be same skill level as a normal human."""

    def __init__(self, lengthOfMap):
        """
        Initialize mediumAI with standard number of ships.
        :param lengthOfMap: Int
        """
        self.shipsLeft = 12
        super().__init__(lengthOfMap)


class hardAI(AI):
    """Hard difficulty AI, designed to use more advanced algorithms and play better than a normal human."""

    def __init__(self, lengthOfMap):
        """
        Initialize hardAI with more ships than standard.
        :param lengthOfMap: Int
        """
        self.shipsLeft = 16
        super().__init__(lengthOfMap)


class human(player):
    """Object for human player, derived from player base class."""

    def __init__(self, lengthOfMap):
        """
        Call the player object constructor and assign a name and place ship.
        :param lengthOfMap: Int.
        """
        super().__init__(lengthOfMap)
        self.shipsLeft = 12
        self.__assignName()
        self.__placeShip()

    def __assignName(self):
        """Ask for user's name."""
        self.name = input("What is your name? ")

    def __placeShip(self):
        """Place ship using information taken in."""
        while self.shipsLeft > 0:
            tempShip = ship(self.map)
            self.map.displayMap(True)
            print("Remaining ship tiles needed : {}".format(self.shipsLeft))
            tempShip.location = self.map.array[inputInt("Where is the ship? ")]
            tempShip.orientation = inputStr("What is the orientation (V,H)? ", ["V", "H"])
            if tempShip.orientation == "H":
                tempShip.offset = +1
            else:
                tempShip.offset = -self.map.length
            tempShip.length = inputInt("What is the length? ")
            valid, error = tempShip.validShipLocation()
            if valid is False:
                print(error)
            else:
                tempShip.place()
                self.shipsLeft -= tempShip.length
                del tempShip

    def attack(self):
        """
        Take an input and attack using the given input, returns True is hit.
        :return: Bool
        """
        while True:
            print("Your Map :", end="\n")
            self.map.displayMap(False)
            print("\n\n", end="")
            print("Opponents Map :", end="\n")
            self.targetMap.displayMap(False)
            print("\n\n", end="")
            attackLoc = inputInt("Where are you attacking {}? ".format(self.name))
            try:
                if self.targetMap.array[attackLoc].attack() is True:
                    print("Hit!")
                    time.sleep(1)
                    return True, "Hit {}".format(attackLoc)
                else:
                    print("Miss")
                    time.sleep(1)
                    return False, "Miss {}".format(attackLoc)
            except IndexError:
                print("Value entered not on map")


class game(object):
    """Game class for usage in main."""

    def __init__(self, mapSize, gameConfig):
        """Initialize mapSize, gameConfig, and players"""
        self.mapSize = mapSize
        self.playerOne = None
        self.playerTwo = None
        self.gameConfig = gameConfig

    def displayFinalScreen(self, endMessage):
        """
        Print Final Game Screen.
        :param endMessage: String.
        """
        print("{}'s Map:".format(self.playerOne.name))
        print("\n", end="")
        self.playerOne.map.displayMap(True)
        print("\n\n", end="")
        print("{}'s Map:".format(self.playerTwo.name))
        print("\n", end="")
        self.playerTwo.map.displayMap(True)
        print("\n\n\n\n", end="")
        print(endMessage)

    def setupAI(self, difficulty):
        """
        Return an AI of difficulty given.
        :param difficulty: Char.
        """
        if difficulty == "E":
            AIObject = easyAI(self.mapSize)
        elif difficulty == "M":
            AIObject = mediumAI(self.mapSize)
        elif difficulty == "H":
            AIObject = hardAI(self.mapSize)
        return AIObject

    def setTargetMaps(self):
        self.playerOne.targetMap = self.playerTwo.map
        self.playerTwo.targetMap = self.playerOne.map

    def setupGame(self):
        if self.gameConfig == "PP":
            self.playerOne = human(self.mapSize)
            cls()
            self.playerTwo = human(self.mapSize)
            cls()
        if self.gameConfig == "PAI":
            self.playerOne = human(self.mapSize)
            cls()
            self.playerTwo = self.setupAI(inputStr("What is the difficulty (E/M/H) ", ["E", "M", "H"]))
        if self.gameConfig == "AIAI":
            self.playerOne = self.setupAI(inputStr("What is the difficulty (E/M/H) ", ["E", "M", "H"]))
            self.playerTwo = self.setupAI(inputStr("What is the difficulty (E/M/H) ", ["E", "M", "H"]))
        self.setTargetMaps()

    def gameLoop(self):
        """
        Run through the game until someone wins, return their object.
        :return: Player.
        """
        playerOneLogic = None
        playerTwoLogic = None
        while True:
            while True:
                cls()
                print(playerTwoLogic, end="\n\n")
                playerOneHit, playerOneLogic = self.playerOne.attack()
                if playerOneHit is False:
                    break
            self.playerTwo.map.displayMap(True)
            if self.playerTwo.map.hasShips() is False:
                self.displayFinalScreen("{} has won!".format(self.playerOne.name))
                return self.playerOne
            while True:
                cls()
                print(playerOneLogic, end="\n\n")
                playerTwoHit, playerTwoLogic = self.playerTwo.attack()
                if playerTwoHit is False:
                    break
            self.playerOne.map.displayMap(True)
            if self.playerOne.map.hasShips() is False:
                self.displayFinalScreen("{} has won!".format(self.playerTwo.name))
                return self.playerTwo

    def AILoop(self):
        """
        Run through the game until someone wins, with limited printing.
        :return: Player.
        """
        while True:
            while True:
                playerOneHit, playerOneLogic = self.playerOne.attack()
                print(playerOneLogic)
                if playerOneHit is False:
                    break
            if self.playerTwo.map.hasShips() is False:
                print("{} has won!".format(self.playerOne.__class__))
                return self.playerOne
            while True:
                playerTwoHit, playerTwoLogic = self.playerTwo.attack()
                print(playerTwoLogic)
                if playerTwoHit is False:
                    break
            if self.playerOne.map.hasShips() is False:
                print("{} has won!".format(self.playerTwo.__class__))
                return self.playerTwo


def cls():
    """Print 100 new lines."""
    print("\n" * 100)


def inputInt(message):
    """
    Take an integer and return it, handling errors.
    :param message: String.
    :return: Int.
    """
    while True:
        try:
            value = int(input(message))
        except ValueError:
            print("Input is not an integer!")
        else:
            return value


def inputStr(message, validEntries):
    """
    Take a string input and return it.
    :param message: String.
    :param validEntries: List.
    :return: String.
    """
    while True:
        value = input(message).upper()
        if value in validEntries:
            return value
        else:
            print("Entry not valid!")


def main():
    """Call everything necessary to start game"""
    random.seed(int(time.time()))
    mapSize = inputInt("What is the length of the maps? ")
    gameConfig = inputStr("What is the game configuration? (PP/PAI/AIAI)? ", ["PP", "PAI", "AIAI"])
    if gameConfig != "AIAI":
        mainGame = game(mapSize, gameConfig)
        mainGame.setupGame()
        mainGame.gameLoop()
        del mainGame
        return 0
    else:
        winners = []
        cycles = inputInt("What is the number of cycles? ")
        while True:
            try:
                difficulty1Class = getattr(modules[__name__], input("What is the first AI's Class? "))
                difficulty2Class = getattr(modules[__name__], input("What is the second AI's Class? "))
                assert isinstance(difficulty1Class(mapSize), AI)
                assert isinstance(difficulty2Class(mapSize), AI)
            except AttributeError:
                print("Input is not a class")
            except (AssertionError, TypeError):
                print("Input is not derived from AI")
            else:
                break
        for i in range(0, cycles):
            cyclesGame = game(mapSize, gameConfig)
            cyclesGame.playerOne = difficulty1Class(mapSize)
            cyclesGame.playerTwo = difficulty2Class(mapSize)
            cyclesGame.setTargetMaps()
            winners.append(cyclesGame.AILoop().__class__)
        print("totals wins for {} : {}".format(difficulty1Class, winners.count(difficulty1Class.__class__)))
        print("totals wins for {} : {}".format(difficulty2Class, winners.count(difficulty2Class.__class__)))


main()
