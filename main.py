import pygame
import math
import time
from pygame.locals import *

#Test

pygame.init()
pygame.font.init()
fontsize = 16
myfont = pygame.font.SysFont('Consolas', fontsize)
height = myfont.get_height()
width = myfont.size("A")[0]

textDisplay_width = 1200
textDisplay_height = 720-(720%height)
screen_height = 720
screen_width = 1280


max_linesw = int(textDisplay_width/width)


upperbound = int(textDisplay_height / height)
max_lines = upperbound




clock = pygame.time.Clock()
textDisplay = pygame.Surface((textDisplay_width, textDisplay_height))
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Text Editor")
stripThickness = 20


b = pygame.Surface((textDisplay_width, textDisplay_height))
bg = b.convert()
bg.fill((255, 255, 255))


s = open("example.txt","r+")
string = s.readlines()
if len(string) == 0:
    string = [""]

if len(string) < max_lines:
    max_lines = len(string)

def assign_max(max):
    global max_lines
    if not max > upperbound:
        max_lines = max


def save(text):
    global s
    s.seek(0)
    s.truncate(0)
    for i in text:
        s.write(i+'\n')
    s.close()


def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))




class KeySustain():
    repeatTime = 30
    def __init__(self,function1):
        self.startTime = 0
        self.lastRepeatTime = 0
        self.once = False
        self.startedRepeat = False
        self.pressed = False
        self.funct = function1

    def run(self, argument=None):
        if self.pressed:
            if not self.once:
                if argument==None:
                    self.funct()
                else:
                    self.funct(argument)
                self.once = True
            elif pygame.time.get_ticks() - self.startTime > 400:
                if not self.startedRepeat:
                    if argument == None:
                        self.funct()
                    else:
                        self.funct(argument)
                    self.startedRepeat = True
                    self.lastRepeatTime = pygame.time.get_ticks()
                elif pygame.time.get_ticks() - self.lastRepeatTime > KeySustain.repeatTime:
                    timedelta = pygame.time.get_ticks() - self.lastRepeatTime
                    for i in range(0,int(timedelta/KeySustain.repeatTime)):
                        if argument == None:
                            self.funct()
                        else:
                            self.funct(argument)
                    self.lastRepeatTime = pygame.time.get_ticks()

    def start(self):
        self.startTime = pygame.time.get_ticks()
        self.pressed = True
        self.once = False

    def end(self):
        self.pressed = False
        self.startedRepeat = False

class Scroll():
    def __init__(self,loc):
        self.loca = loc
        self.pointer_line = 0
        self.pointer_index = 0
        self.scroll_line = 0
        self.strafe_line = 0

        self.scrollable = False
        self.scroll_range = 0
        self.height_offset = 0
        self.width_offset = 0

        self.blinking = True
        self.last_interaction = 0
        self.blinkTime = 0
        self.lastStateSwitch = pygame.time.get_ticks()
        self.state = True
        self.surface = myfont.render("|", True, (0, 0, 0))
        #Scroll Fast boi
        self.scrollDir = 0
        self.strafeDir = 0

        self.scrollSustain = KeySustain(self.scroll_)
        self.strafeSustain = KeySustain(self.strafe)



    def isPointerVisible(self):
        return self.strafe_line<=self.pointer_index<=self.strafe_line+max_linesw

    def pointerMakeVisible(self):
        self.strafe_line = int(self.pointer_index/max_linesw)*max_linesw

    def scroll_(self):
        self.interaction()
        if self.scrollDir is 1 and self.scroll_line+max_lines <= self.pointer_line +1 and self.pointer_line+1 < len(string):
            self.pointer_line +=1
            self.scroll_line  +=1
        elif self.scrollDir is -1 and self.pointer_line - 1 < self.scroll_line and self.scroll_line > 0:
            self.pointer_line -=1
            self.scroll_line -=1
        elif 0 <= self.pointer_line+self.scrollDir < len(string) :
            self.pointer_line += self.scrollDir

        self.pointer_index = constrain(self.pointer_index, 0,len(string[self.pointer_line]))
        if not self.isPointerVisible():
            self.pointerMakeVisible()

    def interaction(self):
        self.last_interaction = pygame.time.get_ticks()
        self.blinking = False

    def strafe(self):
        self.interaction()
        if self.strafeDir == 1 and self.pointer_index+1 >= self.strafe_line+max_linesw and self.pointer_index+1 <= len(string[self.pointer_line]):
            self.pointer_index +=1
            self.strafe_line+=1
        elif self.strafeDir == -1 and self.pointer_index==self.strafe_line and self.strafe_line >0:
            self.pointer_index -=1
            self.strafe_line -=1
        elif 0 <= self.pointer_index+self.strafeDir <=len(string[self.pointer_line]):
            self.pointer_index += self.strafeDir

    def update(self):
        self.scrollSustain.run()
        self.strafeSustain.run()
        if pygame.time.get_ticks() - self.last_interaction > 800:
            self.blinking = True

    def show(self):
        if pygame.time.get_ticks()-self.lastStateSwitch>500:
            self.state = not self.state
            self.lastStateSwitch = pygame.time.get_ticks()

        if self.blinking:
            if self.state:
                textDisplay.blit(self.surface, (0-int(width/2)+(self.pointer_index-self.strafe_line)*width,(self.pointer_line-self.scroll_line) * height))#myfont.size(string[self.pointer_line+self.scroll_line][:self.pointer_index])[1],self.pointer_line*height))
        else:
            textDisplay.blit(self.surface, (0- int(width / 2) +(self.pointer_index-self.strafe_line)* width,(self.pointer_line-self.scroll_line) * height))

class Text():

    def __init__(self,text):
        self.location = (10,10)
        self.backSustain = KeySustain(self.backspace)
        self.alphaSustain = KeySustain(self.addAlpha)
        self.enterSustain = KeySustain(self.enter)
        self.text = text
        self.length = len(self.text)
        self.key = ''
        self.scroll = Scroll(self.location)
        if len(text)*height>textDisplay_height:
            self.scroll.scrollable = True
            self.scroll.scroll_range = len(text)*height-textDisplay_height


        for i in range(0,len(self.text)-1):
            self.text[i] = self.text[i][:-1]


    def update(self):
        self.alphaSustain.run()
        self.backSustain.run()
        self.scroll.update()
        self.enterSustain.run()

    def addAlpha(self):
        ind = self.scroll.pointer_line
        string1 = self.text[ind]
        string1 = string1[:self.scroll.pointer_index]+self.key+string1[self.scroll.pointer_index:]
        self.text[ind] = string1
        if self.scroll.pointer_index >= self.scroll.strafe_line+max_linesw:
            self.scroll.strafe_line +=1
        self.scroll.pointer_index +=1

    def delete_lines(self,index):
        if self.length > 0:
            for i in range (index,self.length-1):
                self.text[i] = self.text[i+1]
            del self.text[-1]
            self.length = len(self.text)
            assign_max(self.length)

    def backspace(self):
        if self.scroll.pointer_index > 0:
            temp  = self.text[self.scroll.pointer_line]
            temp = temp[:self.scroll.pointer_index][:-1]+temp[self.scroll.pointer_index:]
            self.text[self.scroll.pointer_line] = temp
            self.scroll.pointer_index -=1

        elif self.scroll.pointer_line > 0:
            length = len(self.text[self.scroll.pointer_line -1])
            temp = self.text[self.scroll.pointer_line]
            self.text[self.scroll.pointer_line -1] += temp
            self.delete_lines(self.scroll.pointer_line)


            if self.scroll.pointer_line==self.scroll.scroll_line:
                self.scroll.scroll_line -=1


            self.scroll.pointer_line -=1
            self.scroll.strafe_line = int(length/max_linesw)*max_linesw
            self.scroll.pointer_index = length

    def enter(self):
        lineindex = self.scroll.pointer_line
        linewidth = self.scroll.pointer_index
        self.text.append("")
        self.length = len(self.text)
        newline = self.text[lineindex][linewidth:]
        self.text[lineindex] = self.text[lineindex][:linewidth]
        for i in range(len(self.text)-1,lineindex+1,-1):
            self.text[i] = self.text[i-1]
        self.text[lineindex+1] = newline
        self.scroll.scrollDir = 1
        self.scroll.scroll_()
        self.scroll.pointer_index = 0
        self.scroll.strafe_line = 0
        assign_max(self.length)

    def movePointer(self, mouseLoc):
        self.scroll.interaction()
        proposedy  = int(mouseLoc[1]/height)
        proposedx = int((mouseLoc[0]+width/2)/width)
        if proposedy+self.scroll.scroll_line < self.length:
            self.scroll.pointer_line = proposedy+self.scroll.scroll_line
            self.scroll.pointer_index = constrain(proposedx + self.scroll.strafe_line, 0, len(self.text[self.scroll.pointer_line]))

    def show(self):
        for i in range(self.scroll.scroll_line,constrain(self.scroll.scroll_line+max_lines,0,self.length)):
            surf = myfont.render(self.text[i],True,(0,0,0))
            textDisplay.blit(surf,(0-self.scroll.strafe_line*width,(i-self.scroll.scroll_line)*height))
        self.scroll.show()

class Background:
    def __init__(self):
        self.back = pygame.Surface((screen_width, screen_height))
        self.background = self.back.convert()
        self.background.fill((255, 255, 255))

    def show(self):
        screen.blit(self.background, (0, 0))

t = Text(string)
background = Background()

shiftModifier = False
shiftDict = {'1':'!','2':'@','3':'#','4':'$','5':'%','6':'^','7':'&','8':'*','9':'(','0':')'}



def shift(character):
    ascii = ord(character)
    if ascii >=97 and ascii <=122:
        return character.upper()
    elif ascii >=48 and ascii<=57:
        return shiftDict[character]
    return character


translation = (10,10)

I_beam_cursor = (
    "XXX XXX                 ",
    "   X                    ",
    "   X                    ",
    "   X                    ",
    "   X                    ",
    "   X                    ",
    "   X                    ",
    "   X                    ",
    "   X                    ",
    "   X                    ",
    "   X                    ",
    "   X                    ",
    "   X                    ",
    "   X                    ",
    "   X                    ",
    "XXX XXX                 ",
    "                        ",
    "                        ",
    "                        ",
    "                        ",
    "                        ",
    "                        ",
    "                        ",
    "                        "
)

xormasks, andmasks = pygame.cursors.compile(I_beam_cursor)
# cursor size
size = (24, 24)

# point of selection of the cursor
hotspot = (0, 0)

# custom cursor
cursor = (size, hotspot, xormasks, andmasks)
# sets the cursor
pygame.mouse.set_cursor(*cursor)



while True:
    clock.tick(32)
    for event in pygame.event.get():
        if event.type == QUIT:
            exit()
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                save(t.text)
                exit()
            elif event.key == K_UP:
                t.scroll.scrollDir = -1
                t.scroll.scrollSustain.start()

            elif event.key == K_DOWN:
                t.scroll.scrollDir = 1
                t.scroll.scrollSustain.start()

            elif event.key == K_RIGHT:
                t.scroll.strafeDir = 1
                t.scroll.strafeSustain.start()

            elif event.key == K_LEFT:
                t.scroll.strafeDir = -1
                t.scroll.strafeSustain.start()

            elif event.key == K_BACKSPACE:
                t.backSustain.start()
            elif event.key == 304 or event.key == 303:
                shiftModifier = True
            elif event.key == 13:
                t.enterSustain.start()
            else:
                char = chr(event.key)
                if shiftModifier:
                    char = shift(char)
                t.key = char
                t.alphaSustain.start()

        elif event.type == KEYUP:
            if event.key == K_DOWN or event.key == K_UP or event.key == K_RIGHT or event.key == K_LEFT:
                t.scroll.scrollSustain.end()
                t.scroll.strafeSustain.end()

            elif event.key == K_BACKSPACE:
                t.backSustain.end()

            elif event.key == 304 or event.key==303:
                shiftModifier = False

            elif event.key == 13:
                t.enterSustain.end()

            else:
                t.alphaSustain.end()

        elif event.type == MOUSEBUTTONDOWN:
            if event.button ==1:
                pos = pygame.mouse.get_pos()
                pos = (pos[0]-translation[0],pos[1]-translation[1])
                t.movePointer(pos)
            if event.button == 4:
                t.scroll.scrollDir = -1
                t.scroll.scroll_()
            if event.button == 5:
                t.scroll.scrollDir = 1
                t.scroll.scroll_()

        #elif event.type == MOUSEBUTTONUP:

    background.show()
    textDisplay.blit(bg, (0, 0))
    t.update()
    t.show()

    screen.blit(textDisplay,translation)
    #pygame.draw.polygon(textDisplay,(100,100,100),[(0,0),(textDisplay_width,0),(textDisplay_width,stripThickness),(0,stripThickness)])
    pygame.display.update()
    pygame.display.flip()