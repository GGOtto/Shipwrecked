# Name: Shipwrecked
# Author: G.G.Otto
# Date: 1/23/2021
# Version 3.1

# Graphics made by G.G.Otto

import pygame, time, random
from pygame.locals import *

class Bottle:
    '''represents a word on the screen'''

    def __init__(self, game, word):
        '''Bottle(game, word, wpm=0) -> Bottle
        sets up a bottle for game with word'''
        self.game = game
        self.image = pygame.image.load(f"bottle{random.randint(1,3)}.png")
        self.pos = (1400,random.randint(50,250))
        self.font = pygame.font.SysFont("times new roman", 30, bold=True)
        self.word = word
        self.speed = 1
        self.highlight = 0
        self.start = None
        self.paused = False
        self.missed = False
        self.saved = 0
        self.pause()
        
        # attributes for removing word
        self.removed = 0
        self.wordColors = ((255,200,0), (0,162,232))

    def __str__(self):
        '''str(Bottle) -> str
        returns the bottle's word'''
        return self.word        

    def in_view(self):
        '''Bottle.in_view() -> bool
        returns if the bottle is in view or not'''
        return -120 < self.pos[0] < 1171

    def used(self):
        '''Bottle.used() -> bool
        returns whether the bottle has been used'''
        return self.pos[0] < 1171

    def has_word(self):
        '''Bottle.has_word() -> bool
        returns whether bottle has word'''
        return self.removed == 0

    def set_wpm(self):
        '''Bottle.set_wpm() -> None
        sets the bottle's wpm to player avg wpm'''
        if self.game.get_avg_wpm() > len(self.game.get_bottles()):
            self.wpm = self.game.get_avg_wpm()

    def move_in_view(self):
        '''Bottle.move_in_view() -> None
        moves the bottle in view'''
        self.start = time.time()
        self.pos = 1170, self.pos[1]
        self.saved = 0

    def play(self):
        '''Bottle.play() -> None
        plays the bottle'''
        if self.paused:
            self.paused = False
            self.start = time.time()

    def pause(self):
        '''Bottle.pause() -> None
        pauses the bottle'''
        if not self.paused:
            self.paused = True
            if self.start != None:
                self.saved += time.time()-self.start
        
    def match(self, word, leave=False):
        '''Bottle.match(word, leave=False) -> bool
        matches word to the bottle's word'''
        if self.removed or not self.in_view():
            return

        if len(word) > len(self.word):
            self.highlight = 0
        elif self.word[:len(word)] == word:
            self.highlight = len(word)
        else:
            self.highlight = 0
            
        # check whole word
        if self.word == word and leave:
            self.game.get_sounds()["reward"].play()
            self.removed += 1
            return True

        return False
    
    def draw_word(self):
        '''Bottle.draw_word() -> None
        draws the word over the bottle'''
        # create surfaces
        width = 0
        letters = []
        for i in range(len(self.word)):
            if self.removed > 1:
                color = []
                for j in range(3):
                    color.append(self.wordColors[0][j]+self.removed*(self.wordColors[1][j]-self.wordColors[0][j])/100)
                color = tuple(color)
            elif i > self.highlight - 1:
                color = (255,255,255)
            else:
                color = self.wordColors[0]
                
            letters.append(self.font.render(self.word[i], True, color))
            width += letters[-1].get_rect().width

        # blit surfaces
        last = self.pos[0]-width/2+self.image.get_rect().width/2
        for letter in letters:
            self.game.get_screen().blit(letter, (last, self.pos[1]-10-15*self.removed/100))
            last += letter.get_rect().width

        if self.removed and not self.paused:
            self.removed += 1

    def update(self):
        '''Bottle.update() -> None
        updates the bottle'''
        if not self.paused:
            bottles = len(self.game.get_bottles())
            self.pos = 1170-1250*(time.time()-self.start+self.saved)/(60*(bottles//10)/(bottles+bottles//10-1)), self.pos[1]
            
        self.game.get_screen().blit(self.image, self.pos)
        if self.removed < 101:    self.draw_word()

class TextField(pygame.Surface):
    '''represents the text field'''

    def __init__(self, game, pos):
        '''TextField(game, pos) -> TextField
        constructs the text field for the game'''
        pygame.Surface.__init__(self, (450,40))
        self.game = game
        self.pos = pos

        # text attribute
        self.text = ""
        self.font = pygame.font.SysFont("times new roman", 26)
        self.textSurface = self.font.render("", True, (0,0,0))
        self.lastDelete = time.time()
        self.keySound = Sound(game, "click2.wav", 0.07)
        self.game.add_sound(self.keySound)
        
        self.SAND = (245,213,170)
        self.fill(self.SAND)

        # key map for shift
        self.keyMap = {"1":"!", "2":"@", "3":"#", "4":"$", "5":"%",
            "6":"^", "7":"&", "8":"*", "9":"(", "0":")", "-":"_",
            "=":"+", "`":"~", "[":"{", "]":"}", "\\":"|", ";":":",
            "'":"\"", ",":"<", ".":">", "/":"?"}
        for letter in range(ord("a"), ord("z")+1):
            self.keyMap[chr(letter)] = chr(letter).upper()

        # turn everything into number
        for letter in self.keyMap.copy():
            self.keyMap[ord(letter)] = self.keyMap[letter]
                      
    def get(self):
        '''TextField.get() -> str
        returns the text in the field'''
        return self.text

    def set(self, text):
        '''TextField.set(text) -> str
        sets the text to text'''
        self.text = text
        self.textSurface = self.font.render(self.text, True, (0,0,0))

    def process_key(self, event):
        '''TextField.process_key() -> None
        processes the key press'''
        # random characters
        if self.textSurface.get_rect().width < 430 and event.key in self.keyMap:
            self.keySound.play()
            # capitalization
            if pygame.key.get_pressed()[K_LSHIFT] or pygame.key.get_pressed()[K_RSHIFT]:
                self.text += self.keyMap[event.key]
            else:
                self.text += chr(event.key)

        # space to submit
        elif event.key == K_SPACE or (event.key == K_RETURN and self.game.is_last_word()):
            if len(self.text) > 0:
                self.keySound.play()
            for bottle in self.game.get_bottles():
                if bottle.in_view():
                    if bottle.match(self.get(), True): break
            self.set("")
            
        self.textSurface = self.font.render(self.text, True, (0,0,0))

    def update(self):
        '''TextField.update() -> None
        updates the text field'''
        self.fill(self.SAND)
        
        # draw cursor
        if time.time()%1.5 < 0.75 and not self.game.is_paused():
            pygame.draw.line(self, (0,0,0), (self.textSurface.get_rect().width+10, 10),
                (self.textSurface.get_rect().width+10, 30))

        # delete
        keys = pygame.key.get_pressed()
        if not self.game.is_paused() and keys[K_BACKSPACE] and time.time() - self.lastDelete > 0.1:
            if len(self.text) > 0:
                self.keySound.play()
            self.set(self.text[:-1])
            self.lastDelete = time.time()
        elif not self.game.is_paused() and (keys[K_RCTRL] or keys[K_LCTRL]) and keys[K_BACKSPACE]:
            if len(self.text) > 0:
                self.keySound.play()
            self.set("")
            
        self.blit(self.textSurface, (10, 20-self.textSurface.get_rect().height/2))        
        self.game.get_screen().blit(self, self.pos)

class Timer:
    '''manipulates a timer on the screen'''

    def __init__(self, game, timer, pos):
        '''Timer(game, timer, pos) -> Timer
        constructs the timer at pos'''
        self.timer = timer
        self.pos = pos
        self.game = game
        self.started = False
        self.startTime = None
        self.currentTime = 0
        self.savedTime = 0
        self.font = pygame.font.SysFont("Arial", 35, bold=True)

    def is_finished(self):
        '''Timer.is_finished() -> bool
        returns whether the timer is finished or not'''
        return self.currentTime == self.timer

    def get_time(self):
        '''Timer.get_time() -> float
        returns the current time'''
        return self.currentTime

    def pause(self):
        '''Timer.pause() -> None
        pauses the timer'''
        self.started = False
        self.savedTime = self.currentTime
        
    def start(self):
        '''Timer.start() -> None
        starts the timer'''
        self.started = True
        self.startTime = time.time()

    def reset(self):
        '''Timer.reset() -> None
        resets the timer'''
        self.savedTime = 0
        self.currentTime = 0
        self.started = False

    def update(self):
        '''Timer.update() -> None
        updates the timer'''
        if self.started:
            self.currentTime = time.time() - self.startTime + self.savedTime

        if self.currentTime > self.timer:
            self.currentTime = self.timer

        # update text
        color = (255,255,255)            
        text = self.font.render(f"{int((self.timer-self.currentTime)//60)}:"+\
            f"{str(int((self.timer-self.currentTime)%60)).zfill(2)}", True, color)
        self.game.get_screen().blit(text, (self.pos[0]-text.get_rect().width/2, self.pos[1]))

class Level:
    '''represents all the levels of the game'''

    def __init__(self, game):
        '''Level(game) -> Level
        constructs an object for all levels'''
        self.game = game
        self.levelSurface = pygame.image.load("level.png")
        self.levelNum = 1
        self.ended = False
        self.flyout = None
        self.gameOver = False

        # set up fonts
        self.messageFont = pygame.font.SysFont("times new roman", 20)
        self.levelCompleteFont = pygame.font.SysFont("times new roman", 40, bold=True)
        self.statsFont = pygame.font.SysFont("times new roman", 25, bold=True)
        self.sourceFont = pygame.font.SysFont("times new roman", 20, bold=True)

    def is_ended(self):
        '''Level.is_ended() -> bool
        returns whether the level has ended or not'''
        return self.ended

    def process_mouse_click(self, event):
        '''Level.process_mouse_click(event) -> None
        processes mouse clicks on screen for level'''
        if not self.ended or not 363 < event.pos[1] < 393:
            return

        if 525 < event.pos[0] < 675:
            self.game.get_sounds()["button"].play()
            self.redo_level()
        elif 685 < event.pos[0] < 835 and not self.missed:
            self.game.get_sounds()["button"].play()
            self.next_level()
        elif 365 < event.pos[0] < 515:
            self.game.get_sounds()["button"].play()
            self.game.show_popup("restart")

    def end_level(self):
        '''Level.end_level() -> None
        ends the level'''
        self.game.pause()
        self.ended = True
        self.levelEndPos = [0, -400]

        # process text and bottles
        message = ""
        self.missed = False
        last = False
        totalCorrect = 0
        for bottle in self.game.get_bottles():
            # word that is missed
            if bottle.has_word():
                self.missed = True
                if not last:
                    message += "... "
                    last = True
            # not missed
            else:
                message += str(bottle)+" "
                last = False
                totalCorrect += 1

        if totalCorrect/len(self.game.get_bottles()) >= 0.9:
            self.missed = False

        # add message to screen
        ypos = 160; last = 0
        for i in range(0, len(message), 140):
            lastSpace = message.rfind(" ", i, i+140)
            
            line = self.messageFont.render(message[last:lastSpace], True, (255,255,255))
            self.levelSurface.blit(line, (600-line.get_rect().width/2, ypos))
            ypos += 20; last = lastSpace+1

        # other text
        completed = f"Level {self.levelNum}: Completed!"
        nextLevel = "active"
        if self.missed:
            completed = f"Level {self.levelNum}: Incomplete"
            nextLevel = "disabled"
        text = self.levelCompleteFont.render(completed, True, (255,255,255))
        self.levelSurface.blit(text, (600-text.get_rect().width/2, 45))

        # source for text
        if len(self.game.get_lines()[self.levelNum-1].split("|")) > 1:
            source = self.sourceFont.render(self.game.get_lines()[self.levelNum-1].split("|")[1], True, (255,255,255))
            self.levelSurface.blit(source, (600-source.get_rect().width/2, 135))

        # buttons on screen
        self.levelSurface.blit(pygame.image.load("restart_button_2.png"), (365, 363))
        self.levelSurface.blit(pygame.image.load("redo_level_button.png"), (525, 363))
        self.levelSurface.blit(pygame.image.load(f"next_level_button_{nextLevel}.png"), (685, 363))

        # stats
        self.game.log_words(totalCorrect)
        wpm = self.statsFont.render("Words per minute: "+str(int((totalCorrect*60/\
            self.game.get_clock().get_time())*10)/10), True, (255,255,255))
        numWords = self.statsFont.render(f"Words correct: {totalCorrect}/{len(self.game.get_bottles())}", True, (255,255,255))
        self.levelSurface.blit(numWords, (400-numWords.get_rect().width/2, 100))
        self.levelSurface.blit(wpm, (800-wpm.get_rect().width/2, 100))
                
    def update(self):
        '''Level.update() -> None
        updates the level'''
        if self.gameOver:
            return
        
        # update flyout
        if self.flyout != None and self.flyout.is_finished():
            self.set_up_bottles()
            self.game.play()
            self.flyout = None
        elif self.flyout != None:
            self.flyout.update()
            
        # update level end
        if self.ended:
            if self.levelEndPos[1] < 0:
                self.levelEndPos[1] += 10
            self.game.get_screen().blit(self.levelSurface, self.levelEndPos)

    def set_up_bottles(self):
        '''Level.set_up_bottles() -> None
        sets up the bottles for the current level'''
        line = self.game.get_lines()[self.levelNum-1].split("|")
        bottles = self.game.get_bottles()
        for word in line[0].split():
            newBottle = Bottle(self.game, word)
            bottles.append(newBottle)

        # set up wpm
        self.game.set_wpm()
        for bottle in self.game.get_bottles():
            bottle.set_wpm()

    def redo_level(self):
        '''Level.redo_level() -> None
        sets up the level for a redo'''
        self.game.get_bottles().clear()
        self.levelSurface = pygame.image.load("level.png")
        self.game.get_clock().reset()
        self.ended = False

        # set up fly out
        self.flyout = Flyout(self.game, f"Level {self.levelNum}")

    def next_level(self):
        '''Level.next_level() -> None
        goes to the next level'''
        if self.levelNum == len(self.game.get_lines()):
            self.game.end_game()
            self.gameOver = True
            return 
        
        self.levelNum += 1
        self.redo_level()

class Flyout:
    '''represents the flyout the comes before each level'''

    def __init__(self, game, text):
        '''Flyout(game, text) -> Flyout
        constructs the flyout with text on surface'''
        self.game = game
        self.text = pygame.font.SysFont("times new roman", 40).render(text, True, (255,255,255))
        self.pos = [1200,200-self.text.get_rect().height/2]
        self.start = time.time()
        self.saved = 0
        self.savedAdded = False

    def is_finished(self):
        '''Flyout.is_finished() -> bool
        returns whether the flyout has finished or not'''
        return self.pos[0] < -self.text.get_rect().width

    def update(self):
        '''Flyout.update() -> None
        updates the flyout'''
        # update the flyout's distance on screen
        if not self.game.is_popup():
            if self.savedAdded:
                self.start = time.time()
            self.pos[0] = 1170-1300*(time.time()-self.start+self.saved)/3
            self.savedAdded = False
        elif not self.savedAdded:
            self.saved += time.time() - self.start
            self.savedAdded = True
            
        self.game.get_screen().blit(self.text, self.pos)

        # set the game started attribute
        if self.is_finished():
            self.game.set_started(True)
        else:
            self.game.set_started(False)

class Ship:
    '''represents the ship'''

    def __init__(self, game):
        '''Ship(game) -> None
        constructs the ship'''
        self.game = game
        self.image = pygame.image.load("ship.png")
        self.pos = [-self.image.get_rect().width-1, 51]
        self.moving = False

    def is_finished(self):
        '''Ship.is_finished() -> bool
        returns if the ship is finished or not'''
        return self.pos[0] > 600-self.image.get_rect().width/2       

    def start(self):
        '''Ship.start() -> None
        starts the ship'''
        self.moving = True
        self.started = time.time()

    def update(self):
        '''Ship.update()
        updates the ship'''
        if self.moving:
            if not self.is_finished():
                self.pos[0] = -self.image.get_rect().width-1+3000*(time.time()-self.started)/5
            self.game.get_screen().blit(self.image, self.pos)

class Winning:
    '''represents the page at the end with the win'''

    def __init__(self, game, ship):
        '''Winning(game, ship) -> Winning
        constructs the winning page'''
        self.game = game
        self.ship = ship
        self.pos = [0,-400]
        self.font = pygame.font.SysFont("times new romans", 35, bold=True)

    def end_surface(self):
        '''Winning.end_surface() -> Surface
        returns the end surface'''
        surface = pygame.image.load("win.png")
        avgWpm = self.font.render(f"Average WPM: {self.game.get_avg_wpm()}", True, (255,255,255))
        surface.blit(avgWpm, (600-avgWpm.get_rect().width/2, 265))
        surface.blit(pygame.image.load("restart_button.png"), (950/2, 355))
        return surface

    def update(self):
        '''Winning.update() -> None
        updates the win message'''
        if self.ship.is_finished():
            if self.pos[1] < 0:
                self.pos[1] += 20
            self.game.get_screen().blit(self.end_surface(), self.pos)

class Sound(pygame.mixer.Sound):
    '''represents a sound for the game'''

    def __init__(self, game, file, volume=0.4):
        '''Sound(game, file, volume) -> Sound
        constructs the sound'''
        pygame.mixer.Sound.__init__(self, file)
        self.game = game
        self.set_volume(volume)
        self.unmute()
        if game.is_muted():
            self.mute()

    def set_volume(self, newVolume):
        '''Sound.set_volume(newVolume) -> None
        sets the background volume'''
        self.originVolume = newVolume

    def mute(self):
        '''Sound.mute() -> None
        mutes the sound'''
        pygame.mixer.Sound.set_volume(self, 0)

    def unmute(self):
        '''Sound.unmute() -> None
        unmutes the sound'''
        pygame.mixer.Sound.set_volume(self, self.originVolume)

class Shipwrecked:
    '''represents the game'''

    def __init__(self, mute=False):
        '''Shipwrecked() -> Shipwrecked
        constructs the game'''
        pygame.display.set_icon(pygame.image.load("logo.png"))
        pygame.display.set_caption("Shipwrecked")
        self.screen = pygame.display.set_mode((1200,400))

        # minor attributes
        self.WATER = (0,162,232)
        self.background = pygame.image.load("background.png")
        self.title = pygame.image.load("title.png")
        self.title.blit(pygame.image.load("play_button.png"), (950/2, 355))
        self.flyoutFont = pygame.font.SysFont("times new roman", 50)
        self.started = False
        self.paused = True
        self.isTitle = True
        self.totalWords = 0
        self.totalTime = 0
        self.muted = mute
        self.sounds = {}

        # start up
        self.screen.blit(self.background, (0,0))
        pygame.display.update()

        # set up popup
        popupFont = pygame.font.SysFont("times new roman", 25, bold=True)
        self.popupBool = False
        self.popupImg = pygame.image.load("popup.png")
        self.popupImg.blit(popupFont.render("Yes", True, (255,255,255)), (55, 125))
        self.popupImg.blit(popupFont.render("No", True, (255,255,255)), (208, 125))

        # audio on/off icon
        self.audioIcons = [pygame.transform.rotozoom(pygame.image.load(f"audio_{onoff}.png"), 0, 0.3) for onoff in ("on","off")]

        # set up bottles
        file = open("word_script.txt")
        self.lines = []
        for line in file.read().split("\n"):
            if line != '':
                try:
                    self.lines.append(random.choice(line.split("||")[1:]))
                except:
                    print(line)
                
        file.close()
        self.bottles = []
        self.lastAdded = None
        self.lastAddedSave = 0
        
        # other game objects
        self.textfield = TextField(self, (375, 355))
        self.timer = Timer(self, 60, (600,3))
        self.level = Level(self)
        self.ship = Ship(self)
        self.win = Winning(self, self.ship)

        # sounds
        self.buttonSound = Sound(self, "click3.wav", 0.07)
        self.add_sound(self.buttonSound, "button")
        self.add_sound(Sound(self, "reward.wav", 0.3), "reward")
        
        self.mainloop()
        pygame.quit()

    def get_screen(self):
        '''Shipwrecked.get_screen() -> Surface
        returns the screen of the game'''
        return self.screen

    def get_field(self):
        '''Shipwrecked.get_field() -> TextField
        returns the text field'''
        return self.textfield

    def get_bottles(self):
        '''Shipwrecked.get_bottles() -> list
        returns a list fo all bottles'''
        return self.bottles

    def is_paused(self):
        '''Shipwrecked.is_paused() -> bool
        returns whether the game is paused or not'''
        return self.paused

    def get_lines(self):
        '''Shipwrecked.get_lines() -> list
        returns a list of all lines in the text file'''
        return self.lines

    def get_clock(self):
        '''Shipwrecked.get_clock() -> Timer
        returns the timer for the game'''
        return self.timer

    def set_wpm(self):
        '''Shipwrecked.set_wpm() -> None
        sets the wpm of the game'''
        self.wpm = len(self.bottles)
        if self.wpm < self.get_avg_wpm():
            self.wpm = self.get_avg_wpm()

    def is_popup(self):
        '''Shipwrecked.is_popup() -> bool
        returns if there is a popup'''
        return self.popupBool

    def is_last_word(self):
        '''Shipwrecked.is_last_word() -> bool
        returns whether there is only one word on the screen'''
        count = 0
        for bottle in self.bottles:
            if (bottle.in_view() and bottle.has_word()) or not bottle.used():
                count += 1
        return count == 1

    def set_started(self, boolean):
        '''Shipwrecked.set_started(boolean) -> None
        sets the attribute started'''
        self.started = boolean

    def get_avg_wpm(self):
        '''Shipwrecked.get_avg_wpm() -> float
        returns the average words per minute'''
        try: 
            return int(self.totalWords*60/self.totalTime*10)/10
        except ZeroDivisionError:
            return 0

    def get_bottles_correct(self):
        '''Shipwrecked.get_bottles_correct() -> int
        returns all the bottles that are correct'''
        count = 0
        for bottle in self.bottles:
            if not bottle.has_word():
                count += 1
        return count

    def get_sounds(self):
        '''Shipwrecked.get_sounds() -> dict
        returns the sounds'''
        return self.sounds

    def add_sound(self, sound, key=None):
        '''Shipwrecked.add_sound(sound) -> None
        adds a sound to the game'''
        if key == None:
            self.sounds[sound] = sound
        else:
            self.sounds[key] = sound

    def is_muted(self):
        '''Shipwrecked.is_muted() -> bool
        returns whether the game is muted or not'''
        return self.muted

    def end_game(self):
        '''Shipwrecked.end_game() -> None
        ends the game'''
        self.ship.start()

    def log_words(self, words):
        '''Shipwrecked.log_words() -> None
        logs words and time for total avg'''
        self.totalTime += self.timer.get_time()
        self.totalWords += words

    def move_next_bottle(self):
        '''Shipwrecked.move_next_bottle() -> None
        moves the next bottle in view'''
        for bottle in self.bottles:
            if not bottle.used():
                bottle.move_in_view()
                self.lastAdded = time.time()
                self.lastAddedSave = 0
                return

        # check if words are all gone
        if self.level.is_ended() or len(self.bottles) == 0:
            return
        
        hasWords = [True, True]
        for bottle in self.bottles:
            if bottle.in_view() and bottle.has_word():
                hasWords[0] = False
            if bottle.in_view():
                hasWords[1] = False

        if hasWords[0]:
            self.timer.pause()
        if hasWords[1]:
            self.level.end_level()
            self.textfield.set("")

    def update(self):
        '''Shipwrecked.update() -> None
        updates a single frame of the game'''
        self.screen.blit(self.background, (0,0))

        # update audio off and on icon
        if not self.muted:
            self.screen.blit(self.audioIcons[0], (5,5))
        else:
            self.screen.blit(self.audioIcons[1], (5,5))

        # in-game components
        if self.started and not self.ship.is_finished():
            self.textfield.update()

            # update bottles
            noWords = True
            for bottle in self.bottles[:]:
                if bottle.in_view():
                    bottle.update()
                    bottle.match(self.textfield.get())

                    if bottle.has_word():
                        noWords = False

            if noWords:
                self.move_next_bottle()

        # move next bottle in view
        if not self.paused and self.lastAdded != None and \
            (time.time() - self.lastAdded + self.lastAddedSave) > \
            60/(self.wpm + self.wpm//10 - 1):
            self.move_next_bottle()

        if not self.ship.is_finished():
            self.timer.update()
            self.level.update()
        self.ship.update()
        self.win.update()

        # title page
        if self.isTitle:
            self.screen.blit(self.title, (0,0))
        # popup
        if self.popupBool:
            self.screen.blit(self.popupImg, (450, 100))

    def mainloop(self):
        '''Shipwrecked.mainloop() -> None
        the mainloop of the game'''
        running = True
        while running:
            for event in pygame.event.get():
                # open popup
                if event.type == QUIT and not self.popupBool:
                    self.show_popup()
                elif event.type == KEYDOWN:
                    if self.started and not self.paused:
                        self.textfield.process_key(event)

                # buttons
                if event.type == MOUSEBUTTONDOWN:
                    # audio on/off
                    if event.pos[0] < self.audioIcons[0].get_rect().width+5 and event.pos[1] < self.audioIcons[0].get_rect().height+5:
                        self.muted = not self.muted
                        for sound in self.sounds:
                            if self.muted:
                                self.sounds[sound].mute()
                            else:
                                self.sounds[sound].unmute()
                            
                    # close window on popup
                    if self.popupBool:
                        if 475 < event.pos[0] < 570 and 225 < event.pos[1] < 285:
                            self.buttonSound.play()
                            running = False
                            if self.popupAction == "restart":
                                self.__init__(self.muted)
                        elif 628 < event.pos[0] < 723 and 225 < event.pos[1] < 285:
                            self.buttonSound.play()
                            self.popupBool = False
                            if not self.popupPaused:
                                self.play()
                    # start game button or restart button
                    elif self.isTitle or self.ship.is_finished():
                        if 905/2 < event.pos[0] < 905/2+250 and 355 < event.pos[1] < 395:
                            self.buttonSound.play()
                            if not self.started:
                                self.level.redo_level()
                                self.isTitle = False
                            else:
                                running = False
                                self.__init__(self.muted)
                    else:
                        self.level.process_mouse_click(event)

            if running:
                self.update()
                pygame.display.update()

    def pause(self):
        '''Shipwrecked.mainloop() -> None
        pauses the game'''
        if self.paused:
            return
        
        self.timer.pause()
        self.lastAddedSave += time.time() - self.lastAdded

        # pause bottles
        for bottle in self.bottles:
            bottle.pause()

        self.paused = True

    def play(self):
        '''Shipwrecked.play() -> None
        plays the game'''
        if not self.paused:
            return
        
        # start game
        if not self.started:
            self.started = True
            self.move_next_bottle()

        self.timer.start()
        self.lastAdded = time.time()
        self.paused = False

        for bottle in self.bottles:
            bottle.play()

    def show_popup(self, action="close"):
        '''Shipwrecked.show_popup(action) -> None
        shows the popup to ask if the window should be closed
        action is either "close" or "restart"'''
        self.popupBool = True
        if not self.paused:
            self.pause()
            self.popupPaused = False
        else:
            self.popupPaused = True
        self.popupAction = action
    
pygame.init()
Shipwrecked()
