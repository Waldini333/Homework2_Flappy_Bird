import pygame
import time
import os
import random
import pytest
#pygame.font.init()
pygame.init()
from pygame.locals import *
#importing and creating the database:
from database import *

##########################################CONSTANTS########################################
#window size as constants
WIN_WIDTH = 500
WIN_HEIGHT = 800
#list of sprites
#loading the bird images, scale2x transforms than 2x bigger
BIRD_SPRITES = [pygame.transform.scale2x(pygame.image.load(os.path.join("sprites", "bird1.png"))),pygame.transform.scale2x(pygame.image.load(os.path.join("sprites", "bird2.png"))),pygame.transform.scale2x(pygame.image.load(os.path.join("sprites", "bird2.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("sprites", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("sprites", "base.png")))
#background
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("sprites", "bg.png")))

STAT_FONT = pygame.font.SysFont("comicsans", 50)
FONT = pygame.font.SysFont(None, 50)
FONT2 = pygame.font.SysFont(None, 30)

WHITE = (255, 255, 255)
BLACK = (  0,   0,   0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 180)
RED = (255,   0,   0)

#####PLAYERNAME
playername_text_input = ""

class Bird:
    SPRITES = BIRD_SPRITES
    MAX_ROTATION = 25 #degrees in which the bird goes up and down
    ROT_VELOCITY = 20
    ANIMATION_TIME = 5  #how fast sprites are reloaded

    def __init__(self, x, y):
        #starting position of bird
        self.x = x
        self.y = y
        self.tilt = 0 #how much the image is tilted (beginning should be flat)
        self.tick_count = 0 #physics
        self.velocity = 0 #Geschwindigkeit
        self.height = self.y #where is bird in y
        self.img_count = 0 #keeping track which sprite is shown (for animation)
        self.img = self.SPRITES[0] #starting image

    def jump(self):
        self.velocity = -10.5 #negative velocity because (0,0) is in the top left corner in pygame
        self.tick_count = 0 #keep track when last jump was
        self.height = self.y #where the bird jumped from

    def move(self):
        self.tick_count += 1 #frame tick (time tick)

        #Wurfparabel ohne luftwiderstand (bomb trajectory without air resistance)
        d = self.velocity*self.tick_count + 1.5 * self.tick_count**2

        if d >= 16: #velocity cap (terminal velocity)
            d = 16

        if d < 0: #fine tuning of jumping
            d -= 2

        self.y = self.y + d #changing y position of the bird

        #tilting the bird UPWARDS
        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
            #DOWNWARDS
            else:
                if self.tilt > -90:
                    self.tilt -= self.ROT_VELOCITY

    def draw(self, win):
        self.img_count += 1 #tick for while loop

        #Animation
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.SPRITES[0]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.SPRITES[1]
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.SPRITES[2]
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.SPRITES[1]
        elif self.img_count == self.ANIMATION_TIME*4 +1:
            self.img = self.SPRITES[0]
            self.img_count = 0

        if self.tilt <= -80:
            self.img = self.SPRITES[1]
            self.img_count = self.ANIMATION_TIME*2

        #rotating the image for tilting
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft = (self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    def get_mask(self): #hitmask
        return pygame.mask.from_surface(self.img)

class Pipe:
    GAP = 200
    VELOCITY = 5

    def __init__(self,x):
        self.x = x
        self.height = 0


        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True) #flip the pipeimage
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False  #if bird passed the pipes
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50,450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VELOCITY

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask() #create 2D hitmask of bird
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        #checks if bird mask collides with top or bottom mak using its offsets
        # if there is no collission both points will return None
        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        #if not None -> collision
        if t_point or b_point:
            return True

        return False

    #I dont want to lean myself too much out of the window but after I have done repeatedly research
    #on how to pytest pygame game logic, there was only scarce sources for it and the sources which I found
    #where not recommending stateless unit testing such as pytest for testing game logic which does things on
    #spreaded out over multiple frames neted in loops. Summarized I would have to program a pytest event
    #for my game logic which simulates user input and sends back the results. But I was not able to manage that
    #properly.
    #https://stackoverflow.com/questions/63341547/how-to-inject-pygame-events-from-pytest
    #https://www.reddit.com/r/pygame/comments/nlc8b8/anyone_knows_a_good_pytest_tutorial_for_pygame/

    def test_initBird(self):
        bird = Bird(100, 100)
        bird.jump
        bird.move

class Base:
    VELOCITY = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self,y):
        self.y = y
        #two x values for looping bases
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VELOCITY
        self.x2 -= self.VELOCITY

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def draw_window(win, bird, pipes, base, score):
    win.blit(BG_IMG, (0,0))
    for pipe in pipes:
        pipe.draw(win)

    text = STAT_FONT.render("Score: " + str(score), 1,(255,255,255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    base.draw(win)

    bird.draw(win)
    pygame.display.update()

def main():
    bird = Bird(200,350)
    base = Base(730)
    pipes = [Pipe(600)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    score = 0

    run = True
    while run:
        clock.tick(30) #at most 30 ticks every second
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                run = False
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                bird.jump()
        bird.move()
        add_pipe = False
        rem = []
        for pipe in pipes:
            if pipe.collide(bird):
                run = False
                #DATABASE
                currentrun = Player(username = playername_text_input,score=score)
                db.session.add(currentrun)
                db.session.commit()
                results_query = Player.query.all()
                print(results_query[-1].username,results_query[-1].score)
                main()

            if pipe.x + pipe.PIPE_TOP.get_width() < 0: #if pipe is off the screen create a new one
                rem.append(pipe)

            if not pipe.passed and pipe.x < bird.x: #checking if bird passe the pipe
                pipe.passed = True
                add_pipe = True

            pipe.move()

        if add_pipe:
            score += 1
            pipes.append(Pipe(600))

        for r in rem: #remove looped pipes
            pipes.remove(r)

        if bird.y + bird.img.get_height() >= 730: #Bird collides with floor
            run = False
            #DATABASE
            currentrun = Player(username=playername_text_input, score=score)
            db.session.add(currentrun)
            db.session.commit()
            results_query = Player.query.all()
            print(results_query[-1].username, results_query[-1].score)
            main()


        base.move()
        draw_window(win, bird, pipes, base, score)

    pygame.quit()
    quit()

#################################################INTERFACE###################################

def draw_text(text, font, color, surface, x, y):
    #create text surface (object) with the actual string and its color value
    textobj = font.render(text, True, color)
    #get_rect() does store the coordinates of the textobject which is by default (0,0)
    textrect = textobj.get_rect()
    #altering the coordinates starting from top left
    textrect.topleft = (x,y)
    #place the textobject on the surface and its exact position
    surface.blit(textobj, textrect)

#renders multiline text
def blit_text(surface, text, pos, font, color=pygame.Color('white')):
    words = [word.split('/') for word in text.splitlines()]  # 2D array where each row is a list of words.
    space = font.size(' ')[0]  # The width of a space.
    max_width, max_height = surface.get_size()
    x, y = pos
    for line in words:
        for word in line:
            word_surface = font.render(word, 0, color)
            word_width, word_height = word_surface.get_size()
            if x + word_width >= max_width:
                x = pos[0]  # Reset the x.
                y += word_height  # Start on new row.
            surface.blit(word_surface, (x, y))
            x += word_width + space
        x = pos[0]  # Reset the x.
        y += word_height  # Start on new row.



def menu():
    run = True

    click = False
    while run:

        mx, my = pygame.mouse.get_pos()

        win.fill(BLACK)

        draw_text('Flappy Main menu', FONT, (255,255,255), win, 20, 20)


        button_1 = pygame.Rect(50,100,200,50)
        button_2 = pygame.Rect(50,200,200,50)
        if button_1.collidepoint((mx,my)):
            if click:
                click = False
                menu_start_game()
        if button_2.collidepoint((mx, my)):
            if click:
                click = False
                menu_stats()
        pygame.draw.rect(win, (255,0,0), button_1)
        pygame.draw.rect(win, (0, 0, 255), button_2)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                run = False

            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True

        draw_text('Start game', FONT2, (255, 255, 255), win, 105, 115)
        draw_text('Stats', FONT2, (255, 255, 255), win, 125, 215)

        pygame.display.update()

def menu_start_game():
    run = True
    global playername_text_input

    while run:

        win.fill(BLACK)
        draw_text('Flappy Start game', FONT, (255,255,255), win, 20, 20)
        draw_text('Please enter your Username and hit ENTER', FONT2, (255, 255, 255), win, 60, 60)
        draw_text(playername_text_input, FONT, (255, 255, 255), win, 100, 100)
        #pygame.draw.line(win, BLUE, (60, 60), (120, 60), 4)

        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_BACKSPACE:
                    #when Backspace is hit username gets set to new user name from index 0 to -1
                    playername_text_input = playername_text_input[0:-1]
                elif event.key == K_RETURN or event.key == K_KP_ENTER:
                    if len(playername_text_input) != 0:
                        main()
                    else:
                        pass
                else:
                    playername_text_input += event.unicode

        pygame.display.update()

def menu_stats():
    run = True

    results_query = Player.query.all()
    temp = ""
    for i in results_query:
        #Somehow do a formatting
        temp += i.username
        temp += ":"
        temp += str(i.score)
        temp += "/"
        print(i.username, i.score)

    while run:

        win.fill(BLACK)
        draw_text('Flappy Stats', FONT, (255,255,255), win, 20, 20)

        blit_text(win,temp,(300,25),FONT2)



        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    run = False


        pygame.display.update()

pygame.display.set_caption("Flappy Bird")

win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT), 0, 32)

#START
menu()





