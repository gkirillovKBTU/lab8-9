import pygame

def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    clock = pygame.time.Clock()
    
    radius = 15
    x = 0
    y = 0
    mode = 'blue'
    points = []
    geometricals = []
    
    while True:
        
        pressed = pygame.key.get_pressed()
        
        alt_held = pressed[pygame.K_LALT] or pressed[pygame.K_RALT]
        ctrl_held = pressed[pygame.K_LCTRL] or pressed[pygame.K_RCTRL]
        lmouse_held = pygame.mouse.get_pressed()[0]
        
        for event in pygame.event.get():
            
            # determin if X was clicked, or Ctrl+W or Alt+F4 was used
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w and ctrl_held:
                    return
                if event.key == pygame.K_F4 and alt_held:
                    return
                if event.key == pygame.K_ESCAPE:
                    return
            
                # determine if a letter key was pressed
                if event.key == pygame.K_r:
                    if ctrl_held:
                        mode = 'red'
                    else:
                        position = pygame.mouse.get_pos()
                        geometricals.append(('rect', (*position, 50, 50), mode))
                elif event.key == pygame.K_c:
                    position = pygame.mouse.get_pos()
                    geometricals.append(('circ', position, 25, mode))

                elif event.key == pygame.K_g:
                    mode = 'green'
                elif event.key == pygame.K_b:
                    mode = 'blue'
                elif event.key == pygame.K_e:
                    if ctrl_held:
                        # mode = 'black'
                        points = []
                        geometricals = []
                    else:
                        mode = "black"

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and ctrl_held: # left click grows radius
                    radius = min(200, radius + 1)
                elif event.button == 3: # right click shrinks radius
                    radius = max(1, radius - 1)
            
            if event.type == pygame.MOUSEMOTION and lmouse_held:
                # if mouse moved, add point to list - just add coordinates to the general queue
                position = event.pos
                points = points + [(position, mode)]
                # points = points[-256:] # takes only the last -256
                
        screen.fill((0, 0, 0))
        
        # draw all points
        i = 0
        while i < len(points) - 1:
            drawLineBetween(screen, i, points[i][0], points[i + 1][0], radius, points[i][1])
            i += 1

        for geometry in geometricals:
            match geometry[0]:
                case 'rect':
                    pygame.draw.rect(screen, geometry[2], geometry[1], 0, 10)
                case 'circ':
                    pygame.draw.circle(screen, geometry[3], geometry[1], geometry[2])
            # geometry.draw(screen)

        pygame.display.flip()

        clock.tick(60)

# break down the logic 
def drawLineBetween(screen, index, start, end, width, color_mode):
    # print(start, end, color_mode)
    c1 = max(0, min(255, 2 * index - 256)) # the gradient effects
    c2 = max(0, min(255, 2 * index))
    
    if color_mode == 'blue':
        color = (c1, c1, c2)
    elif color_mode == 'red':
        color = (c2, c1, c1)
    elif color_mode == 'green':
        color = (c1, c2, c1)
    elif color_mode == 'black':
        color = (0, 0, 0)

    # takes the difference in coordinates between two adjacent indices
    dx = start[0] - end[0] 
    dy = start[1] - end[1]
    iterations = max(abs(dx), abs(dy))
    
    # iterate over the changed magnitude(step by step)
    for i in range(iterations):
        # progress = 1.0 * i / iterations
        progress = i / float(iterations)
        # left progess
        aprogress = 1 - progress
        x = int(aprogress * start[0] + progress * end[0]) # calculate the interpolated point    
        y = int(aprogress * start[1] + progress * end[1])
        pygame.draw.circle(screen, color, (x, y), width)

main()