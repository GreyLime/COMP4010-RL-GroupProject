import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from copy import deepcopy


GAMMA = 0.99
LR = 1e-5
K_EPOCHS = 10
EPS_CLIP = 0.1
ENTROPY_COEF = 0.01
BATCH_SIZE = 64
MAX_EPISODES = 500
MAX_STEPS_PER_EPISODE = 500

#neural network approximations
class ActorCritic(nn.Module):
    def __init__(self, state_dim, action_dim):
        super(ActorCritic, self).__init__()
        # Simple 2-layer MLP
        self.fc = nn.Sequential(
            nn.Linear(state_dim, 64),
            nn.ReLU(),
            nn.Linear(64,64),
            nn.ReLU()
        )
        self.pi = nn.Linear(64, action_dim)  # policy logits
        self.v = nn.Linear(64, 1)  # state value

    def forward(self, x):
        x = self.fc(x)
        logits = self.pi(x)
        value = self.v(x)
        return logits, value

    def get_action_probs(self, state):
        logits, value = self.forward(state)
        action_probs = torch.softmax(logits, dim=-1)
        return action_probs, value

    def get_action(self, state):
        action_probs, value = self.get_action_probs(state)
        dist = torch.distributions.Categorical(action_probs)
        action = dist.sample()
        return action.item(), dist.log_prob(action), value







class PPOAgent:
    def __init__(self, state_dim, action_dim):
        self.policy = ActorCritic(state_dim, action_dim)
        self.optimizer = optim.Adam(self.policy.parameters(), lr=LR)

    def update(self, memory):
        states = torch.tensor(np.array(memory.states), dtype=torch.float)
        actions = torch.tensor(memory.actions, dtype=torch.long).view(-1,1)
        rewards = torch.tensor(memory.rewards, dtype=torch.float).view(-1,1)
        dones = torch.tensor(memory.dones, dtype=torch.float).view(-1,1)
        old_logprobs = torch.tensor(memory.logprobs, dtype=torch.float).view(-1,1)


        with torch.no_grad():
            _, values = self.policy.get_action_probs(states)
            values = values.view(-1,1)
            next_values = torch.cat([values[1:], torch.zeros(1,1)], dim=0)
            deltas = rewards + GAMMA * next_values * (1 - dones) - values
            advantages = torch.zeros_like(rewards)
            running_adv = 0
            for t in reversed(range(len(rewards))):
                running_adv = running_adv * GAMMA * (1 - dones[t]) + deltas[t]
                advantages[t] = running_adv
            returns = advantages + values

        #normalize advantages
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)

        #update
        for _ in range(K_EPOCHS):
            action_probs, value = self.policy.get_action_probs(states)
            dist = torch.distributions.Categorical(action_probs)
            current_logprobs = dist.log_prob(actions.squeeze())

            ratio = (current_logprobs - old_logprobs.squeeze()).exp()
            surr1 = ratio * advantages.squeeze()
            surr2 = torch.clamp(ratio, 1 - EPS_CLIP, 1 + EPS_CLIP) * advantages.squeeze()

            entropy = dist.entropy().mean()
            loss = -torch.min(surr1, surr2).mean() + 0.5 * ((returns - value)**2).mean() - ENTROPY_COEF * entropy

            self.optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.policy.parameters(), 0.5)
            self.optimizer.step()

    def act(self, state):
        state_t = torch.tensor(state, dtype=torch.float).unsqueeze(0)
        action, logprob, value = self.policy.get_action(state_t)
        return action, logprob.item(), value.item()


#,memory for PPO
class Memory:
    def __init__(self):
        self.states = []
        self.actions = []
        self.rewards = []
        self.logprobs = []
        self.dones = []

    def store(self, state, action, reward, logprob, done):
        self.states.append(state)
        self.actions.append(action)
        self.rewards.append(reward)
        self.logprobs.append(logprob)
        self.dones.append(done)

    def clear(self):
        self.states = []
        self.actions = []
        self.rewards = []
        self.logprobs = []
        self.dones = []







# Helper functions to convert environment state to numeric vector
def state_to_vector(building):
    floors_data = []
    for floor in building.floors:
        floors_data.append(1.0 if floor.lightStatus else 0.0)
        floors_data.append(float(floor.temperature))
        floors_data.append(float(floor.numOccupants))

    state_vec = [building.outsideTemperature] + floors_data + [building.totalEnergyUsed, building.averageComfort]
    state_vec = np.array(state_vec, dtype=float)

    #normalization
    mean = np.mean(state_vec)
    std = np.std(state_vec) + 1e-8
    state_vec = (state_vec - mean) / std
    return state_vec



# training loop function
def algo3(env):
    #state dimension and action dimension
    num_floors = env.building.getNumFloors()
    action_dim = num_floors * 3

    #initial state dimension
    initial_state = env.reset()
    state_vec = state_to_vector(initial_state)
    state_dim = len(state_vec)

    agent = PPOAgent(state_dim, action_dim)
    memory = Memory()

    total_rewards = []

    for episode in range(MAX_EPISODES):
        building = env.reset()
        state = state_to_vector(building)
        memory.clear()
        episode_reward = 0

        for step in range(MAX_STEPS_PER_EPISODE):
            action, logprob, _ = agent.act(state)
            floor_idx = action // 3
            sub_action = action % 3
            step_count = 0

            chosen_floor = env.building.floors[floor_idx]
            if sub_action == 0:
                chosen_floor.actionFunc = chosen_floor.switchLights
            elif sub_action == 1:
                chosen_floor.actionFunc = chosen_floor.increaseTemp
            elif sub_action == 2:
                chosen_floor.actionFunc = chosen_floor.decreaseTemp

            # env expects action as [floorNum, actionNum starting at 1]
            # sub_action:0->1(switch),1->2(inc),2->3(dec)
            act = [floor_idx, sub_action + 1]
            next_building, reward, done = env.step(act)
            next_state = state_to_vector(next_building)

            memory.store(state, action, reward, logprob, done)
            state = next_state
            episode_reward += reward
            step_count += 1  

            if done:
                break
            
            if step_count >= 500: #stop infinite loops
                break
          


        if len(memory.rewards) < 2:
            continue

        agent.update(memory)
        total_rewards.append(episode_reward)
        if episode % 10 == 0:
            print(f"Episode {episode}, Reward: {episode_reward}")

    return total_rewards
