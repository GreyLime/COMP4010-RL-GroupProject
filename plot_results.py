import matplotlib.pyplot as plt
import numpy as np

def plot_rewards(rewards_list, hyperparameters, title="Algorithm Performance with Different Hyperparameters"):
    plt.figure(figsize=(12, 6))
    
    colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown']
    
    for i, (rewards, params) in enumerate(zip(rewards_list, hyperparameters)):
        window_size = 10
        smoothed_rewards = np.convolve(rewards, np.ones(window_size)/window_size, mode='valid')
        
        label = ", ".join([f"{k}={v}" for k, v in params.items() if k != 'maxEpisodes'])
        
        plt.plot(smoothed_rewards, label=label, color=colors[i % len(colors)])

    plt.title(title)
    plt.xlabel("Episode")
    plt.ylabel("Total Reward")
    plt.grid(True)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(f"{title.replace(' ', '_')}.png")
    plt.close()
