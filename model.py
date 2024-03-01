import gym
import numpy as np
import tensorflow as tf
from gym import spaces
from tf_agents.agents.dqn import dqn_agent
from tf_agents.drivers import dynamic_step_driver
from tf_agents.environments import gym_wrapper, tf_py_environment, wrappers
from tf_agents.eval import metric_utils
from tf_agents.metrics import tf_metrics
from tf_agents.networks import q_network
from tf_agents.policies import random_tf_policy
from tf_agents.replay_buffers import tf_uniform_replay_buffer
from tf_agents.trajectories import trajectory
from tf_agents.utils import common
import tf_agents


class WarehouseEnv(gym.Env):
    def __init__(self, width, height, cell_size, item_sizes_queue):
        super().__init__()
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.action_space = spaces.Discrete(width * height)
        self.observation_space = spaces.Box(low=0, high=cell_size,
                                            shape=(height, width), dtype=np.int32)
        self.item_sizes_queue = list(item_sizes_queue)
        self.initial_queue = list(item_sizes_queue)
        self.placement_record = []
        self.state = np.full((height, width),fill_value=cell_size, dtype=np.int32)

    def reset(self):
        self.state = np.full((self.height, self.width),fill_value=self.cell_size, dtype=np.int32)
        self.item_sizes_queue = list(self.initial_queue)
        self.placement_record = []
        return self.state

    def step(self, action):
        if not self.item_sizes_queue:
            return self.state, 0, True, {}
        
        item_size = self.item_sizes_queue[0]
        self.item_sizes_queue.pop(0)
        row, col = divmod(action, self.width)
        reward = 0
        done = False

        if self.state[row, col] >= item_size:
            self.state[row, col] -= item_size
            self.placement_record.append((row, col, item_size))
            reward = 10 - (self.cell_size - self.state[row, col])
            max_reward = 10
            reward = reward / max_reward
        else:
            reward = -10
            done = True

        if not self.item_sizes_queue:  # Check if all items have been placed
            done = True
            reward += 50 # Bonus for placing all the items

        info = {}

        return self.state, reward, done, info

    def render(self, mode='human'):
        for row in self.state:
            print(' '.join(['X' if cell == 1 else '.' for cell in row]))
        print()

    def display_grid(self):
        print("\nWarehouse Grid State (Total Item Sizes Added in Each Cell):")
        max_capacity = self.cell_size
        for row in self.state:
            print(' '.join([str(max_capacity - cell) for cell in row]))

epsilon_start = 1.0
epsilon_end = 0.01
epsilon_decay_steps = 10000

class EpsilonGreedyPolicy(object):
    def __init__(self, epsilon_start, epsilon_end, epsilon_decay_steps, action_spec):
        self.epsilon = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay_steps = epsilon_decay_steps
        self.decay_rate = (epsilon_start - epsilon_end) / epsilon_decay_steps
        self.action_spec = action_spec

    def action(self, time_step, policy):
        if np.random.rand() < self.epsilon:
            action = np.random.randint(self.action_spec.minimum, self.action_spec.maximum + 1)
        else:
            action_step = policy.action(time_step)
            action = action_step.action.numpy()
        self.epsilon = max(self.epsilon_end, self.epsilon - self.decay_rate)
        return action

item_sizes_queue = np.random.randint(1, 4, size=100).tolist()
# Convert the gym environment to a TF-Agents environment
gym_env = WarehouseEnv(width=5, height=5, cell_size=5, item_sizes_queue=item_sizes_queue)
wrapped_env = gym_wrapper.GymWrapper(gym_env)
env = tf_py_environment.TFPyEnvironment(wrapped_env)

# Create the Q-Network
fc_layer_params = (100,)
q_net = q_network.QNetwork(
    env.observation_spec(),
    env.action_spec(),
    fc_layer_params=fc_layer_params)

optimizer = tf.compat.v1.train.AdamOptimizer(learning_rate=1e-4)

train_step_counter = tf.Variable(0)

# Setup DQN Agent
agent = dqn_agent.DqnAgent(
    env.time_step_spec(),
    env.action_spec(),
    q_network=q_net,
    optimizer=optimizer,
    td_errors_loss_fn=common.element_wise_squared_loss,
    train_step_counter=train_step_counter)

agent.initialize()

# Replay Buffer
replay_buffer = tf_uniform_replay_buffer.TFUniformReplayBuffer(
    data_spec=agent.collect_data_spec,
    batch_size=env.batch_size,
    max_length=100000)

# Collect Data (Exploration Policy)
epsilon_greedy_policy = EpsilonGreedyPolicy(epsilon_start, epsilon_end, epsilon_decay_steps, env.action_spec())
# random_policy = random_tf_policy.RandomTFPolicy(env.time_step_spec(), env.action_spec())
def collect_step(environment, policy, buffer):
    time_step = environment.current_time_step()
    action = policy.action(time_step, agent.policy)
    next_time_step = environment.step(action)
    action_step = tf_agents.trajectories.PolicyStep(action=tf.convert_to_tensor([action]), state=(), info=())
    traj = trajectory.from_transition(time_step, action_step, next_time_step)
    buffer.add_batch(traj)

def collect_data(env, policy, buffer, steps):
    for _ in range(steps):
        collect_step(env, policy, buffer)

collect_data(env, epsilon_greedy_policy, replay_buffer, steps=100)

# Dataset generates trajectories with shape [Bx2x...]
dataset = replay_buffer.as_dataset(
    num_parallel_calls=3, 
    sample_batch_size=64, 
    num_steps=2).prefetch(3)

iterator = iter(dataset)

# Training the DQN Agent
num_iterations = 10000

for _ in range(num_iterations):
    # Collect a few steps using collect_policy and save to the replay buffer.
    collect_data(env, agent.collect_policy, replay_buffer, steps=1)

    # Sample a batch of data from the buffer and update the agent's network.
    experience, unused_info = next(iterator)
    train_loss = agent.train(experience).loss

    step = agent.train_step_counter.numpy()

    if step % 1000 == 0:
        print('step = {0}: loss = {1}'.format(step, train_loss))

# Evaluate the agent's policy once training is done.
num_episodes = 10
total_reward = 0.0
for _ in range(num_episodes):
    time_step = env.reset()
    episode_reward = 0
    while not time_step.is_last():
        action_step = agent.policy.action(time_step)
        time_step = env.step(action_step.action)
        episode_reward += time_step.reward.numpy()
    total_reward += episode_reward
avg_reward = total_reward / num_episodes
print('Average Reward = {0}'.format(avg_reward))

gym_env.display_grid()