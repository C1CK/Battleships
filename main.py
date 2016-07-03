import time
import random
import modules.robotNames


class tile(object):
    """Object for all tiles."""
    def __init__(self, _map, location):
        """Create blank entity."""
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
        Return True if any ships adjacent to location
        :return: Bool.
        """
        cardinals = [-1, -self.map.length, +1, +self.map.length]
        for index, item in enumerate(cardinals):
            if self.location+item < self.map.length**2 - 1:
                if self.map.array[self.location+item].entity == "ship":
                    return True

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
            self.length = random.randint(1, maxLength)
            if self.length <= self.homeMap.length:
                valid = True

    def validShipLocation(self):
        if self.location.hasAdjacentShip():
            return False, "Ship adjacent to chosen location"
        if self.location.availableSpace(self.orientation, self.offset) < self.length:
            return False, "Inadequate space to place ship"
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


class player(object):
    """Base class for all players."""
    def __init__(self, lengthOfMap):
        """
        Create map class for all child classes.
        :param lengthOfMap: Int.
        """
        self.map = map_(lengthOfMap)


class AI(player):
    """Object for AI player, derived from player base class."""
    def __init__(self, lengthOfMap):
        """
        Assign name, place ship, create blank list for hits, and create array for tested directions.
        :param lengthOfMap: Int.
        """
        super().__init__(lengthOfMap)
        self.__assignName()
        self.__placeShip()
        self.hits = []
        self.testedDirections = {
            -1: None,
            1: None,
            -10: None,
            10: None
        }  # stores info on checked directions in the format left; right; up; down.

    def __assignName(self):
        """Assign a name for the AI"""
        self.name = modules.robotNames.newName()

    def __legacyplaceShip(self):
        """place own ship with random parameters."""
        shipLoc = random.randint(0, self.map.length ** 2)
        shipOrientation = random.choice(["H", "V"])
        if shipOrientation == "H":
            maxLength = self.map.length - (shipLoc % self.map.length)
            shipLength = random.randint(1, maxLength)
            shipOffset = 1
        else:
            maxLength = int(shipLoc / self.map.length)
            shipLength = random.randint(1, maxLength)
            shipOffset = -self.map.length
        self.map.placeShip(shipLoc, shipLength, shipOffset)

    def __placeShip(self):
        """place own ships with a total length equal to totalLength"""
        while self.shipsLeft > 0:
            tempShip = ship(self.map)
            tempShip.place(self.shipsLeft)
            self.shipsLeft -= tempShip.length
            del tempShip

    def __chooseUntargetedLocations(self, targetMap):
        """
        return all un targeted locations.
        :param targetMap: Map_ class
        :return: List, all un targeted directions
        """
        untargetedLocations = []
        print(targetMap.array)
        for index, item in enumerate(targetMap.array):
            if item.entity != "targeted":
                untargetedLocations.append(index)
        return untargetedLocations

    def __chooseValidShifts(self, hitsIndex, targetMap):
        """
        return a list of valid shift, which haven't been checked and don't run off the end of the map
        :param hitsIndex: Int, index location of hit to check.
        :param targetMap: Map_ class.
        :return: List, all valid directions to attack.
        """
        validDirections = []
        hitToCheck = self.hits[hitsIndex]
        length = targetMap.length
        if (int(hitToCheck / length) == int((hitToCheck - 1) / length)) and (
                    self.testedDirections[-1] is None):  # if y didn't change
            validDirections.append(-1)
        if (int(hitToCheck / length) == int((hitToCheck + 1) / length)) and (
                    self.testedDirections[+1] is None):  # if y didn't change
            validDirections.append(1)
        if (hitToCheck % length == (hitToCheck - 10) % length) and (
                    self.testedDirections[-10] is None):  # if x didn't change
            validDirections.append(-10)
        if (hitToCheck % length == (hitToCheck + 10) % length) and (
                    self.testedDirections[+10] is None):  # if x didn't change
            validDirections.append(10)
        return validDirections

    def __noneHit(self, targetMap):
        """
        Call attack on random location.
        :param targetMap: Map_ class.
        """
        hitLoc = random.choice(self.__chooseUntargetedLocations(targetMap))
        if targetMap.array[hitLoc].attack() is True:
            self.hits.append(hitLoc)

    def __unknownDirection(self, targetMap):
        """
        Call attack to check cardinal directions surrounding initial hit.
        :param targetMap: Map_ class.
        """
        hitShift = random.choice(self.__chooseValidShifts(0, targetMap))
        hitLoc = self.hits[0] + hitShift
        if targetMap.array[hitLoc].attack() is True:
            self.hits.append(hitLoc)
            self.testedDirections[hitShift] = True  # indicate direction for future testing
        else:
            self.testedDirections[hitShift] = False  # indicate direction as checked

    def __knownDirection(self, targetMap):
        """
        Call attack to check cardinal directions surrounding latest hit.
        :param targetMap: Map_ class.
        """
        hitShift = random.choice(self.__chooseValidShifts(len(self.hits) - 1, targetMap))
        hitLoc = self.hits[len(self.hits) - 1] + hitShift
        if targetMap.array[hitLoc].attack() is True:
            self.hits.append(hitLoc)
        else:
            self.testedDirections[hitShift] = False  # indicate that this direction is now invalid

    def attack(self, targetMap):
        """
        Call attack on an appropriate location using known information.
        :param targetMap: Map_ class.
        """
        if len(self.hits) == 0:
            self.__noneHit(targetMap)
        elif not (True in self.testedDirections):
            self.__unknownDirection(targetMap)
        elif True in self.testedDirections:
            self.__knownDirection(targetMap)


class easyAI(AI):
    """Easy difficulty AI, designed to make obvious errors in judgement and play worse than a normal human."""
    def __init__(self, lengthOfMap):
        """
        Initialize easyAI with fewer ships than standard.
        :param lengthOfMap: Int
        """
        self.shipsLeft = 8
        super().__init__(lengthOfMap)

    def attack(self, targetMap):
        """
        Call attack on appropriate location, has 20% chance to hit a random target.
        :param targetMap: Map_ class
        """
        chanceToFail = random.randint(0,100)
        if chanceToFail < 20:
            self.__noneHit(targetMap)
        elif len(self.hits) == 0:
            self.__noneHit(targetMap)
        elif not (True in self.testedDirections):
            self.__unknownDirection(targetMap)
        elif True in self.testedDirections:
            self.__knownDirection(targetMap)


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
        Call the player object contructor and assign a name and place ship.
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

    def attack(self, targetMap):
        """
        Take an input and attack using the given input.
        :param targetMap: Map_ class.
        """
        targetMap.displayMap(False)
        attackLoc = int(input("Where are you attacking {}? ".format(self.name)))
        if targetMap.array[attackLoc].attack() is True:
            print("Hit!")
        else:
            print("Miss")
        time.sleep(1)


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
    elif AIOrPlayer == "AIAI":
        playerOne = setupAI(length)
        playerTwo = setupAI(length)
    while True:
        playerOne.attack(playerTwo.map)
        cls()
        if playerTwo.map.hasShips() is False:
            displayFinalScreen("{} has won!".format(playerOne.name), playerOne, playerTwo)
            break
        playerTwo.attack(playerOne.map)
        cls()
        if playerOne.map.hasShips() is False:
            displayFinalScreen("{} has won!".format(playerTwo.name), playerOne, playerTwo)
            break


main()
