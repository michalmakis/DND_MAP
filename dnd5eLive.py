from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import *
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.video import Video
import getopt, sys
import numpy as np
import math
import argparse


def roundup(number, exponent=10.0):
    return math.ceil(number / exponent) * exponent

class DrawInput(Widget):
    def on_touch_down(self, touch):
        with self.canvas:
            touch.ud["line"] = Line(points=(touch.x, touch.y))

    def on_touch_move(self, touch):
        touch.ud["line"].points += (touch.x, touch.y)

    def on_touch_up(self, touch):
        self.canvas.clear()


class drawLiveMap(App):
    tvsize = 70
    filename = 'demo.mp4'
    videoopacity = 1
    gridopacity = 0.1
    gridcolor = [50, 50, 50]
    gridthickness = 1.2

    def parser(self):

        parser = argparse.ArgumentParser(
            prog='dnd5e live map',
            description='Provides and overlay grid on top of a video file.',
            epilog='@PartyLuckPoints')

        parser.add_argument('--filename', metavar='filename', type=str, # nargs=1,
                            help='video file in current folder with path specified',
                            default='demo.mp4',
                            dest='filename',
                            required=False)

        parser.add_argument('--tvsize', type=int, dest='tvsize', #nargs=1,
                            help='Tv size in cm diagonaly in cm (default 70)', default=70, required=False)

        parser.add_argument('--videoopacity', type=float, dest='videoopacity', #nargs=1,
                            help='Video opacity (float on scale of 0 to 1 - default 1)', default=1, required=False)

        parser.add_argument('--gridopacity', type=float, dest='gridopacity', #nargs=1,
                            help='Grid opacity (float on scale of 0 to 1 - default 0.1)', default=0.1, required=False)

        parser.add_argument('--gridcolor', type=int, nargs=3, dest='gridcolor',
                            help='Grid color in RGB(0-255) default grey - 50 50 50)', default=[50,50,50], required=False)

        parser.add_argument('--gridthickness', type=float, dest='gridthickness', #nargs=1,
                            help='Grid thickness (float on scale of 0 to ?? pixels - default 1.2)', default=1.2, required=False)

        parser.add_argument('--gridhex', type=int, dest='gridhex', #nargs=1,
                            help='Grid in hex shape (default 0)', default=0, required=False)



        args = parser.parse_args()
        return args

    def __init__(self, **kwargs):
        super(drawLiveMap, self).__init__(**kwargs)
        parser_result = self.parser()

        self.filename = parser_result.filename
        self.tvsize = parser_result.tvsize
        self.videoopacity = parser_result.videoopacity
        self.gridopacity = parser_result.gridopacity
        self.gridcolor = parser_result.gridcolor
        self.gridthickness = parser_result.gridthickness
        self.gridhex = parser_result.gridhex

        self.gridHexoffset = 0.82

    def draw_grid(self, tvsize=69, color=[0, 0, 0], thickness=1):
        grid = Widget()
        w, h = (1920,1080) #Window.size
        size=tvsize
        tv_height = size / math.sqrt(math.pow(16 / 9, 2) + 1)
        tv_length = (16 / 9) * tv_height

        rows = round(tv_height / 2.5)
        cols = round(tv_length / 2.5)


        #rows, cols = grid_shape
        dy, dx = h / rows, w / cols

        # draw vertical lines
        with grid.canvas:
            #Color(250, 250, 250)
            Color(color[0], color[1], color[2])
            for x in np.linspace(start=dx, stop=w - dx, num=cols - 1):
                x = int(round(x))
                #print([x, 0, x, h])
                Line(points=[x, 0, x, h], width=thickness)

            # draw horizontal lines
            for y in np.linspace(start=dy, stop=h - dy, num=rows - 1):
                y = int(round(y))
                #print([0, y, w, y])
                Line(points=[0, y, w, y], width=thickness)

        return grid

    def draw_hex_grid(self, tvsize=69, color=[0, 0, 0], thickness=1):
        grid = Widget()
        #w, h = (1920, 1080)  # Window size
        w, h = (2560, 1440)  # Window size
        size = tvsize
        tv_height = size / math.sqrt(math.pow(16 / 9, 2) + 1)

        # Calculate the number of hexagons that fit in a row and column
        #hex_radius = /2.5  # Size of each hexagon side

        hex_radius = h / tv_height * 2.5 / 2  # Size of each hexagon side

        hex_width = hex_radius * 2
        hex_height = math.sqrt(3) * hex_radius

        cols = round(w / hex_width)
        #rows = round(h / (hex_height * 0.75))  # 0.75 accounts for vertical offset
        rows = round(h / (hex_height * self.gridHexoffset ))  # 0.75 accounts for vertical offset

        with grid.canvas:
            Color(color[0], color[1], color[2])

            for row in range(rows):
                for col in range(cols):
                    x_offset = col * hex_width
                    #y_offset = row * (hex_height * 0.75)
                    y_offset = row * (hex_height * self.gridHexoffset )

                    # Offset every other row
                    if row % 2 == 1:
                        x_offset += hex_radius                                      - 0

                    # Calculate the vertices of the hexagon
                    points = []
                    for i in range(6):
                        angle_deg = 60 * i + 30
                        angle_rad = math.pi / 180 * angle_deg
                        x = round(x_offset + hex_radius * math.cos(angle_rad))
                        y = round(y_offset + hex_radius * math.sin(angle_rad))
                        points.extend([x, y])

                    Line(points=points, width=thickness)

        return grid


    def build(self):

        Window.size = (1920, 1080)
        Window.fullscreen = True

        self.root_layout = FloatLayout()
        self.window = GridLayout()
        self.pero = DrawInput()

        if self.gridhex == 1:
            gridOverlay = self.draw_hex_grid(self.tvsize, self.gridcolor, self.gridthickness)
        else:
            gridOverlay = self.draw_grid(self.tvsize,self.gridcolor,self.gridthickness)

        gridOverlay.opacity = self.gridopacity

        video = Video(source=str(self.filename), state='play',allow_stretch= True, options={'eos': 'loop'})
        video.opacity = self.videoopacity  # adjust to make the video lighter/darker

        self.root_layout.add_widget(video)  # add the video first
        self.root_layout.add_widget(gridOverlay)  # add the video first
        self.root_layout.add_widget(self.window)  # now add the GUI window so it will be drawn over the video
        self.root_layout.add_widget(self.pero)  # add the video first

        return self.root_layout  # return the root_layout instead of the window

if __name__ == "__main__":
    # Only run Windows DPI awareness code if operating on Windows
    if sys.platform == "win32":
        try:
            from ctypes import windll, c_int64
            windll.user32.SetProcessDpiAwarenessContext(c_int64(-4))
        except Exception as e:
            print(f"Could not set DPI awareness: {e}")

    drawLiveMap().run()