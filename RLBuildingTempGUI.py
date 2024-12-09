import pygame
import pygame_gui
import queue

def drawScene(buildingInfo, manager,buildingDetails):

    # Kill all existing UI elements
    manager.clear_and_reset()
    
    #general building info + outdoor variable modifiers, displayed at top of gui
    dataLabels = {
       "Average Comfort": pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((20,20),(250,50)),
            text=f"Average Comfort: {buildingInfo.averageComfort:.1f}",
            manager=manager
        ),
        "Expected Energy": pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((300,20),(300,50)),
            text=f"Expected Total Energy: {buildingInfo.expectedEnergyUsage:.2f} kW/h",
            manager=manager
        ),
        "Outside Temperature": pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((600,20),(200,50)),
            text=f"Outside Temperature: {buildingInfo.outsideTemperature}°C",
            manager=manager
        )
    }

    #buttons to adjust outside temp, paired with data label above
    adjustButtons = {
        "Increase Outside Temp": pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((650,55),(50,25)),
            text="+",
            manager=manager
        ),
        "Decrease Outside Temp": pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((700,55),(50,25)),
            text="-",
            manager=manager
        )
    }

    #dynamically creates lables and buttons for each floor
    for i, floor in enumerate(buildingInfo.floors):
        currFloorY = buildingDetails[3] - i* (buildingDetails[3]/len(buildingInfo.floors)) 
        
        #the inner floor label of energy consumption + comfort
        comfort = floor.comfort
        if floor.comfort < 1:
            comfort = 0
            
        dataLabels[f"Floor {i+1} Data"] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((120, currFloorY), (350, 50)),            
            text=f"Floor {i+1} - Energy: {floor.energyUsed:.2f} kW/h - Comfort: {comfort:.2f}",
            manager=manager
        )
        
        #overall floor label:
        dataLabels[f"Floor {i+1}:"] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((600, currFloorY-25), (150, 50)),
            text=f"Floor {i+1} -",
            manager=manager
        )
        
        #next three are the occupants labels and buttons
        dataLabels[f"Floor {i+1} Occupants"] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((625, currFloorY), (150, 50)),
            text=f"Occupants: {floor.numOccupants}",
            manager=manager
        )
        adjustButtons[f"Floor {i+1} Occupants +"] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((800, currFloorY + 10), (50, 25)),
            text="+",
            manager=manager
        )
        adjustButtons[f"Floor {i+1} Occupants -"] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((850, currFloorY + 10), (50, 25)),
            text="-",
            manager=manager
        )
        
        #next three are the temperature labels and buttons
        dataLabels[f"Floor {i+1} Temp"] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((625, currFloorY +25), (150, 50)),
            text=f"Temp: {floor.temperature}°C",
            manager=manager
        )
        adjustButtons[f"Floor {i+1} Temp +"] = pygame_gui.elements.UIButton(  
            relative_rect=pygame.Rect((800, currFloorY +35), (50, 25)),
            text="+",
            manager=manager
        )
        adjustButtons[f"Floor {i+1} Temp -"] = pygame_gui.elements.UIButton( 
            relative_rect=pygame.Rect((850, currFloorY +35), (50, 25)),
            text="-",
            manager=manager
        )


        #floor light toggle button
        adjustButtons[f"Floor {i+1} Lights"] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((800, currFloorY + 65), (100, 25)),
            text="Lights On" if floor.lightStatus else "Lights Off",
            manager=manager
        )

    return dataLabels, adjustButtons

def drawUpdates(screen, buildingInfo,manager, buildingDetails):
    
    #start by filling the screen with the sky blue background, then draw the rest on top
    screen.fill(pygame.Color('#87CEEB'))

    #dynamic building drawing:
    for i in range(len(buildingInfo.floors)):
        
        #dynamically spaces the floor based on the height of the building. 1000 is screen height, so it starts 
        #by drawing the top floor downwards first.
        floorSpacing = (925- buildingDetails[1])-(i*buildingDetails[4])

        #properly color floor based on initial lighton status
        if buildingInfo.floors[i].lightStatus:
            lightsOn =buildingDetails[5][1]
        else:
            lightsOn = buildingDetails[5][0] 
        
        #draw the floor 
        pygame.draw.rect(screen,lightsOn,(buildingDetails[0],floorSpacing,buildingDetails[2],buildingDetails[4]))
        
        #add black border around floor so floors can be decerned 
        border=pygame.Rect(buildingDetails[0], floorSpacing, buildingDetails[2], buildingDetails[4])
        pygame.draw.rect(screen, buildingDetails[5][2], border,4)

    #draw the sun in the corner !!! yay !!! mins and maxs in place otherwise gui will crash when decimal gets to a weird value
    #causing teh yellow value in next line to not be within 0-255
    sunTemp = min(1, max(0, (buildingInfo.outsideTemperature - 10) / 50))

    #max red, yellow is multiplied by a percentage based on how hot it is. like 255*0.85 for 216.75, or lots of yellow
    #so very orange, or very hot. no green.
    sunHue = pygame.Color(255, int(255 * (1 - sunTemp)), 0)

    #draw the sun
    pygame.draw.circle(screen, sunHue, (screen.get_width() - 50, 50), 30)

def runGUI(buildingInfo, gui_queue):
    
    #init pygame
    pygame.init()

    #defines screen borders
    screenWidth = 1000
    screenHeight = 1000
    screen=pygame.display.set_mode((screenWidth,screenHeight))

    #defines the sizing of the building to make func calls cleaner and save rewriting these. makes it more dynamic
    buildingX = 50
    buildingY = 150
    buildingWidth = 500
    buildingHeight =850
    floorHeight= buildingHeight // len(buildingInfo.floors)

    #defines colours for building
    buildingColours =[pygame.Color('#AAAAAA'), pygame.Color('#f4d26c'),pygame.Color('#000000')]

    #compile building details in array to make passing into dynamic drawing func. easier
    buildingDetails = [buildingX,buildingY,buildingWidth,buildingHeight,floorHeight,buildingColours]

    #adds a title for the application
    pygame.display.set_caption('COMP4010 Project - Building Temperature Control')

    #defines a manager for the gui
    manager=pygame_gui.UIManager((screenWidth,screenHeight), 'theme.json')

    #draw static elements here
    dataLabels,adjustButtons =drawScene(buildingInfo,manager, buildingDetails)

    #define a timer and running variable to check for program exit
    clock = pygame.time.Clock()
    applicationRunning = True

    while applicationRunning:

        #track time
        timer = clock.tick(60)/1000.0

        #event checker
        for event in pygame.event.get():

            #if event is quit... quit
            if event.type==pygame.QUIT:
                applicationRunning = False

            #button handlers:
            if event.type == pygame_gui.UI_BUTTON_PRESSED:

                #these two handle the outdoor temps
                if event.ui_element == adjustButtons["Increase Outside Temp"]:
                    buildingInfo.outsideTemperature += 1
                    dataLabels["Outside Temperature"].set_text(f"Outside Temperature: {buildingInfo.outsideTemperature}°C")

                elif event.ui_element == adjustButtons["Decrease Outside Temp"]:
                    buildingInfo.outsideTemperature -= 1
                    dataLabels["Outside Temperature"].set_text(f"Outside Temperature: {buildingInfo.outsideTemperature}°C")

                #these handle all floor buttons
                else:
                    
                    #loop through all floors
                    for i in range(len(buildingInfo.floors)):

                        #check if floor at i's occupants increased
                        if event.ui_element==adjustButtons[f"Floor {i+1} Occupants +"]:
                            buildingInfo.floors[i].addOccupant()
                            dataLabels[f"Floor {i+1} Occupants"].set_text(f"Occupants: {buildingInfo.floors[i].numOccupants}")

                        #check if floor at i's occupants decreased
                        elif event.ui_element == adjustButtons[f"Floor {i+1} Occupants -"]:
                            #check we do not go lower than 0 people...
                            if buildingInfo.floors[i].numOccupants > 0:
                                buildingInfo.floors[i].removeOccupant()
                                dataLabels[f"Floor {i+1} Occupants"].set_text(f"Occupants: {buildingInfo.floors[i].numOccupants}")

                        #check if the floor at i's temp increased
                        if event.ui_element == adjustButtons[f"Floor {i+1} Temp +"]:
                            buildingInfo.floors[i].increaseTemp()
                            dataLabels[f"Floor {i+1} Temp"].set_text(f"Temp: {buildingInfo.floors[i].temperature}°C")
                            #drawUpdates(screen, buildingInfo)

                        #check if the floor at i's temp decreased
                        elif event.ui_element == adjustButtons[f"Floor {i+1} Temp -"]:
                            buildingInfo.floors[i].decreaseTemp()
                            dataLabels[f"Floor {i+1} Temp"].set_text(f"Temp: {buildingInfo.floors[i].temperature}°C")
                            #drawUpdates(screen, buildingInfo)
                        
                        #toggle floor at i's lights
                        elif event.ui_element == adjustButtons[f"Floor {i+1} Lights"]:
                            buildingInfo.floors[i].switchLights()
                            adjustButtons[f"Floor {i+1} Lights"].set_text(f"Lights {'On' if buildingInfo.floors[i].lightStatus else 'Off'}")
                            #draw light update
                            drawUpdates(screen, buildingInfo,manager,buildingDetails)

            #process events
            manager.process_events(event)

        try:
            # Check for updates from the algorithm
            update = gui_queue.get_nowait()
            if update is None:
                applicationRunning = False
            else:
                # Update the building state
                buildingInfo = update
                manager.clear_and_reset()  # Clear UI before redrawing
                dataLabels, adjustButtons = drawScene(buildingInfo, manager, buildingDetails)
        except queue.Empty:
            pass

        #update the timers
        manager.update(timer)

        #draw the dynamic elements
        drawUpdates(screen, buildingInfo,manager,buildingDetails)
        
        #draw the ui elements
        manager.draw_ui(screen)

        #update the display
        pygame.display.update()

    pygame.quit()

