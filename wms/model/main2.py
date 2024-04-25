import gymnasium as gym
from matplotlib import pyplot as plt
import numpy as np
from gymnasium import spaces
from stable_baselines3 import A2C
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.env_util import make_vec_env


class CustomEnv(gym.Env):
    """Custom Environment that follows gym interface."""

    metadata = {"render_modes": ["human"], "render_fps": 30}

    def __init__(self, depth, width, height, cell_size, item_list):
        super().__init__()
        self.depth = depth
        self.width = width
        self.height = height

        self.warehouse = np.zeros((self.height, self.depth, self.width))

        self.cell_value_low = 0
        self.cell_value_high = cell_size
        self.item_size_low = 1
        self.item_size_high = 3

        self.item_list = item_list
        self.original_item_list = item_list

        self.total_cells = self.depth * self.width * self.height
        # Define action and observation space
        # They must be gym.spaces objects
        # Example when using discrete actions:
        self.action_space = spaces.Discrete(self.total_cells)
        # Example for using image as input (channel-first; channel-last also works):
        self.observation_space = spaces.Box(
            low=np.array([self.cell_value_low] * self.total_cells + [self.item_size_low]), 
            high=np.array([self.cell_value_high] * self.total_cells + [self.item_size_high]),
            dtype=np.uint8)
        self.state = None
        self.reset()
        
    def reset(self, seed=None, options=None):
        super().reset(seed=seed, options=options)

        self.state = np.zeros((self.height, self.depth, self.width), dtype=np.uint8)
        self.item_list = self.original_item_list.copy()

        self.observation = np.append(self.state.flatten(), self.item_list[0]).astype(np.uint8)

        return self.observation, {}

    def step(self, action):
        if not self.item_list:
            done = True
            reward = 0
            observation = np.append(self.state.flatten(), 0).astype(np.uint8)
            truncated = False
            info = {}

            return observation, reward, done, truncated, info

        current_item = self.item_list.pop(0)
        if not self.item_list:
            next_item = 0
        else:
            next_item = self.item_list[0]
        reward = 0

        x = (action // self.height) % self.width
        y = action % self.height
        z = action // (self.height * self.width)

        # Check if action is valid
        if self.state[y, z, x] + current_item < self.cell_value_high:
            self.state[y, z, x] += current_item
            reward += 1 / 10
            done = False
        elif self.state[y, z, x] + current_item == self.cell_value_high:
            self.state[y, z, x] += current_item
            reward += 10 / 10
            done = False
        else:
            self.item_list.append(current_item)
            reward += -10 / 10
            done = False

        if np.all(self.state >= self.cell_value_high):
            done = True

        observation = np.append(self.state.flatten(), next_item).astype(np.uint8)
        truncated = False
        info = {}


        return observation, reward, done, truncated, info

    def render(self):
        
        fig = plt.figure(figsize=(10, 7))
        ax = fig.add_subplot(111, projection='3d')
        # Generate coordinates and values for non-empty cells
        x, y, z = self.state.nonzero()
        c = self.state[y, z, x]
        # Plot non-empty cells
        img = ax.scatter(y, z, x, c=c, cmap=plt.hot(), marker='o')
        plt.colorbar(img)
        plt.title("Warehouse State")
        plt.show()

    def close(self):
        plt.close('all')


# Instantiate the env
env = CustomEnv(5,5,3,20,np.random.randint(1, 4, 500).tolist())
check_env(env, warn=True)

# Instantiate the environment
vec_env = make_vec_env(CustomEnv, n_envs=1, env_kwargs=dict(depth=5, width=5, height=3, cell_size=20, item_list=np.random.randint(1, 4, 500).tolist()))

# Define and Train the agent
model = A2C("MlpPolicy", env, verbose=1).learn(5000)

# Test the agent
obs = vec_env.reset()
n_steps = 20
for step in range(n_steps):
    action, _ = model.predict(obs, deterministic=True)
    print(f"Step {step + 1}")
    print("Action: ", action)
    results = vec_env.step(action)
    obs, reward, done, info = results[:4]
    truncated = results[4] if len(results) > 4 else False
    print("Obs: ", obs)
    print("Reward: ", reward)
    print("Done: ", done)
    vec_env.render()
    if done:
        print("Goal reached!", "reward=", reward)
        break 