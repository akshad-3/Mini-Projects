import pygame
from sys import exit
from pygame.locals import *
import random


def welcomescreen():
    playerx=int(SCREENWIDTH/5)
    playery=int((SCREENHIGHT - game_item['player'].get_height())/2)
    messagex=int((SCREENWIDTH - game_item['message'].get_width())/2)
    messagey=int(SCREENHIGHT * 0.13)
    basex=0
    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type==KEYDOWN and event.key==K_ESCAPE):
                pygame.quit()
                exit()
            elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                return
            else:
                screen.blit(game_item['background'],(0,0))
                screen.blit(game_item['player'],(playerx,playery))
                screen.blit(game_item['base'],(basex,540))
                screen.blit(game_item['message'],(messagex,messagey))
                #game_sound['menu'].play()
                pygame.display.update()
                clock.tick(60)
def maingame():
    score=0
    playerx=int(SCREENWIDTH/5)
    playery=int(SCREENHIGHT/2)
    basex=0
    
    newpipe1=getrandomepipe()
    newpipe2=getrandomepipe()
    
    upperpipe=[
        {'x':SCREENWIDTH+200,'y':newpipe1[0]['y']},
        {'x':SCREENWIDTH+200+(SCREENWIDTH/2),'y':newpipe2[0]['y']}
    ]
    lowerpipe=[
        {'x':SCREENWIDTH+200,'y':newpipe1[1]['y']},
        {'x':SCREENWIDTH+200+(SCREENWIDTH/2),'y':newpipe2[1]['y']}
    ]
    
    pipespeedx=-4
    pipespeedy=-9
    
    playerspeedY=-9
    playerMAXspeedY=10
    playerMINspeedY=-8

    playeraccY=1
    
    playerFLAPING=-8
    playerFLPPED=False
    
    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery > 0:
                    playerspeedY = playerFLAPING
                    playerFLPPED=True
                    game_sound['wing'].play()               
        crashing= isCollide(playerx,playery,upperpipe,lowerpipe)

        if crashing:
            return
        
        playerMID= playerx + game_item['player'].get_width()/2
        for pipe in upperpipe:
            pipeMID=pipe['x'] + game_item['pipe'][0].get_width()/2
            if pipeMID <= playerMID < pipeMID + 4:
                score+=1
                print(f"your score is {score}")
                game_sound['point'].play()
            #gamesound
        
        if playerspeedY < playerMAXspeedY and not playerFLPPED:
            playerspeedY+=playeraccY
            
        if playerFLPPED:
            playerFLPPED=False
        playerheight = game_item['player'].get_height()
        playery=playery + min(playerspeedY,540-playery - playerheight)

        for upipe , lpipe in zip(upperpipe,lowerpipe):
            upipe['x']+=pipespeedx
            lpipe['x']+=pipespeedx

        if 0<upperpipe[0]['x']<5:
            newpipe=getrandomepipe()
            upperpipe.append(newpipe[0])
            lowerpipe.append(newpipe[1])
        
        if upperpipe[0]['x'] < -game_item['pipe'][0].get_width():
            upperpipe.pop(0)
            lowerpipe.pop(0)
        
        screen.blit(game_item['background'],(0,0))
        for upipe , lpipe in zip(upperpipe,lowerpipe):
            screen.blit(game_item['pipe'][0],(upipe['x'],upipe['y']))
            screen.blit(game_item['pipe'][1],(lpipe['x'],lpipe['y']))
            
        
        screen.blit(game_item['base'],(basex,540))
        screen.blit(game_item['player'],(playerx,playery))
        myDigits = [int(x) for x in list(str(score))]
        width = 0
        for digit in myDigits:
            width += game_item['numbers'][digit].get_width()
        offset = (SCREENWIDTH - width)/2

        for digit in myDigits:
            screen.blit(game_item['numbers'][digit], (offset, SCREENHIGHT*0.12))
            offset += game_item['numbers'][digit].get_width()
        
        pygame.display.update()
        clock.tick(60)
            

def isCollide(playerx,playery,upperpipe,lowerpipe):
    if playery > 540-65 or playery<0:
        game_sound['die'].play()
        return True
    
    for pipe in upperpipe:
        pipeHight=game_item['pipe'][0].get_height()
        if (playery < pipeHight + pipe['y'] and abs(playerx - pipe['x']) < game_item['pipe'][0].get_width()):
            game_sound['die'].play()
            return True
    
    for pipe in lowerpipe:
        if (playery + game_item['player'].get_height() > pipe['y']) and abs(playerx - pipe['x']) < game_item['pipe'][0].get_width():
            game_sound['die'].play()
            return True
    return False
# def getrandomepipe():
#     pipeHight=game_item['pipe'][0].get_height()
#     offset = SCREENHIGHT/3
#     y2 = offset + random.randrange(0,int(SCREENHIGHT - game_item['base'].get_height() - 1.2 * offset))
#     pipex=SCREENWIDTH + 10
#     y1 = pipeHight - y2 + offset
#     pipe=[
#         {'x': pipex,'y': y1},
#         {'x':pipex,'y':y2}
#     ]
#     return pipe

def getrandomepipe():
    offset = SCREENHIGHT / 3  
    pipe_height = game_item['pipe'][0].get_height()
    base_height = game_item['base'].get_height()

    y2 = offset + random.randrange(0, int(SCREENHIGHT - base_height - 1.5 * offset))
    pipex = SCREENWIDTH + 10

   
    y1 = y2 - pipe_height - offset

    pipe = [
        {'x': pipex, 'y': y1},
        {'x': pipex, 'y': y2}   
    ]
    return pipe

SCREENWIDTH=801
SCREENHIGHT=603     
# GROUNDY=SCREENHIGHT * 0.8
game_sound={}
game_item={}
screen=pygame.display.set_mode((SCREENWIDTH,SCREENHIGHT))
player='bird.png'
background='background.png'
pipe='pipe.png'


pygame.init()
pygame.display.set_caption('Flappy bird')
clock=pygame.time.Clock()
test_font=pygame.font.Font('font.otf',70)

# game_item['number']=(
#     pygame.image.load('')
# )
game_item['numbers']=(
    pygame.transform.scale_by(pygame.image.load('0.png').convert_alpha(),0.5),
    pygame.transform.scale_by(pygame.image.load('1.png').convert_alpha(),0.5),
    pygame.transform.scale_by(pygame.image.load('2.png').convert_alpha(),0.5),
    pygame.transform.scale_by(pygame.image.load('3.png').convert_alpha(),0.5),
    pygame.transform.scale_by(pygame.image.load('4.png').convert_alpha(),0.5),
    pygame.transform.scale_by(pygame.image.load('5.png').convert_alpha(),0.5),
    pygame.transform.scale_by(pygame.image.load('6.png').convert_alpha(),0.5),
    pygame.transform.scale_by(pygame.image.load('7.png').convert_alpha(),0.5),
    pygame.transform.scale_by(pygame.image.load('8.png').convert_alpha(),0.5),
    pygame.transform.scale_by(pygame.image.load('9.png').convert_alpha(),0.5)
    
)
game_item['message']=pygame.image.load('message.png').convert_alpha()
game_item['base']=pygame.image.load('ground.png').convert_alpha()
game_item['pipe']=(
    pygame.transform.rotate(pygame.image.load(pipe).convert_alpha(),180),
    pygame.image.load(pipe).convert_alpha()
)

game_item['background']=pygame.image.load(background).convert()
game_item['player']=pygame.transform.scale_by(pygame.image.load(player).convert_alpha(),0.3)

game_sound['die'] = pygame.mixer.Sound('dry-fart.mp3')
game_sound['point'] = pygame.mixer.Sound('point.wav')
game_sound['wing'] = pygame.mixer.Sound('wing.mp3')
game_sound['menu'] = pygame.mixer.Sound('menu.mp3')

while True:
    welcomescreen()
    maingame()