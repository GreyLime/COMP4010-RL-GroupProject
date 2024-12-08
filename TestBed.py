from Environment import Environment, Building, Floor
from algo1 import algo1
from algo2 import algo2
from plot_results import plot_rewards

def main():
    outsideTemp = 15
    # Create an Building object
    building = Building(outsideTemperature=outsideTemp)

    # Create 3 Floor objects
    floor1 = Floor(building, numOccupants=1, lightStatus=True, temperature=22, outsideTemperature=outsideTemp)
    floor2 = Floor(building, numOccupants=0, lightStatus=False, temperature=20, outsideTemperature=outsideTemp)
    floor3 = Floor(building, numOccupants=5, lightStatus=True, temperature=25, outsideTemperature=outsideTemp)

    building.addFloor(floor1)
    building.addFloor(floor2)
    building.addFloor(floor3)

    env = Environment(building)

    #thing = algo1(env, gamma=0.99, stepSize=0.01, maxEpisodes=400)
    # Render environment
    # TODO aaron gui function here

    print(f"External Temperature: {outsideTemp}, Total Building Energy Consumption: {building.totalEnergyUsed}, Average Building Comfort: {building.averageComfort}")

    #Algorithm 1# 
    Q, total_rewards = algo1(env, gamma=0.99, stepSize=0.01, maxEpisodes=400, epsilon=0.1)
    
    #Algorithm 2
    #Q1, Q2, rewards = algo2(env, gamma=0.99, stepSize=0.01, maxEpisodes=400, alpha=0.1)

    #Algorithm 3
    #theta, total_rewards = algo3(env, gamma=0.99, stepSize=0.01, maxEpisodes=400)
    plot_rewards(total_rewards, title="Q-learning Performance for Building Temperature Control")
    print("Performance graph saved as 'q_learning_performance.png'")

    print(f"External Temperature: {outsideTemp}, Total Building Energy Consumption: {building.totalEnergyUsed:.2f}, Average Building Comfort: {building.averageComfort:.2f}")
    #############
    
    # You can access the floors in the environment like this:
    for floor in building.floors:
        print(f"Floor occupants: {floor.numOccupants}, Lights: {floor.lightStatus}, Temperature: {floor.temperature}, Energy used: {floor.energyUsed}, Comfort: {floor.comfort}")



if __name__ == "__main__":
    main()
