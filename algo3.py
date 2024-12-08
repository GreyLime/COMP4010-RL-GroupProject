import numpy as np
import random
import matplotlib.pyplot as plt

def softmax(x):
    z = x - np.max(x)
    return np.exp(z) / np.sum(np.exp(z))

def algo3(env, gamma=0.99, stepSize=0.01, maxEpisodes=400):
    num_floors = env.building.getNumFloors()
    num_actions = env.numActions
    
    # Initialize policy parameters
    theta = np.random.rand(num_floors, 2, 3, num_actions)
    
    total_rewards = []

    def get_state_index(state, floor):
        light_status = 1 if state.floors[floor].lightStatus else 0
        temp = state.floors[floor].temperature
        if temp < 20:
            t = 0
        elif temp < 23:
            t = 1
        else:
            t = 2
        return floor, light_status, t

    for episode in range(maxEpisodes):
        state = env.reset()
        episode_reward = 0
        step_count = 0
        
        # Store states, actions, and rewards for the episode
        episode_states = []
        episode_actions = []
        episode_rewards = []

        while not env.terminated:
            floor = random.randint(0, num_floors - 1)
            f, ls, ts = get_state_index(state, floor)
            
            # Compute policy (softmax over theta)
            pi = softmax(theta[f, ls, ts, :])
            action_idx = np.random.choice(range(num_actions), p=pi)
            action = [floor, action_idx]
            
            next_state, reward, terminated = env.step(action)
            episode_reward += reward

            # Store the state, action, and reward
            episode_states.append((f, ls, ts))
            episode_actions.append(action_idx)
            episode_rewards.append(reward)

            state = next_state
            step_count += 1

            if step_count >= 500:  # safeguard against infinite loops
                break

        total_rewards.append(episode_reward)

        # Compute returns and update policy parameters
        G = 0
        returns = []
        for r in reversed(episode_rewards):
            G = r + gamma * G
            returns.insert(0, G)
        
        returns = np.array(returns)
        returns = (returns - np.mean(returns)) / (np.std(returns) + 1e-10)  # Normalize returns

        for (f, ls, ts), action_idx, G in zip(episode_states, episode_actions, returns):
            pi = softmax(theta[f, ls, ts, :])
            grad_log_pi = -pi
            grad_log_pi[action_idx] += 1
            theta[f, ls, ts, :] += stepSize * grad_log_pi * G

        if episode % 10 == 0:
            print(f"Episode {episode}, Total Reward: {episode_reward:.2f}, Steps: {step_count}")

    return theta, total_rewards



def plot_rewards(rewards, title="REINFORCE Performance"):
    plt.figure(figsize=(10, 6))
    plt.plot(rewards)
    plt.title(title)
    plt.xlabel("Episode")
    plt.ylabel("Total Reward")
    plt.grid(True)
    plt.savefig("REINFORCE_performance.png")
    plt.close()
