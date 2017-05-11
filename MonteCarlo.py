from random import randint


class MonteCarlo:
    def __init__(self, gameState, name):
        self.state = Hearts(gameState)
        self.ai = name
        self.redistribute()
        self.stats = {}

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


    def getPlay(self):


    def runSimulation(self):




        self.state.simulate()
