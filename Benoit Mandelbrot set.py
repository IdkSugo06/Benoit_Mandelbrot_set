import pygame
import time
import threading

pygame.init()
tempScreenDim = (1300,1300)
screenInfo = {
    "screenInstance" : pygame.display.set_mode(tempScreenDim),
    "screenDim" : tempScreenDim,
    "planeDim" : ((-2,2),(2,-2)), #keep the top left point and the bottom right
    "coloreSfondo" : (0,0,0),

    "drawInfo" : {
        "passo" : [1,1]
    }
}
processingInfo = {
    "maxIteration" : 150,
    "maxColor" : (255,255,255)
}

def aggiornaScreenInfo(planeDim):
    screenInfo["planeDim"] = planeDim.copy()
    screenInfo["drawInfo"]["passo"][0] = (planeDim[1][0] - planeDim[0][0]) / screenInfo["screenDim"][0]
    screenInfo["drawInfo"]["passo"][1] = (planeDim[1][1] - planeDim[0][1]) / screenInfo["screenDim"][1]

def color(i):
    global processingInfo
    i = (i / processingInfo["maxIteration"])
    r = 1-4*(-0.5+i)*(-0.5+i)#min(max(i**3,0),1)
    g = 1-(1-i)*(1-i)#min(max(1-(4*i-4)**3,0),1)
    b = (1-i)*(1-i)#min(max(i**2,0),1)
    return (processingInfo["maxColor"][0] * r, processingInfo["maxColor"][1] * g, processingInfo["maxColor"][2] * b)

def iterazione(nc, c):
    return [nc[0] * nc[0] - nc[1] * nc[1] + c[0], 2 * nc[0] * nc[1] + c[1]]

def provaPerPixel(nc):
    global processingInfo
    global screenInfo
    c = nc.copy()
    colore = (255,255,255)
    for i in range(processingInfo["maxIteration"]):
        nc = iterazione(nc, c)
        if nc[0] * nc[0] + nc[1] * nc[1] > 16:
            colore = color(i)
            break
    return colore
    

def provaPerRiga(xStart, xEnd, y, ImN):
    global screenInfo
    ReNAttuale = screenInfo["planeDim"][0][0]
    passo = screenInfo["drawInfo"]["passo"][0]
    diff = (int(xEnd/2) - xStart)
    t = threading.Thread(target = provaPerRiga_secondaMetà, args = [int(xEnd/2),xEnd,y,ImN,ReNAttuale + passo * diff,passo])
    t.start()
    for x in range(diff):
        screenInfo["screenInstance"].set_at((x, y), provaPerPixel([ReNAttuale,ImN]))
        ReNAttuale += passo
    pygame.display.update()

def provaPerRiga_secondaMetà(xStart, xEnd, y, ImN, ReNAttuale, passo):
    global screenInfo
    for x in range(xStart, xEnd):
        screenInfo["screenInstance"].set_at((x, y), provaPerPixel([ReNAttuale,ImN]))
        ReNAttuale += passo
    pygame.display.update()
    

screenInfo["screenInstance"].fill(screenInfo["coloreSfondo"])
aggiornaScreenInfo([(-2,2),(2,-2)])
zoom = 0.1
resolutionUpdate = 30
mousePos = (0,0)
parallelizzato = True

premuto = True
running = True
while running:
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        if event.type == pygame.KEYDOWN:
            if event.key==pygame.K_e or event.key==pygame.K_q:
                premuto = True
                mousePos = pygame.mouse.get_pos()
                pi = screenInfo["planeDim"]
                nuovoPuntoCentrale = [mousePos[0] / screenInfo["screenDim"][0], mousePos[1] / screenInfo["screenDim"][1]] #da 0 a 1
                nuovoPuntoCentrale = [nuovoPuntoCentrale[0] * (pi[1][0] - pi[0][0]) + pi[0][0], nuovoPuntoCentrale[1] * (pi[1][1] - pi[0][1]) + pi[0][1]]

                
                if event.key==pygame.K_e:
                    planeWidth = (pi[1][0] - pi[0][0]) * zoom / 2
                    planeHeight = (pi[1][1] - pi[0][1]) * zoom / 2
                    pi = [[nuovoPuntoCentrale[0] - planeWidth, nuovoPuntoCentrale[1] - planeHeight],[nuovoPuntoCentrale[0] + planeWidth, nuovoPuntoCentrale[1] + planeHeight]]
                    aggiornaScreenInfo(pi)
                if event.key==pygame.K_q:
                    planeWidth = (pi[1][0] - pi[0][0]) * (1/zoom) / 2
                    planeHeight = (pi[1][1] - pi[0][1]) * (1/zoom) / 2
                    pi = [[nuovoPuntoCentrale[0] - planeWidth, nuovoPuntoCentrale[1] - planeHeight],[nuovoPuntoCentrale[0] + planeWidth, nuovoPuntoCentrale[1] + planeHeight]]
                    aggiornaScreenInfo(pi)

            if event.key==pygame.K_k:
                processingInfo["maxIteration"] -= int(processingInfo["maxIteration"] * resolutionUpdate / 100)
                premuto = True    
            if event.key==pygame.K_l:
                processingInfo["maxIteration"] += int(processingInfo["maxIteration"] * resolutionUpdate / 100)
                premuto = True
            
                
    if premuto:
        premuto = False
        start = time.perf_counter()

        if parallelizzato:
            threads = [threading.Thread(target=provaPerRiga, args = [0,screenInfo["screenDim"][0],y,screenInfo["planeDim"][0][1] + screenInfo["drawInfo"]["passo"][1] * y]) for y in range(screenInfo["screenDim"][1])]
            [thread.start() for thread in threads]
            [thread.join() for thread in threads]
        else:
            for y in range(screenInfo["screenDim"][1]):
                provaPerRiga(0,screenInfo["screenDim"][0],y,screenInfo["planeDim"][0][1] + screenInfo["drawInfo"]["passo"][1] * y)

        finish = time.perf_counter()
        print(finish - start)
