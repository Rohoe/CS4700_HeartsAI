from Hand import Hand
from PlayerTypes import PlayerTypes

class Player:
	def __init__(self, name, player_type):
			self.name = name
			self.hand = Hand()
			self.score = 0
			self.roundscore = 0
			self.tricksWon = []
			self.type = player_type

	def addCard(self, card):
		self.hand.addCard(card)


	def getInput(self, option):
		card = None
		while card is None:
			card = raw_input(self.name + ", select a card to " + option + ": ")
		return card

	def human_play(self, option):
		return self.getInput(option)

	def random_play(self):
		return self.hand.getRandomCard()

	def play(self, option='play', c=None, auto=False):

		card = None
		if c is not None:
			card = c
			card = self.hand.playCard(card)
		elif self.type is PlayerTypes.Human:
			card = self.human_play(option)
		elif self.type is PlayerTypes.Random:
			card = self.random_play()
		if self.type is PlayerTypes.Human:
			card = self.hand.playCard(card)
		return card


	def trickWon(self, trick):
		self.roundscore += trick.points


	def hasSuit(self, suit):
		return len(self.hand.hand[suit.iden]) > 0

	def removeCard(self, card):
		self.hand.removeCard(card)

	def discardTricks(self):
		self.tricksWon = []

	def hasOnlyHearts(self):
		return self.hand.hasOnlyHearts()
