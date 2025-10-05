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
text_rect=text_surfece.get_rect(center=(368,50))

flower_surface=pygame.image.load('Game/flower.png').convert_alpha()
flower_surface = pygame.transform.scale_by(flower_surface, 0.09)  
flower_rect=flower_surface.get_rect(bottomright=(600,356))

cat_surface=pygame.image.load('Game/cat.png')
cat_surface=pygame.transform.scale_by(cat_surface,0.09)
cat_rect=cat_surface.get_rect(topleft=(30,356))
cat_gravity=0



while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if (cat_rect.bottom==370):
            if event.type == pygame.KEYDOWN:
                if event.key ==pygame.K_SPACE :
                    cat_gravity=-20
            if event.type==pygame.MOUSEBUTTONDOWN:
                if cat_rect.collidepoint(pygame.mouse.get_pos()):
                    cat_gravity=-20
            
    
    screen.blit(back_surface,(0,0))
    screen.blit(ground_surface,(0,356))
    pygame.draw.rect(screen,'orange',text_rect,0,20)
    pygame.draw.rect(screen,'orange',text_rect,5,20)
    screen.blit(text_surfece,text_rect)
    #pygame.draw.line(screen,'black',(0,0),pygame.mouse.get_pos())
    
    flower_rect.x-=4
    if flower_rect.right<=0:flower_rect.left=736
    screen.blit(flower_surface,flower_rect)
    
    cat_gravity+=1
    cat_rect.y  += cat_gravity
    if cat_rect.bottom>=356:cat_rect.bottom=356
    screen.blit(cat_surface,cat_rect)
    
    if flower_rect.colliderect(cat_rect):
        pygame.quit()
        exit()
    
    pygame.display.update()
    clock.tick(60)
    
