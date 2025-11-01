import pygame
from sys import exit
from random import randint


def display_score():
    current_time = int(pygame.time.get_ticks()/1000)-start_time
    score_sur=test_font.render(f'SCORE :{current_time}',False,(64,64,64))
    score_rect=score_sur.get_rect(center = (368,50))
    screen.blit(score_sur,score_rect)
    return current_time

def obstacle_movment(obstacle_list):
    if obstacle_list:
        for obstacle_rect in obstacle_list:
            obstacle_rect.x -= 5
            
# def display_score():
#     if flower_rect.bottom==40:
#         score+=1
#         score_sur = test_font.render(f'{score}',False,(64,64,64))
#         score_rect=score_sur.get_rect(center = (368,50))
#         screen.blit(score_sur,score_rect)
#     else:
#         screen.blit(score_sur,score_rect)
        
    
    
pygame.init()
screen=pygame.display.set_mode((736,420))
pygame.display.set_caption('First game')
clock=pygame.time.Clock()
test_font=pygame.font.Font('Python/Game/Pixel Game.otf',80)
game_running= True
start_time = 0
score=0


back_surface=pygame.image.load('Python/Game/clouds.jpg').convert()

ground_surface=pygame.image.load('Python/Game/ground.jpg').convert()

# text_surfece=test_font.render('First Game',False,'White')
# text_rect=text_surfece.get_rect(center=(368,50))

flower_surface=pygame.image.load('Python/Game/flower.png').convert_alpha()
flower_surface = pygame.transform.scale_by(flower_surface, 0.09)  
flower_rect=flower_surface.get_rect(bottomright=(600,356))

obstacle_rect_list=[]

cat_surface=pygame.image.load('Python/Game/cat.png')
cat_surface=pygame.transform.scale_by(cat_surface,0.09)
cat_rect=cat_surface.get_rect(topleft=(30,356))
cat_gravity=0

intro_surface=pygame.image.load('python/Game/introcat.png')
intro_surface=pygame.transform.scale_by(intro_surface,0.08)
intro_rect=intro_surface.get_rect(center=(360,180))

Gover_sur=test_font.render('Game over',False,'black')
Gover_rect=Gover_sur.get_rect(center =(360,60))

# Bscore_sur=test_font.render(f'Best Score :{score}',False,'black')
# Bscore_rect=Bscore_sur.get_rect(center =(360,320))
obstacle_timer=pygame.USEREVENT + 1
pygame.time.set_timer(obstacle_timer,900)



while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if game_running:
            if (cat_rect.bottom==356):
                if event.type == pygame.KEYDOWN:
                    if event.key ==pygame.K_SPACE :
                        cat_gravity=-20
                        #its for moving the cat upward by -20
                if event.type==pygame.MOUSEBUTTONDOWN:
                    if cat_rect.collidepoint(pygame.mouse.get_pos()):
                        cat_gravity=-20
        else:
            if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                game_running=True
                flower_rect.left=736
                start_time=int(pygame.time.get_ticks()/1000)
        if event.type == obstacle_timer and game_running:
            obstacle_rect_list.append(flower_surface.get_rect(bottomright=(randint(900,1100),300)))
        
        
            
    if game_running:
        screen.blit(back_surface,(0,0))
        screen.blit(ground_surface,(0,356))
        # pygame.draw.rect(screen,'orange',text_rect,0,20)
        # pygame.draw.rect(screen,'orange',text_rect,5,20)
        #screen.blit(text_surfece,text_rect)
        #pygame.draw.line(screen,'black',(0,0),pygame.mouse.get_pos())
        score=display_score()
        
        flower_rect.x-=6                 
        if flower_rect.right<=0:flower_rect.left=736
        screen.blit(flower_surface,flower_rect)
        
        cat_gravity+=1
        cat_rect.y  += cat_gravity
        if cat_rect.bottom>=356:cat_rect.bottom=356
        screen.blit(cat_surface,cat_rect)
        obstacle_movment(obstacle_rect_list)

        if flower_rect.colliderect(cat_rect):
            game_running=False
        
    else:
        screen.fill((237,166,43))
        screen.blit(intro_surface,intro_rect)
        
        screen.blit(Gover_sur,Gover_rect)
        
        Bscore_sur=test_font.render(f'Best Score :{score}',False,'black')
        Bscore_rect=Bscore_sur.get_rect(center =(360,320))
        screen.blit(Bscore_sur,Bscore_rect)
        
        
        
        
    
    pygame.display.update()
    clock.tick(60)
