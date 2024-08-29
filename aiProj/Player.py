'''
玩家类，判读用哪种蒙特卡洛方法
'''
from random import randint, choice
from Hand import Hand
from PlayerTypes import PlayerTypes
from MonteCarlo import MonteCarlo
from MonteCarlo_revised import MonteCarlo_revised
from Card import Card,Suit,Rank
import sys
from Variables import hearts,spades,queen
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

	# 模特卡罗模拟
	def monteCarloAIPlay(self,suit):
		mcObj = MonteCarlo(self.gameState, self.name,suit)
		mcObj.update(self.gameState.cardsPlayed)
		card = mcObj.get_play()
		return card
	def MonteCarloPlay_revised(self,suit):
		mcObj = MonteCarlo_revised(self.gameState, self.name,suit)
		mcObj.update(self.gameState.cardsPlayed)
		card = mcObj.get_play()
		return card
	# 出牌框架
	def play(self, option='play', c=None, auto=False,revise=False,suit=None):
		card = None
		if c is not None:
			card = c
			card = self.hand.playCard(card)
		elif self.type == PlayerTypes.MonteCarloAI:
			if(revise==False):
				card = self.monteCarloAIPlay(suit)
			else:
				card=self.MonteCarloPlay_revised(suit)
		return card

	def trickWon(self, trick): # 赢牌后更新得分
		self.roundscore += trick.points


	def hasSuit(self, suit):
		return len(self.hand.hand[suit.iden]) > 0

	def removeCard(self, card):
		self.hand.removeCard(card)

	def hasOnlyHearts(self):
		return self.hand.hasOnlyHearts()	