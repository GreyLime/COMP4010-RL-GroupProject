import numpy as np
import random

def softmax(x):
    #to convert a vector into probability distribution
    #first stabilize by subtracting the max value from x to avoid large exponenTS
    z = x - np.max(x)
    return np.exp(z) / np.sum(np.exp(z))

def algo2(env, gamma=0.99, stepSize=0.01, maxEpisodes=400, alpha=0.1):
    
    
    # this is a discrete adaptation of Soft Actor-Critic
    #operates on a per-floor basis, choosing to either 1: Switch Lights, 2: Increase Temperature, 3: Decrease Temperature
    #maintains two Q-value estimates (Q1 and Q2) for Soft Actor-Critic
    #uses a policy derived from Q-values via a softmax distribution

  
    num_floors = env.building.getNumFloors()
    num_actions_per_floor = 3   #Each floor has exactly 3 discrete actions

    
    # each floor considered as a separate subset of states
    Q1 = np.zeros((num_floors, 2, 3, num_actions_per_floor)) 
    Q2 = np.zeros((num_floors, 2, 3, num_actions_per_floor))

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

        while not env.terminated:
            
            floor = random.randint(0, num_floors - 1)
            f, ls, ts = get_state_index(state, floor)

            Q_min = np.minimum(Q1[f, ls, ts, :], Q2[f, ls, ts, :])
            pi = softmax(Q_min / alpha)

            action_idx = np.random.choice(range(num_actions_per_floor), p=pi)
            action = [floor, action_idx + 1]  # 1,2,3 actions


            # NOW environment can call `self.building.floors[floorNum].actionFunc()`.
            chosen_floor = env.building.floors[floor]
            if action[1] == 1:
                chosen_floor.actionFunc = chosen_floor.switchLights
            elif action[1] == 2:
                chosen_floor.actionFunc = chosen_floor.increaseTemp
            elif action[1] == 3:
                chosen_floor.actionFunc = chosen_floor.decreaseTemp


            next_state, reward, terminated = env.step(action)
            episode_reward += reward

            nf, nls, nts = get_state_index(next_state, floor)

            Q_min_next = np.minimum(Q1[nf, nls, nts, :], Q2[nf, nls, nts, :])
            pi_next = softmax(Q_min_next / alpha)

            log_pi_next = np.log(pi_next + 1e-10)
            V_next = np.sum(pi_next * (Q_min_next - alpha * log_pi_next))
            y = reward + (gamma * V_next if not terminated else 0)

            td_error_1 = y - Q1[f, ls, ts, action_idx]
            td_error_2 = y - Q2[f, ls, ts, action_idx]
            Q1[f, ls, ts, action_idx] += stepSize * td_error_1
            Q2[f, ls, ts, action_idx] += stepSize * td_error_2

            state = next_state
            step_count += 1

            #stop infinite loops
            if step_count >= 500:
                break

        total_rewards.append(episode_reward)
        if episode % 10 == 0:
            print(f"Episode {episode}, Total Reward: {episode_reward:.2f}, Steps: {step_count}")

    return Q1, Q2, total_rewards
