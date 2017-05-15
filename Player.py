from __future__ import print_function
from random import randint, choice
from Hand import Hand
from PlayerTypes import PlayerTypes
from MonteCarlo import MonteCarlo
import Card
import sys
import os
from Variables import *

class Player:
	def __init__(self, name, player_type, game, player=None):
		if player is not None:
			self.name = player.name
			self.hand = player.hand
			self.score = player.score
			self.roundscore = player.roundscore
			self.tricksWon = player.tricksWon
			self.type = player.type
			self.gameState = player.gameState
			# potentially check if changes in copied player affect original
		else:
			self.name = name
			self.hand = Hand()
			self.score = 0
			self.roundscore = 0
			self.tricksWon = []
			self.type = player_type
			self.gameState = game

	def __eq__(self, other):
		return self.name == other.name

	def __str__(self):
		return self.name

	def __repr__(self):
		return self.__str__()

	def __hash__(self):
		return hash(repr(self))

	def addCard(self, card):
		self.hand.addCard(card)


	def getInput(self, option):
		card = None
		while card is None:
			os.system('clear')
			#display game information
			self.gameState.printGameState()
			print()
			print("Your hand: %s: " % self.hand)
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
		#get list of valid cards
		# gameState = self.gameState
		# validClubs = []
		# validDiamonds = []
		# validSpades = []
		# validHearts = []
		# validHand = [validClubs, validDiamonds, validSpades, validHearts]
		# for suit in range(0,4):
		# 	handSuit = self.hand.hand[suit]
		# 	for card in handSuit:
		# 		if gameState.isValidCard(card,self):
 	# 				validHand[suit].append(card)
		return choice(self.gameState.getLegalPlays(self))

		# return self.hand.getRandomCard()

	def print_hand(self, validHand):
		for suit in range(0,4):
			print("Suit ", suit, ":"),
			for card in validHand[suit]:
				print(str(card), " "),
			print

	def naiveMaxAIPlay(self):
		gameState = self.gameState
		validClubs = []
		validDiamonds = []
		validSpades = []
		validHearts = []

		validHand = [validClubs, validDiamonds, validSpades, validHearts]
		for suit in range(0,4):
			handSuit = self.hand.hand[suit]
			for card in handSuit:
				if gameState.isValidCard(card,self):
 					validHand[suit].append(card)

		#if first, play highest card in a random suit
		if gameState.currentTrick.isUnset():
			# print("Going first!")
			#include hearts if hearts not broken or only has hearts
			if gameState.heartsBroken == True or self.hasOnlyHearts():
			  suitRange = 3
			else:
				suitRange = 2
			randomSuit = randint(0,suitRange)
			#return highest card
			# print("Current trick suit is: ", gameState.currentTrick.suit.iden)
			# print("Going first and playing highest card")
			return Hand.highestCard(validHand[randomSuit])
		#if not first:
		else:
			# print("Not going first!")
			trickSuit = gameState.currentTrick.suit.iden
			#if there are cards in the trick suit play highest card in trick suit
			if(len(validHand[trickSuit]) > 0):
				# print("Still cards in trick suit")
				return Hand.highestCard(validHand[trickSuit])
			else:
				# print("No cards in trick suit")

				#play cards by points, followed by rank
				minPoints = sys.maxsize
				minCard = None
				for suit in range(0,4):
					for card in validHand[suit]:
						cardPoints = -card.rank.rank
						if card.suit == Card.Suit(hearts):
							cardPoints -= 15 #Greater than rank of all non-point cards
						if card.suit == Card.Suit(spades) and card.rank == Card.Rank(queen):
							cardPoints -= 13
						if cardPoints < minPoints:
							minPoints = cardPoints
							minCard = card
				return minCard

		#should never get here
		raise Exception("failed programming")

		return None

	#Always tries to avoid taking the trick
	def naiveMinAIPlay(self):
		#get list of valid cards
		gameState = self.gameState
		validClubs = []
		validDiamonds = []
		validSpades = []
		validHearts = []

		validHand = [validClubs, validDiamonds, validSpades, validHearts]
		for suit in range(0,4):
			handSuit = self.hand.hand[suit]
			for card in handSuit:
				if gameState.isValidCard(card,self):
 					validHand[suit].append(card)

 		# self.print_hand(validHand)

		#if first, play lowest card in a random suit
		if gameState.currentTrick.isUnset():
			# print("Going first!")
			#include hearts if hearts not broken or only has hearts
			if gameState.heartsBroken == True or self.hasOnlyHearts():
			  suitRange = 3
			else:
				suitRange = 2
			randomSuit = randint(0,suitRange)
			#return lowest card
			# print("Current trick suit is: ", gameState.currentTrick.suit.iden)
			# print("Going first and playing lowest card")
			return Hand.lowestCard(validHand[randomSuit])
		#if not first:
		else:
			# print("Not going first!")
			trickSuit = gameState.currentTrick.suit.iden
			#if there are cards in the trick suit play lowest card in trick suit
			if(len(validHand[trickSuit]) > 0):
				# print("Still cards in trick suit")
				return Hand.lowestCard(validHand[trickSuit])
			else:
				# print("No cards in trick suit")

				#play cards by points, followed by rank
				maxPoints = -sys.maxsize
				maxCard = None
				for suit in range(0,4):
					for card in validHand[suit]:
						cardPoints = card.rank.rank
						if card.suit == Card.Suit(hearts):
							cardPoints += 15 #Greater than rank of all non-point cards
						if card.suit == Card.Suit(spades) and card.rank == Card.Rank(queen):
							cardPoints += 13
						if cardPoints > maxPoints:
							maxPoints = cardPoints
							maxCard = card
				return maxCard

		#should never get here
		raise Exception("failed programming")

		return None

	def monteCarloAIPlay(self):
		mcObj = MonteCarlo(self.gameState, self.name)
		mcObj.update(self.gameState.cardsPlayed)
		card = mcObj.getPlay()
		return card

	def play(self, option='play', c=None, auto=False):

		card = None
		if c is not None:
			card = c
			card = self.hand.playCard(card)
		elif self.type == PlayerTypes.Human:
			card = self.humanPlay(option)
		elif self.type == PlayerTypes.Random:
			card = self.randomPlay()
		elif self.type == PlayerTypes.NaiveMinAI:
			card = self.naiveMinAIPlay()
		elif self.type == PlayerTypes.NaiveMaxAI:
			card = self.naiveMaxAIPlay()
		elif self.type == PlayerTypes.MonteCarloAI:
			card = self.monteCarloAIPlay()
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

	def validPlays(self, trickSuit, heartsBroken, trickNum):
		if self.hasOnlyHearts():
			return self.hand.hearts

		if heartsBroken:
			if trickSuit==-1:
				return self.hand.clubs + self.hand.diamonds + self.hand.spades + self.hand.hearts
			else:
				if len(self.hand.hand[trickSuit])==0:
					return self.hand.clubs + self.hand.diamonds + self.hand.spades + self.hand.hearts
				else:
					return self.hand.hand[trickSuit]
		else:
			if trickSuit==-1:
				allCards = self.hand.clubs + self.hand.diamonds + self.hand.spades + self.hand.hearts
			else:
				if len(self.hand.hand[trickSuit])==0:
					if trickNum == 0:
						cards = self.hand.clubs + self.hand.diamonds + self.hand.spades
						cards.remove(Card(12,2))
						return cards
					else:
						return self.hand.clubs + self.hand.diamonds + self.hand.spades + self.hand.hearts
				else:
					return self.hand.hand[trickSuit]
