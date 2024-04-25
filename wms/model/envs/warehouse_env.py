import gym
import numpy as np
from gym import spaces


class WarehouseEnv(gym.Env):
    def __init__(self, width, height, cell_size):
        super().__init__()
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.action_space = spaces.Discrete(width * height)
        self.observation_space = spaces.Box(low=0, high=cell_size,
                                            shape=(height, width), dtype=np.int32)
        self.state = np.full((height, width),fill_value=cell_size, dtype=np.int32)

    def reset(self):
        self.state = np.full((self.height, self.width),fill_value=self.cell_size, dtype=np.int32)
        return self.state.flatten()

    def step(self, action, item_size):
        row, col = divmod(action, self.width)
        reward = 0
        done = False
        if self.state[row, col] >= item_size:
            self.state[row, col] -= item_size
            reward = self.calculate_reward(row, col, item_size)
        else:
            reward = -10
            done = True

        if np.all(self.state == 0):
            done = True

        return self.state.flatten(), reward, done
    
    def calculate_reward(self, row, col, item_size):
        remaining_area_after_placement = self.state[row, col] - item_size

        if remaining_area_after_placement == 0:
            # Maximum reward for using the cell optimally
            return 10
        elif remaining_area_after_placement < 0:
            # Lower reward for using the cell, but not optimally
            return 1
        else:
            # Negative reward for overfilling the space
            return -10

    def render(self, mode='human'):
        for row in self.state:
            print(' '.join(['X' if cell == 1 else '.' for cell in row]))
        print()
