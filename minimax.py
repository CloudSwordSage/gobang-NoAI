# -*- coding: utf-8 -*-
# @Time    : 2025/2/12 17:05:26
# @Author  : 墨烟行(GitHub UserName: CloudSwordSage)
# @File    : minimax.py
# @Desc    : 


import copy
import numpy as np
from multiprocessing import Pool, cpu_count
from typing import List, Tuple

from game import Game

KILLER_MOVES = 5

class MiniMax:
    def __init__(self, max_depth=7, n_jobs=1):
        self.max_depth = max_depth
        cpu_num = cpu_count()
        if n_jobs > cpu_num:
            raise ValueError('n_jobs must be less than or equal to the number of CPUs')
        self.n_jobs = cpu_num if n_jobs == -1 else n_jobs

    def search(self, game: 'Game') -> Tuple[int, int]:
        """主入口，返回最优的（x, y）位置"""
        best_move = None
        best_score = -np.inf

        availables = game.availables
        with Pool(self.n_jobs) as pool:
            results = pool.starmap(self._minimax, [(copy.deepcopy(game), move, self.max_depth, True, -np.inf, np.inf) for move in availables])
        for move, score in results:
            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    def _minimax(self, game: 'Game', move: Tuple[int, int], depth: int, is_maximizing: bool, alpha: int, beta: int) -> Tuple[Tuple[int, int], int]:
        """递归搜索，加入 Alpha-Beta 剪枝"""
        game.move(*move)

        game_over, winner = game.game_end()
        if game_over:
            if winner == -1:
                return move, 0
            elif winner == game.current_player:
                return move, 100000
            else:
                return move, -100000

        if depth == 0:
            return move, game.evaluate
    
        availables = game.availables

        best_move = None
        if is_maximizing:
            best_score = -np.inf
            for next_move in availables:
                _, score = self._minimax(game, next_move, depth - 1, False, alpha, beta)
                if score > best_score:
                    best_score = score
                    best_move = next_move
                if best_score >= beta:
                    break
                alpha = max(alpha, best_score)
        else:
            best_score = np.inf
            for next_move in availables:
                _, score = self._minimax(game, next_move, depth-1, True, alpha, beta)
                if score < best_score:
                    best_score = score
                    best_move = next_move
                if best_score <= alpha:
                    break
                beta = min(beta, best_score)

        game.undo_move()
        return best_move, best_score


if __name__ == '__main__':
    game = Game()
    game.move(7, 7)
    print(game.availables)
    print(game.last_move)
    ai = MiniMax(n_jobs=-1)
    best_move, best_score = ai.search(game)
    print(best_move, best_score)