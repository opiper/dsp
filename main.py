from agents.dqn_agent_setup import create_agent
from envs.warehouse_env import WarehouseEnv
from tf_agents.drivers import dynamic_step_driver
from tf_agents.environments import suite_gym, tf_py_environment
from tf_agents.metrics import tf_metrics
from tf_agents.replay_buffers import tf_uniform_replay_buffer
from tf_agents.trajectories import trajectory
from tf_agents.utils import common


def main():
    env = WarehouseEnv()
    train_env = tf_py_environment.TFPyEnvironment(env)
    eval_env = tf_py_environment.TFPyEnvironment(env)

    agent = create_agent(train_env)

    replay_buffer = tf_uniform_replay_buffer.TFUniformReplayBuffer(
        data_spec=agent.collect_data_spec,
        batch_size=train_env.batch_size,
        max_length=100000)

    collect_driver = dynamic_step_driver.DynamicStepDriver(
        train_env,
        agent.collect_policy,
        observers=[replay_buffer.add_batch, tf_metrics.AverageReturnMetric()],
        num_steps=1)  # Collect 1 step for each call to driver.run()

    # Initial data collection
    for _ in range(100):
        collect_driver.run()

    # Training loop
    dataset = replay_buffer.as_dataset(
        num_parallel_calls=3, 
        sample_batch_size=64, 
        num_steps=2).prefetch(3)
    iterator = iter(dataset)

    for _ in range(10000):  # Number of training steps
        experience, unused_info = next(iterator)
        train_loss = agent.train(experience).loss

    print(f'Training loss: {train_loss}')

if __name__ == '__main__':
    main()
