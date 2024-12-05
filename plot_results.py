import matplotlib.pyplot as plt

def plot_rewards(rewards, title="Q-learning Performance"):
    plt.figure(figsize=(10, 6))
    plt.plot(rewards)
    plt.title(title)
    plt.xlabel("Episode")
    plt.ylabel("Total Reward")
    plt.grid(True)
    plt.savefig("q_learning_performance.png")
    plt.close()
