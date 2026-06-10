import os

import random
import collections
import threading
import time
import re
import copy
import uuid
from typing import Dict, Optional, List, Set, Tuple
import itertools

import shutil

import json
import pickle
import pandas as pd
import numpy as np

import socket
from flask import Flask, jsonify, request

import pyspiel
from open_spiel.python.algorithms import mcts

import redis

from visual import PokerTableDrawer


PATH = os.path.dirname(os.path.abspath(__file__))


num_simulations = 10000

def draw_action(lbl, agent_id, round, info, action, is_hero, 
                show_button=False, 
                game_info="", 
                opp_cards=[None, None]):
    """
    round:
        0 - 初始状态
        1 - 发玩家1的私牌
        2 - 发玩家2的私牌 
        3 - 小盲 / 大盲
        4 - 小盲出牌
        5 - 大盲出牌
        ......
    """
    os.makedirs(f"{PATH}/images/{lbl}", exist_ok=True)
    filename = f"{PATH}/images/{lbl}/{round}.png"
    drawer = PokerTableDrawer(card_folder=f"{PATH}/cards", filename=filename)
    hero_info = {
        'name': 'You',
        'stack': info.get('my_stack'),
        'bet': info.get("debug_spent")[agent_id],
        'cards': info.get('my_cards'),
        'avatar': f'{PATH}/avatars/hero.png',
        'is_dealer': True,
        'choices': info.get("detailed_actions", info.get("legal_actions")) if show_button else None,
        'action': action if is_hero else None
    }
    villain_info = {
        'name': 'Player X',
        'stack': info.get('opp_stack'),
        'bet': info.get("debug_spent")[1 - agent_id],
        'cards': opp_cards,
        'avatar': f'{PATH}/avatars/villain.png',
        'is_dealer': False,
        'action': None if is_hero else action
    }
    board = [card if card != 'Unknown' else None for card in info.get('public_cards')]
    drawer.generate(hero_info, villain_info, board, info.get('pot'), game_info)
    return filename


class HoldemEquityCalculator:
    SUIT_INDEX_DICT = {"s": 0, "c": 1, "h": 2, "d": 3}
    REVERSE_SUIT_INDEX = ("s", "c", "h", "d")
    VAL_STRING = "AKQJT98765432"
    HAND_RANKINGS = ("High Card", "Pair", "Two Pair", "Three of a Kind",
                     "Straight", "Flush", "Full House", "Four of a Kind",
                     "Straight Flush", "Royal Flush")
    SUIT_VALUE_DICT = {"T": 10, "J": 11, "Q": 12, "K": 13, "A": 14}
    for num in range(2, 10):
        SUIT_VALUE_DICT[str(num)] = num

    class Card:
        """内部类：表示一张扑克牌"""
        def __init__(self, card_string):
            """将输入的字符串（如 "As", "Tc", "6d"）解析并转换为程序内部可以处理的数值格式"""
            value, self.suit = card_string[0], card_string[1]
            self.value = HoldemEquityCalculator.SUIT_VALUE_DICT[value]
            self.suit_index = HoldemEquityCalculator.SUIT_INDEX_DICT[self.suit]

        def __str__(self):
            """返回这张牌的人类可读的字符串形式。如果你有一个数值为14、花色为's'的对象，它会返回字符串 'As'"""
            return HoldemEquityCalculator.VAL_STRING[14 - self.value] + self.suit

        def __repr__(self):
            """返回这张牌的人类可读的字符串形式。如果你有一个数值为14、花色为's'的对象，它会返回字符串 'As'"""
            return HoldemEquityCalculator.VAL_STRING[14 - self.value] + self.suit

        def __eq__(self, other):
            """只有当两张牌的数值（大小）和花色都完全一致时，才判定这两张牌相等"""
            if self is None:
                return other is None
            elif other is None:
                return False
            return self.value == other.value and self.suit == other.suit

    @classmethod
    def calculate(cls, hole_cards_list, board_cards=None, exact=True, num_simulations=20000):
        """
        计算德州扑克胜率。
        
        :param hole_cards_list: list of list of str. 
               例如: [["As", "Ks"], ["Qh", "Qd"]]
        :param board_cards: list of str. 
               例如: ["Ts", "Js", "2d"]。无公共牌传 None 或 []。
        :param exact: bool. 
               True 使用穷举法（精确，适合有公共牌时）。False 使用蒙特卡洛模拟（适合翻牌前）。
               如果 board_cards 大于3张，会自动穷举。
        :param num_simulations: int. 
               蒙特卡洛模拟的次数。
        :return: dict. 包含每个玩家的胜率信息
        """
        # 1. 数据预处理
        hole_cards_objs = []
        unknown_indices = []  # 记录哪些玩家是未知手牌

        for i, hand in enumerate(hole_cards_list):
            if hand is None:
                hole_cards_objs.append([None, None])
                unknown_indices.append(i)
            else:
                hole_cards_objs.append([cls.Card(c) for c in hand])

        assert len(unknown_indices) <= 1, "只能有一名玩家的手牌未知"
        
        board_objs = []
        if board_cards:
            board_objs = [cls.Card(c) for c in board_cards]

        # 2. 生成牌堆
        deck = cls._generate_deck(hole_cards_objs, board_objs)

        # 3. 初始化统计数据
        num_players = len(hole_cards_objs)
        winner_list = [0] * (num_players + 1)  # 0表示平局
        result_histograms = []
        for _ in range(num_players):
            result_histograms.append([0] * len(cls.HAND_RANKINGS))

        board_length = len(board_objs)

        # 4. 选择生成板牌的方法
        if exact or (board_objs and len(board_objs) >= 3):
            generate_boards = cls._generate_exhaustive_boards
            iter_limit = None 
        else:
            generate_boards = cls._generate_random_boards
            iter_limit = num_simulations

        # --- 处理未知手牌 ---
        if len(unknown_indices) > 0:
            # 遍历牌堆中所有可能的起手牌组合给未知玩家
            unknown_player_idx = unknown_indices[0]
            
            if iter_limit:
                possible_hole_cards = cls._generate_random_boards(deck, int(np.sqrt(iter_limit)), 2)
                iter_limit = int(np.sqrt(iter_limit))
            else:
                possible_hole_cards = cls._generate_exhaustive_boards(deck, iter_limit, 2)
            
            for filler_cards in possible_hole_cards:
                # 临时构建当前的手牌列表
                current_hole_cards = list(hole_cards_objs)
                current_hole_cards[unknown_player_idx] = list(filler_cards)
                
                # 从牌堆中临时移除这两张牌用于本次模拟
                current_deck = list(deck)
                current_deck.remove(filler_cards[0])
                current_deck.remove(filler_cards[1])
                
                # 执行模拟
                cls._find_winner(
                    generate_boards, 
                    tuple(current_deck), 
                    current_hole_cards, 
                    iter_limit, 
                    board_length, 
                    board_objs, 
                    winner_list, 
                    result_histograms
                )
        else:
            # --- 所有手牌已知 ---
            cls._find_winner(
                generate_boards, 
                deck, 
                hole_cards_objs, 
                iter_limit, 
                board_length, 
                board_objs, 
                winner_list, 
                result_histograms
            )

        # 6. 格式化结果 (保持不变)
        total_iterations = sum(winner_list)
        results = []
        tie_rate = float(winner_list[0]) / float(total_iterations) if total_iterations > 0 else 0

        for i in range(num_players):
            win_rate = float(winner_list[i + 1]) / float(total_iterations) if total_iterations > 0 else 0
            results.append({
                "player_id": i,
                "hole_cards": hole_cards_list[i],               # 手牌
                "win_rate": win_rate,                           # 胜率
                "tie_rate": tie_rate,                           # 平局率
                "equity": win_rate + (tie_rate / num_players)   # 总权益 (胜率 + 平局率/玩家数)
            })
        
        return results
    
    @classmethod
    def _find_winner(cls, generate_boards, deck, hole_cards, num, board_length,
                     given_board, winner_list, result_histograms):
        result_list = [None] * len(hole_cards)
        
        # 迭代生成剩余的公共牌
        for remaining_board in generate_boards(deck, num, 5 - board_length):
            if given_board:
                board = given_board[:]
                board.extend(remaining_board)
            else:
                board = remaining_board
            
            # 预处理板牌
            suit_histogram, histogram, max_suit = cls._preprocess_board(board)
            
            # 为每个玩家计算最佳手牌
            for index, hole_card in enumerate(hole_cards):
                result_list[index] = cls._detect_hand(hole_card, board, suit_histogram, histogram, max_suit)
            
            # 比较并记录赢家
            winner_index = cls._compare_hands(result_list)
            winner_list[winner_index] += 1
            
            # 记录手牌类型分布
            for index, result in enumerate(result_list):
                result_histograms[index][result[0]] += 1

    @staticmethod
    def _generate_deck(hole_cards, board):
        deck = []
        for suit in HoldemEquityCalculator.REVERSE_SUIT_INDEX:
            for value in HoldemEquityCalculator.VAL_STRING:
                deck.append(HoldemEquityCalculator.Card(value + suit))
        taken_cards = []
        for hole_card in hole_cards:
            for card in hole_card:
                if card is not None:
                    taken_cards.append(card)
        if board and len(board) > 0:
            taken_cards.extend(board)
        for taken_card in taken_cards:
            if taken_card in deck:
                deck.remove(taken_card)
        return tuple(deck)

    @staticmethod
    def _generate_random_boards(deck, num_iterations, num_samples):
        for _ in range(num_iterations):
            yield random.sample(deck, num_samples)

    @staticmethod
    def _generate_exhaustive_boards(deck, num_iterations, num_samples):
        return itertools.combinations(deck, num_samples)

    @staticmethod
    def _generate_suit_board(flat_board, flush_index):
        """生成同花的值列表"""
        histogram = [card.value for card in flat_board if card.suit_index == flush_index]
        histogram.sort(reverse=True)
        return histogram

    @staticmethod
    def _preprocess(histogram):
        return [(14 - index, frequency) for index, frequency in enumerate(histogram) if frequency]

    @staticmethod
    def _preprocess_board(flat_board):
        """将公共牌的原始数据转换成统计数据（花色、点数、最大同花数），以便后续快速判断牌型。"""
        suit_histogram, histogram = [0] * 4, [0] * 13
        for card in flat_board:
            histogram[14 - card.value] += 1
            suit_histogram[card.suit_index] += 1
        return suit_histogram, histogram, max(suit_histogram)

    @staticmethod
    def _detect_straight_flush(suit_board):
        contiguous_length, fail_index = 1, len(suit_board) - 5
        for index, elem in enumerate(suit_board):
            if index + 1 >= len(suit_board): 
                break
            current_val, next_val = elem, suit_board[index + 1]
            if next_val == current_val - 1:
                contiguous_length += 1
                if contiguous_length == 5:
                    return True, current_val + 3
            else:
                if index >= fail_index:
                    # 特殊情况处理：A-5-4-3-2 (最小的顺子，俗称"轮子")
                    if (index == fail_index and next_val == 5 and suit_board[0] == 14):
                        return True, 5
                    break
                contiguous_length = 1
        return False,

    @staticmethod
    def _detect_straight(histogram_board):
        contiguous_length, fail_index = 1, len(histogram_board) - 5
        for index, elem in enumerate(histogram_board):
            if index + 1 >= len(histogram_board): break
            current_val, next_val = elem[0], histogram_board[index + 1][0]
            if next_val == current_val - 1:
                contiguous_length += 1
                if contiguous_length == 5:
                    return True, current_val + 3
            else:
                if index >= fail_index:
                    if (index == fail_index and next_val == 5 and
                            histogram_board[0][0] == 14):
                        return True, 5
                    break
                contiguous_length = 1
        return False,

    @staticmethod
    def _detect_three_of_a_kind_kickers(histogram_board):
        kicker1 = -1
        for elem in histogram_board:
            if elem[1] != 3:
                if kicker1 == -1:  # 第一大
                    kicker1 = elem[0]
                else:  # 第二大
                    return kicker1, elem[0]

    @staticmethod
    def _detect_highest_kicker(histogram_board, floor):        
        """
            histogram_board: [(点数, 出现次数), (点数, 出现次数), ...]
        """
        for elem in histogram_board:
            if elem[1] < floor:
                return elem[0]

    @staticmethod
    def _detect_pair_kickers(histogram_board):
        kicker1, kicker2 = -1, -1
        for elem in histogram_board:
            if elem[1] != 2:
                if kicker1 == -1:
                    kicker1 = elem[0]
                elif kicker2 == -1:
                    kicker2 = elem[0]
                else:
                    return kicker1, kicker2, elem[0]

    @staticmethod
    def _get_high_cards(histogram_board):
        return histogram_board[:5]

    @classmethod
    def _detect_hand(cls, hole_cards, given_board, suit_histogram,
                    full_histogram, max_suit):
        """返回牌型等级 + 用于比较大小的关键牌
        9 -皇家同花顺
        8 - 同花顺
        7 - 四条
        6 - 葫芦
        5 - 同花
        4 - 顺子
        3 - 三条
        2 - 两对
        1 - 一对
        0 - 高牌
        """
        # 判断是否有同花的可能
        if max_suit >= 3:
            flush_index = suit_histogram.index(max_suit)
            for hole_card in hole_cards:
                if hole_card.suit_index == flush_index:
                    max_suit += 1
            # 判断是否有顺子可能
            if max_suit >= 5:
                flat_board = list(given_board)
                flat_board.extend(hole_cards)
                suit_board = cls._generate_suit_board(flat_board, flush_index)
                result = cls._detect_straight_flush(suit_board)
                if result[0]:
                    return (8, result[1], None, None, None, None) if result[1] != 14 else (9, None, None, None, None, None)
                kicker1, kicker2, kicker3, kicker4, kicker5 = cls._get_high_cards(suit_board)
                return 5, kicker1, kicker2, kicker3, kicker4, kicker5

        # 将手牌加入直方图统计
        full_histogram = full_histogram[:]
        for hole_card in hole_cards:
            full_histogram[14 - hole_card.value] += 1
        histogram_board = cls._preprocess(full_histogram)

        # 查找出现次数最多的点数
        current_max, max_val, second_max, second_max_val = 0, 0, 0, 0
        for item in histogram_board:
            val, frequency = item[0], item[1]
            if frequency > current_max:
                second_max, second_max_val = current_max, max_val
                current_max, max_val = frequency, val
            elif frequency > second_max:
                second_max, second_max_val = frequency, val

        # 检查成牌等级
        if current_max == 4:  # 四条
            return 7, max_val, cls._detect_highest_kicker(histogram_board, 4), None, None, None
        if current_max == 3 and second_max >= 2:  # 葫芦
            return 6, max_val, second_max_val, None, None, None
        if len(histogram_board) >= 5:
            result = cls._detect_straight(histogram_board)
            if result[0]:  # 顺子
                return 4, result[1], None, None, None, None
        if current_max == 3:  # 三条
            kicker1, kicker2 = cls._detect_three_of_a_kind_kickers(histogram_board)
            return 3, max_val, kicker1, kicker2, None, None
        if current_max == 2:
            if second_max == 2:  # 两对
                return 2, max_val, second_max_val, cls._detect_highest_kicker(histogram_board, 2), None, None
            else:  # 一对
                kicker1, kicker2, kicker3 = cls._detect_pair_kickers(histogram_board)
                return 1, max_val, kicker1, kicker2, kicker3, None
        kicker1, kicker2, kicker3, kicker4, kicker5 = cls._get_high_cards(histogram_board)
        return 0, kicker1, kicker2, kicker3, kicker4, kicker5

    @staticmethod
    def _compare_hands(result_list):
        """result_list: [(等级, 最大, 次大, ...), ...] """
        best_hand = max(result_list)
        winning_player_index = result_list.index(best_hand) + 1  # 不要从0开始
        if best_hand in result_list[winning_player_index:]:
            return 0  # 平局
        return winning_player_index


def get_perfect_information(state):
    raw_str = str(state)
    p0_cards = []
    p1_cards = []
    board_cards = []

    lines = raw_str.split('\n')
    for line in lines:
        if line.startswith("ACPC State:"):
            try:
                state_content = line.split("ACPC State:")[-1].strip()
                parts = state_content.split(":")
                if len(parts) >= 1:
                    cards_section = parts[-1] 
                    
                    hole_part = cards_section
                    if '/' in cards_section:
                        hole_part, board_part = cards_section.split('/', 1)
                        board_cards = re.findall(r'[2-9TJQKA][shdc]', board_part)
                    
                    hands = hole_part.split('|')
                    if len(hands) >= 2:
                        p0_cards = re.findall(r'[2-9TJQKA][shdc]', hands[0])
                        p1_cards = re.findall(r'[2-9TJQKA][shdc]', hands[1])
            except:
                pass

        if not p0_cards and "P0 Cards:" in line:
            p0_cards = re.findall(r'[2-9TJQKA][shdc]', line)
        if not p1_cards and "P1 Cards:" in line:
            p1_cards = re.findall(r'[2-9TJQKA][shdc]', line)
        if not board_cards and "BoardCards" in line:
            board_cards = re.findall(r'[2-9TJQKA][shdc]', line)
    
    return p0_cards, p1_cards, board_cards


def parse_spent_from_str(state_str: str) -> List[int]:
    p0_match = re.search(r'P0:\s*(\d+)', state_str)
    p1_match = re.search(r'P1:\s*(\d+)', state_str)
    return [int(p0_match.group(1)), int(p1_match.group(1))]
    

class SimpleRandomBot:
    def __init__(self, player_id):
        self._player_id = player_id

    def step(self, state):
        legal_actions = state.legal_actions(self._player_id)
        return random.choice(legal_actions)


class EquityBot:
    """
    基于胜率阈值的通用扑克 Bot。
    可以通过调整阈值参数来模拟 '激进派' 或 '保守派'。
    """
    def __init__(self, player_id, call_threshold, raise_threshold, all_threshold, num_simulations):
        """
        num_simulations = -1时，表示遍历所有可能
        """
        self._player_id = player_id
        self._call_threshold = call_threshold
        self._raise_threshold = raise_threshold
        self._all_threshold = all_threshold
        self._num_simulations = num_simulations
        assert all_threshold >= raise_threshold >= call_threshold, "概率设定需要满足: allin >= raise >= call"

    def step(self, state):
        legal_actions = state.legal_actions(self._player_id)
        
        # 如果只有一个动作，直接执行
        if len(legal_actions) == 1:
            return legal_actions[0]

        # 1. 计算当前胜率
        # 注意：这里传入 state 的克隆，防止修改原游戏状态
        p0_cards, p1_cards, board_cards = get_perfect_information(state)
        my_cards = p0_cards if self._player_id == 0 else p1_cards
        t0 = time.time()
        results = HoldemEquityCalculator.calculate([my_cards, None], 
                                                   board_cards=board_cards, 
                                                   exact=self._num_simulations == -1, 
                                                   num_simulations=self._num_simulations)
        t1 = time.time()
        
        print(f"{self._num_simulations} 次模拟实验的耗时是 {t1 - t0} s")
        equity = results[0]["win_rate"] + results[0]["tie_rate"]
                                   
        # 2. 解析动作含义
        action_map = self._parse_actions(state, legal_actions)
       
        # 3. 根据胜率和阈值决定策略
        chosen_action = self._decide_action(equity, action_map, legal_actions)
        
        return chosen_action
    
    def _parse_actions(self, state, legal_actions):
        """将动作 ID 映射为字符串类型"""
        action_map = {}
        for action in legal_actions:
            action_str = state.action_to_string(self._player_id, action).lower()
            
            match = False
            for key in ["fold", "call", "allin", "bet", "raise"]:  # "check", 
                if key in action_str:
                    if key == "call":  # call 0 映射为 check
                        player_id = state.current_player()
                        current_spent = parse_spent_from_str(str(state))

                        cloned_state = state.clone()
                        cloned_state.apply_action(action)
                        new_spent = parse_spent_from_str(str(cloned_state))

                        cost = new_spent[player_id] - current_spent[player_id]

                        if cost == 0:
                            key = "check"
                    action_map[key] = action
                    match = True
                    break

            if not match:
                import pdb
                pdb.set_trace()
                
        return action_map

    def _decide_action(self, equity, action_map, legal_actions):
        """核心决策逻辑"""

        # --- 牌力极强 (大于allin阈值) ---
        if (equity >= self._all_threshold) and ("allin" in action_map):
            return action_map["allin"]
        
        # --- 牌力较强 (大于raise阈值) ---
        if equity >= self._raise_threshold:  # bet和raise互斥
            if "bet" in action_map:
                return action_map["bet"]
            if "raise" in action_map:
                return action_map["raise"]

        # --- 牌力尚可 (大于跟注阈值) ---
        if (equity >= self._call_threshold) and ("call" in action_map):
            return action_map["call"]

        # --- 牌力较差 (低于跟注阈值) ---
        if "check" in action_map:  # 能 Check 绝不 Fold
            return action_map["check"]
        if "fold" in action_map:  # 每轮都有fold选项
            return action_map["fold"]


class TexasHoldemEnv:
    def __init__(self, lbl, agent_id, bot_style, cards):
        self.initial_stack = 20000
        self.smallblind, self.bigblind = 50, 100
        self.game = pyspiel.universal_poker.load_universal_poker_from_acpc_gamedef(self._get_gamedef())
        self.lbl = lbl

        self.agent_id = agent_id
        self.opponent_id = 1 - agent_id

        self._bot_style_key = bot_style  # 保存原始 key 用于序列化恢复
        self._create_bot(bot_style)

        self.state = self.game.new_initial_state()

        self.cards = cards
        self.game_result = 0.0 
        self.last_opponent_actions = []
        self.init_actions = self._fast_forward()

    def _get_gamedef(self):
        """返回 ACPC 游戏定义字符串，供 __init__ 和 __setstate__ 共用"""
        return f"""
GAMEDEF
nolimit
numPlayers = 2
numRounds = 4
blind = {self.smallblind} {self.bigblind}
stack = {self.initial_stack} {self.initial_stack}
numBoardCards = 0 3 1 1
numHoleCards = 2
numSuits = 4
numRanks = 13
firstPlayer = 1 2 2 2
END GAMEDEF
"""

    def _create_bot(self, bot_style):
        """根据 bot_style key 创建对应的 bot 实例"""
        if bot_style == "new":
            self.bot = SimpleRandomBot(player_id=self.opponent_id)
            self.bot_style = "【新手】：出牌完全随机，毫无逻辑。"
        elif bot_style == "mad":
            self.bot = EquityBot(
                                player_id=self.opponent_id,
                                call_threshold=0.15, 
                                raise_threshold=0.35,
                                all_threshold=0.60,
                                num_simulations=num_simulations  # 只模拟1000次来计算大致胜率
                            )
            self.bot_style = "【疯鱼】：极度激进，只要有机会就会下注或加注，绝不轻易弃牌！"
        elif bot_style == "cons":
            self.bot = EquityBot(
                                player_id=self.opponent_id,
                                call_threshold=0.45,
                                raise_threshold=0.75,
                                all_threshold=0.90,
                                num_simulations=num_simulations  # 只模拟1000次来计算大致胜率
                            )
            self.bot_style = "【保守】：谨小慎微，只玩大牌。如果他跟注了，手里一定有好牌。"
        elif bot_style == "shark":
            self.bot = mcts.MCTSBot(self.game, uct_c=2, max_simulations=num_simulations, evaluator=mcts.RandomRolloutEvaluator())
            self.bot_style = "【鲨鱼】：计算精准，深思熟虑，是极难对付的顶尖高手。"
        else:
            import pdb
            pdb.set_trace()

    def __getstate__(self):
        """pickle 序列化：将不可序列化的 pyspiel 对象替换为动作历史"""
        d = self.__dict__.copy()
        d['_action_history'] = self.state.history()
        del d['state']
        del d['game']
        del d['bot']
        return d

    def __setstate__(self, d):
        """pickle 反序列化：从动作历史重建 pyspiel 游戏状态，并重建 bot"""
        action_history = d.pop('_action_history')
        self.__dict__.update(d)
        # 重建 game
        self.game = pyspiel.universal_poker.load_universal_poker_from_acpc_gamedef(self._get_gamedef())
        # 通过重放动作历史恢复 state
        self.state = self.game.new_initial_state()
        for action in action_history:
            self.state.apply_action(action)
        # 重建 bot
        self._create_bot(self._bot_style_key)

    def _clean_openspiel_action(self, raw_action: str) -> str:
        return re.sub(r'player=\d+\s+move=', '', raw_action)
    
    # def _get_legal_action_strs(self):
    #     raw_actions = [self.state.action_to_string(self.agent_id, a) for a in self.state.legal_actions()]
    #     return [self._clean_openspiel_action(a) for a in raw_actions]
    
    def _parse_action(self, action_str, legal_actions):
        target_str = action_str.lower()
        
        action_map = {}
        for a in legal_actions:
            raw_name = self.state.action_to_string(self.agent_id, a)
            clean_name = self._clean_openspiel_action(raw_name)
            action_map[clean_name.lower()] = a
            
        if target_str in action_map: 
            return action_map[target_str]
        else:
            return None
        
    def _handle_terminal(self, context_msg):
        self.game_result = self.state.returns()[self.agent_id]
        if self.game_result == self.state.returns()[1 - self.agent_id]:
            self.game_result = 0
        return context_msg, True
    
    def _fast_forward(self) -> List[str]:
        logs = []
        while not self.state.is_terminal() and self.state.current_player() != self.agent_id:
            # 系统发牌
            if self.state.is_chance_node():
                # outcomes = self.state.chance_outcomes()
                # action_list, prob_list = zip(*outcomes)
                # action = np.random.choice(action_list, p=prob_list)

                action_str = f"Deal {self.cards.pop(0)}"
                legal_actions = self.state.legal_actions()
                action = self._parse_action(action_str, legal_actions)

                self.state.apply_action(action)
                if not self.state.is_chance_node():  # 前面一张一张发的不显示，只看最后一次发的结果
                    logs.append(
                        draw_action(self.lbl, 
                                self.agent_id, 
                                f"{self.state.move_number() - 1}", 
                                self.get_info(), 
                                action=None, 
                                is_hero=False, 
                                show_button=self.state.current_player() == self.agent_id,
                                game_info="Initial Deck" if self.state.move_number() == 4 else "Flop round")  # 发牌结果
                    )
            # 玩家决策
            else:
                curr_player = self.state.current_player()

                action = self.bot.step(self.state)

                # 获取动作名称
                raw_action_name = self.state.action_to_string(curr_player, action)
                action_name = self._clean_openspiel_action(raw_action_name)

                # 动作前，记录对手已投入金额
                spent_before = parse_spent_from_str(str(self.state))[self.opponent_id]
                move_before = self.state.move_number()
                info_before = self.get_info()
                
                # 执行动作（状态更新）
                self.state.apply_action(action)

                # 动作后，再次获取对手已投入金额
                spent_after = parse_spent_from_str(str(self.state))[self.opponent_id]
                
                # 计算本次动作的实际花费
                cost = spent_after - spent_before

                if action_name == "Call" and cost == 0:
                    action_name = "Check"
                elif cost > 0:
                    action_name = f"{action_name} {cost}"

                logs.append(
                        draw_action(self.lbl, 
                                    self.agent_id, 
                                    f"{move_before}-0", 
                                    info_before, 
                                    action=action_name, 
                                    is_hero=False, 
                                    show_button=False,
                                    game_info="Opp's Turn")  # 对手动作
                )
                if not self.state.is_chance_node() and not self.state.is_terminal():
                    logs.append(
                            draw_action(self.lbl, 
                                        self.agent_id, 
                                        f"{move_before}-1", 
                                        self.get_info(), 
                                        action=None, 
                                        is_hero=False, 
                                        show_button=True,
                                        game_info="Stack Change")  # 对手结果
                    )
        
        self.last_opponent_actions = logs 
        return logs

    def step(self, action_str: str) -> Tuple[str, bool]:
        legal_actions = self.state.legal_actions() 

        action_id = self._parse_action("Call" if action_str=="Check" else action_str, legal_actions)
        
        if action_id is None:
            legal_strs = [action.split(" ")[0] for action in self.get_detailed_legal_actions()]
            raise ValueError(f"非法动作 '{action_str}'。请从以下动作中选择: {legal_strs}")

        # 结合cost信息
        for action in self.get_detailed_legal_actions():
            if action.split(" ")[0] == action_str:
                action_str = action

        # 1. 记录玩家自己的动作
        action_summary = [
                    draw_action(self.lbl, 
                                self.agent_id, 
                                f"{self.state.move_number()}-0", 
                                self.get_info(), 
                                action=action_str, 
                                is_hero=True, 
                                show_button=False,
                                game_info="Your Turn")  # 动作
        ]
        self.state.apply_action(action_id)
        if not self.state.is_chance_node() and not self.state.is_terminal() and action_str != "Check":
            action_summary.append(
                            draw_action(self.lbl, 
                                        self.agent_id, 
                                        f"{self.state.move_number() - 1}-1", 
                                        self.get_info(), 
                                        action=None, 
                                        is_hero=True, 
                                        show_button=False,
                                        game_info="Stack Change")  # 结果
            )
        
        if self.state.is_terminal():
            return self._handle_terminal(action_summary)

        # 2. 快进对手和发牌阶段
        opponent_logs = self._fast_forward()
        action_summary.extend(opponent_logs)

        if self.state.is_terminal():
            return self._handle_terminal(action_summary)
        else:
            return action_summary, False

    def get_detailed_legal_actions(self) -> List[str]:
        legal_actions = self.state.legal_actions()
        current_state_str = str(self.state)
        current_spent = parse_spent_from_str(current_state_str)
        my_current_spent = current_spent[self.agent_id]
        
        detailed_actions = []
        
        for action in legal_actions:
            # 这里获取原始名称用于判断类型，因为 "fold", "call" 等关键字是不变的
            raw_action_name = self.state.action_to_string(self.agent_id, action)
            
            cloned_state = self.state.clone()
            cloned_state.apply_action(action)
            new_spent = parse_spent_from_str(str(cloned_state))
            
            my_new_spent = new_spent[self.agent_id]
            cost = my_new_spent - my_current_spent

            # 格式化输出
            if "fold" in raw_action_name.lower():
                detailed_actions.append(f"{self._clean_openspiel_action(raw_action_name)}")
            elif "call" in raw_action_name.lower():
                if cost == 0:
                    detailed_actions.append("Check")
                else:
                    detailed_actions.append(f"{self._clean_openspiel_action(raw_action_name)} {cost}")
            elif "raise" in raw_action_name.lower():
                detailed_actions.append(f"{self._clean_openspiel_action(raw_action_name)} {cost}")
            elif "all" in raw_action_name.lower():
                detailed_actions.append(f"{self._clean_openspiel_action(raw_action_name)} {cost}")
            elif "bet" in raw_action_name.lower():
                detailed_actions.append(f"{self._clean_openspiel_action(raw_action_name)} {cost}")
            else:
                import pdb
                pdb.set_trace()
                
        return detailed_actions
    
    def _calculate_gamestate_info(self):
        spent = parse_spent_from_str(str(self.state))

        current_pot = spent[0] + spent[1]
        my_stack = self.initial_stack - spent[self.agent_id]
        opp_stack = self.initial_stack - spent[1 - self.agent_id]
        
        diff = spent[1 - self.agent_id] - spent[self.agent_id]
        to_call = max(0, diff)
        
        return {
            "pot": current_pot,
            "my_stack": my_stack,
            "opp_stack": opp_stack,
            "to_call": to_call,
            "debug_spent": spent
        }

    def get_info(self):
        # if self.state.is_terminal():
        #     return {"status": "Game Over", "result": self.game_result}
        
        p0_cards, p1_cards, board_cards = get_perfect_information(self.state)
        my_cards = p0_cards if self.agent_id == 0 else p1_cards
        
        display_board = ["Unknown"] * 5
        for i in range(min(len(board_cards), 5)):
            display_board[i] = board_cards[i]

        info = {
            "detailed_actions": [] if self.state.is_chance_node() else self.get_detailed_legal_actions(),
            "my_cards": my_cards if my_cards else "Unknown",
            "public_cards": display_board,
            "raw_state": str(self.state)
        }
        info["legal_actions"] = [action.split(" ")[0] for action in info["detailed_actions"]]
        
        info.update(self._calculate_gamestate_info())
        return info


class GameRegistry:
    """基于 Redis 的游戏注册表，支持多进程并发访问"""
    _instance = None

    TIMEOUT_SECONDS = 30 * 60
    KEY_PREFIX = "poker:game:"
    LOCK_PREFIX = "poker:lock:"

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._redis = redis.Redis(host=os.environ.get('REDIS_HOST'), port=6379, db=0, password='bc')

    def register(self, env: TexasHoldemEnv, lbl: str):
        """注册新游戏，利用 Redis TTL 自动过期"""
        key = self.KEY_PREFIX + lbl
        self._redis.set(key, pickle.dumps(env), ex=self.TIMEOUT_SECONDS)

    def get(self, lbl: str) -> Optional[TexasHoldemEnv]:
        """从 Redis 反序列化获取游戏实例"""
        key = self.KEY_PREFIX + lbl
        data = self._redis.get(key)
        if data is None:
            return None
        return pickle.loads(data)

    def save(self, lbl: str, env: TexasHoldemEnv):
        """将修改后的游戏状态保存回 Redis，保留剩余 TTL"""
        key = self.KEY_PREFIX + lbl
        ttl = self._redis.ttl(key)
        if ttl and ttl > 0:
            self._redis.set(key, pickle.dumps(env), ex=ttl)
        else:
            self._redis.set(key, pickle.dumps(env), ex=self.TIMEOUT_SECONDS)

    def get_game_lock(self, lbl: str):
        """返回 Redis 分布式锁（替代 threading.Lock，支持多进程）"""
        lock_key = self.LOCK_PREFIX + lbl
        return self._redis.lock(lock_key, timeout=300, blocking_timeout=120)

    def exists(self, lbl: str) -> bool:
        key = self.KEY_PREFIX + lbl
        return bool(self._redis.exists(key))

    def remove(self, lbl: str):
        key = self.KEY_PREFIX + lbl
        self._redis.delete(key)
        shutil.rmtree(os.path.join(PATH, "images", lbl), ignore_errors=True)

    def list_all(self) -> List[str]:
        pattern = self.KEY_PREFIX + "*"
        keys = self._redis.keys(pattern)
        prefix_len = len(self.KEY_PREFIX)
        return [k.decode()[prefix_len:] for k in keys]


app = Flask(__name__)

registry = GameRegistry.get_instance()


@app.route('/create_game', methods=['POST'])
def create_game():
    agent_id = int(random.random() > 0.5)

    rand = random.random()
    if rand < 0.25:
        bot_style = "new"
    elif rand < 0.50:
        bot_style = "mad"
    elif rand < 0.75:
        bot_style = "cons"
    else:
        bot_style = "shark"

    deck = list(range(52))
    random.shuffle(deck)
    selected_cards_ids = deck[:9]
    cards = []
    for card_id in selected_cards_ids: 
        ranks = "23456789TJQKA"
        suits = "shdc"  # Spades, Hearts, Diamonds, Clubs
        suit_idx = card_id // 13
        rank_idx = card_id % 13
        cards.append(f"{ranks[rank_idx]}{suits[suit_idx]}")

    # 去重
    game_id = str(uuid.uuid4())
    while os.path.exists(f"{PATH}/libraries/{game_id}.json"):
        game_id = str(uuid.uuid4())

    with open(f"{PATH}/libraries/{game_id}.json", 'w', encoding='utf-8') as f:
        json.dump(
            {
                "agent_id": agent_id,
                "bot_style": bot_style,
                "cards": cards}, 
            f, 
            ensure_ascii=False, 
            indent=2)

    return jsonify({
        "game_id": game_id,
        "agent_id": agent_id,
        "bot_style": bot_style
    })


@app.route('/createGameSession', methods=['POST'])
def createGameSession():
    data = request.get_json()
    game_id = data["game_id"]

    filepath = f"{PATH}/libraries/{game_id}.json"

    if not os.path.exists(filepath):
        return jsonify({
            "success": False, 
            "init_actions": None,
            "info": f"库中未记录 game_id={game_id} 的游戏设置，请检查是否输入有误"})
    with open(filepath, 'r', encoding='utf-8') as f:
        content = json.load(f)

    number = random.randint(0, 999999)
    pin = str(number).zfill(6)
   
    game = TexasHoldemEnv(game_id, content["agent_id"], content["bot_style"], [card for card in content["cards"]])
    registry.register(game, f"{game_id}-{pin}")
    init_actions = game.init_actions

    if game.state.is_terminal():
        score = game.game_result
        if score > 0:
            result = "你赢了"
        elif score == 0:
            result = "平局"
        else:
            result = "你输了"
        extra = f"游戏结束。{result}！请按规定格式返回你的pin。"
    else:
        extra = ""

    return jsonify({
            "success": True,
            "init_actions": init_actions,
            "info": f"游戏(game_id={game_id})初始化成功，通行证 pin={pin}。{extra}"})


@app.route('/applyAction', methods=['POST'])
def applyAction():
    data = request.get_json()
    action, game_id, pin = data["action"], data["game_id"], data["pin"]
    lbl = f"{game_id}-{pin}"

    game_lock = registry.get_game_lock(lbl)

    with game_lock:  # Redis 分布式锁，同一局游戏跨进程串行执行
        game = registry.get(lbl)
        if game is None:
            return jsonify({"message": "game_id或pin输入有误", "obs": []})

        try:
            obs, _ = game.step(action)
        except Exception as e:
            return jsonify({"message": str(e), "obs": []})

        if game.state.is_terminal():
            score = game.game_result
            if score > 0:
                result = "你赢了"
            elif score == 0:
                result = "平局"
            else:
                result = "你输了"
            feedback = f"游戏结束。{result}！请按规定格式返回你的pin。"
            obs = []
        else:
            feedback = "你的选择已经生效，牌局已进入新阶段。请根据最新的对局图片，分析当前局面并做出你的下一步选择。"

        # 将修改后的游戏状态写回 Redis
        registry.save(lbl, game)

    return jsonify({"message": feedback, "obs": obs})


@app.route('/ScoreBoard', methods=['POST'])
def ScoreBoard():
    data = request.get_json()
    game_id, pin = data["game_id"], data["pin"]
    lbl = f"{game_id}-{pin}"

    game_lock = registry.get_game_lock(lbl)

    with game_lock:
        game = registry.get(lbl)
        if game is None:
            return jsonify({"success": False, "my_score": None, "opp_score": None,
                            "actual_return": None, "initial_stack": None})

        if not game.state.is_terminal():
            return jsonify({"success": False, "my_score": None, "opp_score": None,
                            "actual_return": None, "initial_stack": None})

        p0_cards, p1_cards, board_cards = get_perfect_information(game.state)
        if game.agent_id == 0:
            my_cards, opp_cards = p0_cards, p1_cards
        else:
            my_cards, opp_cards = p1_cards, p0_cards

        results = HoldemEquityCalculator.calculate(
            [my_cards, opp_cards], board_cards=board_cards,
            exact=False, num_simulations=num_simulations)

        return jsonify({
            "success": True,
            "my_score": results[0]["win_rate"],
            "opp_score": results[1]["win_rate"],
            "actual_return": game.game_result,
            "initial_stack": game.initial_stack
        })


@app.route('/remove_game', methods=['POST'])
def remove_game():
    data = request.get_json()
    game_id, pin = data["game_id"], data["pin"]
    lbl = f"{game_id}-{pin}"
    if registry.exists(lbl):
        registry.remove(lbl)
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})
  

from internbootcamp.utils.tool_server.utils import find_available_port
from gunicorn.app.base import BaseApplication
import multiprocessing


class StandaloneApplication(BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        for key, value in self.options.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


if __name__ == "__main__":
    # 获取 port
    port = find_available_port("0.0.0.0", 49152)

    # 获取 ip
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()

    # 保存 ip
    with open("ip.py", "w", encoding="utf-8") as f:
        f.write(f'ips = ["http://{ip}:{port}"]\n')

    # app.run(debug=False, host="0.0.0.0", port=port)
    options = {
        "bind": f"0.0.0.0:{port}",
        "workers": multiprocessing.cpu_count() + 1,  # 已改为多进程，由 Redis 保证状态一致性
        "threads": 32,               # 每个 worker 内的线程数
        "worker_class": "gthread",  # 多线程模式需要指定
    }
    StandaloneApplication(app, options).run()
    