from random import randint
from random import choice
from Hand import Hand
import datetime
import copy
from Variables import *

class MonteCarlo:
    def __init__(self, gameState, name, **kwargs):
        self.gameState = gameState
        self.ai = name
        self.aiplayer = None
        for p in gameState.players:
            if p.name == name:
                self.aiplayer = p
        self.states = []
        seconds = kwargs.get('time', 5)
        self.calculation_time = datetime.timedelta(seconds=seconds)
        self.max_moves = kwargs.get('max_moves',100)

    def redistribute(self, board):
        #gets all cards from players
        # if printsOn:
        #     print ("Redistributing cards... Current hands:")
        #     for player in board.players:
        #         print player.hand

        cards = []
        numOfCards = {}
        for player in board.players:
            if player.name != self.ai:
                num = 0
                for suit in player.hand.hand:
                    cards = cards + suit
                    num += len(suit)
                numOfCards[player.name] = num
        #distribute randomly
        for player in board.players:
            if player.name != self.ai:
                hand = Hand()
                for x in range(numOfCards[player.name]):
                    index = randint(0,len(cards)-1)
                    cardAdd = cards[index]
                    cards.remove(cardAdd)
                    hand.addCard(cardAdd)
                player.hand = hand

        # if printsOn:
        #     print ("Redistributed hands:")
        #     for player in board.players:
        #         print player.hand


    def update(self, state):
        self.states.append(state)

    def getPlay(self):
        begin = datetime.datetime.utcnow()
        while datetime.datetime.utcnow() - begin < self.calculation_time:
            # if printsOn:
            #     print("Time Elapsed: %s" % (datetime.datetime.utcnow() - begin))
            self.runSimulation()
        return 

    def runSimulation(self):
        states_copy = self.states[:]
        state = states_copy[-1]
        board = copy.deepcopy(self.gameState)
        self.redistribute(board)

        # for t in xrange(self.max_moves):



        return