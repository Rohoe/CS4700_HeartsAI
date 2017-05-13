from random import randint
from Hand import Hand
import datetime
import copy

class MonteCarlo:
    def __init__(self, gameState, name, **kwargs):
        self.state = copy.deepcopy(gameState)
        self.ai = name
        self.aiplayer = None
        for p in self.state.players:
            if p.name == name:
                self.aiplayer = p
        self.redistribute()
        self.stats = {}
        seconds = kwargs.get('time', 30)
        self.calculation_time = datetime.timedelta(seconds=seconds)

    def redistribute(self):
        #gets all cards from players
        cards = []
        numOfCards = {}
        for player in self.state.players:
            if player.name != self.ai:
                num = 0
                for suit in player.hand.hand:
                    cards = cards + suit
                    num += len(suit)
                numOfCards[player.name] = num
        #distribute randomly
        for player in self.state.players:
            if player.name != self.ai:
                hand = Hand()
                for x in range(numOfCards[player.name]):
                    index = randint(0,len(cards)-1)
                    cardAdd = cards[index]
                    cards.remove(cardAdd)
                    hand.addCard(cardAdd)
                player.hand = hand

    def update(self):
        return


    def getPlay(self):
        begin = datetime.datetime.utcnow()
        while datetime.datetime.utcnow() - begin < self.calculation_time:
            self.runSimulation()


    def runSimulation(self):
        self.state.simulate()
