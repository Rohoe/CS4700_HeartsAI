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

        self.wins = {}
        self.plays = {}

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
        iterations = 0
        while datetime.datetime.utcnow() - begin < self.calculation_time:
            if printsOnMonte:
                print("Iteration %s" % iterations)
            self.runSimulation()
            iterations += 1
            # raw_input("Enter to continue")



        return 

    def runSimulation(self):
        visited_states = set()
        states_copy = self.states[:]
        state = states_copy[-1]
        board = copy.deepcopy(self.gameState)
        self.redistribute(board)

        expand = True
        for t in xrange(self.max_moves):
            player = board.getCurrentPlayer()
            legal = board.getLegalPlays(player)
            card = choice(legal)
            board.step(card, player)
            state = board.cardsPlayed
            states_copy.append(state)

            if expand and (player, state) not in self.plays:
                expand = False
                self.plays[(player, state)] = 0
                self.wins[(player, state)] = 0

            visited_states.add((player,state))

            winner = board.winningPlayer
            if winner:
                break

        if printsOnMonte:
            print ("Winner of simulation: %s" % winner.name)

        for player, state in visited_states:
            if (player, state) not in self.plays:
                continue
            self.plays[(player, state)] += 1
            if player == winner:
                self.wins[(player,state)] += 1


        return