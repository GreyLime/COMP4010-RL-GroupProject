class Building:
    def __init__(self, outsideTemperature):
        """
        Initializes an Building object with zero floors.

        Args:                        
            outsideTemperature (int): The outside temperature in degrees Celsius.
        """
        self.floors = []
        self.totalEnergyUsed = 0
        self.averageComfort = 0
        self.outsideTemperature = outsideTemperature                
        self.ExpectedTotalBuildingEnergy = 0


    def addFloor(self, floor):
        self.floors.append(floor)        
        # Expected energy used assumes lights on for all floors and all floors at comfortable temp. This can likely be tweaked, as this is related to the goal state in the environment.
        self.ExpectedTotalBuildingEnergy = len(self.floors) * 0.5 + (len(self.floors) * (abs(self.outsideTemperature - 21) * 0.1))
        self.updateAverageComfort()        
        self.updateTotalEnergyUsed()

    def updateTotalEnergyUsed(self, floorUpdate=[]):
        # If no floorUpdate is passed in, update it based on all floors
        if floorUpdate == []:
            self.totalEnergyUsed = 0
            for floor in self.floors:                                
                self.totalEnergyUsed += floor.energyUsed
        # If a specific floor is passed in, update it based only that floor
        else:
            prevFloorEnergy = floorUpdate[0].energyUsed
            newFloorEnergy = floorUpdate[1].energyUsed
            self.totalEnergyUsed -= prevFloorEnergy
            self.totalEnergyUsed += newFloorEnergy
        
    def updateAverageComfort(self, floorUpdate=[]):
        # If no floorUpdate is passed in, update it based on all floors
        if floorUpdate == []:
            totalComfort = 0
            floorsWithOccupants = 0
            for floor in self.floors:
                if floor.comfort != -1:
                    floorsWithOccupants += 1
                    totalComfort += floor.comfort     
            self.averageComfort = totalComfort / floorsWithOccupants
        # If a specific floor is passed in, update it based only that floor
        else:
            numFloors = len(self.floors)
            prevFloorComfort = floorUpdate[0].comfort
            newFloorComfort = floorUpdate[1].comfort
            # Replaces old value in average with new value
            self.averageComfort = (numFloors * self.averageComfort - prevFloorComfort + newFloorComfort) / numFloors
            

class Floor:
    def __init__(self, building, numOccupants=0, lightStatus=False, temperature=21, outsideTemperature=0):
        """
        Initializes a Floor object.

        Args:
            numOccupants (int): The number of occupants on the floor.
            lightStatus (bool): The status of the lights (True for on, False for off).
            temperature (int): The temperature of the floor in degrees Celsius.
            outsideTemperature (int): The outside temperature in degrees Celsius.
        """
        self.building = building
        self.numOccupants = numOccupants
        self.lightStatus = lightStatus
        self.temperature = temperature
        self.outsideTemperature = outsideTemperature
        # Energy used is measured in kW/h
        self.energyUsed = 0
        # Comfort of 0 is uncomfortable, 1 is medium comfort, 2 is high comfort. -1 is used when no occupants are on the floor, so that the comfort for that floor can be disregarded
        self.comfort = 0
        
        self.calculateComfort()
        self.calculateEnergyUsage()

    def calculateComfort(self):
        # -1 is used when no occupants are on the floor, so that the comfort for that floor can be disregarded
        if self.numOccupants == 0:
            self.comfort = -1
            return
        
        if self.lightStatus:
            self.comfort += 1

        # Calculate how the floor's temperature effects the comfort of the floor.
        # The comfortable room temperatures are 21 and 22. Made it a small range to see that the model always chooses 21, since 22 would always be a waste of energy in this scenario.
        if self.temperature == 21 or self.temperature == 22:
            self.comfort += 1
        # If temperature is 2 degrees above or below from comfort temp, comfort will drop by 1.
        elif (self.temperature - 2 <= 19) or (self.temperature + 2 >= 24):
            if self.comfort >= 1:
                self.comfort -= 1
        # If temperature is 4 degrees above or below from comfort temp, comfort will drop by 2.
        elif (self.temperature - 4 <= 17) or (self.temperature + 4 >= 26):
            if self.comfort == 2:
                self.comfort -= 2
            # If comfort is lower than 2, set to 0. Comfort cant be a negative number.
            else:
                self.comfort = 0
        
    def calculateEnergyUsage(self):
        if self.lightStatus:
            self.energyUsed += 0.5

        # Calculate energy used based on difference of floor temperature and outside temp
        self.energyUsed += (abs(self.outsideTemperature - self.temperature) * 0.1)
        
    def addOccupant(self):
        self.numOccupants += 1

    def removeOccupant(self):
        self.numOccupants -= 1

    def switchLights(self):
        prev = self
        self.lightStatus = not self.lightStatus
        self.calculateComfort()
        self.calculateEnergyUsage()
        new = self
        floorUpdate = [prev,new]
        self.building.updateAverageComfort(floorUpdate)
        self.building.updateTotalEnergyUsed(floorUpdate)

    def increaseTemp(self):
        prev = self
        self.temperature += 1
        self.calculateComfort()
        self.calculateEnergyUsage()
        new = self
        floorUpdate = [prev,new]
        self.building.updateAverageComfort(floorUpdate)
        self.building.updateTotalEnergyUsed(floorUpdate)

    def decreaseTemp(self):
        prev = self
        self.temperature -= 1
        self.calculateComfort()
        self.calculateEnergyUsage()
        new = self
        floorUpdate = [prev,new]
        self.building.updateAverageComfort(floorUpdate)
        self.building.updateTotalEnergyUsed(floorUpdate)
        
# TODO setup rewards/states/actions system in this class
class Environment:
    def __init__(self, building):
        
        # Used to track how many actions have been taken since the start of the run.
        self.numActionsTaken = 0

        
        # NOTE: Goal state will be when building.averageComfort > 1.5 and building.totalEnergyUsed < building.expectedEnergyUsage

    # TODO
    def computeReward():
        return None
