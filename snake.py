#!/usr/bin/python

import math
import random 
import curses
import curses.wrapper

class Window(object):
        
        def __init__(self,curses_window):
                self.dims          = curses_window.getmaxyx()
                self.curses_window = curses_window
		curses_window.erase()
                curses_window.hline(1,0,curses.ACS_HLINE,self.dims[1])

        def addlist( self, list, ch, attr ):
                for l in list:
                        self.curses_window.addch(l[0],l[1],ch,attr)

        def addstatus( self, status ):
                def _add_line( curses_window, x, status ):
                        if isinstance(status,str):
                                curses_window.addstr(0,x,status,curses.color_pair(4))
                                return len(status)
                        if isinstance(status,tuple) and isinstance(status[0],str):
                                curses_window.addstr(0,x,status[0],status[1])
                                return len(status[0])
                        elif isinstance(status,list):
                                result = 0
                                for s in status:
                                         result += _add_line(curses_window,x+result,s)
                                return result
                        else:
                                return 0
                # wipe out the previous status
                self.curses_window.hline(0,0,ord(" "),self.dims[1]-1)
                # handle depending on the type of status, make it really versatile
                _add_line(self.curses_window,0,status)

        def get_random_point(self):
                return [random.randint(2,self.dims[0]-1),random.randint(0,self.dims[1]-1)] 

        def __getattr__(self,name,*args):
                # This simply redirects all the unknown attributes and calls
                # to the main curses window
                return getattr(self.curses_window,name)

class Snake(object):

	direction_keys = [curses.KEY_UP,curses.KEY_DOWN,curses.KEY_LEFT,curses.KEY_RIGHT]

	def __init__(self,head,color_pair_ndx):
		self.body           = [head]
                self.direction      = self.direction_keys[random.randint(0,len(self.direction_keys)-1)] 
		self.grow_by        = 0
                self.color_pair_ndx = color_pair_ndx
                self.apples_eaten   = 0

        def __str__(self):
                return "{head="+str(self.body[0])+",length="+str(len(self.body))+",apples="+str(self.apples_eaten)+"}";

        def get_closest_apple( self, apples ):
                min_distance = 100000
                min_ndx = 0
                for ndx in range(len(apples)):
                        distance = abs(apples[ndx][0]-self.body[0][0])+abs(apples[ndx][1]-self.body[0][1])
                        if distance<min_distance:
                                min_distance = distance
                                min_ndx      = ndx
                return apples[min_ndx]

	def move(self,window):
                new_head = None
		if self.direction==curses.KEY_UP:
                        new_head = [self.body[0][0]-1,self.body[0][1]]
		elif self.direction==curses.KEY_DOWN:
                        new_head = [self.body[0][0]+1,self.body[0][1]]
		elif self.direction==curses.KEY_LEFT:
                        new_head = [self.body[0][0],self.body[0][1]-1]
		elif self.direction==curses.KEY_RIGHT:
                        new_head = [self.body[0][0],self.body[0][1]+1]
                if new_head:
                        # let's see if the head of the snake reached any of the walls. If so then do not move
                        if (new_head[0]<2) or (new_head[0]>=window.dims[0]):
                                return
                        if (new_head[1]<0) or (new_head[1]>=window.dims[1]):
                                return
                        if self.grow_by>0:
                                # if we just need to grow, then simply stick the new head in front
                                # of the reast of the body
                                self.body.insert(0,new_head)
                                self.grow_by -= 1
                        else:
                                # Here we need to stick the new head in front of the body and remove the tail
                                tail = self.body[-1]
                                self.body[1:] = self.body[0:-1]
                                self.body[0] = new_head
                                # erase the tail from the screen
                                window.addch(tail[0],tail[1],ord(" "))
                        # draw the new head but first let's normalize it
                        if len(self.body)>1:
                                window.addch(self.body[1][0],self.body[1][1],ord("%"),curses.A_BOLD|curses.color_pair(self.color_pair_ndx))    
                        window.addch(new_head[0],new_head[1],ord("B"),curses.A_BOLD|curses.color_pair(4))        

	def set_direction(self,key):
                if key in self.direction_keys:
                        self.direction = key
	
        def get_direction_to(self,apple):
                y = self.body[0][0]-apple[0]
                x = self.body[0][1]-apple[1]
                if y>0:
                        return curses.KEY_UP
                if y<0:
                        return curses.KEY_DOWN
                if x<0:
                        return curses.KEY_RIGHT
                return curses.KEY_LEFT
        
	def eat_apple(self,grow_by):
		self.grow_by += grow_by
                self.apples_eaten += 1

def main( curses_window ):

        # initialization of some constants
        random.seed()
	curses.curs_set(0)
	curses.start_color()
	curses.init_pair(1,curses.COLOR_RED,curses.COLOR_BLACK)
	curses.init_pair(2,curses.COLOR_GREEN,curses.COLOR_BLACK) 
	curses.init_pair(3,curses.COLOR_BLUE,curses.COLOR_BLACK) 
	curses.init_pair(4,curses.COLOR_WHITE,curses.COLOR_BLACK) 
        timeout     = 500
        grow_by     = 2
        apple_count = 10

	while True: 

                # starting new game
                window     = Window(curses_window)
		my_snake   = Snake(window.get_random_point(),2)
                auto_snake = Snake(window.get_random_point(),3)
		apples     = [window.get_random_point() for x in range(apple_count)]
		window.addlist(apples,"@",curses.A_BOLD|curses.color_pair(1))

		while len(apples)>0:

                        # draw the status
                        window.addstatus([("Apples eaten: "+str(apple_count-len(apples))+". ",curses.color_pair(4)),
                                          ("My snake is "+str(my_snake)+". ",curses.color_pair(my_snake.color_pair_ndx)),
                                          ("Auto snake is "+str(auto_snake)+". ",curses.color_pair(auto_snake.color_pair_ndx))])

			# wait for the key to move my snake
                        window.timeout(timeout)
                        my_snake.set_direction(window.getch())
                        my_snake.move(window)

                        # now move the auto snake
                        auto_snake.set_direction(auto_snake.get_direction_to(auto_snake.get_closest_apple(apples)))
                        auto_snake.move(window)

                        # has my snake or auto snake eaten an apple?
                        for s in [my_snake,auto_snake]:
                                if s.body[0] in apples:
                                        apples.remove(s.body[0])
                                        curses.beep()
                                        s.eat_apple(grow_by)

                        # has my snake bit itself?
                        if my_snake.body[0] in my_snake.body[1:]:
                                window.addstatus(("You have bit yourself. Press any key",curses.A_BOLD|curses.color_pair(1)))
                                window.timeout(-1)
                                window.getch()
                                apple_count -= 10
                                break

                grow_by     += 1
		apple_count += 10

curses.wrapper(main)

