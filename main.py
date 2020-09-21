import pygame
import random
import sys
import pickle

def make_menu(screen): #the main menu function
    menu=True
    buttons={
            "Single player": 1,
            "Two players": 2,
            "Three players": 3,
            "Four playes": 4,
            "Exit": "Exit"
            }
    for key in buttons:
        buttons[key]=button(key, buttons[key])
    menu_screen(buttons, screen)
    pygame.display.flip()
    while menu: #controlls the input in the menu
        for event in pygame.event.get():
            if event.type==pygame.KEYDOWN:
                if event.key==27: #key 27 is escape, clicking it quits the game
                    pygame.quit()
                    sys.exit()
            if event.type==pygame.MOUSEBUTTONDOWN:
                pos=pygame.mouse.get_pos()
                for rec in buttons:
                    if buttons[rec].rec.collidepoint(pos):
                        if buttons[rec].command!=("Exit"):
                            in_game(screen, buttons[rec].command)
                        else:
                            pygame.quit()
                            sys.exit()

def menu_screen(buttons, screen): #renders the buttons of the menu
    rec=pygame.Rect([0, 0], [screen_x, screen_y])
    pygame.draw.rect(screen, [255,255,255], rec) #draws a white background on the screen
    i=0
    positions=[
            [screen_x*0.2, screen_y*0.2],
            [screen_x*0.8-screen_x/5, screen_y*0.2],
            [screen_x*0.2, screen_y*0.8-screen_y/5],
            [screen_x*0.8-screen_x/5, screen_y*0.8-screen_y/5],
            [screen_x*0.2+screen_x/5, screen_y*0.2+screen_y/5]
            ] #has all the button coordinates hard coded in
    for key in buttons:
        buttons[key].position(positions[i], [screen_x/5, screen_y/5])
        buttons[key].make_button()
        pygame.draw.rect(screen, [0,0,0], buttons[key].rec, int(screen_x/100))
        screen.blit(buttons[key].text, [positions[i][0]+screen_x/100, positions[i][1]+screen_y/12])
        i+=1

class button():

    def __init__(self, text, command): #the command sends to a corresponding function
        self.text=text
        self.command=command

    def position(self, pos, size):
        self.position=pos
        self.size=size

    def make_button(self):
        self.rec=pygame.Rect(self.position, self.size)
        font=pygame.font.Font('freesansbold.ttf', 32) #the normal font used to display stuff
        self.text=font.render(self.text, False, [0,0,0])

################################################################################
################################################################################

def in_game(screen, car_num):
    pygame.mouse.set_visible(False)
    paused=False #cam be toggled by space if in game, all movement will stop
    playing=True #the game loop will run when true, disaboeld by loosing or exiting

    play=game(screen, car_num)
    while playing:
        playing=play.frame()
        for event in pygame.event.get():
            if event.type==pygame.KEYDOWN:
                for car in play.cars:
                    if event.key in car.controls:
                        car.move(car.controls.index(event.key))
                if event.key==27: #key 27 is escape, clicking it quits the game
                    play.end_game(play)
                    playing=False
                elif event.key==32: #pausing the game
                    paused=True
        while paused:
            for event in pygame.event.get():
                if event.type==pygame.KEYDOWN:
                    if event.key==32:
                        paused=False
        pygame.display.flip()
    pygame.display.flip()
    pygame.time.delay(2000) #gives the user 2 seconds so they don't accidentaly close their score before looking
    pygame.mouse.set_visible(True)
    while not playing:
        for event in pygame.event.get():
            if event.type==pygame.KEYDOWN or event.type==pygame.MOUSEBUTTONDOWN:
                make_menu(screen)

class game():

    def __init__(self, screen, car_num):
        self.define_vars(screen, car_num) #initializes the variables

        self.cars=[]
        for i in range(0, car_num):
            self.cars.append(car(self._screen, i))
        self.track()

    def define_vars(self, screen, car_num): #define all the initial variables for the game
        self._screen=screen #surface for the game
        self._objects=[] #obstacles in the player way
        self._box_probability=99.9 #10 is divided by a random number between 1 and 100, if the anwser is bigger than this var, a box spawns

        self._plane_distance=screen_x/4 #the plane distance from side to the first track
        self._track_width=screen_x-2*self._plane_distance #defines the width of the track that player can drive on
        self.lane_width=self._track_width/5 #the width of one lane on the track

        self.playing=True #true if game is not closed

        self.car_num=car_num
        self._font=pygame.font.Font('freesansbold.ttf', 128) #the normal font used to display stuff
        self.user_score=0 #the current score in the game
        file=open("High_scores.high", "rb")
        self.high_scores=pickle.load(file)
        file.close()

    def track(self): #redraws the track every game
        rec=pygame.Rect([0, 0], [screen_x, screen_y])
        pygame.draw.rect(self._screen, [255,255,255], rec) #draws a white background on the screen

        for i in range(0, 6): #draws the track outlines
            x_pos=self._plane_distance+self.lane_width*i
            pygame.draw.line(self._screen, [0,0,0], [x_pos, 0], [x_pos, screen_y], 10)

        for i in self._objects: #moves and redraws all the already spawned boxes
            i.create_box()
            a_box=i.a_box
            pygame.draw.rect(self._screen, [0,0,0], a_box)
            i.move_box()
            if i.position[1]>screen_y: #deletes the box if it goes off screen
                self._objects.pop(self._objects.index(i))

    def score(self): #updates the user score
        self.user_score=self.user_score+(10*self.car_num/self._box_probability) #adds new points to the player
        user_score_dis=self._font.render(str(int(self.user_score)), False, [0,0,0])
        self._screen.blit(user_score_dis, [0,0]) #draws the user score on the side

        for i in range(0, len(self.high_scores)): #draws the high scores table on the side
            high_scores_dis=self._font.render(str(int(self.high_scores[i])), False, [0,0,0])
            self._screen.blit(high_scores_dis, [screen_x*0.75+screen_x/100, i*128])

    def draw_obs(self): #spawnes and draws new obstacles
        number=random.random()*100
        if number>self._box_probability:
            box1=box(self._screen, self.car_num)
            box1.create_box()
            a_box=box1.a_box
            self._objects.append(box1)
            pygame.draw.rect(self._screen, [0,0,0], a_box)
        else:
            self._box_probability=self._box_probability-0.0000001*self._box_probability

    def draw_vechicles(self): #draws the vechicals on the scren
        for car in self.cars:
            car.draw_car()

    def check_collisions(self): #checks are any cars colliding with obstacles
        for i in self._objects:
            for car in self.cars:
                if car.car_box.colliderect(i.a_box):
                    self.end_game(car)

    def frame(self): #every frame calls all the functions that need to update
        self.track()
        self.draw_vechicles()
        self.draw_obs()
        self.check_collisions()
        self.score()
        return self.playing

    def end_game(self, loose): #called at the end of a single game, updates the high score table
        for i in range(0, len(self.high_scores)):
            if self.user_score>self.high_scores[i]:
                self.high_scores.insert(i, self.user_score)
                self.high_scores=self.high_scores[0:5]
                file=open("High_scores.high", "wb")
                pickle.dump(self.high_scores, file)
                file.close()
                break
        self.end_game_screen()
        self.playing=False

    def end_game_screen(self): #shows the end game screen with the score in the middle
        rec=pygame.Rect([0, 0], [screen_x, screen_y])
        pygame.draw.rect(self._screen, [255,255,255], rec) #draws a white background on the screen
        self.user_score=self.user_score+10/self._box_probability
        user_score_dis=self._font.render(str(int(self.user_score)), False, [0,0,0])
        self._screen.blit(user_score_dis, [screen_x/2-64, screen_y/2-64])

class box(game): #includes all parameters and operations needed for the game obstacles

    def __init__(self, screen, car_num):
        super().define_vars(screen, car_num) #initializes the variables already existing in the main game object
        self.lane=random.randint(0, 4) #pickes a random lne for the new obstacle to spawn into
        x_position=self._plane_distance+self.lane*self.lane_width #defines the x coordinate of the left conrner of the spawning obstacle
        y_position=random.randint(0, int(screen_y/2-screen_y/3)) #defines the y coordinate of the top of the spawning obstacle
        self.position=[x_position, y_position]
        y_size=random.randint(int(screen_y/10), int(screen_y/3))
        self.size=[self.lane_width, y_size]

    def create_box(self): #reacrates the box in new coordinates after moving
        self.a_box=pygame.Rect(self.position, self.size)

    def move_box(self): #moves the object by one pixel down
        self.position[1]+=1

class car(game):

    def __init__(self, screen, car_num):
        super().define_vars(screen, car_num) #initializes the variables already existing in the main game object
        self.car_num=car_num #defines which car this is
        self.image=car_dic[self.car_num][0] #reades in the image for this vechicle accordingly to the entered parameters
        self.controls=car_dic[self.car_num][1] #reades in the controls for the this vechicle

        self.size=[int(self.lane_width), int(screen_y/4)]
        self.lane=0 #the initial lane
        self.car_img=pygame.image.load("Resources/"+self.image).convert_alpha()
        self.car_img=pygame.transform.scale(self.car_img, [int(self.size[0]-0.2*self.lane_width), self.size[1]])

    def position(self): #calculates the car position baised on the lane that it is in
        x=self._plane_distance+self.lane_width*self.lane #defines the x-coordinate of the left conrner of the car
        y=screen_y-1.2*self.size[1] #defines the y-coordinate of the top conrner of the car
        self.coordinates=[x, y]

    def draw_car(self):
        self.position()
        self.car_box=pygame.Rect(self.coordinates, self.size) #the actuall box that the user uses to dodge the obstacles
        #pygame.draw.rect(self._screen, [0,0,0], car)

        self._screen.blit(self.car_img, [self.coordinates[0]+0.1*self.lane_width, self.coordinates[1]]) #blits the visible image of the car on the screen

    def move(self, side): #moves the vechcial accodingly the key pressed
        dir=0 #it is the directin of movement, with positive being right and negative left
        if side==(0): #the car is moved to the left
            dir=-1
        elif side==(1): #the car is moved to the rihgt
            dir=1
        self.lane+=dir
        if self.lane==-1: #allows the car to jump from between sides
            self.lane=4
        elif self.lane==5: #allows the car to jump from between sides
            self.lane=0
        else:
            pass

################################################################################
################################################################################

def main():
    pygame.init()
    screen=pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Car game")
    global screen_x, screen_y #globalises the hight and the width of the screen
    screen_x, screen_y=pygame.display.Info().current_w, pygame.display.Info().current_h
    global car_dic
    car_dic={
            0: ["Race_car.png", [97, 100]],
            1: ["Race_car.png", [276, 275]],
            2: ["Race_car.png", [104, 107]],
            3: ["Race_car.png", [260, 262]]
            } #this dic defines the filenames for vechical visualisation and the controls for cars [1, 2, 3, 4]

    make_menu(screen)

if __name__==("__main__"):
    main()
