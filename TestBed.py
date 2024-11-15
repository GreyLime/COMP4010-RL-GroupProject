from Environment import Environment, Building, Floor

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

    print(f"External Temperature: {outsideTemp}, Total Building Energy Consumption: {building.totalEnergyUsed}, Average Building Comfort: {building.averageComfort}")
    # You can access the floors in the environment like this:
    for floor in building.floors:
        print(f"Floor occupants: {floor.numOccupants}, Lights: {floor.lightStatus}, Temperature: {floor.temperature}, Energy used: {floor.energyUsed}, Comfort: {floor.comfort}")


if __name__ == "__main__":
    main()