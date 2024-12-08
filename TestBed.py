from Environment import Environment, Building, Floor
from algo1 import algo1
from algo2 import algo2
from algo3 import algo3
from plot_results import plot_rewards
import numpy as np

def run_algorithm(algo, env, hyperparameters):
    rewards_list = []
    for params in hyperparameters:
        if algo.__name__ == 'algo1':
            _, rewards = algo(env, **params)
        elif algo.__name__ == 'algo2':
            _, _, rewards = algo(env, **params)
        elif algo.__name__ == 'algo3':
            _, rewards = algo(env, **params)
        rewards_list.append(rewards)
    return rewards_list

def main():
    outsideTemp = 15
    building = Building(outsideTemperature=outsideTemp)

    floor1 = Floor(building, numOccupants=1, lightStatus=True, temperature=22, outsideTemperature=outsideTemp)
    floor2 = Floor(building, numOccupants=0, lightStatus=False, temperature=20, outsideTemperature=outsideTemp)
    floor3 = Floor(building, numOccupants=5, lightStatus=True, temperature=25, outsideTemperature=outsideTemp)

    building.addFloor(floor1)
    building.addFloor(floor2)
    building.addFloor(floor3)

    env = Environment(building)
    # Render environment
    # TODO aaron gui function here
    
    # Hyperparameters for each algorithm
    algo1_hyperparameters = [
        {'gamma': 0.95, 'stepSize': 0.1, 'maxEpisodes': 400, 'epsilon': 0.2},
        {'gamma': 0.99, 'stepSize': 0.01, 'maxEpisodes': 400, 'epsilon': 0.1},
        {'gamma': 0.999, 'stepSize': 0.001, 'maxEpisodes': 400, 'epsilon': 0.05}
    ]

    algo2_hyperparameters = [
        {'gamma': 0.95, 'stepSize': 0.1, 'maxEpisodes': 400, 'alpha': 0.2},
        {'gamma': 0.99, 'stepSize': 0.01, 'maxEpisodes': 400, 'alpha': 0.1},
        {'gamma': 0.999, 'stepSize': 0.001, 'maxEpisodes': 400, 'alpha': 0.05}
    ]

    algo3_hyperparameters = [
        {'gamma': 0.95, 'stepSize': 0.1, 'maxEpisodes': 400},
        {'gamma': 0.99, 'stepSize': 0.01, 'maxEpisodes': 400},
        {'gamma': 0.999, 'stepSize': 0.001, 'maxEpisodes': 400}
    ]

    # Run algorithms with different hyperparameters
    print("Running algorithm 1 (Q-learning)...")
    algo1_rewards = run_algorithm(algo1, env, algo1_hyperparameters)
    print("Running algorithm 2 (Soft Actor-Critic)...")
    algo2_rewards = run_algorithm(algo2, env, algo2_hyperparameters)
    print("Running algorithm 3 (Policy Gradient)...")
    algo3_rewards = run_algorithm(algo3, env, algo3_hyperparameters)

    # Plot results
    plot_rewards(algo1_rewards, algo1_hyperparameters, title="Algorithm 1 (Q-learning) Performance")
    plot_rewards(algo2_rewards, algo2_hyperparameters, title="Algorithm 2 (Soft Actor-Critic) Performance")
    plot_rewards(algo3_rewards, algo3_hyperparameters, title="Algorithm 3 (Policy Gradient) Performance")

    # Find best hyperparameters for each algorithm
    for algo_name, rewards, hyperparams in [
        ("Algorithm 1 (Q-learning)", algo1_rewards, algo1_hyperparameters),
        ("Algorithm 2 (Soft Actor-Critic)", algo2_rewards, algo2_hyperparameters),
        ("Algorithm 3 (Policy Gradient)", algo3_rewards, algo3_hyperparameters)
    ]:
        best_performance = float('-inf')
        best_params = None
        for rewards, params in zip(rewards, hyperparams):
            avg_reward = np.mean(rewards[-50:])  # Average of last 50 episodes
            if avg_reward > best_performance:
                best_performance = avg_reward
                best_params = params
        print(f"{algo_name} - Best Hyperparameters:", best_params)
        print(f"{algo_name} - Best Average Reward: {best_performance}")

    print(f"External Temperature: {outsideTemp}, Total Building Energy Consumption: {building.totalEnergyUsed:.2f}, Average Building Comfort: {building.averageComfort:.2f}")

if __name__ == "__main__":
    main()
