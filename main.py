import math
import time
import random


class tile(object):
    def __init__(self):
        self.entity = ""

    def getImage(self):
        if self.entity == "":
            return "□"
        if self.entity == "ship":
            return "○"
        if self.entity == "destroyedShip":
            return "⊛"
        if self.entity == "targeted":
            return "■"

    def attack(self):
        if self.entity == "ship":
            self.entity = "destroyedShip"
            return True
        elif self.entity == "destroyedShip":
            return True
        else:
            self.entity = "targeted"
            return False


class map_(object):
    def __init__(self, length):
        self.array = []
        self.length = length
        for x in range(0, length**2):
            self.array.append(tile())

    def placeShip(self, startingPos, length, offset):
        for i in range(0, length):
            self.array[startingPos + (offset * i)].entity = "ship"

    def displayMap(self, shipVis):
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
        for i in range(0, self.length**2):
            if self.array[i].entity == "ship":
                return True
        return False


class player(object):
    def __init__(self, lengthOfMap):
        self.map = map_(lengthOfMap)


class AI(player):
    def __init__(self, lengthOfMap):
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
        self.name = "AI"

    def __placeShip(self):
        """
        place own ship with random parameters.
        """
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

    def __chooseValidShifts(self, hitsIndex, targetMap):
        """
        return a list of valid shift, which haven't been checked and don't run off the end of the map
        :param hitsIndex: index location of hit to check.
        :param targetMap: map class.
        :return: list of all valid directions to attack.
        """
        validDirections = []
        hitToCheck = self.hits[hitsIndex]
        length = targetMap.length
        if (int(hitToCheck / length) == int((hitToCheck - 1) / length)) and (
                    self.testedDirections[-1] is None):  # if y didn't change
            validDirections.append(-1)
        if (int(hitToCheck / length) == int((hitToCheck + 1) / length)) and (
                    self.testedDirections[-1] is None):  # if y didn't change
            validDirections.append(1)
        if (hitToCheck % length == (hitToCheck - 10) % length) and (
                    self.testedDirections[-1] is None):  # if x didn't change
            validDirections.append(-10)
        if (hitToCheck % length == (hitToCheck + 10) % length) and (
                    self.testedDirections[-1] is None):  # if x didn't change
            validDirections.append(10)
        return validDirections

    def __noneHit(self, targetMap):
        """
        Call attack on random location.
        :param targetMap: map class.
        """
        hitLoc = random.randint(0, len(targetMap.array) - 1)
        if targetMap.array[hitLoc].attack() is True:
            self.hits.append(hitLoc)

    def __unknownDirection(self, targetMap):
        """
        Call attack to check cardinal directions surrounding initial hit.
        :param targetMap: map class.
        """
        hitShift = random.choice(
            self.__chooseValidShifts(0, targetMap))
        hitLoc = self.hits[0] + hitShift
        if targetMap.array[hitLoc].attack() is True:
            self.hits.append(hitLoc)
            self.testedDirections[hitShift] = True  # indicate direction for future testing
        else:
            self.testedDirections[hitShift] = False  # indicate direction as checked

    def __knownDirection(self, targetMap):
        """
        Call attack to check cardinal directions surrounding latest hit.
        :param targetMap: map class.
        """
        hitShift = random.choice(
            self.__chooseValidShifts(len(self.hits) - 1, targetMap))
        hitLoc = self.hits[len(self.hits) - 1] + hitShift
        if targetMap.array[hitLoc].attack() is True:
            self.hits.append(hitLoc)
        else:
            self.testedDirections[hitShift] = False  # indicate that this direction is now invalid

    def attack(self, targetMap):
        """
        Call attack on an appropriate location using known information.
        :param
        targetMap: map class.
        """
        if len(self.hits) == 0:
            self.__noneHit(targetMap)
        elif not (True in self.testedDirections):
            self.__unknownDirection(targetMap)
        elif True in self.testedDirections:
            self.__knownDirection(targetMap)


class human(player):
    def __init__(self, lengthOfMap):
        super().__init__(lengthOfMap)
        self.__assignName()
        self.__placeShip()

    def __assignName(self):
        self.name = input("What is your name? ")

    def __placeShip(self):
        self.map.displayMap(False)
        shipLoc = int(input("Where is {}'s ship? ".format(self.name)))
        shipLength = int(input("What is the length? "))
        shipOrientation = input("What is the orientation (V,H)? ")
        if shipOrientation == "V":
            shipOffset = self.map.length
        if shipOrientation == "H":
            shipOffset = 1
        self.map.placeShip(shipLoc, shipLength, shipOffset)

    def attack(self, targetMap):
        targetMap.displayMap(False)
        attackLoc = int(input("Where are you attacking {}? ".format(self.name)))
        if targetMap.array[attackLoc].attack() is True:
            print("Hit!")
        else:
            print("Miss")
        time.sleep(1)


def displayFinalScreen(endMessage, playerOne, playerTwo):
    """
    print the two players maps and display an end message
    :param endMessage: message ending the maps
    :param playerOne: player class
    :param playerTwo: player class
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


def cls(): print("\n"*100)


def main():
    random.seed(int(time.time()))
    length = int(input("What is the length of the maps? "))
    AIOrPlayer = input("What is the game configuration? (PP/PAI/AIAI)? ").upper()
    if AIOrPlayer == "PP":
        playerOne = human(length)
        playerTwo = human(length)
    elif AIOrPlayer == "PAI":
        playerOne = human(length)
        playerTwo = AI(length)
    elif AIOrPlayer == "AIAI":
        playerOne = AI(length)
        playerTwo = AI(length)
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
