from __future__ import division
from math import log, sqrt
from random import randint
from random import choice
from Hand import Hand
import datetime
import copy
from Variables import *
import Variables

class MonteCarlo:
    def __init__(self, gameState, name, **kwargs):
        self.gameState = gameState
        self.ai = name
        self.aiplayer = None
        for p in gameState.players:
            if p.name == name:
                self.aiplayer = p
        self.states = []
        seconds = kwargs.get('time', Variables.monteCarloTime)
        self.calculation_time = datetime.timedelta(seconds=seconds)
        self.max_moves = kwargs.get('max_moves',100)
        self.max_depth = 0

        self.wins = {}
        self.plays = {}
        self.C = kwargs.get('C', 1.4)

        #parameters
        self.useRoundScoreOnly = False

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
        #suppress prints
        restorePrints = False
        if Variables.printsOn == True:
            Variables.printsOn = False
            restorePrints = True

        self.max_depth = 0
        state = self.states[-1]
        player = self.gameState.getCurrentPlayer()
        legal = self.gameState.getLegalPlays(player)

        #return early if no choice to be made
        if len(legal) == 0:
            return -1
        if len(legal) == 1:
            return legal[0]

        games = 0
        begin = datetime.datetime.utcnow()
        while datetime.datetime.utcnow() - begin < self.calculation_time:
            self.runSimulation()
            games += 1
            # raw_input("Enter to continue")

        # Display the number of calls of `run_simulation` and the
        # time elapsed.
        if printsOnMonte:
            print games, datetime.datetime.utcnow() - begin

        moves_states = []
        for p in legal:
            legalState = self.gameState.cardsPlayed + (p,)
            moves_states.append((p, legalState))

        #Pick the move with the highest percentage of wins.
        percent_wins, move = max(
            (self.wins.get((player, S), 0) /
             self.plays.get((player, S), 1),
             p)
            for p, S in moves_states
        )

        if printsOnMonte: 
            # Display the stats for each possible play.
            for x in sorted(
                ((100 * self.wins.get((player, S), 0) /
                  self.plays.get((player, S), 1),
                  self.wins.get((player, S), 0),
                  self.plays.get((player, S), 0), p)
                 for p, S in moves_states),
                reverse=True
            ):
                print "{3}: {0:.2f}% ({1} / {2})".format(*x)
        if printsOnMonte:
            print "Maximum depth searched:", self.max_depth

        #restore prints
        if restorePrints:
            Variables.printsOn = True

        return move

    def runSimulation(self):

        plays, wins = self.plays, self.wins

        visited_states = set()
        states_copy = self.states[:]
        state = states_copy[-1]
        board = copy.deepcopy(self.gameState)
        self.redistribute(board)

        expand = True
        for t in xrange(self.max_moves):
            player = board.getCurrentPlayer()
            legal = board.getLegalPlays(player)

            moves_states = []
            for p in legal:
                legalState = board.cardsPlayed + (p,)
                moves_states.append((p, legalState))

            #if stats available on all legal moves, use them
            if all(plays.get((player, S)) for p, S in moves_states):
                # If we have stats on all of the legal moves here, use them.
                log_total = log(
                    sum(plays[(player, S)] for p, S in moves_states))
                value, move, state = max(
                    ((wins[(player, S)] / plays[(player, S)]) +
                     self.C * sqrt(log_total / plays[(player, S)]), p, S)
                    for p, S in moves_states
                )
            else: 
                #make arbitrary decision
                move, state = choice(moves_states)

            board.step(move, player, True)
            state = board.cardsPlayed
            states_copy.append(state)

            if expand and (player, state) not in self.plays:
                expand = False
                self.plays[(player, state)] = 0
                self.wins[(player, state)] = 0
                if (t > self.max_depth):
                    self.max_depth = t

            visited_states.add((player,state))

            winners = None
            if self.useRoundScoreOnly:
                winners = board.winningPlayers
            else:
                if board.winningPlayer is not None:
                    winners = [board.winningPlayer]

            if winners:
                break

        for player, state in visited_states:
            if (player, state) not in self.plays:
                continue
            self.plays[(player, state)] += 1
            if player in winners:
                self.wins[(player,state)] += 1
        return