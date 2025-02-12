# -*- coding: utf-8 -*-
# @Time    : 2025/2/11 13:01:02
# @Author  : 墨烟行(GitHub UserName: CloudSwordSage)
# @File    : game.py
# @Desc    : 游戏对象


import numpy as np
from dataclasses import dataclass
from collections import deque

@dataclass
class GameConfig:
    size: int = 15
    radius: int = 3

class Game:
    def __init__(self, config = GameConfig()):
        self.config = config
        self.init_board()
    
    def init_board(self):
        self.board = np.zeros((self.config.size, self.config.size))
        self.current_player = 1
        self.winner = 0
        self.is_over = False
        self.last_move = []
    
    def move(self, x: int, y: int):
        if self.is_over:
            return

        if self.board[x, y] != 0:
            return

        self.board[x, y] = self.current_player
        self.last_move.append((x, y))

        if self.check_win():
            self.winner = self.current_player
            self.is_over = True
            return

        if 0 not in self.board.flatten():
            self.winner = -1
            self.is_over = True
            return

        self.current_player = 2 if self.current_player == 1 else 1
        return
    
    def undo_move(self):
        """撤销一步"""
        if self.last_move == []:
            return
        self.board[self.last_move[-1][0], self.last_move[-1][1]] = 0
        self.last_move.pop()
        self.current_player = 3 - self.current_player
    
    def get_patterns(self, player):
        """返回当前玩家所有模式及其出现次数"""
        patterns = {
            '五连': 0,
            '活四': 0,
            '冲四': 0,
            '活三': 0,
            '冲三': 0,
            '活二': 0,
            '冲二': 0
        }

        directions = [(1,0), (0,1), (1,1), (1,-1)]

        for i in range(self.config.size):
            for j in range(self.config.size):
                if self.board[i, j] != player:
                    continue

                for dx, dy in directions:
                    if self._is_new_direction(i, j, dx, dy):
                        line = self._get_line(i, j, dx, dy, 6)
                        if pattern := self._analyze_line(line, player):
                            patterns[pattern] += 1

        return patterns

    def _is_new_direction(self, x, y, dx, dy):
        """检查是否新的方向起点"""
        nx, ny = x - dx, y - dy
        return not (0 <= nx < self.config.size and 0 <= ny < self.config.size and self.board[nx, ny] == self.board[x, y])

    def _get_line(self, x, y, dx, dy, length):
        """获取指定方向的棋子序列"""
        line = []
        for i in range(length):
            nx = x + dx * i
            ny = y + dy * i
            if 0 <= nx < self.config.size and 0 <= ny < self.config.size:
                line.append(self.board[nx, ny])
            else:
                line.append(-1)  # 边界外标记
        return line

    def _analyze_line(self, line, player):
        """分析单行模式"""
        line_str = ''.join(['1' if p == player else '0' if p == 0 else '2' for p in line])

        if '11111' in line_str:
            return '五连'

        if '011110' in line_str:
            return '活四'

        if '011112' in line_str or '211110' in line_str:
            return '冲四'

        if '01110' in line_str:
            return '活三'

        if '01112' in line_str or '21110' in line_str:
            return '冲三'

        if '0110' in line_str:
            return '活二'
        return '冲二' if '0112' in line_str or '2110' in line_str else None

    def check_win(self):
        x, y = self.last_move[-1]
        player = self.current_player
        for dx, dy in [(1, 0), (0, 1), (1, 1), (1, -1)]:
            count = 1
            for i in range(1, 5):
                nx, ny = x + dx * i, y + dy * i
                if 0 <= nx < self.config.size and 0 <= ny < self.config.size and self.board[nx, ny] == player:
                    count += 1
                else:
                    break
                if count == 5:
                    return True
            for i in range(1, 5):
                nx, ny = x - dx * i, y - dy * i
                if 0 <= nx < self.config.size and 0 <= ny < self.config.size and self.board[nx, ny] == player:
                    count += 1
                else:
                    break
                if count == 5:
                    return True
        return False
    
    @property
    def evaluate(self):
        """
        评估当前玩家的当前棋盘得分.
        """
        player = self.current_player
        opponent = 3 - player

        player_patterns = self.get_patterns(player)
        opponent_patterns = self.get_patterns(opponent)

        score = 0

        # 根据模式分配分数
        score += player_patterns['五连'] * 100000
        score += player_patterns['活四'] * 10000
        score += player_patterns['冲四'] * 5000
        score += player_patterns['活三'] * 1000
        score += player_patterns['冲三'] * 500
        score += player_patterns['活二'] * 100
        score += player_patterns['冲二'] * 50

        score -= opponent_patterns['五连'] * 100000
        score -= opponent_patterns['活四'] * 10000
        score -= opponent_patterns['冲四'] * 5000
        score -= opponent_patterns['活三'] * 1000
        score -= opponent_patterns['冲三'] * 500
        score -= opponent_patterns['活二'] * 100
        score -= opponent_patterns['冲二'] * 50

        return score
    
    @property
    def availables(self):
        if self.last_move == []:
            return [(i, j) for i in range(self.config.size) for j in range(self.config.size) if self.board[i, j] == 0]
            
        x, y = self.last_move[-1]
        # 搜索范围限制
        min_x = max(0, x - self.config.radius)
        max_x = min(self.config.size - 1, x + self.config.radius)
        min_y = max(0, y - self.config.radius)
        max_y = min(self.config.size - 1, y + self.config.radius)
        
        return [(i, j) for i in range(min_x, max_x + 1)
                for j in range(min_y, max_y + 1)
                if self.board[i, j] == 0]

    def game_end(self):
        done = self.is_over
        return (True, self.winner) if done else (False, None)
    
    @property
    def get_current_player(self):
        return self.current_player
    def reset(self):
        self.init_board()
