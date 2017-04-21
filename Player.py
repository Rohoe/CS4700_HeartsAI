from Hand import Hand
from PlayerTypes import PlayerTypes
import State
import Card

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

	def humanPlay(self, option):
		card_str = self.getInput(option)
		cardInfo = self.hand.strToCard(card_str)
		if cardInfo is None:
			return None
		else:
			cardRank, suitIden = cardInfo[0], cardInfo[1]

		#see if player has that card in hand
		if self.hand.containsCard(cardRank, suitIden):
			return Card.Card(cardRank, suitIden)
		else:
			return None

	def randomPlay(self):
		return self.hand.getRandomCard()

	def naiveMinAIPlay(self):
		return None

	def play(self, option='play', c=None, auto=False):

		card = None
		if c is not None:
			card = c
			card = self.hand.playCard(card)
		elif self.type == PlayerTypes.Human:
			card = self.humanPlay(option)
		elif self.type == PlayerTypes.Random:
			card = self.randomPlay()
		elif self.type == Player.Types.NaiveMinAI:
			card = self.naiveMinAIPlay()
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
