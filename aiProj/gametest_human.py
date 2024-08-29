from encapsule import MonteCarloPlay_revised
from encapsule import MonteCarloPlay
import random
import collections
import json
from typing import List
from encapsule import MonteCarloPlay
import random
import collections
import pygame
import sys
import numpy as np
import os
from PIL import Image
Card = collections.namedtuple('Card', ['point', 'suit'])
'''
使用namedtuple创建Card类型，包含point,suit两个属性
point: 纸牌点数, 2-14, 11为J, 12为Q, 13为K,14为A
suit: 纸牌花色，梅花:0, 方块:1, 黑桃:2, 红桃:3
使用：spadeQ: Card(12,2)
'''
Human_play = True
def card2chinese(card):
    '''
    将某张牌类转换为中文可读
    __input:
    card: Card类型
    __output:
    str类型，牌的中文名称
    '''
    ranks = [str(n) for n in range(2, 11)] + list('JQKA')
    suits = '梅花 方块 黑桃 红桃'.split()
    try:
        return suits[card.suit] + ranks[card.point - 2]
    except:
        print(f"wrong type for card2chinese(card):{type(card)}")
        return 0

class Deck:
    #牌堆类，一堆52张牌
    def __init__(self):
        # 建立牌堆
        card = []
        for i in range(4):
            for j in range(13):
                card.append(Card(j + 2, i))
        self.card = card

    def shuffle(self):
        # 洗牌
        random.shuffle(self.card)

    def deal(self, n=4):
        # 发牌，分四份
        if not len(self.card):
            print('no cards')
            return [[] * n]
        p = []
        for i in range(n):
            p.append((self.card[len(self.card) // n * i:len(self.card) // n * (i + 1)]))
        return p


class Player:
    # 玩家类
    def __init__(self, player_id, hand=[]):
        self.player_id = player_id
        self.hand = hand # 玩家手牌

    def sortHand(self):  # 整理，排序手发到的牌
        self.hand.sort(key=lambda x: (x.suit, x.point))

    def sortSuit(self):
        # 将剩余的牌按花色分类，便于后续的出牌的判断
        club = []
        diamond = []
        spade = []
        heart = []
        for i in range(len(self.hand)):
            if self.hand[i].suit == 0:
                club.append(i)
            elif self.hand[i].suit == 1:
                diamond.append(i)
            elif self.hand[i].suit == 2:
                spade.append(i)
            elif self.hand[i].suit == 3:
                heart.append(i)
        return [club, diamond, spade, heart]
def judge_card(x):
    if (type(x) != Card):
        print("not a card!!")
        return False
    return True
def bad_action(state:int,suitsDeck:List[List[Card]],thisTurnOutCard:List,outHeart:bool):
    #手牌数>=10时，说明是偏早回合，可以大胆出大牌
    buffer_Deck = [[],[],[],[]]
    for suits in suitsDeck:
        if suits:
            buffer_Deck[suits[0].suit] = suits
    early = sum([len(suitKind) for suitKind in buffer_Deck]) >= 10

    if state == 1:#状态一 即第一个出牌 && 没有黑桃或者黑桃最大值大于Q && 黑桃Q未出
        if len(buffer_Deck[2])==0:#1。没有黑桃
            for suit_kind in buffer_Deck:
                if len(suit_kind)!=0:#出非黑桃最大牌
                    ret = suit_kind[-1]
                    if(judge_card(ret)):
                        return ret
                    else:
                        return None
        else:#1.max黑桃>Q
            if not early:#回合较晚，拿到猪的可能性增大，保守起见出小于Q的黑桃,
                #或者干脆不出黑桃
                for idx,black_peach in enumerate(buffer_Deck[2]) :
                    if black_peach.point>12 and idx>=1:
                        ret = buffer_Deck[2][idx-1]
                        if(judge_card(ret)):
                            return ret
                        else:
                            return None
                #没有小于Q的黑桃时，出其他牌的最小
                for suits in buffer_Deck:
                    if len(suits)>=1:
                        ret = suits[0]
                        if(judge_card(ret)):
                            return ret
                        else:
                            return None
            else:#回合较早，可以冒险出黑桃以外的大牌
                for kind_idx,suit_kind in enumerate(buffer_Deck):
                    if len(suit_kind)>0 and kind_idx != 2:
                        ret=suit_kind[-1]
                        if(judge_card(ret)):
                            return ret
                        else:
                            return None

    elif state == 2:#状态二 即第一个出牌 && 如果有小黑桃 && 黑桃Q未出
        if early:#如果时间早，可以先消耗别人的黑桃,先打出最大的、小于Q的黑桃
            for idx,black_peach in enumerate(buffer_Deck[2]):
                if black_peach.point>12 and idx>=1:
                    ret = buffer_Deck[2][idx-1]
                    if(judge_card(ret)):
                        return ret
                    else:
                        return None
                elif buffer_Deck[2][-1].point<12:
                    ret=buffer_Deck[2][-1]
                    if(judge_card(ret)):
                        return ret
                    else:
                        return None

        else:#时间偏晚时，考虑到红心，先从小牌数最多的花色里出最小牌
            def count_point_less_than_8(suits:List[Card]):
                return sum(1 for card in suits if card.point < 8)
            most_small_cards_deck = max(buffer_Deck,\
                                    key=count_point_less_than_8)
            if count_point_less_than_8(most_small_cards_deck)>0:#有花色的最小牌小于8
                ret=most_small_cards_deck[0]
                if(judge_card(ret)):
                    return ret
                else:
                    return None
            else:
                for suit_kind in buffer_Deck:
                    if len(suit_kind)>0:
                        ret= suit_kind[0]
                        if(judge_card(ret)):
                            return ret
                        else:
                            return None

    elif state == 3:# 状态三 即第一个出牌 && 如果黑桃Q已出
        if buffer_Deck[2]:#有黑桃
            ret = buffer_Deck[2][-1]#出最大的黑桃
            if(judge_card(ret)):
                return ret
            else:
                return None
        else:#没有黑桃
            if outHeart:
                if  buffer_Deck[3] and buffer_Deck[3][0].point<=6:
                    #出个小一点的红桃，坑一下别人
                    ret=buffer_Deck[3][0]
                    if(judge_card(ret)):
                        return ret
                    else:
                        return None
                else:
                    if len(buffer_Deck[0])>len(buffer_Deck[1]):
                        ret=buffer_Deck[0][0]
                        if(judge_card(ret)):
                            return ret
                        else:
                            return None
                    print(buffer_Deck[0])
                    print(buffer_Deck[1])
                    try:
                        ret=buffer_Deck[1][0]
                    except:
                        ret=buffer_Deck[3][0]
                    if(judge_card(ret)):
                        return ret
                    else:
                        return None
            else:
                #没有人出过红桃
                if early:
                    for suits in buffer_Deck[0:2]:
                        if suits:
                            ret=suits[-1]
                            if(judge_card(ret)):
                                return ret
                            else:
                                return None
                else:
                    for suits in buffer_Deck[0:2]:
                        if suits:
                            ret=suits[0]
                            if(judge_card(ret)):
                                return ret
                            else:
                                return None



    elif state == 4:# 状态四：第二、三个出牌 && 没有相同花色 && 有黑桃Q
        ret = buffer_Deck[2][-1]#出最大的黑桃
        if(judge_card(ret)):
            return ret
        else:
            return None
    elif state == 5:#状态五：第二、三个出牌 && 没有相同花色 && 没有黑Q
        if buffer_Deck[2]:#如果有黑桃
            ret=buffer_Deck[2][-1]#出最大的黑桃
            if(judge_card(ret)):
                return ret
            else:
                return None
        else:#如果没有黑桃，
            if outHeart and buffer_Deck[3]:
                ret=buffer_Deck[3][-1]#把最大的红心出出去
                if(judge_card(ret)):
                    return ret
                else:
                    return None
            else:#没有红心，没有黑桃
                for suits in buffer_Deck:
                    if suits:
                        ret=suits[-1]
                        if(judge_card(ret)):
                            return ret
                        else:
                            return None

    elif state == 6:# 状态六 ：2~3出牌 && 有相同花色 && 有比当前已出最大牌小的
        first_card:Card = thisTurnOutCard[0][1]
        this_turn_suit = first_card.suit
        if early:#回合尚早，可以出大牌
            ret=buffer_Deck[this_turn_suit][-1]
            if(judge_card(ret)):
                return ret
            else:
                return None
        else:#如果太晚了，就出小牌
            ret=buffer_Deck[this_turn_suit][0]
            if(judge_card(ret)):
                return ret
            else:
                return None
    elif state == 7:
        first_card:Card = thisTurnOutCard[0][1]
        this_turn_suit = first_card.suit
        if early:#回合尚早，可以把最大牌出了
            ret=buffer_Deck[this_turn_suit][-1]
            if(judge_card(ret)):
                return ret
            else:
                return None
        else:#如果太晚了，就出最小牌，希望之后玩家出更大的
            ret=buffer_Deck[this_turn_suit][0]
            if(judge_card(ret)):
                return ret
            else:
                return None
    elif state == 8:#状态八：最后一个出牌 && 无相同花色 && 有黑桃Q
        first_card:Card = thisTurnOutCard[0][1]
        this_turn_suit = first_card.suit
        has_heart = bool(len(buffer_Deck[3]))
        if outHeart and first_card.suit != 3 and has_heart :#不出黑桃Q，
                                                            #把最大的红心出了
            ret=buffer_Deck[3][-1]
            if(judge_card(ret)):
                return ret
            else:
                return None
        #没法出红心坑别人时，干脆先清一下大牌
        #优先清掉大于10的大牌
        for idx,suit_kind in enumerate(buffer_Deck):
            if suit_kind and suit_kind[-1].point > 10:
                ret=suit_kind[-1]
                if(judge_card(ret)):
                    return ret
                else:
                    return None
        #如果没有大于10的大牌，先把牌最多的出了
        ret=max(buffer_Deck[0:3],key=lambda cards: len(cards))[-1]
        if(judge_card(ret)):
            return ret
        else:
            return None
    elif state == 9:#状态九：最后一个出牌 && 无相同花色 && 如果没黑桃Q
        ########和state 8 一样
        first_card:Card = thisTurnOutCard[0][1]
        this_turn_suit = first_card.suit
        has_heart = bool(len(buffer_Deck[3]))
        if outHeart and first_card.suit != 3 and has_heart :#不出黑桃Q，
                                                            #把最大的红心出了
            ret=buffer_Deck[3][-1]
            if(judge_card(ret)):
                return ret
            else:
                return None
        #没法出红心坑别人时，干脆先清一下大牌

        #优先清掉大于10的大牌
        for idx,suit_kind in enumerate(buffer_Deck):
            if suit_kind and suit_kind[-1].point > 10:
                ret=suit_kind[-1]
                if(judge_card(ret)):
                    return ret
                else:
                    return None
        #如果没有大于10的大牌，先把牌最多的出了
        ret=max(buffer_Deck[0:3],key=lambda cards: len(cards))[-1]
        if(judge_card(ret)):
            return ret
        else:
            return None
    elif state == 10:#状态十最后一个出牌 && 有相同花色 && 出的牌里没有猪和红桃
        first_card:Card = thisTurnOutCard[0][1]
        this_turn_suit = first_card.suit
        def buffer_func(x:List,first_suit:int):
            if x[1].suit != first_suit:
                return -100
            else:
                return x[1].point
        others_max_card = max(thisTurnOutCard,key=lambda x:buffer_func(x,this_turn_suit))
        #把自己最小的牌出了
        if not (buffer_Deck[this_turn_suit][0].suit == 2 and\
            buffer_Deck[this_turn_suit][0].point == 12):
            ret=buffer_Deck[this_turn_suit][0]
            if(judge_card(ret)):
                return ret
            else:
                return None
        else:
            ret=buffer_Deck[this_turn_suit][-1]
            if(judge_card(ret)):
                return ret
            else:
                return None
    elif state == 11:#状态十一：最后一个出牌 && 有相同花色 && 有猪和红桃如果出现了分 && 有小牌
        #把同花色最小的牌出了，如果无法避免拿分就把最大的牌出了
        first_card:Card = thisTurnOutCard[0][1]
        this_turn_suit = first_card.suit
        def buffer_func(x:List,first_suit:int):
            if x[1].suit != first_suit:
                return -100
            else:
                return x[1].point
        others_max_card = max(thisTurnOutCard,key=lambda x:buffer_func(x,this_turn_suit))[1]
        my_min_card = buffer_Deck[this_turn_suit][0]
        if my_min_card.point < others_max_card.point:
            ret=my_min_card
            if(judge_card(ret)):
                return ret
            else:
                return None
        else:#拿分不可避免,干脆把最大的出了
            ret=buffer_Deck[this_turn_suit][-1]
            if(judge_card(ret)):
                return ret
            else:
                return None
    elif state==12: #状态十二：最后一个出牌 && 有相同花色 && 有猪和红桃如果出现了分 && 没有小牌
        #把最小的牌出了
        first_card:Card = thisTurnOutCard[0][1]
        this_turn_suit = first_card.suit
        ret=buffer_Deck[this_turn_suit][0]
        if(judge_card(ret)):
            return ret
        else:
            return None


class State:
    def __init__(self) :
        self.first_in_turn = False
        self.have_blackpeach = False
        self.have_blackpeach_larger_than_Q = False
        self.have_blackpeach_lessEqual_Q = False
        self.have_blackpeach_Q = False
        self.sec_or_thir_in_turn = False
        self.have_current_suit = False#是否有当前花色，即是否可以按对应花色跟牌
        self.have_smaller_than_others_max = False#是否有比其他人已出的最大牌还小的牌
        self.last_in_turn = False
    def to_false(self):
        #把所有条件全部归为False
        self.first_in_turn = False
        self.have_blackpeach = False
        self.have_blackpeach_larger_than_Q = False
        self.have_blackpeach_lessEqual_Q = False
        self.have_blackpeach_Q = False
        self.sec_or_thir_in_turn = False
        self.have_current_suit = False#是否有当前花色，即是否可以按对应花色跟牌
        self.have_smaller_than_others_max = False#是否有比其他人已出的最大牌还小的牌
        self.last_in_turn = False
    def buffer_func(card:Card,suit):
            if card.suit == suit:
                return card.rank
            else:
                return -1000#本函数只用于从本轮已出牌中找出最大同花色跟牌


    '''def update_state(self,this_turn_out_card:List,card_in_hand:List[Card]):
       
        
        self.to_false()
        idx_in_turn = len(this_turn_out_card)+1
        #分清自己是本轮第几个
        self.first_in_turn = (idx_in_turn==1)
        self.sec_or_thir_in_turn = (idx_in_turn==2 or idx_in_turn==3)
        self.last_in_turn = (idx_in_turn==4)
        if not self.first_in_turn:
            first_suit = this_turn_out_card[0][1].suit
            max_card_and_owner = max(this_turn_out_card,key=lambda x:  self.buffer_func(x[1],first_suit))
        else:
            max_card_and_owner = None
        for idx,card in enumerate(card_in_hand):
            if card.suit == 2:#有黑桃
                self.have_blackpeach = True
                if card.rank>12:#是否有黑桃>Q的
                    self.have_blackpeach_larger_than_Q =True
                else:
                    self.have_blackpeach_lessEqual_Q = True
                if card.rank==12:
                    self.have_blackpeach_Q = True
            if not self.first_in_turn:#如果不是本轮第一个出牌，判断是否有相同花色
                if card.suit == this_turn_out_card[0][1].suit:
                    self.have_current_suit = True
                    if card.rank < max_card_and_owner[1].rank:
                        self.have_smaller_than_others_max = True'''



class QLearning:
    def __init__(self,alpha:float,gamma:float,train=True,load_parameters = False):#gamma is learn rate
        self.round = 0
        self.last_state = -1
        self.last_action = None
        self.alpha = alpha
        self.gamma = gamma
        self.Reward = {'good':10,'bad':5}
        self.train = train
        # 对于Q值我们分为12种状态，且每种状态对应两个action：“greedy”与非“greedy”
        if load_parameters:
            filename = 'Q_values_trained.json'
            with open(filename, 'r') as file:
                loaded_data = json.load(file)
            self.Q = {eval(key): value for key, value in loaded_data.items()}
        else:
            self.Q = {(1,'good'):0,(1,'bad'):0,(2,'good'):0,(2,'bad'):0,(3,'good'):0,(3,'bad'):0,(4,'good'):0,(4,'bad'):0,(5,'good'):0,(5,'bad'):0,(6,'good'):0,(6,'bad'):0,(7,'good'):0,(7,'bad'):0,\
                  (8,'good'):0,(8,'bad'):0,(9,'good'):0,(9,'bad'):0,(10,'good'):0,(10,'bad'):0,(11,'good'):0,(11,'bad'):0,(12,'good'):0,(12,'bad'):0}
    def reward(self,action):#奖励函数
        return self.Reward[(action)]

    def Q_value(self,state,action):#返回Q值
        if (state,action) in self.Q:
            return self.Q[(state,action)]
        else:
            print(f"warning: ({state},{action}) not in Q")
            return 0
    def Q_update(self,action,state_new):# Q值更新，参见PPT
        if self.last_state != -1:
            sample = self.reward(self.last_action) + self.gamma * max(self.Q[state_new,'good'],self.Q[state_new,'bad'])
            self.Q[(self.last_state,self.last_action)] = (1-self.alpha)*self.Q[(self.last_state,self.last_action)]+self.alpha*sample
        self.round +=1
        self.last_state=state_new
        self.last_action = action
    def whether_do_good(self,state:int):
        good_Q = self.Q_value(state,'good')
        bad_Q = self.Q_value(state,'bad')
        threshod = 0.5
        if good_Q == 0 or bad_Q == 0:
            threshod = 0.5
        else:
            threshod = good_Q/(good_Q+bad_Q)
        draw = random.random()
        if draw <= threshod:
            self.Q_update('good',state)
            return True
        else:
            self.Q_update('bad',state)
            return False


class Game:
    # 游戏类,该类中封装了一个规则玩牌函数PlayCards，和传牌函数TransferThreeCards
    # find_first, choose_card, split_by_suit都是上述两函数用到的
    # getScoreFromGame是从游戏记录中history_P0以及history中统计得分情况
    # auto_play为一局13个回合的游戏函数，游戏过程将会打印出来
    def __init__(self):
        self.deck = Deck()
        self.players = [None]*4
        self.history = [[], [], [], []] # 四个玩家已经出的牌
        self.history_P0 = [] # 每轮先出的玩家的index
        self.deck.shuffle()
        # 先洗牌

        for player_id, one_deck in enumerate(self.deck.deal()):
            self.players[player_id] = Player(player_id, one_deck)
            # 发牌
        self.players[0].sortHand()
        self.players[1].sortHand()
        self.players[2].sortHand()
        self.players[3].sortHand()
        # 排序手中的牌

    def find_first(self):
        '''
        从已出牌中判断该谁先出牌
        '''
        first_id = 0
        if not self.history_P0: # 如果还未出牌，则有梅花2的先出
            for player_id in range(4):
                if self.players[player_id].hand[0] == Card(2, 0):
                    first_id = player_id
        else: # 找到上回合得到出牌权的玩家
            last_first = self.history_P0[-1]
            card_max = self.history[last_first][-1]
            for i in range(4):
                now_card = self.history[(last_first + i) % 4][-1]
                if now_card.suit == card_max.suit and now_card.point > card_max.point:
                    card_max = now_card
                    first_id = (last_first + i) % 4
        return first_id

    def choose_card(self, suitsDeck, flag):
        '''
        传入待选择的几个花色，选出最大的值或者最小的值。(此时应可任选花色)
        suitsDeck: 不同花色牌的列表
        flag: 0,选最大; 1,选最小
        '''
        k = flag * 15
        m, pos = None, None
        for oneSuitDeck in suitsDeck:
            if len(oneSuitDeck) == 0:
                continue
            else:
                if flag == 1:
                    if oneSuitDeck[0].point <= k:  # 跨花色最最小的牌
                        pos = oneSuitDeck[0]  # 出最小
                        k = oneSuitDeck[0].point
                        m = oneSuitDeck
                elif flag == 0:
                    if oneSuitDeck[-1].point >= k:  # 跨花色选最大的牌
                        pos = oneSuitDeck[-1]
                        k = oneSuitDeck[-1].point
                        m = oneSuitDeck
        if m:
            m.remove(pos)
            return pos
        else:
            return None

    def choose_card_1(self, suitsDeck, flag):
        '''随机出牌'''
        k = flag * 15
        m, pos = None, None
        for oneSuitDeck in suitsDeck:
            if len(oneSuitDeck) == 0:
                continue
            else:
                if flag == 1:
                    if oneSuitDeck[0].point <= k:
                        r = random.randint(0, len(oneSuitDeck)-1)
                        pos = oneSuitDeck[r]
                        k = oneSuitDeck[r].point
                        m = oneSuitDeck
                elif flag == 0:
                    if oneSuitDeck[-1].point >= k:
                        r = random.randint(0, len(oneSuitDeck)-1)
                        pos = oneSuitDeck[r]
                        k = oneSuitDeck[r].point
                        m = oneSuitDeck
        if m:
            m.remove(pos)
            return pos
        else:
            return None

    def split_by_suit(self, deck):
        '''
        将一摞牌按花色分摞
        '''
        a, b, c, d = [], [], [], []
        suitsDeck = [a, b, c, d]
        for card in deck:
            suitsDeck[card.suit].append(card)
        return suitsDeck

    # -------------传牌---出牌函数------------------------------

    def TransferThreeCards(self, deck):
        '''
        input:
        deck:         列表，当前玩家手中的13张牌，如：
                      deck = [Card(point=7, suit=0),Card(point=10, suit=3),Card(point=11, suit=3),...]
        output:
        transferCards:应当传出的三张牌
                      transferCards = [Card(point=7, suit=0),Card(point=10, suit=3),Card(point=11, suit=3)]
        '''
        deck = sorted(deck, key=lambda x: x.suit * 10 + x.point)
        kinds = self.split_by_suit(deck)
        select = []
        for i in range(3):  # 先选大于黑桃Q的AKQ
            if len(kinds[2]) != 0:  # 若有黑桃
                if kinds[2][-1].point >= 10:  #
                    select.append(kinds[2].pop())
            else:  #
                break
        for i in range(4):  # 再选红桃大于J的AKQJ
            if len(kinds[3]) != 0:
                if kinds[3][-1].point >= 9:
                    select.append(kinds[3].pop())
            else:
                break
        while len(select) < 3:  # 还不足三个的话，在梅花，方块里选最大的
            select.append(self.choose_card(kinds, 0))
        transferCards = [select[0], select[1], select[2]]
        return transferCards

    def PlayCards(self, deck, history_self, history_A, history_B, history_C, history_P0, REPLAY=False):
        '''
        输入一摞牌，选出最应该出的牌

        规则打牌的判断机制，对于自己第几个出，自己出牌前已经打出的牌，红桃牌，黑桃Q的打出情况，
        以及应该打出大小点等各类情况都进行判断，从而选出应当打出的最适合的牌。
        input:
        deck:           列表，当前玩家手中的牌，如：
                        deck = [Card(point=7, suit=0),Card(point=10, suit=3),Card(point=11, suit=3)]
        history_self:   同deck列表，当前玩家已出的牌
        history_A:      同deck列表，玩家A已出的牌
        history_B:      同deck列表，玩家B已出的牌
        history_C:      同deck列表，玩家C已出的牌
        history_P0:     列表，每个回合第一个发牌的人的index。当前玩家:0, A:1, B:2, C:3
                        如：history_P0 = [0,1,1]表示第一回合是当前玩家先出的牌，第二回合玩家1先出的牌，第三回合还是玩家1先出的牌
        REPLAY如果出牌不符合要求，则重新出牌
        output:
        pos: Card类型，选出的最优的牌
        '''

        deck = sorted(deck, key=lambda x: x.suit * 10 + x.point)
        history = [history_self, history_A, history_B, history_C]

        # 从输入参数中计算每轮出的牌
        allTurnsCard = []
        for i, j in enumerate(history_P0):
            tmp = []
            for k in range(4):
                now = history[(j + k) % 4]
                if len(now) > i:
                    tmp.append([(j + k) % 4, now[i]])
            allTurnsCard.append(tmp)

        thisTurnOutCard = allTurnsCard[-1] if allTurnsCard and len(allTurnsCard[-1]) != 4 else []
        if thisTurnOutCard:
            maxCard = \
                max([i for i in thisTurnOutCard if i[1].suit == thisTurnOutCard[0][1].suit], key=lambda x: x[1].point)[
                    1]
            print(maxCard)
        # outQueen = True if Card(12,2) in allTurnsCard else False
        outQueen = True if [outCard for turn in allTurnsCard for outCard in turn if
                            outCard[1] == Card(12, 2)] else False
        outHeart = True if [j for i in allTurnsCard for j in i if j[1].suit == 3] else False
        nowSuit = thisTurnOutCard[0][1].suit if thisTurnOutCard else None
        # print('queen:',outQueen,'heart:',outHeart)
        # 各花色已出牌数统计
        suit_numbers = list(map(lambda x: x.suit, sum(self.history, [])))
        suit_count_dict = {i: suit_numbers.count(i) for i in set(suit_numbers)}
        # print('thisTurn',thisTurnOutCard)
        kinds = self.split_by_suit(deck)  # 按花色分成四类排序
        if len(thisTurnOutCard) == 0:  # 如果是第一个出牌的
            if len(deck) == 13:  # 因为是第一回合且第一个出牌，最小的肯定是梅花2
                pos = deck[0]
            else:
                if (outHeart == False) and (deck[0].suit != 3):  # 如果红桃还没出，且当前最小值不是红桃
                    del kinds[3]  # 不能出红桃类
                if outQueen == False:
                    if (len(kinds[2]) == 0) or (kinds[2][-1].point >= 12):  # 没有黑桃或者黑桃最大值大于Q
                        pos = self.choose_card(kinds, 1)
                    else:  # 如果有小黑桃
                        pos = kinds[2][0]  # 出黑桃最小牌，拱猪
                else:  # 如果黑桃Q已出
                    pos = self.choose_card(kinds, 1)

        elif len(thisTurnOutCard) < 3:  # 如果电脑不是最后一个出的
            maxCard = 0
            for outCard in thisTurnOutCard:  # 对于每个出牌
                card = outCard[1]
                if card.suit == nowSuit:  # 找到这一轮花色的最大值
                    if card.point > maxCard:
                        maxCard = card.point
            if len(kinds[nowSuit]) == 0:  # 如果没有该花色，优先黑桃Q
                hasPig = False
                for spadeCard in kinds[2]:  # 黑桃中每个牌
                    if spadeCard.point == 12:  # 如果有黑桃Q
                        pos = spadeCard  # 打黑Q
                        HasPig = True
                        break
                if not hasPig:  # 如果没有黑Q
                    del kinds[nowSuit]  # 不出黑桃
                    pos = self.choose_card(kinds, 0)  # 在剩余的几个花色里选择最优的
                if len(deck) == 13:  # 如果是第一次出牌
                    while (pos.suit == 2 and pos.point == 12) or (pos.suit == 3):  # 如果是黑Q或红桃，一直再找最优
                        pos = self.choose_card(kinds, 0)  # flag是0，选最大值
                        # card = per.hand[pos]
            else:  # 如果有该花色
                if len(deck) == 13:  # 如果是第一轮出牌
                    pos = kinds[0][-1]  # 第一轮出最大的牌，第一轮肯定是梅花，故suit0
                else:
                    bigpos = []
                    smallpos = []
                    for card in kinds[nowSuit]:  # 分为比当前回合最大牌大和比它小的两摞
                        if card.point > maxCard:
                            bigpos.append(card)
                        else:
                            smallpos.append(card)
                    if len(smallpos) != 0:  # 如果有小的
                        pos = smallpos[-1]  # 就出小的里面最大的
                    else:
                        pos = bigpos[0]  # 大牌里面最小的
                        if pos.suit == 2 and pos.point == 12 and len(bigpos) >= 2:
                            pos = kinds[nowSuit][1]  # 如果没有小的，如果大的里面最小的是黑桃Q且大的有两张牌以上，选择比最小的大一的

        elif len(thisTurnOutCard) == 3:  # 如果该玩家最后一个出牌

            maxCard = 0  # 该花色最大的牌
            for outCard in thisTurnOutCard:
                card = outCard[1]  # 每个人出的牌
                if card.suit == nowSuit:
                    if card.point > maxCard:
                        maxCard = card.point
            if len(kinds[nowSuit]) == 0:  # 无该花色的牌
                hasPig = False
                for spadeCard in kinds[2]:  # 找黑桃Q
                    if spadeCard.point == 12:
                        pos = spadeCard
                        hasPig = True
                        break
                if not hasPig:
                    del kinds[nowSuit]  # 如果没黑桃Q，在除了该花色以外的里面选最优
                    pos = self.choose_card(kinds, 0)
                if len(deck) == 13:  # 如果是第一次出牌
                    while (pos.suit == 2 and pos.point == 12) or (pos.suit == 3):  # 找到的最优不能是黑桃Q或者红桃
                        pos = self.choose_card(kinds, 0)
            else:  # 有该花色的牌
                if len(deck) == 13:  # 第一轮出该花色最大的牌
                    pos = kinds[0][-1]
                else:  # 其他轮小心猪和红桃
                    hasScoreCard = False  # 看出的牌里是否有猪和红桃
                    for outCard in thisTurnOutCard:
                        card = outCard[1]
                        if (card.suit == 2 and card.point == 12) or (card.suit == 3):
                            hasScoreCard = True
                            break
                    if not hasScoreCard:  # 如果没有分
                        pos = kinds[nowSuit][-1]  # 出最大的，最大的是猪的话出黑桃里小一点的。
                        if pos.suit == 2 and pos.point == 12 and len(kinds[nowSuit]) >= 2:
                            pos = kinds[nowSuit][-2]  # （如果黑桃只有一张Q了，就只能出去了）
                    else:  # 如果出现了分
                        bigpos = []
                        smallpos = []
                        for card in kinds[nowSuit]:
                            if card.point > maxCard:
                                bigpos.append(card)
                            else:
                                smallpos.append(card)
                        if len(smallpos) != 0:  # 有小牌， 就出比当前最大的小一的牌
                            pos = smallpos[-1]
                        else:  # 没有小牌，就只能拿分了，用最大的牌来拿分，如果最大的牌是黑Q尽量避免黑Q，选用黑小，无黑小则只能用黑Q了
                            pos = bigpos[-1]
                            if pos.suit == 2 and pos.point == 12 and len(bigpos) >= 2:
                                pos = bigpos[-2]
        return pos

    def Q_learning(self,deck, history_self, history_A, history_B, history_C, history_P0, Q_class:QLearning):
    
        which_action_we_choose = 2 # 0:good action 1:bad action
        def sorter(x:Card):
            return x.suit*10 + x.point
        deck = sorted(deck, key=sorter)
        history = [history_self, history_A, history_B, history_C]
        flag = random.random()
        
        allTurnsCard = []
        for i, j in enumerate(history_P0):
            tmp = []
            for k in range(4):
                now = history[(j + k) % 4]
                if len(now) > i:
                    tmp.append([(j + k) % 4, now[i]])
            allTurnsCard.append(tmp)

        if allTurnsCard:
            if len(allTurnsCard[-1]) != 4:
                thisTurnOutCard = allTurnsCard[-1]
            else:
                thisTurnOutCard = list()
        else:
            thisTurnOutCard = list()
        #thisTurnOutCard = allTurnsCard[-1] if allTurnsCard and len(allTurnsCard[-1]) != 4 else []
        if thisTurnOutCard:
            maxCard = \
            max([i for i in thisTurnOutCard if i[1].suit == thisTurnOutCard[0][1].suit], key=lambda x: x[1].point)[1]
            print(maxCard)
        outQueen = False
        outHeart = False
        for i in allTurnsCard:
            for j in i:
                if j[1].point == 12 and j[1].suit == 2:
                    outQueen = True
                if j[1].suit == 3:
                    outHeart = True
        nowSuit = None
        if thisTurnOutCard:
            nowSuit = thisTurnOutCard[0][1].suit
        first_round = len(deck) == 13
        first_in_turn = len(thisTurnOutCard) == 0
        sec_or_third_in_turn = len(thisTurnOutCard) == 1 or len(thisTurnOutCard) == 2
        last_in_turn = len(thisTurnOutCard) == 3
        kinds = self.split_by_suit(deck)  # four suits are splited
        def card_point_judge(player_card_pair:tuple,suit):
                this_card = player_card_pair[1]
                if this_card.suit != suit:
                    return 0
                else:
                    return this_card.point
        if first_in_turn:  # 如果是第一个出牌的
            if first_round:  # 因为是第一回合且第一个出牌，最小的肯定是梅花2
                pos = deck[0]
            else:
                if (outHeart == False) and (deck[0].suit != 3):  
                    del kinds[3]  
                if outQueen:
                    if Q_class.whether_do_good(3):
                        which_action_we_choose = 0
                        pos = self.choose_card(kinds, 1)
                    else:
                        which_action_we_choose = 1
                        pos = bad_action(3,kinds,thisTurnOutCard,outHeart)
                    
                else:  # 状态三 即第一个出牌 && 如果有小黑桃 && 如果黑桃Q已出
                    if (kinds[2] == []) or (kinds[2][-1].point >= 12):  # 没有黑桃或者黑桃最大值大于Q
                        # 状态一 即第一个出牌 && 没有黑桃或者黑桃最大值大于Q && 黑桃Q未出
                        if Q_class.whether_do_good(1):
                            which_action_we_choose = 0
                            pos = self.choose_card(kinds, 1) #选择所有牌中最小的牌 good action

                        else:
                            which_action_we_choose = 1
                            pos = bad_action(1,kinds,thisTurnOutCard,outHeart)
                    else:  # 状态二 即第一个出牌 && 如果有小黑桃 && 黑桃Q未出
                        if Q_class.whether_do_good(2): # good action
                            which_action_we_choose = 0
                            pos = kinds[2][0]
                        else:
                            which_action_we_choose = 1
                            pos = bad_action(2,kinds,thisTurnOutCard,outHeart)
        elif not last_in_turn:  
            maxCard = max(thisTurnOutCard,key=lambda x: card_point_judge(x,nowSuit))[1].point
            if kinds[nowSuit] == []:  # 状态四：第二、三个出牌 && 没有相同花色 && 有黑桃Q
                hasPig = False
                for i in kinds[2]:  # 黑桃中每个牌
                    if i.point == 12:  # 如果有黑桃Q
                        if Q_class.whether_do_good(4): # good action
                            which_action_we_choose = 0
                            pos = i  # 打黑Q
                            hasPig = True
                            break
                        else: #bad action
                            which_action_we_choose = 1
                            pos = bad_action(4,kinds,thisTurnOutCard,outHeart)
                            break

                if not hasPig:  # 状态五：第二、三个出牌 && 没有相同花色 && 没有黑Q
                    if Q_class.whether_do_good(5):
                        which_action_we_choose = 0
                        del kinds[nowSuit]  # 不出黑桃
                        pos = self.choose_card(kinds, 0) 
                    else:
                        which_action_we_choose = 1
                        pos = bad_action(5,kinds,thisTurnOutCard,outHeart)
                if first_round:  # 如果是第一次出牌
                    while (pos.suit == 2 and pos.point == 12) or (pos.suit == 3):  # 如果是黑Q或红桃，一直再找最优
                        pos = self.choose_card(kinds, 0)  # flag是0，选最大值
                        # card = per.hand[pos]
            else:  # 如果有该花色
                if first_round:  
                    pos = kinds[0][-1]
                else:
                    bigpos = [i for i in kinds[nowSuit] if i.point>maxCard]
                    smallpos = [i for i in kinds[nowSuit] if i.point<=maxCard]
                    # 分为比当前回合最大牌大和比它小的两摞

                    # 状态六 ：2~3出牌 && 有相同花色 && 有比当前已出最大牌小的
                    if smallpos:
                        if Q_class.whether_do_good(6): # good action
                            which_action_we_choose = 0
                            pos = smallpos[-1]  # 就出小的里面最大的
                        else:
                            which_action_we_choose = 1
                            pos = bad_action(6,kinds,thisTurnOutCard,outHeart)
                    else: #状态七 ：2~3出牌 && 有相同花色 && 只有比当前max大的牌
                        if Q_class.whether_do_good(7): # good action
                            which_action_we_choose = 0
                            pos = bigpos[0]  # 大牌里面最小的
                            if pos.suit == 2 and pos.point == 12 and len(bigpos) >= 2:
                                pos = kinds[nowSuit][1]  # 如果没有小的，如果大的里面最小的是黑桃Q且大的有两张牌以上，选择比最小的大一的
                        else:
                            which_action_we_choose = 1
                            pos = bad_action(7,kinds,thisTurnOutCard,outHeart)

        elif last_in_turn:  
            maxCard = max(thisTurnOutCard,key=lambda x: card_point_judge(x,nowSuit))[1].point
            if kinds[nowSuit]:  
                if first_round:  
                    pos = kinds[0][-1]
                else:  
                    hasScoreCard = False  
                    for outCard in thisTurnOutCard:
                        card = outCard[1]
                        if (card.suit == 2 and card.point == 12) or (card.suit == 3):
                            hasScoreCard = True
                            break
                    if not hasScoreCard:  #  状态十最后一个出牌 && 有相同花色 && 看出的牌里没有猪和红桃
                        if Q_class.whether_do_good(10):
                            which_action_we_choose = 0
                            pos = kinds[nowSuit][-1]  
                            if pos.suit == 2 and pos.point == 12 and len(kinds[nowSuit]) >= 2:
                                pos = kinds[nowSuit][-2]  
                        else:
                            which_action_we_choose = 1
                            pos = bad_action(10,kinds,thisTurnOutCard,outHeart)
                    else:  # 如果出现了分
                        bigpos = []
                        smallpos = []
                        for card in kinds[nowSuit]:
                            if card.point > maxCard:
                                bigpos.append(card)
                            else:
                                smallpos.append(card)
                        if len(smallpos) >1:  #   状态十一：最后一个出牌 && 有相同花色 && 有猪和红桃如果出现了分 && 有小牌
                            if Q_class.whether_do_good(11):
                                which_action_we_choose = 0
                                pos = smallpos[-1] #就出比当前最大的小一的牌
                            else:
                                which_action_we_choose = 1
                                pos = bad_action(11,kinds,thisTurnOutCard,outHeart)
                        else:
                            # 状态十二：最后一个出牌 && 有相同花色 && 有猪和红桃如果出现了分 && 没有小牌
                            if Q_class.whether_do_good(12):
                                which_action_we_choose = 0
                                
                                pos = bigpos[-1]
                                if pos.suit == 2 and pos.point == 12 and len(bigpos) >= 2:
                                    pos = bigpos[-2]
                            else:
                                which_action_we_choose = 1
                                pos = bad_action(12,kinds,thisTurnOutCard,outHeart)
                
            else:
                hasPig = False
                for sc in kinds[2]:  # 状态八：最后一个出牌 && 五相同花色 && 有黑桃Q
                    if sc.point == 12:
                        if Q_class.whether_do_good(8):
                            which_action_we_choose = 0
                            pos = sc
                            hasPig = True
                            break
                        else:
                            which_action_we_choose = 1
                            pos = bad_action(8,kinds,thisTurnOutCard,outHeart)
                            break
                if not hasPig:
                    del kinds[nowSuit]  # 状态九：最后一个出牌 && 五相同花色 && 如果没黑桃Q
                    if Q_class.whether_do_good(9):
                        which_action_we_choose = 0
                        pos = self.choose_card(kinds, 0)
                    else:
                        which_action_we_choose = 1
                        pos = bad_action(9,kinds,thisTurnOutCard,outHeart)
                if first_round:  # 如果是第一次出牌
                    while (pos.suit == 2 and pos.point == 12) or (pos.suit == 3):  # 找到的最优不能是黑桃Q或者红桃
                        pos = self.choose_card(kinds, 0)
                                
        return pos

    def random_play(self, deck, history_self, history_A, history_B, history_C, history_P0, REPLAY=False):

        deck = sorted(deck, key=lambda x: x.suit * 10 + x.point)
        history = [history_self, history_A, history_B, history_C]

        # 从输入参数中计算每轮出的牌
        allTurnsCard = []
        for i, j in enumerate(history_P0):
            tmp = []
            for k in range(4):
                now = history[(j + k) % 4]
                if len(now) > i:
                    tmp.append([(j + k) % 4, now[i]])
            allTurnsCard.append(tmp)

        thisTurnOutCard = allTurnsCard[-1] if allTurnsCard and len(allTurnsCard[-1]) != 4 else []
        if thisTurnOutCard:
            maxCard = \
            max([i for i in thisTurnOutCard if i[1].suit == thisTurnOutCard[0][1].suit], key=lambda x: x[1].point)[1]
            # print(maxCard)
        # outQueen = True if Card(12,2) in allTurnsCard else False
        outQueen = True if [outCard for turn in allTurnsCard for outCard in turn if
                            outCard[1] == Card(12, 2)] else False
        outHeart = True if [j for i in allTurnsCard for j in i if j[1].suit == 3] else False
        nowSuit = thisTurnOutCard[0][1].suit if thisTurnOutCard else None
        # print('queen:',outQueen,'heart:',outHeart)
        # 各花色已出牌数统计
        suit_numbers = list(map(lambda x: x.suit, sum(self.history, [])))
        suit_count_dict = {i: suit_numbers.count(i) for i in set(suit_numbers)}
        # print('thisTurn',thisTurnOutCard)
        kinds = self.split_by_suit(deck)  # 按花色分成四类排序
        if len(thisTurnOutCard) == 0:  # 如果是第一个出牌的
            if len(deck) == 13:  # 因为是第一回合且第一个出牌，最小的肯定是梅花2
                pos = deck[0]
            else:
                if (outHeart == False) and (deck[0].suit != 3):  # 如果红桃还没出，且当前最小值不是红桃
                    del kinds[3]  # 不能出红桃类
                if outQueen == False:
                    if (len(kinds[2]) == 0) or (kinds[2][-1].point >= 12):  # 没有黑桃或者黑桃最大值大于Q
                        pos = self.choose_card_1(kinds, 1)
                    else:  # 如果有小黑桃
                        pos = kinds[2][random.randint(0,len(kinds[2])-1)]  # 出黑桃最小牌，拱猪
                else:  # 如果黑桃Q已出
                    pos = self.choose_card_1(kinds, 1)

        elif len(thisTurnOutCard) < 3:  # 如果电脑不是最后一个出的

            maxCard = 0
            for outCard in thisTurnOutCard:  # 对于每个出牌
                card = outCard[1]
                if card.suit == nowSuit:  # 找到这一轮花色的最大值
                    if card.point > maxCard:
                        maxCard = card.point
            if len(kinds[nowSuit]) == 0:  # 如果没有该花色，优先黑桃Q
                # hasPig = False
                # for spadeCard in kinds[2]:  # 黑桃中每个牌
                #     if spadeCard.point == 12:  # 如果有黑桃Q
                #         pos = spadeCard  # 打黑Q
                #         HasPig = True
                #         break
                # if not hasPig:  # 如果没有黑Q
                #     del kinds[nowSuit]  # 不出黑桃
                pos = self.choose_card_1(kinds, 0)  # 在剩余的几个花色里选择最优的
                if len(deck) == 13:  # 如果是第一次出牌
                    while (pos.suit == 2 and pos.point == 12) or (pos.suit == 3):  # 如果是黑Q或红桃，一直再找最优
                        pos = self.choose_card_1(kinds, 0)  # flag是0，选最大值
                        # card = per.hand[pos]
            else:  # 如果有该花色
                if len(deck) == 13:  # 如果是第一轮出牌
                    pos = kinds[0][random.randint(0,len(kinds[0])-1)]  # 第一轮出最大的牌，第一轮肯定是梅花，故suit0
                else:
                    bigpos = []
                    smallpos = []
                    for card in kinds[nowSuit]:  # 分为比当前回合最大牌大和比它小的两摞
                        if card.point > maxCard:
                            bigpos.append(card)
                        else:
                            smallpos.append(card)
                    if len(smallpos) != 0:  # 如果有小的
                        pos = random.choice(smallpos)  # 就出小的里面最大的
                    else:
                        pos = random.choice(bigpos)  # 大牌里面最小的
                        # if pos.suit == 2 and pos.point == 12 and len(bigpos) >= 2:
                        #     pos = kinds[nowSuit][1]  # 如果没有小的，如果大的里面最小的是黑桃Q且大的有两张牌以上，选择比最小的大一的

        elif len(thisTurnOutCard) == 3:  # 如果该玩家最后一个出牌

            maxCard = 0  # 该花色最大的牌
            for outCard in thisTurnOutCard:
                card = outCard[1]  # 每个人出的牌
                if card.suit == nowSuit:
                    if card.point > maxCard:
                        maxCard = card.point
            if len(kinds[nowSuit]) == 0:  # 无该花色的牌
                hasPig = False
                for spadeCard in kinds[2]:  # 找黑桃Q
                    if spadeCard.point == 12:
                        pos = spadeCard
                        hasPig = True
                        break
                if not hasPig:
                    del kinds[nowSuit]  # 如果没黑桃Q，在除了该花色以外的里面选最优
                    pos = self.choose_card_1(kinds, 0)
                if len(deck) == 13:  # 如果是第一次出牌
                    while (pos.suit == 2 and pos.point == 12) or (pos.suit == 3):  # 找到的最优不能是黑桃Q或者红桃
                        pos = self.choose_card_1(kinds, 0)
            else:  # 有该花色的牌
                if len(deck) == 13:  # 第一轮出该花色最大的牌
                    pos = kinds[0][-1]
                else:  # 其他轮小心猪和红桃
                    hasScoreCard = False  # 看出的牌里是否有猪和红桃
                    for outCard in thisTurnOutCard:
                        card = outCard[1]
                        if (card.suit == 2 and card.point == 12) or (card.suit == 3):
                            hasScoreCard = True
                            break
                    if not hasScoreCard:  # 如果没有分
                        pos = kinds[nowSuit][-1]  # 出最大的，最大的是猪的话出黑桃里小一点的。
                        if pos.suit == 2 and pos.point == 12 and len(kinds[nowSuit]) >= 2:
                            pos = kinds[nowSuit][-2]  # （如果黑桃只有一张Q了，就只能出去了）
                    else:  # 如果出现了分
                        bigpos = []
                        smallpos = []
                        for card in kinds[nowSuit]:
                            if card.point > maxCard:
                                bigpos.append(card)
                            else:
                                smallpos.append(card)
                        if len(smallpos) != 0:  # 有小牌， 就出比当前最大的小一的牌
                            pos = smallpos[-1]
                        else:  # 没有小牌，就只能拿分了，用最大的牌来拿分，如果最大的牌是黑Q尽量避免黑Q，选用黑小，无黑小则只能用黑Q了
                            pos = bigpos[-1]
                            if pos.suit == 2 and pos.point == 12 and len(bigpos) >= 2:
                                pos = bigpos[-2]
        return pos


    def getScoreFromGame(self):
        '''
        从游戏状态中获得得分情况
        '''
        allTurnsCard = [] # 每个回合的出牌情况，总共三层，第一层为玩家i，出牌c，第二层为4个玩家，第三层为出了几个回合[[[1,Card(2,3)],[2,Card(3,3)],[],[]]]
        for i, j in enumerate(self.history_P0):
            tmp = []
            for k in range(4):
                now = self.history[(j + k) % 4]
                if len(now) > i:
                    tmp.append([(j + k) % 4, now[i]])
            allTurnsCard.append(tmp)

        score = {i: 0 for i in range(4)}
        for turn in allTurnsCard:
            maximum = 0
            turnSuit = turn[0][1].suit
            s = 0
            for c in turn:
                if c[1].suit == 3:
                    s += 1
                if c[1] == Card(12, 2):
                    s += 13
                if c[1].suit == turnSuit and c[1].point > maximum:
                    maximum = c[0]
            score[maximum] += s
        if 26 in score.values(): # 是否有人收全红
            for i,j in score.items():
                if j == 26:
                    score[i] = 0
                else:
                    score[i]=26
        return score

    def show_the_picture(self,player_cards,turn):
        print(player_cards)
        pygame.init()
        # 设置窗口大小
        window_size = (1000, 750)

        # 创建第一个窗口
        screen1 = pygame.display.set_mode(window_size)
        pygame.display.set_caption("Window 1")

        # 创建第二个窗口
        screen2 = pygame.display.set_mode(window_size)
        pygame.display.set_caption("Window 2")

        # 设置窗口标题
        pygame.display.set_caption("Card Game")

        # 创建4x13的矩阵
        rows, cols = 4, 13
        photo_matrix = np.empty((rows, cols), dtype=object)

        # 调整照片大小为30x40
        def resize_photo(photo_path):
            original_photo = Image.open(photo_path)
            resized_photo = original_photo.resize((50, 60))
            return pygame.image.fromstring(resized_photo.tobytes(), resized_photo.size, resized_photo.mode)

        card_image_size = (50, 60)  # 根据需要调整卡片的大小
        # 填充矩阵数据
        for i in range(rows):
            for j in range(cols):
                suit = i  # 花色标为0到3 (梅花方块黑桃红桃)
                rank = j + 1  # 牌的大小标为1到13
                photo_path = f"card_picture/{suit}{rank}.png"

                # 检查文件是否存在
                if os.path.exists(photo_path):
                    resized_photo = resize_photo(photo_path)
                    photo_matrix[i, j] = resized_photo
                else:
                    print(suit,rank)
                    print("is none")
                    photo_matrix[i, j] = None



        font = pygame.font.Font(None, 36)  # 设置字体和大小

        running = True
        round_number = 0
        while running and round_number < 1:
            round_number += 1
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # 清空屏幕，将窗口底色更改为淡黄色
            screen1.fill((245, 245, 220)) # 这里是淡黄色的 RGB 值

            # 绘制每位玩家的出牌和名字
            for player, cards in player_cards.items():
                # 出牌位置
                card_positions = {
                    "Player 0 out": (100, 400),
                    "Player 0": (60, 300),
                    "Player 1 out": (500 - card_image_size[0]/2, 200),
                    "Player 1": (500 - (card_image_size[0]-20) * len(cards) / 2, 100),
                    "Player 2 out": (900, 400),
                    "Player 2": (750 - (card_image_size[0]-20) * len(cards) / 2, 300),
                    "Player 3 out": (500 - card_image_size[0]/2, 600),
                    "Player 3": (500 - (card_image_size[0]-20) * len(cards) / 2, 500),
                }
                position = card_positions[player]
                # 绘制玩家名字
                font = pygame.font.Font(None, 24)  # 设置字体和大小为24
                text = font.render(player, True, (0, 0, 0))
                text_rect = text.get_rect(
                    center=(position[0] + card_image_size[0] * len(cards) / 2, position[1] + card_image_size[1] + 10))
                screen1.blit(text, text_rect)
                # 绘制每张卡片

                for i, (value, suit) in enumerate(cards):
                    card_x = position[0] + i * (card_image_size[0]-20)  # 加入间隔
                    card_y = position[1]

                    # 照片名字编号顺序与函数不符，做出调整
                    real_card = 0
                    if value == 14:
                        real_card = 1
                    else:
                        real_card = value
                    screen1.blit(photo_matrix[suit][real_card-1], (card_x, card_y))
            # 绘制轮次信息
            round_text = font.render(f"Round {turn}", True, (0, 0, 0))
            screen1.blit(round_text, (20, 60))  # 调整轮次信息的位置
            # 更新显示
            pygame.display.flip()
            # 模拟一定的延迟，以便观察窗口变化
            pygame.time.delay(5000)
        pygame.quit()
        # sys.exit()

    def AutoPlay(self):

        train = True
        # whether we have a parameter .jason file
        load_params = False
        Q_class = QLearning(0.5,0.5,train=train,load_parameters=load_params)
        for turn_index in range(13):
            first_id = self.find_first()
            print(f'第{turn_index+1}回合___从玩家{first_id}开始' + '_' * 100)
            self.history_P0.append(first_id)
            player_cards_out = {
                "Player 0 out": [],
                "Player 1 out": [],
                "Player 2 out": [],
                "Player 3 out": [],
                "Player 0": [],
                "Player 1": [],
                "Player 2": [],
                "Player 3": [],
            }
            the_first_card = 0
            for i in range(4):
                out_index = (first_id + i) % 4
                print('玩家', out_index)
                before_hand = self.players[out_index].hand
                now_p0 = [(p0 + 4 - out_index) % 4 for p0 in self.history_P0]
                # 此处history_P0需做转换，对于不同的玩家，每个玩家都认为自己是玩家0，玩家0,1,2,3只是相对的指出各个玩家的顺序
                allTurnsCard = []
                history_P0=self.history_P0
                history=[ self.history[(out_index) % 4],
                                                self.history[(out_index + 1) % 4], self.history[(out_index + 2) % 4],
                                                self.history[(out_index + 3) % 4]]
                for i, j in enumerate(history_P0):
                    tmp = []
                    for k in range(4):
                        now = history[(j + k) % 4]
                        if len(now) > i:
                            tmp.append([(j + k) % 4, now[i]])
                    allTurnsCard.append(tmp)

                thisTurnOutCard = allTurnsCard[-1] if allTurnsCard and len(allTurnsCard[-1]) != 4 else []
                if thisTurnOutCard:
                    maxCard = \
                    max([i for i in thisTurnOutCard if i[1].suit == thisTurnOutCard[0][1].suit], key=lambda x: x[1].point)[1]
                nowSuit = thisTurnOutCard[0][1].suit if thisTurnOutCard else None
               
                
                if out_index == 0:  # 使用MonteCarlo
                    out_card = MonteCarloPlay_revised(self.players[out_index].hand, self.history[(out_index) % 4],
                                              self.history[(out_index + 1) % 4], self.history[(out_index + 2) % 4],
                                              self.history[(out_index + 3) % 4], now_p0,nowSuit)
                elif out_index == 1:  # 使用Q learning method
                    out_card = self.Q_learning(self.players[out_index].hand, self.history[(out_index) % 4],
                                              self.history[(out_index + 1) % 4], self.history[(out_index + 2) % 4],
                                              self.history[(out_index + 3) % 4], now_p0, Q_class=Q_class)
                elif out_index == 2 and Human_play == False: # 使用random 规则
                    out_card = self.random_play(self.players[out_index].hand, self.history[(out_index) % 4],
                                              self.history[(out_index + 1) % 4], self.history[(out_index + 2) % 4],
                                              self.history[(out_index + 3) % 4], now_p0)
                elif out_index == 2 and Human_play == True: # 我们将电脑玩家替换为人类玩家，引入输入窗口
                    flag = True
                    while flag == True:
                        print("now you have this cards:")
                        print([card2chinese(i) for i in before_hand])
                        card = input("which card would you like to play? (e.g. 0 represent the first card)")
                        if int(card) >= len(before_hand):
                            print("illegal input")
                            continue
                        out_card = before_hand[int(card)]

                        # 判断出牌是否合理
                        flag = False
                        if first_id != out_index:
                            # 判断是否有与第一个玩家相同化色：
                            flagsuit = False
                            for i in before_hand:
                                if i.suit == the_first_card:
                                    flagsuit = True
                            if out_card.suit != the_first_card and flagsuit:
                                print("you want to use card with suit: "+str(out_card.suit)+" but base on rule you should use card with suit: "+str(the_first_card) + " note: suit: 纸牌花色，梅花:0, 方块:1, 黑桃:2, 红桃:3")
                                print("please try again")
                                flag = True
                            else:
                                print("you want to use card with suit: " + str(out_card.suit) + "and base on rule you should " + str(the_first_card))

                else:
                    out_card = self.PlayCards(self.players[out_index].hand, self.history[(out_index) % 4],
                                              self.history[(out_index + 1) % 4], self.history[(out_index + 2) % 4],
                                              self.history[(out_index + 3) % 4], now_p0)
                if first_id == out_index:
                    the_first_card = out_card.suit
                print('hand:', [card2chinese(i) for i in before_hand])
                print('out_card:', card2chinese(out_card))
                if out_index == 0:
                    player_cards_out["Player 0 out"].append(out_card)
                if out_index == 1:
                    player_cards_out["Player 1 out"].append(out_card)
                if out_index == 2:
                    player_cards_out["Player 2 out"].append(out_card)
                if out_index == 3:
                    player_cards_out["Player 3 out"].append(out_card)
                if out_index == 0:
                    player_cards_out["Player 0"]=before_hand
                if out_index == 1:
                    player_cards_out["Player 1"]=before_hand
                if out_index == 2:
                    player_cards_out["Player 2"]=before_hand
                if out_index == 3:
                    player_cards_out["Player 3"]=before_hand

                self.players[out_index].hand.remove(out_card)
                self.history[out_index].append(out_card)
                print('------------------------------------------')
            self.show_the_picture(player_cards_out,turn_index+1)
        if train:
            filename = 'Q_values_trained.json'
            converted_data = {str(key): value for key, value in Q_class.Q.items()}
            with open(filename, 'w') as file:
                json.dump(converted_data, file)
        score = self.getScoreFromGame()
        for i, j in score.items():
            print(f'玩家{i}最终得分:{j}')
        return score

if __name__ == '__main__':
    scores = []
    '''
    进行n次游戏,统计得分情况
    '''
    NUM_GAME = 1
    for _ in range(NUM_GAME):
        game = Game()
        score = game.AutoPlay()
        scores.append(score)
        print(score)
