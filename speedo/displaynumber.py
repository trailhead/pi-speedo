import sys
import os
from sdl2 import *
from sdl2.sdlttf import *
from ctypes import c_long, c_int, pointer

class DisplayNumber:
    def __init__(self, font, renderer):
        self.x = 0
        self.y = 0
        self.txt = ''
        self.font = font
        self.renderer = renderer
        self.color = SDL_Color(255,255,255)
        self.rect = None

    def setFont(self, font):
        self.font = font

    def setText(self, txt):
        self.txt = txt
        surface = TTF_RenderText_Solid(self.font, str.encode(self.txt), self.color)
        self.texture = SDL_CreateTextureFromSurface(self.renderer, surface)
        self.rect = SDL_Rect(0,0,surface.contents.w, surface.contents.h)
        SDL_FreeSurface(surface)

    def setPosition(self, x, y):
        self.x = x
        self.y = y

    def drawCenter(self, x = None, y = None):
        if x is None:
            x = self.x
        
        if y is None:
            y = self.y

        SDL_RenderCopy( self.renderer,
                        self.texture,
                        self.rect, 
                        SDL_Rect(int(x - self.rect.w / 2),
                                 int(y - self.rect.h / 2),
                                 self.rect.w,
                                 self.rect.h
                        )
        )

