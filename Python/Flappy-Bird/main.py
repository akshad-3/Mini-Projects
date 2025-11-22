import os
import sys
import pygame
from sys import exit
from pygame.locals import *
import random
def get_data_path():
    if getattr(sys, 'frozen', False):
        base_path = os.path.join(os.getenv('APPDATA'), "FlappyBirdClone")
    else:
        base_path = os.path.dirname(__file__)

    if not os.path.exists(base_path):
        os.makedirs(base_path)

    return base_path

HIGHSCORE_FILE = os.path.join(get_data_path(), "highscore.txt")

def load_highscore():
    try:
        with open(HIGHSCORE_FILE, "r") as f:
            return int(f.read())
    except:
        return 0

def save_highscore(score):
    with open(HIGHSCORE_FILE, "w") as f:
        f.write(str(score))

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
                game_sound['menu'].stop()
                return
            else:
                screen.blit(game_item['background'],(0,0))
                screen.blit(game_item['player'],(playerx,playery))
                screen.blit(game_item['base'],(basex,540))
                screen.blit(game_item['message'],(messagex,messagey))
                game_sound['menu'].play()
                pygame.display.update()
                clock.tick(60)
def gameover(score, best_score):

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type==KEYDOWN and event.key==K_ESCAPE):
                pygame.quit()
                exit()
            elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                return
        
        screen.blit(game_item['background'],(0,0))
        screen.blit(game_item['base'],(0,540))
        
        game_over_x = (SCREENWIDTH - game_item['Over'].get_width()) / 2 
        game_over_y = SCREENHIGHT * 0.34
        screen.blit(game_item['Over'], (game_over_x, game_over_y))
        
        score_text = test_font.render('Score :', True, (255, 255, 255))
        score_text_rect = score_text.get_rect(center=(SCREENWIDTH/4.5, SCREENHIGHT * 0.20))
        screen.blit(score_text, score_text_rect)
        
        myDigits = [int(x) for x in list(str(score))]
        width = sum([game_item['numbers'][digit].get_width() for digit in myDigits])
        offset = (SCREENWIDTH - width) / 2.3
        for digit in myDigits:
            screen.blit(game_item['numbers'][digit], (offset, SCREENHIGHT * 0.16))
            offset += game_item['numbers'][digit].get_width()
        
        best_text = test_font.render('Best :', True, (255, 255, 255))
        best_text_rect = best_text.get_rect(center=(SCREENWIDTH/1.4, SCREENHIGHT * 0.20))
        screen.blit(best_text, best_text_rect)
        
        bestDigits = [int(x) for x in list(str(best_score))]
        width = sum([game_item['numbers'][digit].get_width() for digit in bestDigits])
        offset = (SCREENWIDTH - width) / 1.1
        for digit in bestDigits:
            screen.blit(game_item['numbers'][digit], (offset, SCREENHIGHT * 0.16))
            offset += game_item['numbers'][digit].get_width()
        
        restart_text = test_font.render('Press SPACE', True, (255, 255, 255))
        restart_text_rect = restart_text.get_rect(center=(SCREENWIDTH/2, SCREENHIGHT * 0.79))
        screen.blit(restart_text, restart_text_rect)
        
        pygame.display.update()
        clock.tick(60)

def maingame(best_score):
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
            if score > best_score:
                best_score = score
            return score, best_score
        
        playerMID= playerx + game_item['player'].get_width()/2
        for pipe in upperpipe:
            pipeMID=pipe['x'] + game_item['pipe'][0].get_width()/2
            if pipeMID <= playerMID < pipeMID + 4:
                score+=1
                print(f"your score is {score}")
                game_sound['point'].play()
        
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
player='C:/Users/uchih/Desktop/Mini-Projects/Python/Flappy-Bird/bird.png'
background='C:/Users/uchih/Desktop/Mini-Projects/Python/Flappy-Bird/background.png'
pipe='C:/Users/uchih/Desktop/Mini-Projects/Python/Flappy-Bird/pipe.png'
Over='C:/Users/uchih/Desktop/Mini-Projects/Python/Flappy-Bird/Over.png '


pygame.init()
pygame.display.set_caption('Flappy bird')
clock=pygame.time.Clock()
test_font=pygame.font.Font('C:/Users/uchih/Desktop/Mini-Projects/Python/Flappy-Bird/font.otf',70)


game_item['numbers']=(
    pygame.transform.scale_by(pygame.image.load('C:/Users/uchih/Desktop/Mini-Projects/Python/Flappy-Bird/0.png').convert_alpha(),0.5),
    pygame.transform.scale_by(pygame.image.load('C:/Users/uchih/Desktop/Mini-Projects/Python/Flappy-Bird/1.png').convert_alpha(),0.5),
    pygame.transform.scale_by(pygame.image.load('C:/Users/uchih/Desktop/Mini-Projects/Python/Flappy-Bird/2.png').convert_alpha(),0.5),
    pygame.transform.scale_by(pygame.image.load('C:/Users/uchih/Desktop/Mini-Projects/Python/Flappy-Bird/3.png').convert_alpha(),0.5),
    pygame.transform.scale_by(pygame.image.load('C:/Users/uchih/Desktop/Mini-Projects/Python/Flappy-Bird/4.png').convert_alpha(),0.5),
    pygame.transform.scale_by(pygame.image.load('C:/Users/uchih/Desktop/Mini-Projects/Python/Flappy-Bird/5.png').convert_alpha(),0.5),
    pygame.transform.scale_by(pygame.image.load('C:/Users/uchih/Desktop/Mini-Projects/Python/Flappy-Bird/6.png').convert_alpha(),0.5),
    pygame.transform.scale_by(pygame.image.load('C:/Users/uchih/Desktop/Mini-Projects/Python/Flappy-Bird/7.png').convert_alpha(),0.5),
    pygame.transform.scale_by(pygame.image.load('C:/Users/uchih/Desktop/Mini-Projects/Python/Flappy-Bird/8.png').convert_alpha(),0.5),
    pygame.transform.scale_by(pygame.image.load('C:/Users/uchih/Desktop/Mini-Projects/Python/Flappy-Bird/9.png').convert_alpha(),0.5)
    
)
game_item['message']=pygame.image.load('C:/Users/uchih/Desktop/Mini-Projects/Python/Flappy-Bird/message.png').convert_alpha()
game_item['base']=pygame.image.load('C:/Users/uchih/Desktop/Mini-Projects/Python/Flappy-Bird/ground.png').convert_alpha()
game_item['pipe']=(
    pygame.transform.rotate(pygame.image.load(pipe).convert_alpha(),180),
    pygame.image.load(pipe).convert_alpha()
)

game_item['background']=pygame.image.load(background).convert()
game_item['player']=pygame.transform.scale_by(pygame.image.load(player).convert_alpha(),0.3)
game_item['Over']=pygame.transform.scale_by(pygame.image.load(Over).convert_alpha(),0.5)
game_sound['die'] = pygame.mixer.Sound('C:/Users/uchih/Desktop/Mini-Projects/Python/Flappy-Bird/die.mp3')
game_sound['point'] = pygame.mixer.Sound('C:/Users/uchih/Desktop/Mini-Projects/Python/Flappy-Bird/point.wav')
game_sound['wing'] = pygame.mixer.Sound('C:/Users/uchih/Desktop/Mini-Projects/Python/Flappy-Bird/wing.mp3')
game_sound['menu'] = pygame.mixer.Sound('C:/Users/uchih/Desktop/Mini-Projects/Python/Flappy-Bird/menu.mp3')
best_score = load_highscore()
while True:
    welcomescreen()
    score, best_score = maingame(best_score)
    save_highscore(best_score)
    gameover(score, best_score)