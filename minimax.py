# -*- coding: utf-8 -*-
# @Time    : 2025/2/12 17:05:26
# @Author  : 墨烟行(GitHub UserName: CloudSwordSage)
# @File    : minimax.py
# @Desc    : Minimax 算法的核心实现


import copy
import numpy as np
from multiprocessing import Pool, cpu_count
from typing import List, Tuple

from game import Game

KILLER_MOVES = 5

class MiniMax:
    def __init__(self, max_depth=3):
        self.max_depth = max_depth

    def search(self, game: 'Game') -> Tuple[int, int]:
        """主入口，返回最优的（x, y）位置"""
        best_move = None
        best_move = self._minimax(copy.deepcopy(game), self.max_depth, True, -np.inf, np.inf)
        
        return best_move['move']

    def _minimax(self, game: 'Game', depth: int, is_maximizing: bool, alpha: int, beta: int) -> Tuple[Tuple[int, int], int]:
        """递归搜索，加入 Alpha-Beta 剪枝"""

        game_over, winner = game.game_end()
        if game_over:
            if winner == -1:
                return {'score': 0}
            elif winner == game.current_player:
                return {'score': 100000}
            else:
                return {'score': -100000}

        if depth == 0:
            return {'score': game.evaluate}
    
        availables = game.availables

        best_move = None
        if is_maximizing:
            best_move = {'score': -np.inf}
            for next_move in availables:
                game.move(*next_move)
                score = self._minimax(game, depth - 1, False, alpha, beta)
                score['move'] = next_move
                game.undo_move()
                if score['score'] > best_move['score']:
                    best_move['score'] = score['score']
                    best_move['move'] = score['move']
                if best_move['score'] >= beta:
                    break
                alpha = max(alpha, best_move['score'])
        else:
            best_move = {'score': np.inf}
            for next_move in availables:
                game.move(*next_move)
                score = self._minimax(game, depth-1, True, alpha, beta)
                score['move'] = next_move
                game.undo_move()
                if score['score'] < best_move['score']:
                    best_move['score'] = score['score']
                    best_move['move'] = score['move']
                if best_move['score'] <= alpha:
                    break
                beta = min(beta, best_move['score'])
        return best_move


if __name__ == '__main__':
    game = Game()
    game.move(7, 7)
    print(game.last_move)
    ai = MiniMax(n_jobs=-1, max_depth=2)
    best_move, best_score = ai.search(game)
    print(best_move, best_score)