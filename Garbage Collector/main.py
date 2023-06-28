import pygame
import random
import sys
import os
import numpy as np
from os import listdir
from os.path import isfile, join
from houses import *
import time

pygame.init()

pygame.display.set_caption('Garbage Collector')

WIDTH, HEIGHT = 700, 600
FPS = 60
COUNT = 0
current_garbage_pos = []
current_garbage_val = []
city_tot_garbage = 0
city_garbage_left = 0
garbage_removed_pos = []
messages = ["Metro Vancouver generates 3,490,425 tonnes of solid waste each year",
            "In 2019 Vancouver, each person was responsible for producing 1400 kg per person ",
            "Spoiled and uneaten food represents 25% of BC's waste, the most common form of waste",
            "Landfills are responsible for 5% of all greenhouse gas emmissions, (methane)",
            "In Metro Vancouver, 25% of waste gets recycled and 75% gets disposed of",
            "Largest component of garbage: organics (38%), paper (16%), plastic and household (15%)",
            "Largest component of recycling: paper (53%), cardboard (24%), glass",
            "Vancouver set a goal to divert its disposal by 80% by 2020 and got 64% diversion",
            "In 2018 82 million single-use cups were thrown in the garbage in Vancouver alone",
            "In 2016, textiles are 5% of the region's waste, to about 40,000 tonnes per year",
            "Less than 1% of disposed clothing gets recycled into new clothing"]
full = False
win = 800
game_pause = False

info_surface = pygame.image.load('Assets/info_icon.png')
info = pygame.transform.scale(info_surface, (30, 30))

instructions_surface = pygame.image.load('Assets/instructions.png')
instructions = pygame.transform.scale(instructions_surface, (60, 60))

class Truck(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        truck_surface = pygame.image.load('Assets/truck.png')
        self.truck = pygame.transform.scale(truck_surface, (125, 125))


        self.east = 1
        self.west = 3
        self.north = 4
        self.south = 2
        self.x = 475
        self.y = 500
        self.vel = 2
        self.truck_state = self.east
        self.image = self.truck
        self.rect = pygame.Rect(self.x,self.y,150,150)
        self.garbage_val = 0
        self.tot_garbage = 0

    def do_turn(self):
        keys = pygame.key.get_pressed()
        if self.truck_state == self.east:
            if keys[pygame.K_LEFT]:
                self.truck = pygame.transform.rotate(self.truck, 90)
                self.truck_state = self.north
            elif keys[pygame.K_RIGHT]:
                self.truck = pygame.transform.rotate(self.truck, -90)
                self.truck_state = self.south
        elif self.truck_state == self.south:
            if keys[pygame.K_LEFT]:
                self.truck = pygame.transform.rotate(self.truck, 90)
                self.truck_state = self.east
            elif keys[pygame.K_RIGHT]:
                self.truck = pygame.transform.rotate(self.truck, -90)
                self.truck_state = self.west
        elif self.truck_state == self.north:
            if keys[pygame.K_LEFT]:
                self.truck = pygame.transform.rotate(self.truck, 90)
                self.truck_state = self.west
            elif keys[pygame.K_RIGHT]:
                self.truck = pygame.transform.rotate(self.truck, -90)
                self.truck_state = self.east
        elif self.truck_state == self.west: 
            if keys[pygame.K_LEFT]:
                self.truck = pygame.transform.rotate(self.truck, 90)
                self.truck_state = self.south
            elif keys[pygame.K_RIGHT]:
                self.truck = pygame.transform.rotate(self.truck, -90)
                self.truck_state = self.north
        

    def do_movement(self):

        keys = pygame.key.get_pressed()
        if self.truck_state == self.east:
            if keys[pygame.K_UP]:
                self.rect.x += self.vel
            elif keys[pygame.K_DOWN]:
                self.rect.x -= self.vel
        elif self.truck_state == self.south:
            if keys[pygame.K_UP]:
                self.rect.y += self.vel
            elif keys[pygame.K_DOWN]:
                self.rect.y -= self.vel
        elif self.truck_state == self.west: 
            if keys[pygame.K_UP]:
                self.rect.x -= self.vel
            elif keys[pygame.K_DOWN]:
                self.rect.x += self.vel
        elif self.truck_state == self.north:
            if keys[pygame.K_UP]:
                self.rect.y -= self.vel
            elif keys[pygame.K_DOWN]:
                self.rect.y += self.vel 
    
    def update_truck(self, window):
        window.blit(self.truck, (self.rect.x, self.rect.y))
    
    def is_near(self, pos):
        x = pos[0]
        y = pos[1]
        rectx = self.rect.x
        recty = self.rect.y

        if x-rectx < 60 and x-rectx > -60:
            if y-recty < 75 and y-recty > -10:
                return True
            else:
                return False
        else:
            return False
        
    def display(self, window):
        global full

        percent_num = (self.garbage_val*100)//600
        if percent_num >= 100:
            percent_num = 100
            full = True
        else:
            full = False

        percent = str(percent_num) + "%"
        font = pygame.font.SysFont("Arial", 24)
        txt = font.render(percent, True, (0,0,0))
        str_cgl = str(city_garbage_left)
        garbage_left_txt = font.render("Garbage Left: " + str_cgl, True, (0,0,0))
        str_tg = str(city_tot_garbage)
        tot_garbage_txt = font.render("Total Garbage: " + str_tg, True, (0,0,0))
        window.blit(txt,(220,560))
        window.blit(garbage_left_txt, (70, 530))
        window.blit(tot_garbage_txt, (70, 500))
    
    def dump(self):
        if self.rect.x >= 425 and self.rect.y >= 450:
            self.garbage_val = 0
        

#####

class Garbage(pygame.sprite.Sprite):
    
    def __init__(self, window, pos):
        global city_tot_garbage, city_garbage_left

        super().__init__()
        gar_surf = pygame.image.load('Assets/Garbage.png')
        self.image = pygame.transform.scale(gar_surf, (75,75))
        window.blit(self.image, pos)
        self.rect = self.image.get_rect(topleft = pos)
        self.pos = pos

def select_garbage():
    global garbage_pos

    num = random.randint(0, 23)

    return garbage_pos[num]

def get_map():
    road_surface = pygame.image.load('Assets/Road.png')
    road = pygame.transform.scale(road_surface, (700, 650))

    grass_surface = pygame.image.load('Assets/grass.png')
    grass = pygame.transform.scale(grass_surface, (700, 650))

    return road, grass

def draw(window, road, grass, info, instructions):
    text_surf = pygame.image.load('Assets/truck_cap_text.png')
    text = pygame.transform.scale(text_surf, (300,300))
    window.blit(grass, (0,0))
    window.blit(road, (0,0))
    window.blit(text, (-30,425))
    window.blit(info, (660, 20))
    window.blit(instructions, (650, 45))

purple = (221, 160, 221)

def collision_checks(truck, garbage, window):
    global current_garbage_pos, city_garbage_left, garbage_removed_pos
    garbage_removed_pos.clear()
    coll_sprite = pygame.sprite.spritecollide(truck, garbage, False)
    for i in coll_sprite:
        if i.pos in current_garbage_pos:
            if truck.is_near(i.pos):
                if not full:
                    index = current_garbage_pos.index(i.pos)
                    truck.garbage_val += current_garbage_val[index]
                    truck.tot_garbage += current_garbage_val[index]
                    city_garbage_left -= current_garbage_val[index]
                    del current_garbage_val[index]
                    del current_garbage_pos[index]
                    garbage_removed_pos.append(i.pos)
                if full:
                    sign = pygame.image.load('Assets/sign.png')
                    window.blit(sign, (0,0))
class text():
    def __init__(self):
        global window
        self.font = pygame.font.SysFont('Arial', 20)
        self.window = window
            
    def rectangle(self):
        self.rect = pygame.draw.rect(self.window, (purple), (190, 145, 350, 350), 0)
    def text_1(self):
        self.window.blit(self.font.render('Metro Vancouver generates 3,490,425', True, (0, 0, 0)), (225, 175))
        self.window.blit(self.font.render('tonnes of solid waste each year.', True, (0, 0, 0)), (225, 215))
        self.window.blit(self.font.render('In 2019 Vancouver, each person', True, (0, 0, 0)), (225, 255))
        self.window.blit(self.font.render('was responsible for producing 1400 kg', True, (0, 0, 0)), (225, 295))
        self.window.blit(self.font.render('per person. Spoiled and uneaten food', True, (0, 0, 0)), (225, 335))
        self.window.blit(self.font.render("represents 25% of BC's waste, the most", True, (0, 0, 0)), (225, 375))
        self.window.blit(self.font.render('common form of waste', True, (0, 0, 0)), (225, 415))

    def text_2(self):
        self.window.blit(self.font.render('Landfills are responsible for 5% of', True, (0, 0, 0)), (225, 175))
        self.window.blit(self.font.render('all greenhouse gas emmissions, (methane).', True, (0, 0, 0)), (225, 215))
        self.window.blit(self.font.render('In Metro Vancouver, 25% of waste', True, (0, 0, 0)), (225, 255))
        self.window.blit(self.font.render('gets recycled and 75% gets disposed of.', True, (0, 0, 0)), (225, 295))
        self.window.blit(self.font.render('Largest component of garbage: ', True, (0, 0, 0)), (225, 335))
        self.window.blit(self.font.render('organics (38%), paper (16%),', True, (0, 0, 0)), (225, 375))
        self.window.blit(self.font.render('plastic and household (15%).', True, (0, 0, 0)), (225, 415))
    def text_3(self):
        self.window.blit(self.font.render('Largest component of recycling:', True, (0, 0, 0)), (225, 175))
        self.window.blit(self.font.render('paper (53%), cardboard (24%), glass.', True, (0, 0, 0)), (225, 215))
        self.window.blit(self.font.render('Vancouver set a goal to divert its', True, (0, 0, 0)), (225, 255))
        self.window.blit(self.font.render('disposal by 80% by 2020 and got 64%', True, (0, 0, 0)), (225, 295))
        self.window.blit(self.font.render('diversion. In 2018 82 million single-use', True, (0, 0, 0)), (225, 335))
        self.window.blit(self.font.render('cups were thrown in the garbage in', True, (0, 0, 0)), (225, 375))
        self.window.blit(self.font.render('Vancouver alone.', True, (0, 0, 0)), (225, 415))
    def text_4(self):
        self.window.blit(self.font.render("In 2016, textiles are 5% of the region's", True, (0, 0, 0)), (225, 175))
        self.window.blit(self.font.render('waste, to about 40,000 tonnes per year. ', True, (0, 0, 0)), (225, 215))
        self.window.blit(self.font.render('Less than 1% of disposed clothing gets', True, (0, 0, 0)), (225, 255))
        self.window.blit(self.font.render('recycled into new clothing. Metro', True, (0, 0, 0)), (225, 295))
        self.window.blit(self.font.render('Vancouver is responsible for disposing', True, (0, 0, 0)), (225, 335))
        self.window.blit(self.font.render('of the waste generated by residents and', True, (0, 0, 0)), (225, 375))
        self.window.blit(self.font.render('businesses in the region.', True, (0, 0, 0)), (225, 415))
    def text_5(self):
        self.window.blit(self.font.render(random.choice(messages), True, (0, 0, 0)), (10, 350))
    def text_6(self):
        self.window.blit(self.font.render('Hello! Welcome to Garbage Collector!', True, (0, 0, 0)), (225, 175))
        self.window.blit(self.font.render('You, the player are using the truck', True, (0, 0, 0)), (225, 225))
        self.window.blit(self.font.render('to collect garbage bags that each house is', True, (0, 0, 0)), (225, 275))
        self.window.blit(self.font.render('producing. Be careful...if the truck capacity', True, (0, 0, 0)), (225, 325))
        self.window.blit(self.font.render('reaches 100%, then you have to dump its', True, (0, 0, 0)), (225, 375))
        self.window.blit(self.font.render('contents into the landfill.', True, (0, 0, 0)), (225, 425))
    def text_7(self):
        self.window.blit(self.font.render('To move the truck, use the right', True, (0, 0, 0)), (225, 175))
        self.window.blit(self.font.render('and left arrow keys to turn and use', True, (0, 0, 0)), (225, 225))
        self.window.blit(self.font.render('the up and down arrow keys to move', True, (0, 0, 0)), (225, 275))
        self.window.blit(self.font.render('forward and backward.', True, (0, 0, 0)), (225, 325))


def win_chk(window, win):
    global city_garbage_left, city_tot_garbage, game_pause
    if city_tot_garbage - city_garbage_left >= win:
        win_surf = pygame.image.load('Assets/Win_Txt.png')
        win = pygame.transform.scale(win_surf, (700, 600))
        window.blit(win, (0,0))
        game_pause = True

def lose(window):
    global city_garbage_left, game_pause
    if city_garbage_left >= 500:
        lose_surf = pygame.image.load('Assets/lose_Txt.png')
        lose = pygame.transform.scale(lose_surf, (700, 600))
        window.blit(lose, (0,0))
        game_pause = True

def bound(x,y):
    if x>= 610:
        x = 610
    if y >= 515:
        y = 515
    if x < -40:
        x = -40
    if y <= -50:
        y = -50
    
    return x,y

window = pygame.display.set_mode((WIDTH, HEIGHT))

def main(window):

    global COUNT, city_garbage_left, win, garbage_pos
    global current_garbage_pos, city_tot_garbage

    clock = pygame.time.Clock()
    road, grass = get_map()
    garbage_group = pygame.sprite.Group()
    truck = Truck()


    run = True
    info_count = 0
    instructions_count = 0
    while run:
        clock.tick(FPS)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse = pygame.mouse.get_pos()
                if mouse[0] >= 662 and mouse[0] <= 687 and mouse[1] >= 22 and mouse[1] <= 47:
                    info_count += 1
                    if info_count == 5:
                        info_count = 0
                else:
                    info_count = 0

                if mouse[0] >= 663 and mouse[0] <= 696 and mouse[1] >= 62 and mouse[1] <= 85:
                    instructions_count += 1
                    if instructions_count == 5:
                        instructions_count = 0
                
                else:
                    instructions_count = 0

                


            if event.type == pygame.KEYDOWN:
                truck.do_turn()

        if not game_pause:


            truck.do_movement()

            draw(window, road, grass, info, instructions)

        # SACCHU_TMP 
            truck.update_truck(window)

            if ((info_count == 0) and (instructions_count == 0)):
                if COUNT > 119:
                    current_garbage_pos.append(select_garbage())
                    gar_v = random.randint(3,10)*5
                    current_garbage_val.append(gar_v)
                    city_tot_garbage += gar_v
                    COUNT = 0 
            
            garbage_group.empty()
            city_garbage_left = 0
            index = 0

            for i in current_garbage_pos:
                garbage_group.add(Garbage(window, i))
                city_garbage_left += current_garbage_val[index]
                index += 1
            
            collision_checks(truck, garbage_group, window)

            for i in garbage_removed_pos:
                coin_sound = pygame.mixer.Sound("Assets/coin_sound.mp3")
                pygame.mixer.Sound.play(coin_sound)
                random_nums = random.randint(0, 3)
                if random_nums == 2:
                    message = text()
                    message.text_5()
                    for o in range(10000):
                        pygame.display.update()

        truck.display(window)
        truck.dump()
        truck.rect.x, truck.rect.y = bound(truck.rect.x, truck.rect.y)

        win_chk(window, win)
        lose(window)

        if info_count == 1:
            rect_1 = text()
            rect_1.rectangle()
            rect_1.text_1()
        elif info_count == 2:
            rect_2 = text()
            rect_2.rectangle()
            rect_2.text_2()
        elif info_count == 3:
            rect_3 = text()
            rect_3.rectangle()
            rect_3.text_3()
        elif info_count == 4:
            rect_4 = text()
            rect_4.rectangle()
            rect_4.text_4()

        if instructions_count == 1:
            instruc_1 = text()
            instruc_1.rectangle()
            instruc_1.text_6()
        elif instructions_count == 2:
            instruc_2 = text()
            instruc_2.rectangle()
            instruc_2.text_7()
        

        pygame.display.update()
        COUNT += 1

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main(window)
    