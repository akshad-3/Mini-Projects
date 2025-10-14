import pygame
from sys import exit
from pygame.locals import *
import random


def welcomescreen():
    playerx=int(SCREENWIDTH/5)
    playery=int((SCREENHIGHT - game_sprites['player'].get_height())/2)
    messagex=int((SCREENWIDTH - game_sprites['message'].get_width())/2)
    messagey=int(SCREENHIGHT * 0.13)
    basex=0
    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type==KEYDOWN and event.key==K_ESCAPE):
                pygame.quit()
                exit()
            elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == k_UP):
                return
            else:
                screen.blit(game_sprites['background'],(0,0))
                screen.blit(game_sprites['player'],(playerx,playery))
                screen.blit(game_sprites['base'],(basex,540))
                screen.blit(game_sprites['message'],(messagex,messagey))
                pygame.display.update()
                clock.tick(60)
SCREENWIDTH=801
SCREENHIGHT=603     
# GROUNDY=SCREENHIGHT * 0.8
game_sound={}
game_sprites={}
screen=pygame.display.set_mode((SCREENWIDTH,SCREENHIGHT))
player='bird.png'
background='background.png'
pipe='pipe.png'


pygame.init()
pygame.display.set_caption('Flappy bird')
clock=pygame.time.Clock()
test_font=pygame.font.Font('font.otf',70)

# game_sprites['number']=(
#     pygame.image.load('')
# )
game_sprites['message']=pygame.image.load('message.png').convert_alpha()
game_sprites['base']=pygame.image.load('ground.png').convert_alpha()
game_sprites['pipe']=(
    pygame.transform.rotate(pygame.image.load(pipe).convert_alpha(),180),
    pygame.image.load(pipe).convert_alpha()
)

game_sprites['background']=pygame.image.load(background).convert()
game_sprites['player']=pygame.transform.scale_by(pygame.image.load(player).convert_alpha(),0.2)


while True:
    welcomescreen()