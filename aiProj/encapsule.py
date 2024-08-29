from Card import Suit, Rank
from Hearts import Hearts
from Deck import Deck
from Card import Card
from Player import Player
from PlayerTypes import PlayerTypes
from Trick import Trick
import collections

Card_C = collections.namedtuple('Card', ['point', 'suit'])

def Card_C2Card(card_c):
    return Card(card_c.point, card_c.suit)

def getScoreFromAllcards(all_cards):
    score_dict = {0:0,1:0,2:0,3:0}
    for turn in all_cards:
        if len(turn) == 4:
            score = 0
            max_card = turn[0][1]
            max_index = turn[0][0]
            for player_id, card in turn:
                if card.suit == 3:
                    score += 1
                elif card == Card_C(point = 12,suit = 2):
                    score += 13
                if card.suit == max_card.suit and card.point > max_card.point:
                    max_card, max_index = card, player_id
            score_dict[max_index] += score
    return score_dict

def MonteCarloPlay(deck, history_self, history_A, history_B, history_C, history_P0,suit):
    deck = sorted(deck, key=lambda x: x.suit * 10 + x.point)
    history = [history_self, history_A, history_B, history_C]

    allTurnsCard = []
    for i, first_player in enumerate(history_P0):
        turn = []
        for k in range(4):
            now = history[(first_player + k) % 4]
            if len(now) > i:
                turn.append([(first_player + k) % 4, now[i]])
        allTurnsCard.append(turn)

    score_dict = getScoreFromAllcards(allTurnsCard)
    thisTurnOutCard = allTurnsCard[-1] if allTurnsCard and len(allTurnsCard[-1]) != 4 else []
    outHeart = any(j[1].suit == 3 for i in allTurnsCard for j in i)
    nowSuit = suit
    h = Hearts()

    oneMonte_threeNaive_anon = [Player("AI 1", PlayerTypes.MonteCarloAI, h), Player("AI 2", PlayerTypes.greedyPlay, h),
                                Player("AI 3", PlayerTypes.NaiveMinAI, h), Player("AI 4", PlayerTypes.NaiveMaxAI, h,)]
    h.players = oneMonte_threeNaive_anon
    h.heartsBroken = outHeart
    h.losingPlayer = None
    h.allTricks = []
    h.currentTrick = Trick()
    for j, player in enumerate(h.players):
        player.score = score_dict[j]
    for player_id, card in thisTurnOutCard:
        h.currentTrick.addCard(Card_C2Card(card), player_id)
    if thisTurnOutCard:
       h.trickWinner = thisTurnOutCard[0][0]
    else:
       h.trickWinner = 0  

    h.cardsPlayed = tuple(Card_C2Card(card) for player_id, card in sum(allTurnsCard, []))
    h.cardsPlayedbyPlayer = {h.players[j]: [Card_C2Card(k) for k in i] for j, i in enumerate(history)}

    h.shift = len(thisTurnOutCard)
    h.winningPlayer = None
    h.winningPlayers = None
    h.trickNum = len(history_P0) - 1

    MontoPlayer = h.players[0]
    for card in deck:
        MontoPlayer.hand.addCard(Card(card.point, card.suit))
        MontoPlayer.hand.updateHand()

    if MontoPlayer.hand.contains2ofclubs:
        addCard = MontoPlayer.play(option="play", c='2c')
    else:
        addCard = None
        while addCard is None:
            addCard = MontoPlayer.play(auto=True,revise=False,suit=nowSuit)
            if addCard is not None and not h.isValidCard(addCard, MontoPlayer):
                addCard = None

    out_card = Card_C(point=addCard.rank.rank, suit=addCard.suit.iden)

    return out_card

def MonteCarloPlay_revised(deck, history_self, history_A, history_B, history_C, history_P0, suit):
    deck = sorted(deck, key=lambda x: x.suit * 10 + x.point)
    history = [history_self, history_A, history_B, history_C]

    allTurnsCard = []
    for i, first_player in enumerate(history_P0):
        turn = []
        for k in range(4):
            now = history[(first_player + k) % 4]
            if len(now) > i:
                turn.append([(first_player + k) % 4, now[i]])
        allTurnsCard.append(turn)

    score_dict = getScoreFromAllcards(allTurnsCard)
    if allTurnsCard and len(allTurnsCard[-1]) != 4:
        thisTurnOutCard = allTurnsCard[-1]
    else:
        thisTurnOutCard = []
    outHeart = any(j[1].suit == 3 for i in allTurnsCard for j in i)

    h = Hearts()
    oneMonte_threeNaive_anon = [Player("AI 1", PlayerTypes.MonteCarloAI, h), Player("AI 2", PlayerTypes.greedyPlay, h),
                                Player("AI 3", PlayerTypes.NaiveMinAI, h), Player("AI 4", PlayerTypes.NaiveMaxAI, h)]
    h.players = oneMonte_threeNaive_anon
    h.heartsBroken = outHeart
    h.losingPlayer = None
    h.allTricks = []
    h.currentTrick = Trick()
    for j, player in enumerate(h.players):
        player.score = score_dict[j]
    for player_id, card in thisTurnOutCard:
        h.currentTrick.addCard(Card_C2Card(card), player_id)
    h.trickWinner = thisTurnOutCard[0][0] if thisTurnOutCard else 0

    h.cardsPlayed = tuple(Card_C2Card(card) for player_id, card in sum(allTurnsCard, []))
    h.cardsPlayedbyPlayer = {h.players[j]: [Card_C2Card(k) for k in i] for j, i in enumerate(history)}

    h.shift = len(thisTurnOutCard)
    h.winningPlayer = None
    h.winningPlayers = None
    h.trickNum = len(history_P0) - 1

    MontoPlayer = h.players[0]
    for card in deck:
        MontoPlayer.hand.addCard(Card(card.point, card.suit))
        MontoPlayer.hand.updateHand()

    if MontoPlayer.hand.contains2ofclubs:
        addCard = MontoPlayer.play(option="play", c='2c')
    else:
        addCard = None
        while addCard is None:
            addCard = MontoPlayer.play(auto=True,revise=True,suit=suit)
            if addCard is not None and not h.isValidCard(addCard, MontoPlayer):
                addCard = None

    out_card = Card_C(point=addCard.rank.rank, suit=addCard.suit.iden)
    return out_card