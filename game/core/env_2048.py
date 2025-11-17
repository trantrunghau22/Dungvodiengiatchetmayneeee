import numpy as np
import random

#Di chuyển của user
UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3

class Game2048Env:
    def __init__(self, size=4, seed=None):
        self.size = size
        self.board = np.zeros((size, size), dtype=int)
        self.score = 0

        if seed is not None:
            np.random.seed(seed)
            random.seed(seed)

    def reset(self):
        self.board = np.zeros((self.size, self.size), dtype=int)
        self.score = 0
        self._spawn_tile()
        self._spawn_tile()
        return self.get_state()

    def get_state(self):
        return self.board.copy()

    def _spawn_tile(self):
        empty = list(zip(*np.where(self.board == 0)))
        if not empty:
            return False
        r, c = random.choice(empty)
        self.board[r, c] = 4 if random.random() < 0.1 else 2
        return True

    def is_done(self):
        if (self.board == 0).any():
            return False
        for r in range(self.size):
            for c in range(self.size - 1):
                if self.board[r, c] == self.board[r, c + 1]:
                    return False
        for r in range(self.size - 1):
            for c in range(self.size):
                if self.board[r, c] == self.board[r + 1, c]:
                    return False
        return True

    def step(self, action):
        prev = self.get_state()
        prev_score = self.score

        if action == LEFT:
            self._move_left()
        elif action == RIGHT:
            self._move_right()
        elif action == UP:
            self._move_up()
        elif action == DOWN:
            self._move_down()

        moved = not np.array_equal(prev, self.board)
        reward = self.score - prev_score

        if moved:
            self._spawn_tile()

        done = self.is_done()
        info = {"moved": moved}
        return self.get_state(), reward, done, info

    #core logic của game
    def _compress(self, row):
        new = row[row != 0]
        zeros = np.zeros(self.size - len(new), dtype=int)
        return np.concatenate([new, zeros])

    def _merge(self, row):
        gained = 0
        for i in range(self.size - 1):
            if row[i] != 0 and row[i] == row[i + 1]:
                row[i] *= 2
                gained += row[i]
                row[i + 1] = 0
        self.score += gained
        return row

    def _move_left(self):
        for r in range(self.size):
            row = self.board[r]
            row = self._compress(row)
            row = self._merge(row)
            row = self._compress(row)
            self.board[r] = row

    def _move_right(self):
        self.board = np.fliplr(self.board)
        self._move_left()
        self.board = np.fliplr(self.board)

    def _move_up(self):
        self.board = self.board.T
        self._move_left()
        self.board = self.board.T

    def _move_down(self):
        self.board = self.board.T
        self._move_right()
        self.board = self.board.T