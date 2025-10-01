import pygame
from sys import exit

pygame.init()
screen=pygame.display.set_mode((736,420))
clock=pygame.time.Clock()
back_surface=pygame.image.load('Game/clouds.jpg')
tile_surface=pygame.image.load('Game/download.jpg')



while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    
    screen.blit(back_surface,(0,0))
    screen.blit(tile_surface,(0,355))

    pygame.display.update()
    clock.tick(60)
