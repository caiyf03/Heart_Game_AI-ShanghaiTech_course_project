import datetime
from math import log, sqrt
from random import randint, choice
from Hand import Hand
import copy
from Variables import *
import Variables
import sys

class MonteCarlo_revised:
    # 构造函数初始化蒙特卡洛对象
    def __init__(self, game_state, name,suit, **kwargs):
        self.game_state = game_state  # 当前游戏状态
        self.ai = name  # AI的名称
        self.ai_player = self.get_ai_player()  # 获取AI玩家对象
        self.states = []  # 存储游戏状态的列表
        # 设置AI计算的时间
        self.calculation_time = datetime.timedelta(seconds=kwargs.get('time', Variables.monteCarloTime))
        self.max_moves = kwargs.get('max_moves', 100)  # 最大移动步数
        self.max_depth = 0  # 最大搜索深度
        self.wins = {}  # 胜利统计
        self.plays = {}  # 游戏次数统计
        self.C = kwargs.get('C', 1.4)  # 探索参数，默认1.4
        self.threshold_difference = 6  # 阈值差，用于决策，越大时间越长效果要求高，越小约快
        self.it=0
        self.suit=suit

    def redistribute(self, board):
        cards = []
        numOfCards = {}
        for player in board.players:
            if player.name != self.ai:
                num = 0
                for suit in player.hand.hand:
                    cards = cards + suit
                    num += len(suit)
                numOfCards[player.name] = num
        for player in board.players:
            if player.name != self.ai:
                hand = Hand()
                for x in range(numOfCards[player.name]):
                    index = randint(0,len(cards)-1)
                    cardAdd = cards[index]
                    cards.remove(cardAdd)
                    hand.addCard(cardAdd)
                player.hand = hand
                    
    # 获取AI玩家对象
    def get_ai_player(self):
        for player in self.game_state.players:
            if player.name == self.ai:
                return player
        return None

    # 更新游戏状态
    def update(self, state):
        self.states.append(state)

    # 获取下一个行动
    def get_play(self):
        legal_moves = self.get_legal_moves()  # 获取合法移动
        
        min_score = sys.maxsize
        max_score = -sys.maxsize - 1
        for p in self.game_state.players:
            if p.score < min_score:
                min_score = p.score
            if p.score > max_score:
                max_score = p.score
        if self.ai_player.score - min_score >= self.threshold_difference or \
           max_score - self.ai_player.score >= self.threshold_difference:
            self.useRoundScoreOnly = True
        else:
            self.useRoundScoreOnly = False
        
        if not legal_moves:
            return None
        if len(legal_moves) == 1:  # 如果只有一个合法移动，则选择它
            return legal_moves[0]

        self.simulate_games()  # 模拟游戏以更新统计数据
        return self.choose_best_move(legal_moves)  # 选择最佳移动

    # 获取合法移动
    def get_legal_moves(self):
        dic={"c":0,"d":1,"s":2,"h":3}
        hand=self.game_state.getLegalPlays(self.ai_player)
        real_legal=[]
        if(self.suit==None):
            return hand
        flag=0
        for i in hand:
            if(i.suit.iden==self.suit):
                real_legal.append(i)
                flag=1
        if flag==0:
            return hand
      
        return real_legal

    # 模拟多局游戏
    def simulate_games(self):
        begin = datetime.datetime.utcnow()  # 开始时间
        if(self.useRoundScoreOnly==True):
            self.calculation_time*=0.2
        while datetime.datetime.utcnow() - begin < self.calculation_time:#在规定时间内一直模拟
            self.run_simulation()  # 运行模拟


    # 从合法移动中选择最佳移动
    def choose_best_move(self, legal_moves):
        # 将移动和状态配对
        moves_states = [(move, self.game_state.cardsPlayed + (move,)) for move in legal_moves]
        if sum(self.wins.values()) == 0:  # 如果还没有胜利统计，则随机选择一个移动
            return choice(legal_moves)
        # 选择胜率最高的移动
        return max(
            (self.wins.get((self.ai_player, state), 0) / self.plays.get((self.ai_player, state), 1), move)
            for move, state in moves_states
        )[1]

    # 运行一次模拟
    def run_simulation(self):
        board = copy.deepcopy(self.game_state)  # 拷贝游戏状态
        state = self.states[-1]  # 获取最新状态
        visited_states = set()  # 访问过的状态集合
        expand = True  # 是否扩展新节点
        self.redistribute(board)
        for _ in range(self.max_moves):
            self.simulate_move(board, expand, visited_states)  # 模拟移动一步

        self.it=0
        self.update_stats(visited_states, board)  # 更新统计数据

    # 模拟一个移动
        # 如果扩展新节点且该状态未被访
    # 如果扩展新节点且该状态未被访问过，则将其加入plays和wins
    def simulate_move(self, board, expand, visited_states):
        player = board.getCurrentPlayer()  # 获取当前玩家
        legal_moves = board.getLegalPlays(player)  # 获取合法移动
        #print(player,legal_moves)
        if not legal_moves:
            return
        self.it+=1
        move, state = self.select_move(legal_moves, player, board)  # 选择移动
        board.step(move, player, True)  # 执行移动
        visited_states.add((player, state))  # 添加到访问过的状态


        if expand and (player, state) not in self.plays:
            self.plays[(player, state)] = 0  # 初始化该状态的游戏次数
            self.wins[(player, state)] = 0  # 初始化该状态的胜利次数
            expand = False

    # 选择一个移动
    def select_move(self, legal_moves, player, board):
        moves_states = [(move, board.cardsPlayed + (move,)) for move in legal_moves]
        #print(moves_states)
        # 如果所有可能的移动都至少被探索过一次
        if(player==self.ai_player ):
            #print("this is player mcts")    
            if all(self.plays.get((player, state)) for _, state in moves_states):
                log_total = log(sum(self.plays[(player, state)] for _, state in moves_states))
                _, move, state = max(
                    ((self.wins[(player, state)] / self.plays[(player, state)]) +
                    self.C * sqrt(log_total / self.plays[(player, state)]), move, state)
                    for move, state in moves_states
                )
            else:
                move, state = choice(moves_states)  # 否则随机选择一个移动
        else:  # Other AIs make decisions based on their simplistic strategy
            if(self.useRoundScoreOnly==True):#如果领先很多，就假定对面是naive模型
                if player.name == "AI 2":  # Pure Random
                    move, state = choice(moves_states)
                    #print("pass,random")
                elif player.name == "AI 3":  # Naive Min
                    move = min(legal_moves, key=lambda x: (x.suit, x.rank))
                    state = board.cardsPlayed + (move,)
                    #print("pass min")
                elif player.name== "AI 4":  # Naive Max
                    move = max(legal_moves, key=lambda x: (x.suit, x.rank))
                    state = board.cardsPlayed + (move,)
                    #print("pass max")
            else:#如果分差并不大，则假定对面是mcts
                if all(self.plays.get((player, state)) for _, state in moves_states):
                    log_total = log(sum(self.plays[(player, state)] for _, state in moves_states))
                    _, move, state = max(
                        ((self.wins[(player, state)] / self.plays[(player, state)]) +
                        self.C * sqrt(log_total / self.plays[(player, state)]), move, state)
                        for move, state in moves_states
                    )
                else:
                    move, state = choice(moves_states)  # 否则随机选择一个移动
        return move, state  # 返回选择的移动和对应的状态

    # 更新统计信息
    def update_stats(self, visited_states, board):
        winners=None
        if self.useRoundScoreOnly:
            winners = board.winningPlayers
        else:
            if board.winningPlayer is not None:
                winners = [board.winningPlayer]

        for player, state in visited_states: # 将本次模拟的结果添加到MonteCarlo类的plays和wins中
            if (player, state) not in self.plays:
                continue
            self.plays[(player, state)] += 1
            if player in winners:
                self.wins[(player,state)] += 1
        return