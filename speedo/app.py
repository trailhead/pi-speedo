import sys
import os
import math
from sdl2 import *
import sdl2.ext
from sdl2.sdlttf import *
from sdl2.sdlgfx import *
from ctypes import c_long, c_int, pointer
from speedo.displaynumber import DisplayNumber
import RPi.GPIO as GPIO
import time

class App:

    def __init__(self):
        self.win_width = 1024
        self.win_height = 600
        self.fontSize = int(self.win_height / 12)
        self.interval = 10
        self.maxspeed = 100
        self.startangle = -70
        self.endangle = 70
        self.numradius = self.win_width * 0.4
        self.fontName = "roboto-v20-latin-regular"
        self.fontFile = os.path.join("./", self.fontName + ".ttf")
        self.window = None
        self.renderer = None
        #self.winsurf = None
        self.font = None
        self.message = None
        self.pixelformat = None
        self.nums = []
        self.channel = 36
        self.millis_last = 0
        self.interval_last = 0
        self.num_samples = 20
        self.sample_buffer = []
        self.rpm = 0

    def my_callback_one(self, channel):
        millis_now = self.millis()
        if self.millis_last > 0:
            self.interval_last = millis_now - self.millis_last
        self.millis_last = millis_now
        print("in callback")

    def millis(self):
        return int(round(time.time() * 1000.0))

    def calc_speed(self, interval):
        wheel_diam = 33.0
        magnets = 3.0
        self.rpm = 1000.0 / (interval * magnets) * 60.0
        miles_per_rev = ((wheel_diam * 3.14159) / 12.0) / 5280.0
        miles_per_minute = self.rpm * miles_per_rev
        miles_per_hour = miles_per_minute * 60.0
        print(miles_per_hour)
        return miles_per_hour

    def initSDL(self):
        SDL_Init(SDL_INIT_VIDEO)

        self.window = SDL_CreateWindow(
            b"SDL2 TTF test",  # window title
            SDL_WINDOWPOS_CENTERED,  # initial x position
            SDL_WINDOWPOS_CENTERED,  # initial y position
            self.win_width,  # width, in pixels
            self.win_height,  # height, in pixels
            SDL_WINDOW_SHOWN  # flags
        )

        self.renderer = SDL_CreateRenderer(self.window, -1, SDL_RENDERER_ACCELERATED)

        self.pixelformat = SDL_GetWindowPixelFormat(self.window)

        # Getting the window size.
        self.SCREEN_WIDTH = pointer(c_int(0))
        self.SCREEN_HEIGHT = pointer(c_int(0))
        SDL_GetWindowSize(self.window, self.SCREEN_WIDTH, self.SCREEN_HEIGHT)

    def initTTF(self):
        self.tfi = TTF_Init()
        if self.tfi != 0:
            print("TTF_Init failed")
            exit(1)

        # Open the font
        SDL_ClearError()
        try:
            # assume python 3 and encode as byte
            self.font = TTF_OpenFont(str.encode(self.fontFile), self.fontSize)
        except:
            print("TTF_OpenFont error: ", SDL_GetError())

    def run(self):

        self.initSDL()
        self.initTTF()

        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(self.channel, GPIO.IN)

        GPIO.add_event_detect(self.channel, GPIO.RISING)
        GPIO.add_event_callback(self.channel, self.my_callback_one)

        color = SDL_Color(255, 255, 255)
        #SDL_SetRenderDrawColor( self.renderer, 0, 0, 0, 255 );

        arcangle = self.endangle - self.startangle
        stepdegrees = arcangle / ((self.maxspeed / self.interval))
        mph_multiplier = float(arcangle) / float(self.maxspeed)

        #print (stepdegrees)

        for i in range(0, self.maxspeed+1, self.interval):
            num = DisplayNumber(self.font, self.renderer)
            num.setText(str(i))
            num.setPosition(math.sin(math.radians(-len(self.nums) * stepdegrees + 180 - self.startangle)) * self.numradius + self.win_width / 2,
                            math.cos(math.radians(-len(self.nums) * stepdegrees + 180 - self.startangle)) * self.numradius + self.win_height * 0.8
            )
            self.nums.append(num)

        running = 1
        event = SDL_Event()
        while running:
            if SDL_PollEvent(event):
                if event.type == SDL_QUIT:
                    running = 0
                elif event.type == SDL_WINDOWEVENT:
                    if event.window.event == SDL_WINDOWEVENT_RESIZED:
                        SDL_GetWindowSize(self.window, SCREEN_WIDTH, SCREEN_HEIGHT)
            if running:
                millis_since_last = self.millis() - self.millis_last
                if self.interval_last > 0.0 and millis_since_last < self.interval_last * 2:
                    mph = self.calc_speed(self.interval_last)
                else:
                    mph = 0

                self.sample_buffer.append(mph)

                if len(self.sample_buffer) > self.num_samples:
                    self.sample_buffer.pop(0)

                mph = sum(self.sample_buffer) / len(self.sample_buffer)

                SDL_SetRenderDrawColor(self.renderer, 0, 0, 0, 255)
                SDL_RenderClear(self.renderer)
                # We can draw our message as we do any other texture, since it's been
                # rendered to a texture

                thickLineRGBA (  self.renderer,
                            int(self.win_width / 2),
                            int(self.win_height * 0.8),
                            int(math.sin(math.radians(-mph * mph_multiplier + 180 - self.startangle)) * self.numradius + self.win_width / 2),
                            int(math.cos(math.radians(-mph * mph_multiplier + 180 - self.startangle)) * self.numradius + self.win_height * 0.8),
                            int(self.win_width / 200.0),
                            255,
                            0,
                            0,
                            255
                )
                for num in self.nums:
                    num.drawCenter()

                SDL_RenderPresent(self.renderer)

        self.cleanup()

    def cleanup(self):
        SDL_DestroyRenderer(self.renderer)
        # Get rid of old surface
        SDL_FreeSurface(self.message)
        SDL_DestroyWindow(self.window)
        SDL_Quit()
