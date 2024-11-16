import pygame
import pygame_gui

def drawScene(screen, buildingInfo, manager):

    skyBlue = pygame.Color('#87CEEB')
    white = pygame.Color('#FFFFFF')
    black = pygame.Color('#000000')
    yellow = pygame.Color('#FFFF00')
    grey = pygame.Color('#AAAAAA')
    lightsOn = pygame.Color('#f4d26c')

    dataLabels = {
       "Average Comfort": pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((20, 20), (250, 50)), 
            text=f"Average Comfort: {buildingInfo.averageComfort:.2f}",  
            manager=manager
        ),
        "Expected Energy": pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((300, 20), (300, 50)), 
            text=f"Expected Total Energy: {buildingInfo.ExpectedTotalBuildingEnergy:.2f} kW/h",
            manager=manager
        ),
        "Outside Temperature": pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((600, 20), (200, 50)),
            text=f"Outside Temperature: {buildingInfo.outsideTemperature}°C",  
            manager=manager
        )
    }

    adjustButtons = {
        "Increase Outside Temp": pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((650, 55), (50, 25)),  
            text="+",
            manager=manager
        ),
        "Decrease Outside Temp": pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((700, 55), (50, 25)), 
            text="-",
            manager=manager
        )
    } 

    #calculate the y-coordinate for the first floor's controls (bottom floor)
    first_floor_y = screen.get_height() - 100

    #create labels and buttons for each floor
    for i, floor in enumerate(buildingInfo.floors):
        floor_y = first_floor_y - i * 100  # determine spacing between floors here
        floorHeight = 750 // len(buildingInfo.floors)
        dataLabels[f"Floor {i+1} Data"] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((120, floor_y - floorHeight), (350, 50)), #needs to be properly positioned at the top of the floor
            text=f"Floor {i+1} - Energy: {floor.energyUsed:.2f} kW/h - Comfort: {floor.comfort:.2f}",
            manager=manager
        )
        dataLabels[f"Floor {i+1} Occupants"] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((625, floor_y), (150, 50)),  # Use floor_y
            text=f"Floor {i+1} Occupants: {floor.numOccupants}",
            manager=manager
        )
        adjustButtons[f"Floor {i+1} Occupants +"] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((800, floor_y + 10), (50, 25)),  # Use floor_y + 10
            text="+",
            manager=manager
        )
        adjustButtons[f"Floor {i+1} Occupants -"] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((850, floor_y + 10), (50, 25)),  # Use floor_y + 10
            text="-",
            manager=manager
        )
        dataLabels[f"Floor {i+1} Temp"] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((625, floor_y + 50), (150, 50)),  # Use floor_y + 50
            text=f"Floor {i+1} Temp: {floor.temperature}°C",
            manager=manager
        )
        adjustButtons[f"Floor {i+1} Temp +"] = pygame_gui.elements.UIButton(  # New temperature increase button
            relative_rect=pygame.Rect((900, floor_y + 10), (50, 25)),
            text="+",
            manager=manager
        )
        adjustButtons[f"Floor {i+1} Temp -"] = pygame_gui.elements.UIButton(  # New temperature decrease button
            relative_rect=pygame.Rect((950, floor_y + 10), (50, 25)),
            text="-",
            manager=manager
        )
        adjustButtons[f"Floor {i+1} Lights"] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((800, floor_y + 60), (100, 25)),  # Use floor_y + 60
            text="Lights On" if floor.lightStatus else "Lights Off",
            manager=manager
        )

    return dataLabels, adjustButtons

def drawUpdates(screen, buildingInfo):
    """Draws the dynamic elements that need to be updated."""

    ## --- Define building parameters ---
    buildingX = 100
    buildingY = 200
    buildingWidth = 500
    buildingHeight = 750
    floorHeight = buildingHeight // len(buildingInfo.floors)
    floorColors = [pygame.Color('#AAAAAA'), pygame.Color('#f4d26c')]  # grey, lightsOn 
    yellow = pygame.Color('#FFFF00')
    black = pygame.Color('#000000')  # Black color for borders

    # --- Clear the ENTIRE screen ---
    screen.fill(pygame.Color('#87CEEB'))  # Clear the entire screen 

    # --- Draw the building ---
    for i in range(len(buildingInfo.floors)):
        floor_y = buildingY + i * floorHeight
        
        # Determine floor color based on lightStatus
        current_floor_color = floorColors[1] if buildingInfo.floors[i].lightStatus else floorColors[0] 
        
        # Draw floor with the determined color
        pygame.draw.rect(screen, current_floor_color, (buildingX, floor_y, buildingWidth, floorHeight))
        
        # Draw thick black border around the floor
        border_rect = pygame.Rect(buildingX, floor_y, buildingWidth, floorHeight)
        pygame.draw.rect(screen, black, border_rect, 4)  # 4 is the border thickness

        # No need to draw separate circles for lights anymore

    # --- Draw the sun ---
    temp_factor = min(1, max(0, (buildingInfo.outsideTemperature - 10) / 50))
    sun_color = pygame.Color(255, int(255 * (1 - temp_factor)), 0)
    pygame.draw.circle(screen, sun_color, (screen.get_width() - 50, 50), 30)


def runGUI(buildingInfo):
    pygame.init()

    # Sets up the window
    windowWidth = 1000
    windowHeight = 1000
    screen = pygame.display.set_mode((windowWidth, windowHeight))

    # Adds a little name for the application
    pygame.display.set_caption('Reinforcement Learning - Building Temperature Control')

    # Defines the manager for gui
    manager = pygame_gui.UIManager((windowWidth, windowHeight), 'theme.json')

    dataLabels, adjustButtons = drawScene(screen, buildingInfo, manager)  # Draw static elements once

    clock = pygame.time.Clock()
    is_running = True

    while is_running:
        time_delta = clock.tick(60)/1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False

            # --- Handle button presses ---
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == adjustButtons["Increase Outside Temp"]:
                    buildingInfo.outsideTemperature += 1
                    dataLabels["Outside Temperature"].set_text(f"Outside Temperature: {buildingInfo.outsideTemperature}°C")
                    # No need to call drawUpdates() here, the sun will be redrawn in the main loop

                elif event.ui_element == adjustButtons["Decrease Outside Temp"]:
                    buildingInfo.outsideTemperature -= 1
                    dataLabels["Outside Temperature"].set_text(f"Outside Temperature: {buildingInfo.outsideTemperature}°C")
                    # No need to call drawUpdates() here

                else:
                    # Handle floor-specific buttons
                    for i in range(len(buildingInfo.floors)):
                        if event.ui_element == adjustButtons[f"Floor {i+1} Occupants +"]:
                            buildingInfo.floors[i].addOccupant()
                            dataLabels[f"Floor {i+1} Occupants"].set_text(f"Floor {i+1} Occupants: {buildingInfo.floors[i].numOccupants}")
                            

                        elif event.ui_element == adjustButtons[f"Floor {i+1} Occupants -"]:
                            if buildingInfo.floors[i].numOccupants > 0:
                                buildingInfo.floors[i].removeOccupant()
                                dataLabels[f"Floor {i+1} Occupants"].set_text(f"Floor {i+1} Occupants: {buildingInfo.floors[i].numOccupants}")

                        if event.ui_element == adjustButtons[f"Floor {i+1} Temp +"]:  # Handle temp increase
                            buildingInfo.floors[i].increaseTemp()
                            dataLabels[f"Floor {i+1} Temp"].set_text(f"Floor {i+1} Temp: {buildingInfo.floors[i].temperature}°C")
                            drawUpdates(screen, buildingInfo)  # Redraw to update comfort and energy

                        elif event.ui_element == adjustButtons[f"Floor {i+1} Temp -"]:  # Handle temp decrease
                            buildingInfo.floors[i].decreaseTemp()
                            dataLabels[f"Floor {i+1} Temp"].set_text(f"Floor {i+1} Temp: {buildingInfo.floors[i].temperature}°C")
                            drawUpdates(screen, buildingInfo)  # Redraw
                        
                        elif event.ui_element == adjustButtons[f"Floor {i+1} Lights"]:
                            buildingInfo.floors[i].switchLights()
                            adjustButtons[f"Floor {i+1} Lights"].set_text(f"Lights {'On' if buildingInfo.floors[i].lightStatus else 'Off'}")
                            drawUpdates(screen, buildingInfo)

            manager.process_events(event)

        manager.update(time_delta)

        drawUpdates(screen, buildingInfo)  # Draw dynamic elements
        
        manager.draw_ui(screen)  # Draw the UI elements

        pygame.display.update()

    pygame.quit()