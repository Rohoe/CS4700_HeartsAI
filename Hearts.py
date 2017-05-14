from __future__ import print_function, division
from timeit import default_timer as timer
from Deck import Deck
from Card import Card, Suit, Rank
from Player import Player
from Trick import Trick
from PlayerTypes import PlayerTypes
from Variables import *
import Variables
import Hand
from multiprocessing import Pool as ThreadPool
from math import floor

'''
Change auto to False if you would like to play the game manually.
This allows you to make all passes, and plays for all four players.
When auto is True, passing is disabled and the computer plays the
game by "guess and check", randomly trying moves until it finds a
valid one.
'''



#Only necessary state is the current trick and all previously played tricks.
class Hearts:
	def __init__(self):
		# if orig is None:
		#Player names must be unique
		allRandom = [Player("Random 1", PlayerTypes.Random, self), Player("Random 2", PlayerTypes.Random, self),
								 Player("Random 3", PlayerTypes.Random, self), Player("Random 4", PlayerTypes.Random, self)]
		allHuman = [Player("Human 1", PlayerTypes.Human, self), Player("Human 2", PlayerTypes.Human, self),
							  Player("Human 3", PlayerTypes.Human, self), Player("Human 4", PlayerTypes.Human, self)]
		oneHuman = [Player("Human 1", PlayerTypes.Human, self), Player("Random 2", PlayerTypes.Random, self),
							  Player("Random 3", PlayerTypes.Random, self), Player("Random 4", PlayerTypes.Random, self)]
		oneNaiveMin_allRandom = [Player("NaiveMin 1", PlayerTypes.NaiveMinAI, self), Player("Random 2", PlayerTypes.Random, self),
							  				  Player("Random 3", PlayerTypes.Random, self), Player("Random 4", PlayerTypes.Random, self)]
		oneNaiveMin_oneHuman = [Player("NaiveMin 1", PlayerTypes.NaiveMinAI, self), Player("Human 2", PlayerTypes.Human, self),
							  				    Player("Random 3", PlayerTypes.Random, self), Player("Random 4", PlayerTypes.Random, self)]
		oneNaiveMax_allRandom = [Player("NaiveMax 1", PlayerTypes.NaiveMaxAI, self), Player("Random 2", PlayerTypes.Random, self),
							  				  Player("Random 3", PlayerTypes.Random, self), Player("Random 4", PlayerTypes.Random, self)]
		oneNaiveMax_allNaiveMin = [Player("NaiveMin 1", PlayerTypes.NaiveMinAI, self), Player("NaiveMin 2", PlayerTypes.NaiveMinAI, self),
							  				       Player("NaiveMin 3", PlayerTypes.NaiveMinAI, self), Player("NaiveMax 4", PlayerTypes.NaiveMaxAI, self)]
		oneMonte_allRandom = [Player("MonteCarlo 1", PlayerTypes.MonteCarloAI, self), Player("Random 2", PlayerTypes.Random, self),
							  				  Player("Random 3", PlayerTypes.Random, self), Player("Random 4", PlayerTypes.Random, self)]
		oneMonte_allHuman = [Player("MonteCarlo 1", PlayerTypes.MonteCarloAI, self), Player("Human 2", PlayerTypes.Human, self),
							  Player("Human 3", PlayerTypes.Human, self), Player("Human 4", PlayerTypes.Human, self)]
		oneMonte_allNaive = [Player("MonteCarlo 1", PlayerTypes.MonteCarloAI, self), Player("NaiveMin 2", PlayerTypes.NaiveMinAI, self),
							  				       Player("NaiveMin 3", PlayerTypes.NaiveMinAI, self), Player("NaiveMin 4", PlayerTypes.NaiveMinAI, self)]

		thePlayers = allRandom
		self.roundNum = 0
		self.trickNum = 0 # initialization value such that first round is round 0
		self.dealer = -1 # so that first dealer is 0
		#self.passes = [1, -1, 2, 0] # left, right, across, no pass
		self.allTricks = []
		self.currentTrick = Trick()
		self.allTricks < self.currentTrick
		self.trickWinner = -1
		self.heartsBroken = False
		self.losingPlayer = None
		self.winningPlayer = None
		self.winningPlayers = None
		self.shift = 0

		self.cardsPlayed = () #keep track of state in a tuple

		#self.passingCards = [[], [], [], []]

		# Make four players

		self.players = thePlayers

		'''
		Player physical locations:
		Game runs clockwise

			p3
		p2		p4
			p1

		'''

		# Generate a full deck of cards and shuffle it
		self.newRound()
		# else:
		# 	self = copy.deepcopy(orig)

	#return array of players with lowest score
	def roundWinners(self):
		winners = []
		for player in self.players:
			if player.roundscore == 26:
				shotMoon = True
				winners.append(player)
				return winners

		minScore = 200 # impossibly high
		winner = None
		for p in self.players:
			if p.roundscore < minScore:
				winner = p
				minScore = p.roundscore

		winners.append(winner)
		#check for a draw
		for p in self.players:
			if p != winner and p.roundscore == minScore:
				winners.append(p)
		return winners

	def handleScoring(self, suppressPrints = False):
		p, highestScore = None, 0
		if not suppressPrints:
			if Variables.printsOn:
				print ("\nScores:\n")
		shotMoon = False
		for player in self.players:
			if player.roundscore == 26:
				shotMoon = True
		for player in self.players:
			if shotMoon and player.roundscore != 26:
				player.score += 26
			elif not shotMoon:
				player.score += player.roundscore
			player.roundscore = 0
			if Variables.printsOn:
				print (player.name + ": " + str(player.score))
			if player.score > highestScore:
				p = player
				highestScore = player.score
			self.losingPlayer = p

	def newRound(self):
		self.deck = Deck()
		self.deck.shuffle()
		self.roundNum += 1
		self.trickNum = 0
		self.trickWinner = -1
		self.heartsBroken = False
		self.dealer = (self.dealer + 1) % len(self.players)
		self.dealCards()
		self.currentTrick = Trick()
		self.allTricks = []
		#self.passingCards = [[], [], [], []]
		self.cardsPlayed = ()
		for p in self.players:
			p.discardTricks()

	def getFirstTrickStarter(self):
		for i,p in enumerate(self.players):
			if p.hand.contains2ofclubs:
				self.trickWinner = i

	def dealCards(self):
		i = 0
		while(self.deck.size() > 0):
			self.players[i % len(self.players)].addCard(self.deck.deal())
			i += 1


	def evaluateTrick(self, suppressPrints = False):
		self.trickWinner = self.currentTrick.winner
		p = self.players[self.trickWinner]
		p.trickWon(self.currentTrick)
		if not suppressPrints:
			self.printCurrentTrick()
			if Variables.printsOn:
				print (p.name + " won the trick.")
		# print 'Making new trick'
		self.currentTrick = Trick()
		self.allTricks < self.currentTrick
		if not suppressPrints:
			if Variables.printsOn:
				print (self.currentTrick.suit)


	def passCards(self, index):
		print (self.printPassingCards())
		passTo = self.passes[self.trickNum] # how far to pass cards
		passTo = (index + passTo) % len(self.players) # the index to which cards are passed
		while len(self.passingCards[passTo]) < cardsToPass: # pass three cards
			passCard = None
			while passCard is None: # make sure string passed is valid
				passCard = self.players[index].play(option='pass')
				if passCard is not None:
					# remove card from player hand and add to passed cards
					self.passingCards[passTo].append(passCard)
					self.players[index].removeCard(passCard)

	def distributePassedCards(self):
		for i,passed in enumerate(self.passingCards):
			for card in passed:
				self.players[i].addCard(card)
		self.passingCards = [[], [], [], []]


	def printPassingCards(self):
		out = "[ "
		for passed in self.passingCards:
			out += "["
			for card in passed:
				out += card.__str__() + " "
			out += "] "
		out += " ]"
		return out


	def playersPassCards(self):
		self.printPlayers()
		if not self.trickNum % 4 == 3: # don't pass every fourth hand
			for i in range(0, len(self.players)):
				print # spacing
				self.printPlayer(i)
				self.passCards(i % len(self.players))

			self.distributePassedCards()
			self.printPlayers()

	#return flat array of cards
	def getLegalPlays(self, player):
		validHand = []
		for suit in range(0,4):
			handSuit = player.hand.hand[suit]
			for card in handSuit:
				if self.isValidCard(card,player):
 					validHand.append(card)
		return validHand

	#Check if a card is a valid play in the current state
	def isValidCard(self, card, player):
		if card is None:
			return False

		# if it is not the first trick and no cards have been played:
		if self.trickNum != 0 and self.currentTrick.cardsInTrick == 0:
			if card.suit == Suit(hearts) and not self.heartsBroken:
				# if player only has hearts but hearts have not been broken,
				# player can play hearts
				if not player.hasOnlyHearts():
					if Variables.printsOn and player.type == PlayerTypes.Human:
						print ("Hearts have not been broken.")
					return False

		# player tries to play off suit but has trick suit
		# print(self.currentTrick.suit)
		# print (card)
		if self.currentTrick.suit != Suit(-1) and card.suit != self.currentTrick.suit:
			 if player.hasSuit(self.currentTrick.suit):
					if Variables.printsOn and player.type == PlayerTypes.Human:
						print ("Must play the suit of the current trick.")
					return False

		#Can't play hearts or queen of spades on first hand
		if self.trickNum == 0:
			if card.suit == Suit(hearts):
				if Variables.printsOn and player.type == PlayerTypes.Human:
					print ("Hearts cannot be broken on the first hand.")
				return False
			elif card.suit == Suit(spades) and card.rank == Rank(queen):
				if Variables.printsOn and player.type == PlayerTypes.Human:
					print ("The queen of spades cannot be played on the first hand.")
				return False

	 #  #Can't lead with hearts unless hearts broken
		# if self.currentTrick.cardsInTrick == 0:
		# 	if card.suit == Suit(hearts) and not self.heartsBroken:
		# 		print ("Hearts not yet broken.")
		# 		return False

		#Valid otherwise
		return True

	#Can be edited to use isValidCard to make method more efficient
	def playTrick(self, start):
		shift = 0
		if self.trickNum == 0:
			startPlayer = self.players[start]
			addCard = startPlayer.play(option="play", c='2c')
			startPlayer.removeCard(addCard)

			self.currentTrick.addCard(addCard, start)

			shift = 1 # alert game that first player has already played

		# have each player take their turn
		for i in range(start + shift, start + len(self.players)):
			self.printCurrentTrick()
			curPlayerIndex = i % len(self.players)
			self.printPlayer(curPlayerIndex)
			curPlayer = self.players[curPlayerIndex]
			addCard = None

			while addCard is None: # wait until a valid card is passed


				addCard = curPlayer.play(auto=auto) # change auto to False to play manually
				# print(curPlayer.name, "playing: "),
				# print(addCard)

				# the rules for what cards can be played
				# card set to None if it is found to be invalid
				if addCard is not None:

					#set to None if card is invalid based on rules
					if self.isValidCard(addCard, curPlayer) == False:
						addCard = None
					else:
						#change game state according to card

						#hearts broken
						if addCard.suit == Suit(hearts):
							self.heartsBroken = True
						if addCard.suit == Suit(spades) and addCard.rank == Rank(queen):
							self.heartsBroken = True

			curPlayer.removeCard(addCard)
			self.currentTrick.addCard(addCard, curPlayerIndex)

		self.evaluateTrick()
		self.trickNum += 1

	# print player's hand
	def printPlayer(self, i):
		p = self.players[i]
		if Variables.printsOn:
			print (p.name + "'s hand: " + str(p.hand))

	# print all players' hands
	def printPlayers(self):
		for p in self.players:
			if Variables.printsOn:
				print (p.name + ": " + str(p.hand))

	# show cards played in current trick
	def printCurrentTrick(self):
		trickStr = '\nCurrent table:\n'
		trickStr += "Trick suit: " + self.currentTrick.suit.__str__() + "\n"
		for i, card in enumerate(self.currentTrick.trick):
			if self.currentTrick.trick[i] is not 0:
				trickStr += self.players[i].name + ": " + str(card) + "\n"
			else:
				trickStr += self.players[i].name + ": None\n"
		if Variables.printsOn:
			print (trickStr)

	def getWinner(self):
		minScore = 200 # impossibly high
		winner = None
		for p in self.players:
			if p.score < minScore:
				winner = p
				minScore = p.score
		return winner

	#Plays a game and returns winning player
	def playGame(self):
		hearts = self
		# play until someone loses
		while hearts.losingPlayer is None or hearts.losingPlayer.score < maxScore:
			while hearts.trickNum < totalTricks:
				if Variables.printsOn:
					print ("Round", hearts.roundNum)
				if hearts.trickNum == 0:
					# if not auto:
					# 	hearts.playersPassCards()
					hearts.getFirstTrickStarter()
				if Variables.printsOn:
					print ('\nPlaying trick number', hearts.trickNum + 1)
				hearts.playTrick(hearts.trickWinner)

			# tally scores
			hearts.handleScoring()

			# new round if no one has lost
			if hearts.losingPlayer.score < maxScore:
				if Variables.printsOn:
					print ("New round")
				hearts.newRound()

		if Variables.printsOn:
			print # spacing
			print (hearts.getWinner().name, "wins!")

		winner = hearts.getWinner()

		#Game over: Reset all player fields
		for p in self.players:
			p.score = 0
			p.roundScore = 0
			p.hand = Hand.Hand()
			p.tricksWon = []

		return winner

	def step(self, card, player, monteCarlo = False):
		#add card to state
		self.cardsPlayed = self.cardsPlayed + (card,)

		player.removeCard(card)
		start = (self.trickWinner + self.shift) % len(self.players)
		self.currentTrick.addCard(card, start)
		self.shift += 1
		if self.shift == 4:
			self.evaluateTrick()
			self.trickNum += 1
			self.shift = 0
			if Variables.printsOn:
				print ('\nPlaying trick number', self.trickNum)
				self.printCurrentTrick()
			#end game and evaluate winner if round is over
			if monteCarlo: 
				if (self.trickNum >= totalTricks):
					self.winningPlayers = self.roundWinners()
					self.handleScoring()
					self.winningPlayer = self.getWinner()
					# if Variables.printsOnMonte:
					# 	print ("Game over: Winner is %s" % self.winningPlayer)
					# 	print ("Score: %s" % self.winningPlayer.roundscore)

	def playTrickStepping(self, start):
		if self.trickNum == 0:
			startPlayer = self.players[start]
			addCard = startPlayer.play(option="play", c='2c')
			self.step(addCard, startPlayer)

		# have each player take their turn
		for i in range(start + self.shift, start + len(self.players)):
			self.printCurrentTrick()

			if Variables.printsOn:
				print ("Current player: %s" % self.getCurrentPlayer())

			curPlayerIndex = i % len(self.players)
			self.printPlayer(curPlayerIndex)
			curPlayer = self.players[curPlayerIndex]
			addCard = None

			while addCard is None: # wait until a valid card is passed
				addCard = curPlayer.play(auto=auto) # change auto to False to play manually
				# print(curPlayer.name, "playing: "),
				# print(addCard)
				# the rules for what cards can be played
				# card set to None if it is found to be invalid
				if addCard is not None:
					#set to None if card is invalid based on rules
					if self.isValidCard(addCard, curPlayer) == False:
						addCard = None
					else: #change game state according to card
						#hearts broken
						if addCard.suit == Suit(hearts):
							self.heartsBroken = True
						if addCard.suit == Suit(spades) and addCard.rank == Rank(queen):
							self.heartsBroken = True
			


			self.step(addCard,curPlayer)
			if Variables.printsOn:
				print ("Cards played: %s" % (self.cardsPlayed,))

	def playGameStepping(self):
		hearts = self
		# play until someone loses
		while hearts.losingPlayer is None or hearts.losingPlayer.score < maxScore:
			while hearts.trickNum < totalTricks:
				if Variables.printsOn:
					print ("Round", hearts.roundNum)
				if hearts.trickNum == 0:
					# if not auto:
					# 	hearts.playersPassCards()
					hearts.getFirstTrickStarter()
				if Variables.printsOn:
					print ('\nPlaying trick number', hearts.trickNum + 1)
				hearts.playTrickStepping(hearts.trickWinner)

			# tally scores
			hearts.handleScoring()

			# #End game if out of cards and max score has not been reached
			# winner = hearts.getWinner()
			# return winner

			# new round if no one has lost
			if hearts.losingPlayer.score < maxScore:
				if Variables.printsOn:
					print ("New round")
				hearts.newRound()

			#End game if max rounds reached
			if self.roundNum >= Variables.maxRounds:
				winner = hearts.getWinner()
				return winner

		if Variables.printsOn:
			print # spacing
			print (hearts.getWinner().name, "wins!")

		winner = hearts.getWinner()

		#Game over: Reset all player fields
		for p in self.players:
			p.score = 0
			p.roundScore = 0
			p.hand = Hand.Hand()
			p.tricksWon = []

		return winner

	#returns the current player
	def getCurrentPlayer(self):
		return self.players[self.currentTrick.getCurrentPlayer(self.trickWinner)]

	def getDeepCopy(self):
		return Hearts(self)

def runGames(numGames):
	numWins = None
	thePlayers = None
	for i in range(0,numGames):
		hearts = Hearts()
		if numWins is None:
			thePlayers = hearts.players
			numWins = {thePlayers[0].name:0, thePlayers[1].name:0, thePlayers[2].name:0, thePlayers[3].name:0}
		winningPlayer = hearts.playGameStepping()
		numWins[winningPlayer.name] += 1
	return numWins

def main():
	while True:
		try:
			numGames = int(raw_input("How many games to play?\n"),10)
			if(numGames < 0):
				print("Not a valid number. Try again.")
			else:
				break			
		except ValueError:
			print("Not a valid number. Try again.")

	#Timing start
	start = timer()

	# Play numGames and store the number of times each player has won
	# Player names must be unique
	numWins = runGames(numGames)

	# parallelize
	numThreads = Variables.numThreads
	gamesPerThread = int(floor(numGames / numThreads))

	#assign games per thread
	threadGames = []
	gamesAssigned = 0
	for i in range(0,numThreads):
		if (i != numThreads - 1):
			threadGames.append(gamesPerThread)
			gamesAssigned += gamesPerThread
		else:
			gamesLeft = numGames - gamesAssigned
			threadGames.append(gamesLeft)
			gamesAssigned += gamesLeft

	pool = ThreadPool(numThreads)
	results = pool.map(runGames, threadGames)
	pool.close()
	pool.join()

	# results = []
	# results.append(runGames(numGames))

	#aggregate results
	thePlayers = results[-1].keys()
	p0 = thePlayers[0]
	p1 = thePlayers[1]
	p2 = thePlayers[2]
	p3 = thePlayers[3]
	p0_wins = 0
	p1_wins = 0
	p2_wins = 0
	p3_wins = 0
	for r in results:
		if r is not None:
			p0_wins += r[p0]
			p1_wins += r[p1]
			p2_wins += r[p2]
			p3_wins += r[p3]

	#Timing end
	end = timer()


	print("-----------------------")
	print("Win Rates (Total Games:", numGames, ")")
	print("-----------------------")
	print(p0, ":" ,"%.2f%%"%(100 * float(p0_wins)/float(numGames))),
	print(p1, ":" ,"%.2f%%"%(100 * float(p1_wins)/float(numGames))),
	print(p2, ":" ,"%.2f%%"%(100 * float(p2_wins)/float(numGames))),
	print(p3, ":" ,"%.2f%%"%(100 * float(p3_wins)/float(numGames)))

	print("Time elapsed:", (end-start))


if __name__ == '__main__':
	main()
