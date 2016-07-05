import time
import random
import modules.robotNames


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
            if (self.location + item < self.map.length**2 - 1) and (self.location + item >= 0):
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
            while self.location + count * offset >= 0:
                count += 1
        return count


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
            if (self.location + item < self.map.length**2 - 1) and (self.location + item >= 0):
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
            if (self.location + item < self.map.length**2 - 1) and (self.location + item >= 0):
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
            if (self.location + item < self.map.length**2 - 1) and (self.location + item >= 0):
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
        while True:
            self.location = random.choice(self.homeMap.array)
            if self.validShipLocation()[0] is True:
                break

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
        if self.orientation is None:
            self.__chooseOrientation()
        if self.length is None:
            self.__chooseLength(maxLength)
        if self.location is None:
            self.__chooseLocation()
        self.homeMap.placeShip(self.location.location, self.length, self.offset)


class map_(object):
    """Object for each player's map."""
    def __init__(self, length):
        """
        Create array and save length.
        :param length: Int, length of map array to create
        """
        self.array = []
        self.length = length
        for x in range(0, length**2):
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
        for x in range(0, length**2):
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
            if location + item < self.length**2 - 1:
                self.array[location + item].entity = "cardinalCheck"

    def horizontalShip(self):
        """Remove "cardinalCheck" markers and place "shipCheck" markers for horizontal locations."""
        for index, item in enumerate(self.array):
            if item.hasVerticalShip() is True:
                item.entity = "impossible"
            elif item.hasHorizontalShip() is True:
                item.entity = "shipCheck"

    def verticalShip(self):
        """Remove "cardinalCheck" markers and place "shipCheck" markers for vertical locations."""
        for index, item in enumerate(self.array):
            if item.hasHorizontalShip() is True:
                item.entity = "impossible"
            elif item.hasVerticalShip() is True:
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
        """Replace vertical "cardinalCheck" with "probable" markers."""
        for index, item in enumerate(self.array):
            if item.hasVerticalShip() is True:
                item.entity = "likelyCardinal"

    def verticalChecked(self):
        """Replace horinzontal "cardinalCheck" with "probable" markers."""
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
        Mark next cardinal as shipCheck
        :param location: Index.
        """
        horizontals = [-1, +1]
        verticals = [-self.length, +self.length]
        if self.array[location].hasHorizontalShip() is True:
            directionToCheck = horizontals
        else:
            directionToCheck = verticals
        for index, item in enumerate(directionToCheck):
            if (location + item < self.length ** 2 - 1) and (location + item >= 0):
                if self.array[location + item].entity == "possible":
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
        self.name = modules.robotNames.newName()

    def __placeShip(self):
        """place own ships with a total length equal to totalLength"""
        while self.shipsLeft > 1:
            tempShip = ship(self.map)
            tempShip.place(self.shipsLeft)
            self.shipsLeft -= tempShip.length
            del tempShip

    def __callAttack(self, location):
        """
        call attack and update the knowledgeMap.
        :param location: index.
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
            if any(item.entity == "shipCheck" for index, item in enumerate(self.knowledge.array)):
                self.knowledge.sunkShip()
        if (attackInfo == "possible") and (self.knowledge.array[location].entity == "hit"):
            self.knowledge.shipLocated(location)
        if (attackInfo == "cardinalCheck") and (self.knowledge.array[location].entity == "hit"):
            self.knowledge.cardinalConfirmed(location)
        elif (attackInfo == "cardinalCheck") and (self.knowledge.array[location].entity != "hit"):
            self.knowledge.resetCardinalPriorities()
            self.knowledge.cardinalChecked(location)
        if (attackInfo == "likelyCardinal") and (self.knowledge.array[location].entity == "hit"):
            self.knowledge.cardinalConfirmed(location)
        elif (attackInfo == "likelyCardinal") and (self.knowledge.array[location].entity != "hit"):
            self.knowledge.resetCardinalPriorities()
            self.knowledge.cardinalChecked(location)

    def attack(self):
        """Call attack on appropriate location"""
        highestPriority = self.knowledge.highestPriority()
        locationsToRandomise = []
        for index, item in enumerate(self.knowledge.array):
            if item.entity == highestPriority:
                locationsToRandomise.append(index)
        locationToAttack = random.choice(locationsToRandomise)
        hit = self.__callAttack(locationToAttack)
        self.__updateKnowledge(locationToAttack, highestPriority)
        return hit


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
        self.map.displayMap(False)
        while self.shipsLeft > 0:
            tempShip = ship(self.map)
            print("Remaining ship tiles needed : {}".format(self.shipsLeft))
            tempShip.location = self.map.array[int((input("Where is the ship? ")))]
            tempShip.orientation = input("What is the orientation (V,H)? ")
            if tempShip.orientation == "H":
                tempShip.offset = +1
            else:
                tempShip.offset = -self.map.length
            tempShip.length = int(input("What is the length? "))
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
        self.targetMap.displayMap(False)
        attackLoc = int(input("Where are you attacking {}? ".format(self.name)))
        if self.targetMap.array[attackLoc].attack() is True:
            print("Hit!")
            time.sleep(1)
            return True
        else:
            print("Miss")
            time.sleep(1)
            return False


def displayFinalScreen(endMessage, playerOne, playerTwo):
    """
    Print the two player's maps and display an end message.
    :param endMessage: String, message ending the maps.
    :param playerOne: Player class
    :param playerTwo: Player class
    """
    cls()
    print("{}'s Map:".format(playerOne.name))
    print("\n", end="")
    playerOne.map.displayMap(True)
    print("\n\n", end="")
    print("{}'s Map:".format(playerTwo.name))
    print("\n", end="")
    playerTwo.map.displayMap(True)
    print(endMessage)


def cls():
    """Print 100 new lines."""
    print("\n"*100)


def setupAI(length):
    """
    return an AI class of difficulty given.
    :param length: Int.
    :return: AI class.
    """
    diff = input("What is the difficulty (E/M/H/P)? ")
    if diff == "E":
        AIObject = easyAI(length)
    elif diff == "M":
        AIObject = mediumAI(length)
    elif diff == "H":
        AIObject = hardAI(length)
    elif diff == "P":
        AIObject = AI(length)
    return AIObject


def main():
    """Call everything necessary to start game"""
    random.seed(int(time.time()))
    length = int(input("What is the length of the maps? "))
    AIOrPlayer = input("What is the game configuration? (PP/PAI/AIAI)? ").upper()
    if AIOrPlayer == "PP":
        playerOne = human(length)
        cls()
        playerTwo = human(length)
        cls()
    elif AIOrPlayer == "PAI":
        playerOne = human(length)
        cls()
        playerTwo = setupAI(length)
    else:
        playerOne = setupAI(length)
        playerTwo = setupAI(length)
    playerOne.targetMap = playerTwo.map
    playerTwo.targetMap = playerOne.map
    while True:
        while True:
            cls()
            if playerOne.attack() is False:
                break
        playerTwo.map.displayMap(True)
        if playerTwo.map.hasShips() is False:
            displayFinalScreen("{} has won!".format(playerOne.name), playerOne, playerTwo)
            break
        while True:
            cls()
            if playerTwo.attack() is False:
                break
        playerOne.map.displayMap(True)
        if playerOne.map.hasShips() is False:
            displayFinalScreen("{} has won!".format(playerTwo.name), playerOne, playerTwo)
            break


main()
