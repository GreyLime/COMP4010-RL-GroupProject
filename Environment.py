from copy import deepcopy as copy

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
        self.expectedEnergyUsage = 0


    def addFloor(self, floor):
        self.floors.append(floor)        
        # Expected energy used assumes lights on for all floors and all floors at comfortable temp. This can likely be tweaked, as this is related to the goal state in the environment.
        self.expectedEnergyUsage = len(self.floors) * 0.5 + (len(self.floors) * (abs(self.outsideTemperature - 21) * 0.1))
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
        # If no floorUpdate is passed in, update it based on all floors that have occupants
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
            prevFloor = floorUpdate[0]
            newFloor = floorUpdate[1]
            numFloors = len(self.floors)

            # NOTE: This average updating stuff hasnt been thoroughly tested... beware of bugs
            # Only update comfort on the floor if the floor has occupants, or 
            if newFloor.numOccupants > 0:
                # Replaces old value in average with new value
                self.averageComfort = (numFloors * self.averageComfort - prevFloor.comfort + newFloor.comfort) / numFloors
            # if the floor previously had occupants but now has 0, remove it from averageComfort
            if (prevFloor.numOccupants > 0 and newFloor.numOccupants == 0):
                # Remove floor comfort from average
                self.averageComfort = ((self.averageComfort * numFloors) - prevFloor.comfort) / (numFloors - 1)

    def getNumFloors(self):
        return len(self.floors)            


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
        prev = copy(self)
        self.lightStatus = not self.lightStatus
        self.calculateComfort()
        self.calculateEnergyUsage()
        new = self
        floorUpdate = [prev,new]
        # Update building average comfort
        self.building.updateAverageComfort(floorUpdate)
        # Update total building energy
        self.building.updateTotalEnergyUsed(floorUpdate)

    def increaseTemp(self):
        prev = copy(self)
        self.temperature += 1
        self.calculateComfort()
        self.calculateEnergyUsage()
        new = self
        floorUpdate = [prev,new]
        self.building.updateAverageComfort(floorUpdate)
        self.building.updateTotalEnergyUsed(floorUpdate)

    def decreaseTemp(self):
        prev = copy(self)
        self.temperature -= 1
        self.calculateComfort()
        self.calculateEnergyUsage()
        new = self
        floorUpdate = [prev,new]
        self.building.updateAverageComfort(floorUpdate)
        self.building.updateTotalEnergyUsed(floorUpdate)
        

class Environment:
    def __init__(self, building):
        self.building = building
        self.startingState = copy(building) # Create copy of memory so when changes to building occur we still retain the original building

        # Used to track how many actions have been taken since the start of the run.
        self.numStepsTaken = 0
        self.terminated = False

        self.actionSpace = []
        self.numActions = 0
        actionIndex = 1
        for i in range(len(building.floors)):  # Add actions for each floor
            self.numActions += 3
            floorActions = [1,2,3]
            self.actionSpace.append(floorActions)

        print(self.numActions)
        print(self.actionSpace)

    # NOTE: This function's logic/values may need tweaking upon testing!
    def computeReward(self, prevState):
        totalReward = 0

        # Increase rewards
        # Did action improve on state, i.e. get closer to end goal?
        if prevState.averageComfort < self.building.averageComfort:
            totalReward += 0.1
        if prevState.totalEnergyUsed > self.building.totalEnergyUsed:
            totalReward += 0.1
        # Did action reach an optimal state? big reward
        if (self.building.totalEnergyUsed < self.building.expectedEnergyUsage):
            reward += 1
        if (self.building.averageComfort > 1.5):
            reward += 1
        
        # Decrease rewards
        # If building is less than high comfort but higher than uncomfortable, drop rewards if comfort continues to decrease. No need to punish if comfort drops when its already in a high state.
        if self.building.averageComfort < 2 and self.building.averageComfort > 1:
            if prevState.averageComfort > self.building.averageComfort:
                totalReward -= 0.1
        # If the building average comfort is uncomfortable, bigger punishment
        elif self.building.averageComfort < 1:
            totalReward -= 1

        if prevState.totalEnergyUsed < self.building.totalEnergyUsed:
            # If the difference between the totalEnergyUSed and the expectedEnergyUsage is greater or equal to 2 kW/h, bigger punishment 
            # NOTE 2 is an arbitrary value, this may need tweaking!!
            if (self.building.totalEnergyUsed - self.building.expectedEnergyUsage) > 2:
                totalReward -= 1
            # Otherwise, minor punishment for when action increases energy usage.
            else:
                totalReward -= 0.1
            
        return totalReward
    
    def reset(self):
        self.numStepsTaken = 0
        self.terminated = False
        self.building = self.startingState

        return self.building
    
    def isEpisodeFinished(self):
        # This is the goal state
        if (self.building.totalEnergyUsed < self.building.expectedEnergyUsage) and (self.building.averageComfort >= 1.5):
            self.terminated = True
            return self.terminated        
        # This is to truncate runs after 500 steps.
        elif (self.numStepsTaken > 500):
            self.terminated = True
            return self.terminated
        
        return False

    def step(self, action):
        # Copy building before changes are made from action. Used to calculate reward for action.
        prevState = copy(self.building)

        # action is in form [floornumber,actionnumber]
        floorNum = action[0]
        actionNum = action[1]

        match actionNum:
            # Agent does nothing for a step (maybe remove if causing problems?)
            case 0:
                actionFunc = None
            # The rest area standard actions
            case 1:
                actionFunc = Floor.switchLights
            case 2:
                actionFunc = Floor.increaseTemp
            case 3:
                actionFunc = Floor.decreaseTemp            
        
        if actionFunc:
            self.building.floors[floorNum].actionFunc()
                
        # Check if episode terminated after action
        terminated = self.isEpisodeFinished()
        if terminated:
            # By convention, reaching goal state has reward of 0. NOTE: double check if this is true
            reward = 0
        else:
            reward = self.computeReward(prevState)

        #next_state, reward, terminated
        return self.building, reward, terminated

