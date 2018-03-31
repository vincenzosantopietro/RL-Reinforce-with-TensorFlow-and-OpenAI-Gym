from collections import deque

from rl_pg_reinforce import PolicyGradientReinforce
import tensorflow as tf
import numpy as np
import gym

MAX_EPISODES = 10000
MAX_STEPS = 200


def policy_network(states, state_dim, num_actions):
    # define policy neural network - MultiLayerPerceptron (MLP)
    W1 = tf.get_variable("W1", shape=[state_dim, 20],
                         initializer=tf.random_normal_initializer())
    b1 = tf.get_variable("b1", shape=[20],
                         initializer=tf.constant_initializer(0))
    h1 = tf.nn.tanh(tf.matmul(states, W1) + b1)

    W2 = tf.get_variable("W2", [20, num_actions],
                         initializer=tf.random_normal_initializer(stddev=0.1))
    b2 = tf.get_variable("b2", [num_actions],
                         initializer=tf.constant_initializer(0))
    p = tf.matmul(h1, W2) + b2
    return p


def main():
    env_name = 'CartPole-v0'
    env = gym.make(env_name)

    sess = tf.Session()
    optimizer = tf.train.RMSPropOptimizer(learning_rate=0.0005, decay=0.99)
    writer = tf.summary.FileWriter("/tmp/{}-experiment-4".format(env_name))

    state_dim = env.observation_space.shape[0]
    print("State dimensionality: {}".format(state_dim))
    num_actions = env.action_space.n

    pg_reinforce = PolicyGradientReinforce(session=sess,
                                           optimizer=optimizer,
                                           policy_network=policy_network,
                                           state_dim=state_dim,
                                           num_actions=num_actions,
                                           summary_writer=writer)

    episode_history = deque(maxlen=100)
    for i_episode in range(MAX_EPISODES):

        # initialize
        state = env.reset()
        total_rewards = 0

        for t in range(MAX_STEPS):
            env.render()  # render environment's frames
            action = pg_reinforce.sampleAction(state[np.newaxis, :])
            next_state, reward, done, _ = env.step(action)

            total_rewards += reward
            reward = -10 if done else 0.1  # normalize reward
            pg_reinforce.storeRollout(state, action, reward)

            state = next_state
            if done: break

        pg_reinforce.updateModel()

        episode_history.append(total_rewards)
        mean_rewards = np.mean(episode_history)

        print("Episode: {}".format(i_episode))
        print("Finished after {} steps".format(t + 1))
        print("Reward for this episode: {}".format(total_rewards))
        print("Average reward for last 100 episodes: {:.2f}".format(mean_rewards))
        if mean_rewards >= 195.0 and len(episode_history) >= 100:
            print("Reinforce solved {} after {} episodes".format(env_name, i_episode + 1))
            break


if __name__ == '__main__':
    main()
