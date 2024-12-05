import numpy as np
import random

def algo1(env, gamma=0.99, stepSize=0.01, maxEpisodes=400, epsilon=0.1):
    num_floors = env.building.getNumFloors()
    num_actions = env.numActions
    Q = np.zeros((num_floors, 2, 3, num_actions))
    
    total_rewards = []

    for episode in range(maxEpisodes):
        state = env.reset()
        episode_reward = 0
        step_count = 0

        while not env.terminated:
            floor = random.randint(0, num_floors - 1)
            light_status = 1 if state.floors[floor].lightStatus else 0
            temp_status = 0 if state.floors[floor].temperature < 20 else (1 if state.floors[floor].temperature < 23 else 2)
            
            if random.uniform(0, 1) < epsilon:
                action_num = random.randint(0, num_actions - 1)
            else:
                action_num = np.argmax(Q[floor, light_status, temp_status])

            action = [floor, action_num]
            next_state, reward, terminated = env.step(action)
            episode_reward += reward

            next_light_status = 1 if next_state.floors[floor].lightStatus else 0
            next_temp_status = 0 if next_state.floors[floor].temperature < 20 else (1 if next_state.floors[floor].temperature < 23 else 2)

            best_next_value = np.max(Q[floor, next_light_status, next_temp_status])
            td_target = reward + gamma * best_next_value
            Q[floor, light_status, temp_status, action_num] += stepSize * (td_target - Q[floor, light_status, temp_status, action_num])

            state = next_state
            step_count += 1

            if step_count >= 500: #safeguard against infinite loops
                break

        total_rewards.append(episode_reward)

        if episode % 10 == 0:
            print(f"Episode {episode}, Total Reward: {episode_reward:.2f}, Steps: {step_count}")

    return Q, total_rewards


