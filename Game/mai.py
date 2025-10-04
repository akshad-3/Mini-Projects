import pygame
from sys import exit

pygame.init()
screen=pygame.display.set_mode((736,420))
pygame.display.set_caption('First game')
clock=pygame.time.Clock()
test_font=pygame.font.Font('Game/Pixel Game.otf',80)


back_surface=pygame.image.load('Game/clouds.jpg').convert()

ground_surface=pygame.image.load('Game/ground.jpg').convert()

text_surfece=test_font.render('First Game',False,'White')

flower_surface=pygame.image.load('Game/flower.png').convert_alpha()
flower_surface = pygame.transform.scale_by(flower_surface, 0.09)  
flower_rect=flower_surface.get_rect(bottomright=(600,370))

cat_surface=pygame.image.load('Game/cat.png')
cat_surface=pygame.transform.scale_by(cat_surface,0.09)
cat_rect=cat_surface.get_rect(topleft=(0,280))




while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.MOUSEMOTION:
            if cat_rect.collidepoint(event.pos):print('collide')
            
    
    screen.blit(back_surface,(0,0))
    screen.blit(ground_surface,(0,356))
    screen.blit(text_surfece,(230,50))
    
    flower_rect.x-=4
    if flower_rect.right<=0:flower_rect.left=736
    screen.blit(flower_surface,flower_rect)
    
    screen.blit(cat_surface,cat_rect)

    pygame.display.update()
    clock.tick(60)
    
