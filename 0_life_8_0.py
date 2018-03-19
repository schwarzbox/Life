# !/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LIFE
"""
__version__ = 8.0

# 0_life_8_0.py

# MIT License
# Copyright (c) 2017 Alexander Veledzimovich veledz@gmail.com

# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.


# 1.0 (2016 - 3 days to build, but I am only start to code!)
# 3.0 (2017 - use signal flag to stop, many comments with old code)
# 3.5 (2017 – always erase, after_cancel, improve speed, pep-8)
# 4.0 (2017 – 4 px. very slow fill pixels, 200 cells)
# 4.5 (2017 – 1 px. improve painting and syntax, 600 cells)
# 5.0 (2017 – 1 px. virtual matrix, del self.cell=int, 900 cells)
# 5.1 (2017 – 1 px. virtual matrix, total update very slow)
# 5.2 (2017 - 1 px. thread pool executor, same perfomans)
# 6.0 (2017 - 1 px. use pygame, made simple GUI by pygame, 9000 cells 4 fps)
# 7.0 (2017 - 1 px. no img, add editor, dark theme, class glider, users data)
# 8.0 (2017 - 1 px. cython 30000 cells 4 fps)
# 9.0 (2017 - 1 px. numpy 22000 cells 4 fps)

# add DISPLAY.set_alpha(0, pygame.RLEACCEL)
# evolution

import shelve
import time
from math import hypot
from string import ascii_lowercase
from sys import exit as sysexit
from sys import setcheckinterval

import pygame
from pygame.locals import *

import lifelogic_cyt

setcheckinterval(300)

WID = 940
HEI = 834

pygame.init()

FONT_L = pygame.font.Font('/System/Library/Fonts/SFNSText.ttf', 26)
FONT_M = pygame.font.Font('/System/Library/Fonts/SFNSText.ttf', 18)
FONT_S = pygame.font.Font('/System/Library/Fonts/SFNSText.ttf', 13)

BIGCELL = 8
SMALLCELL = 1

PADDING = 7
BORBUT = 1
LABELMARG = (PADDING + BORBUT) * 2

F_HEI = FONT_S.size('H')[1]

GLIDERMARG = PADDING + BORBUT
GLIDEPAD = 8

LEFTMEN_WID = BIGCELL * 12 + GLIDERMARG * 2
BOTMEN_HEI = LABELMARG * 2 + F_HEI

GAME_WID = WID - LEFTMEN_WID
GAME_HEI = HEI - BOTMEN_HEI

MENU_TOP = (HEI // 2) - 150
STR_Y = LABELMARG
STR_NUM = 7
STR_TOT = STR_NUM * F_HEI + STR_Y * (STR_NUM - 1) + STR_Y * 2

GREEN = (0, 255, 30, 255)
LIGHTGREEN = (0, 125, 60)

BLACK = (0, 0, 0, 200)
WHITE = (255, 255, 255, 200)
GRAY = (208, 208, 208, 100)
DARKGRAY = (128, 128, 128)
DARKDARKGRAY = (28, 28, 28)

TXTCOL = GREEN
BGCOL = BLACK
GAME_CLR = DARKDARKGRAY
CELL_COLOR = GREEN
DEAD_COLOR = DARKGRAY

ENABLE = TXTCOL
DISABLE = DARKGRAY
FILLBUT = LIGHTGREEN

ERASE_RAD = 10

FPS = 20


class GameLife(object):
    """
    Game of life logic
    """

    def __init__(self, main):
        self.main = main
        # matrix for count events

        self.virt_mat = [[0] * GAME_HEI for i in range(GAME_WID)]

        self.live = set()
        self.start_cell = 0
        self.epoh = 0
        self.score = 0
        self.max_score = 0

        self.erase = False
        self.old_x, self.old_y = None, None

    def add_pixels(self, x, y):
        pack = []
        dist_x = (x - self.old_x)
        dist_y = (y - self.old_y)
        hyp = int(hypot(dist_x, dist_y))

        for i in range(hyp):
            x = int(i * (dist_x / hyp) + self.old_x)
            y = int(i * (dist_y / hyp) + self.old_y)
            pack.append((x, y))
        return pack

    def motion_paint(self, x, y):
        xcell = int(x)
        ycell = int(y)
        pack = []
        if self.old_x and self.old_y:
            pack = self.add_pixels(xcell, ycell)
        # make smooth painting
        self.old_x, self.old_y = xcell, ycell
        self.black_cell(xcell, ycell)
        for i in pack:
            self.black_cell(i[0], i[1])

    def start_paint(self, x, y):
        self.black_cell(x, y)

    def black_cell(self, x, y):

        x = x % GAME_WID
        y = y % GAME_HEI

        live_rem = self.live.remove
        live_add = self.live.add
        if not self.erase:
            if self.virt_mat[x][y] == 0:
                self.virt_mat[x][y] = 1

                self.fill_black(self.virt_mat, [(x, y)], CELL_COLOR, 1)

                self.start_cell += 1
                live_add((x, y))
        else:
            for i in range(x - ERASE_RAD, x + ERASE_RAD):
                for j in range(y - ERASE_RAD, y + ERASE_RAD):
                    i = i % GAME_WID
                    j = j % GAME_HEI
                    if self.virt_mat[i][j] == 1:
                        self.fill_black(self.virt_mat, [(i, j)], GAME_CLR, 0)
                        # not count how much erase when start game
                        if self.epoh == 0:
                            self.start_cell -= 1
                        live_rem((i, j))

    def fill_black(self, virt_matrix, coords, color, virt_color):
        set_pixels = self.main.cell_matrix.set_at
        # 30000 4 fps
        # set at cython without set
        virt_matrix = lifelogic_cyt.fill_black(virt_matrix, coords,
                                               virt_color)

        for coord in coords:
            set_pixels(coord, color)

        # set at
        # 30000 4 fps
        # for coord in coords:
        #     virt_matrix[coord[0]][coord[1]] = virt_color
        #     set_pixels(coord, color)

    def start_life(self):
        # for generation
        self.epoh += 1

        total_cell_scr = len(self.live)

        # clean
        self.born = []
        self.dead = []
        t = time.time()

        # check coords
        # cythonize module
        self.born, self.dead = lifelogic_cyt.check_live(list(self.live),
                                                        total_cell_scr,
                                                        self.born,
                                                        self.dead,
                                                        self.virt_mat,
                                                        GAME_WID,
                                                        GAME_HEI)

        print('dead born', time.time() - t)

        # update screen counters
        self.main.update_counters(self.epoh, total_cell_scr)

        live_rem = self.live.remove
        live_add = self.live.add

        t = time.time()

        list(map(live_rem, self.dead))
        self.fill_black(self.virt_mat, self.dead, DEAD_COLOR, 0)

        list(map(live_add, self.born))
        self.fill_black(self.virt_mat, self.born, CELL_COLOR, 1)
        print('lifelogic', time.time() - t)

        # counters for maximum population
        if not self.max_score:
            self.max_score = total_cell_scr
        elif total_cell_scr > self.max_score:
            self.max_score = total_cell_scr
        else:
            self.max_score = self.max_score

        # after dead cells need to check how many stay alive
        total_cell_scr += len(self.born) - len(self.dead)
        # count population
        self.score += total_cell_scr

        # start goal for end message
        if total_cell_scr == 0:
            return False
        # for stop button
        else:
            return True

    def clear(self):
        # clear virtual board
        self.virt_mat = [[0] * GAME_HEI
                         for i in range(GAME_WID)]

        self.live = set()
        self.start_cell = 0
        self.score = 0
        self.max_score = 0
        self.epoh = 0

        self.old_x, self.old_y = None, None
        self.erase = False


class Glider(object):
    """
    Gliders surfaces for cursors and images on side menu.
    """

    def __init__(self, matrix, size, color, main):
        self.main = main
        self.matrix = matrix
        self._set_color = color
        self.cell_size = size

        self.size = [len(self.matrix * self.cell_size),
                     len(self.matrix[0]) * self.cell_size]

        self.visible = False
        self.selected = False
        # for scroling
        self.delta = 0
        # to made transparent image
        self.surface = pygame.Surface(self.size)
        self.surface = self.surface.convert_alpha()

    def show(self, x, y, anchor='center'):
        self.surface.fill((255, 255, 255, 0))
        for i in range(len(self.matrix)):
            for j in range(len(self.matrix[i])):
                if self.matrix[i][j]:
                    rct = pygame.Rect((0, 0, self.cell_size, self.cell_size))
                    rct.topleft = i * self.cell_size, j * self.cell_size
                    pygame.draw.rect(self.surface, self._set_color, rct)

        surrect = self.surface.get_rect()

        if self.cell_size == BIGCELL:
            # make scrolable
            surrect = self.main.make_anchor(surrect,
                                            x, y + self.delta, anchor)
            self.main.gliders_sur.blit(self.surface, surrect)

        else:
            surrect = self.main.make_anchor(surrect, x, y, anchor)
            self.main.DISPLAY.blit(self.surface, surrect)
        return surrect

    def create_glider(self, x, y):
        # from the lefttop
        for i in range(len(self.matrix)):
            for j in range(len(self.matrix[i])):
                if self.matrix[i][j]:
                    self.main.GL.black_cell(x + i, j + y)

    @property
    def set_color(self):
        return self._set_color

    @set_color.setter
    def set_color(self, color):
        self.selected = True
        self._set_color = color


class Main(object):

    def __init__(self):

        pygame.display.set_caption('CONWAY\'S GAME OF LIFE')
        pygame.mouse.set_visible(True)

        self.CLOCK = pygame.time.Clock()
        self.DISPLAY = pygame.display.set_mode((WID, HEI), 0, 32)
        self.DISPLAY.set_alpha(0, pygame.RLEACCEL)

        # set up icon in taskbar
        icon = self.create_game_icon()
        pygame.display.set_icon(icon)

        # field for cells
        self.cell_matrix = pygame.Surface((GAME_WID, GAME_HEI))
        # menu fields
        self.side_menu_sur = pygame.Surface((LEFTMEN_WID, GAME_HEI))
        # surface for gliders images and editor
        border = self.create_border()
        self.gliders_sur = pygame.Surface((border[2],
                                           border[3]))
        # key for private data
        self.user = False
        self.user_edit = False
        self.blink_time = 10
        self.color_cursor = TXTCOL
        self.text_cursor = pygame.Rect(0, 0, 2, F_HEI)

        # left menu
        # original images
        self.all_gliders = self.glider_matrix(self.default_matrix())
        # user gliders empty before choose right user
        self.user_gliders = []

        # editor content
        self.make_gliders = []
        # to allow user made creatures in side menu
        self.edit = False
        self.see_editor = False
        self.edit_cursor = pygame.Rect(0, 0, BIGCELL, BIGCELL)
        # content of side menu
        self.menu_content = ('CREATURES', self.all_gliders)

        # scroll in user gliders
        self.scroll = False
        self.cursor = None

        # var for start/stop game
        self.start = False

        self.fps = FPS
        # create object with all game logic
        self.GL = GameLife(self)

        # main loop
        self.game()

    def create_game_icon(self):
        matrix = list(zip(*[[0, 1, 0], [0, 0, 1], [1, 1, 1]]))
        one_cell = 38
        icon = pygame.Surface((128, 128))
        icon = icon.convert_alpha()
        icon.fill((255, 255, 255, 0))
        for i in range(len(matrix)):
            for j in range(len(matrix[i])):
                if matrix[i][j]:
                    rct = pygame.Rect((0, 0, one_cell, one_cell))
                    rct.topleft = i * (one_cell + 3), j * (one_cell + 3)
                    pygame.draw.rect(icon, TXTCOL, rct)
        return icon

    def default_matrix(self):
        ship_1 = [[0, 1, 0], [0, 0, 1], [1, 1, 1]]
        ship_2 = [[1, 0, 0, 1, 0], [0, 0, 0, 0, 1],
                  [1, 0, 0, 0, 1], [0, 1, 1, 1, 1]]
        fig_1 = [[1, 1, 0], [0, 1, 0], [0, 1, 0], [0, 1, 1]]
        fig_2 = [[0, 1, 1], [1, 1, 0], [0, 1, 0]]
        fig_3 = [[0, 1, 0], [0, 1, 0], [1, 0, 1], [0, 1, 0], [0, 1, 0],
                 [0, 1, 0], [0, 1, 0], [1, 0, 1], [0, 1, 0], [0, 1, 0]]
        fig_4 = [[1, 1, 1, 0, 1], [1, 0, 0, 0, 0], [0, 0, 0, 1, 1],
                 [0, 1, 1, 0, 1], [1, 0, 1, 0, 1]]
        ship_3 = [[0, 1, 1, 0, 0, 1, 1, 0], [0, 0, 0, 1, 1, 0, 0, 0],
                  [0, 0, 0, 1, 1, 0, 0, 0], [1, 0, 1, 0, 0, 1, 0, 1],
                  [1, 0, 0, 0, 0, 0, 0, 1], [0, 0, 0, 0, 0, 0, 0, 0],
                  [1, 0, 0, 0, 0, 0, 0, 1], [0, 1, 1, 0, 0, 1, 1, 0],
                  [0, 0, 1, 1, 1, 1, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 1, 1, 0, 0, 0], [0, 0, 1, 0, 0, 1, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0, 1, 0],
                  [1, 1, 0, 0, 0, 0, 1, 1], [0, 1, 0, 1, 1, 0, 1, 0],
                  [0, 0, 1, 1, 1, 1, 0, 0], [0, 0, 0, 1, 1, 0, 0, 0]]
        gun1 = [[0, 0, 1, 1, 0, 0, 0, 0, 0], [0, 0, 1, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0], [1, 1, 0, 0, 0, 1, 1, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 1, 1, 1, 0, 0, 0, 0], [0, 0, 1, 1, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 1, 0, 0, 0], [0, 0, 0, 0, 1, 1, 1, 0, 0],
                [0, 0, 0, 1, 0, 0, 0, 1, 0], [0, 0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0, 0, 1], [0, 0, 1, 0, 0, 0, 0, 0, 1],
                [0, 0, 0, 1, 0, 0, 0, 1, 0], [0, 0, 0, 0, 1, 1, 1, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 1, 0, 0, 0], [0, 0, 0, 0, 1, 1, 0, 0, 0]]
        return (ship_1, ship_2, fig_1, fig_2, fig_3, fig_4, ship_3, gun1)

    def glider_matrix(self, maps):
        all_ships = []
        for i in maps:
            all_ships.append(
                Glider(list(zip(*i)), BIGCELL, ENABLE, self))
        return all_ships

    def made_gui(self, groups, stx, sty, width, buttons=False):
        """
        Made buttons and labels objects
        """
        objects = {}
        menu_groups = groups

        total_x = 0
        for group in menu_groups:
            items = len(group)
            all_margin = LABELMARG * (items + 1)
            total_x += max([FONT_S.size(i)[0]
                            for i in group]) * items

            total_x += all_margin
        total_groups = len(menu_groups)

        group_dist = 0
        if total_groups > 1:
            group_dist = (width - total_x) / (total_groups - 1)

        # start x for first object
        start = stx
        for num_group in range(total_groups):
            # find biggest text in group
            xt = max([FONT_S.size(i)[0] for i in menu_groups[num_group]])
            yt = max([FONT_S.size(i)[1] for i in menu_groups[num_group]])

            for j in range(len(menu_groups[num_group])):
                cx = start + LABELMARG + xt / 2 + LABELMARG * j + xt * j
                cy = sty + LABELMARG + yt / 2

                # label obj frame = 0
                for bool_ in buttons[num_group]:
                    if bool_:
                        frame = (cx - xt / 2 - PADDING, cy - yt / 2 - PADDING,
                                 xt + PADDING * 2, yt + PADDING * 2)
                    else:
                        frame = False
                    scheme = {
                        'x': cx, 'y': cy, 'text': menu_groups[num_group][j],
                        'textsize': (xt, yt),
                        'fg': ENABLE, 'bg': None, 'anchor': 'center',
                        'framesize': frame, 'bd': BORBUT, 'bdcol': ENABLE,
                        'pad': PADDING
                    }
                    objects[menu_groups[num_group][j]] = scheme

            # change next start point anchor = center
            start = cx + xt / 2 + LABELMARG + group_dist
        return objects

    def scheme_user_menu(self):
        """
        Made blueprint for button in main menu
        """
        us_rct, us_str = self.make_labframe('GAME OF LIFE',
                                            FONT_L, FONT_S, None,
                                            WID // 2, HEI // 2, STR_TOT,
                                            fram=True, inf=False)
        x, y = us_rct.bottomleft
        user_menu_obj = self.made_gui([('DEL', 'EDIT', 'NEW'), ('OK',)],
                                      x - LABELMARG // 2, y,
                                      us_rct.width + LABELMARG,
                                      ([1, 1, 1], [1]))

        user_menu_obj['OK']['fg'] = DISABLE
        user_menu_obj['EDIT']['fg'] = DISABLE
        user_menu_obj['DEL']['fg'] = DISABLE

        return user_menu_obj, us_str, us_rct

    def scheme_bottom_menu(self):
        """
        Made blueprints for bottom menu
        """
        menu_groups = [('USER', 'EDIT'), ('SQUARE UNIVERSUM',),
                       ('CYCLE', 'EPOCHS', 'CELL', 'POPULUS'),
                       ('<<', 'FPS', '>>'),
                       ('CLEAR', 'STOP', 'START')]

        bottom_obj = self.made_gui(menu_groups, 0, GAME_HEI, WID,
                                   ([1, 1], [0],
                                    [0, 0, 0, 0],
                                    [1, 0, 1], [1, 1, 1]))

        # set up counters
        bottom_obj['POPULUS']['text'] = str(self.GL.score)
        bottom_obj['EPOCHS']['text'] = str(self.GL.epoh)
        bottom_obj['FPS']['text'] = str(self.fps)

        # chose enable/disable buttons for first time
        bottom_obj['STOP']['fg'] = DISABLE

        return bottom_obj

    def make_labframe(self, lab, font, font_s, s_clr, x, y, size,
                      fram=False, inf=False):
        """
        Made blueprints for first and last menu
        """
        xt, yt = font.size(lab)
        size_info = 0

        if inf:
            inf_l = len(inf)
            size_info = int(inf_l * F_HEI + STR_Y * (inf_l - 1) + STR_Y * 2)

        if size:
            size_info = size

        menu_sur = pygame.Surface((xt, size_info))
        menu_rct = menu_sur.get_rect()
        self.make_anchor(menu_rct, x, y - yt, 'center')

        usr_str = {}
        if inf:
            for i in range(inf_l):
                usr_str[f'stlft_{i}'] = self.ad_str(inf[i][0], font_s,
                                                    STR_Y,
                                                    STR_Y + STR_Y * 2 * i,
                                                    TXTCOL, s_clr, 'nw', fram)

                usr_str[f'strht_{i}'] = self.ad_str(inf[i][1], font_s,
                                                    xt - STR_Y,
                                                    STR_Y + STR_Y * 2 * i,
                                                    TXTCOL, s_clr, 'ne')

        usr_str['title'] = {'text': lab, 'font': font,
                            'x': menu_rct.centerx,
                            'y':  menu_rct.top - yt, 'anchor': 's',
                            'fg': TXTCOL, 'bg': None}

        return menu_rct, usr_str

    def ad_str(self, txt, font_s, x, y, fg_col, bg_col, anc, frame=False):
        rct = None
        if frame:
            rct = pygame.Rect(x - STR_Y, y - STR_Y // 2,
                              self.us_rct[2], STR_Y * 2)

        st = {'text': txt, 'font': font_s, 'framesize': rct,
              'x': x, 'y': y, 'anchor': anc, 'fg': fg_col, 'bg': bg_col}

        return st

    def place_menu(self, menu_pack):
        """
        Show buttons and labels
        """
        ob = dict(**menu_pack)
        for i in menu_pack:
            # frame show difference beetwen labels and buttons
            if ob[i]['framesize']:
                pygame.draw.rect(self.DISPLAY, ob[i]['bdcol'],
                                 ob[i]['framesize'], ob[i]['bd'])

            self.make_txt(ob[i]['text'],
                          FONT_S, self.DISPLAY,
                          ob[i]['x'], ob[i]['y'], ob[i]['anchor'],
                          fg=ob[i]['fg'], bg=ob[i]['bg'])

    def update_counters(self, gen, total_cell_scr):
        self.bottom_obj['POPULUS']['text'] = str(total_cell_scr)
        self.bottom_obj['EPOCHS']['text'] = str(gen)

    def change_fps(self, value):
        self.fps = value
        if self.fps >= 60:
            self.fps = 60
        if self.fps <= 0:
            self.fps = 1

        self.bottom_obj['FPS']['text'] = str(self.fps)

    def create_border(self, height=F_HEI):
        """
        Invisible border for gliders
        """
        sizex = LEFTMEN_WID - GLIDERMARG * 2
        sizey = (GAME_HEI - BOTMEN_HEI)

        rect = pygame.Rect(0, 0, sizex, sizey)
        rect.midtop = (LEFTMEN_WID // 2, LABELMARG * 2 + height)
        return rect

    def side_menu(self, txt, data):
        """
        Create side menu every iteration.
        """
        self.make_txt(txt,
                      FONT_S, self.side_menu_sur,
                      LEFTMEN_WID // 2, LABELMARG,
                      'n', fg=TXTCOL, bg=None)
        all_obj = []
        if not self.edit:
            # images
            start_img = GLIDEPAD
            next_rect_top = start_img

            for i in data[:]:
                obj = i.show((LEFTMEN_WID - GLIDERMARG * 2) // 2,
                             next_rect_top, 'n')
                next_rect_top = obj.bottom + GLIDEPAD
                all_obj.append(obj)
            return all_obj
        else:
            for i in data:
                pygame.draw.rect(self.gliders_sur, CELL_COLOR, i)
            return all_obj

    def game(self):
        while True:
            if not self.user:
                self.create_user()
            # game loop
            self.start_game()
            # game over screen
            self.end_game()

            pygame.display.update()
            self.CLOCK.tick(self.fps)

    def new_user(self, value=['NEW USER', '0'], edit=False):
        name_num = [0]
        # add all incoming objects
        if value[0].startswith('NEW USER') and value[0][-1].isdigit():
            name_num.append(int(value[0].split('_')[1]))

        # make different users numbers
        for i in self.usr_str:
            if self.usr_str[i]['text'].startswith('NEW USER'):
                name_num.append(int(self.usr_str[i]['text'].split('_')[1]))

        self.update_position()

        self.user_edit = edit
        # add new string
        # use len w -1 because title in list
        ind = (len(self.usr_str) - 1) // 2

        xt = self.us_rct[2]

        title = value[0]
        data = value[1]
        if value[0] == 'NEW USER':
            new_num = 0
            while new_num in name_num:
                new_num += 1

            title = f'{title}_{str(new_num)}'

        self.usr_str[f'stlft_{ind}'] = self.ad_str(title,
                                                   FONT_S, STR_Y,
                                                   STR_Y + STR_Y * 2 * ind,
                                                   TXTCOL, None, 'nw', True)
        self.usr_str[f'strht_{ind}'] = self.ad_str(data, FONT_S,
                                                   xt - STR_Y,
                                                   STR_Y + STR_Y * 2 * ind,
                                                   TXTCOL, None, 'ne')

        self.user = f'stlft_{ind}'
        # show new user
        self.change_position()
        # save new data
        self.save_user_glider(menu=True)

    def create_user(self):
        # made a scheme for menu
        self.usr_men_butt, self.usr_str, self.us_rct = self.scheme_user_menu()
        # load user images
        with shelve.open('0_life.dat') as data:
            for i in data.keys():
                self.new_user([i, str(len(data[i]))])

        final_selection = True
        while final_selection:
            self.DISPLAY.fill(BGCOL)

            if self.user:
                self.usr_men_butt['OK']['fg'] = ENABLE
                # move to ok function
                with shelve.open('0_life.dat') as data:
                    self.user_gliders = self.glider_matrix(data.get(
                        self.usr_str[self.user]['text'], []))
                for i in ('OK', 'EDIT', 'DEL'):
                    self.usr_men_butt[i]['fg'] = ENABLE

            final_selection = self.make_input_menu()

            self.show_labframe(self.us_rct, self.usr_str)
            # show buttons
            self.place_menu(self.usr_men_butt)

            pygame.display.update()
            self.CLOCK.tick(self.fps)

    def update_main_loop(self):
        """
        Use to show all widgets in mail loop
        """
        self.DISPLAY.fill(BGCOL)
        self.side_menu_sur.fill(BGCOL)
        self.gliders_sur.fill(GAME_CLR)
        # move game field in right place
        place = self.cell_matrix.get_rect()
        place.topright = (WID, 0)
        self.DISPLAY.blit(self.cell_matrix, place)

        # menu
        self.place_menu(self.bottom_obj)
        # gliders menu consist of two surfaces
        self.side_menu(*self.menu_content)
        side_menu_rct = self.side_menu_sur.get_rect()
        self.DISPLAY.blit(self.side_menu_sur, side_menu_rct)
        plc_glider = self.create_border()
        self.DISPLAY.blit(self.gliders_sur, (plc_glider[0],
                                             plc_glider[1]))

    def start_game(self):
        # made a scheme for menu
        self.bottom_obj = self.scheme_bottom_menu()
        game_loop = True
        self.cell_matrix.fill(GAME_CLR)
        while game_loop:
            # update main screen
            self.update_main_loop()
            # place here to correct filled buttons
            game_loop = self.make_input()
            if game_loop and self.start:

                game_loop = self.GL.start_life()

            # move glider cursor and switch to default
            if self.cursor and self.cursor.visible:
                pygame.mouse.set_visible(False)
                self.cursor.show(*pygame.mouse.get_pos(), 'nw')

            elif self.edit and self.see_editor:
                pygame.mouse.set_visible(False)
                pygame.draw.rect(self.DISPLAY, CELL_COLOR, self.edit_cursor)
                pygame.mouse.set_pos(self.edit_cursor.centerx,
                                     self.edit_cursor.centery)
            else:
                pygame.mouse.set_visible(True)

            # scroll with grag
            for i in self.user_gliders:
                mousey = pygame.mouse.get_rel()[1]
                if self.scroll:
                    i.delta += mousey

            real_fps = int(self.CLOCK.get_fps())
            if real_fps < self.fps:
                self.bottom_obj['FPS']['text'] = str(real_fps)

            pygame.display.update()
            self.CLOCK.tick(self.fps)

    def end_game(self):
        pygame.mouse.set_visible(True)
        pygame.mouse.set_cursor(*pygame.cursors.arrow)

        self.fin_m_obj, self.fin_m_rct, self.fin_m_str = self.make_fin_info()
        self.clear()
        end_loop = True
        while end_loop:
            # update main screen
            self.update_main_loop()
            # create trasparent field
            self.make_alpha(WID, HEI, self.DISPLAY, BGCOL)
            end_loop = self.make_input_end()

            self.show_labframe(self.fin_m_rct, self.fin_m_str)
            # show buttons
            self.place_menu(self.fin_m_obj)

            pygame.display.update()
            self.CLOCK.tick(self.fps)

    def clear(self):
        self.start = False
        # clear board
        self.cell_matrix.fill(GAME_CLR)
        # clear game logic
        self.GL.clear()

        self.menu_content = ('CREATURES', self.all_gliders)
        self.bottom_obj = self.scheme_bottom_menu()
        self.edit = False
        self.see_editor = False

        self.fps = FPS
        self.del_cursor()
        self.update_counters(0, 0)

    def make_fin_info(self):
        """
        Last menu scheme
        """
        st = 'CYCLE' if self.GL.epoh == 1 else 'CYCLES'

        info = [('LIFE EXIST', '%10i%9s' % (self.GL.epoh, st)),
                ('TOTAL', '%10i%10s' % (self.GL.score + self.GL.start_cell,
                                        'CELLS')),
                ('SEEDS', '%10i%10s' % (self.GL.start_cell, 'CELLS')),
                ('MAXIMUM', '%10i%10s' % (self.GL.max_score, 'CELLS'))]

        fin_menu_rct, fin_menu_str = self.make_labframe('EMPTY UNIVERSUM',
                                                        FONT_L, FONT_S, None,
                                                        WID // 2, HEI // 2, 0,
                                                        fram=False, inf=info)

        x, y = fin_menu_rct.bottomleft
        fin_menu_obj = self.made_gui([('RESTART LIFE',), ('SELECT USER',)],
                                     x - LABELMARG // 2, y,
                                     fin_menu_rct.width + LABELMARG,
                                     ([1], [1]))

        return fin_menu_obj, fin_menu_rct, fin_menu_str

    def make_alpha(self, wid, hei, surface, color):
        alpha = pygame.Surface((WID, HEI))
        alpha = alpha.convert_alpha()
        rect = alpha.get_rect()
        alpha.fill(BGCOL)
        self.DISPLAY.blit(alpha, rect)

    def show_labframe(self, rct, strings):
        """
        Show first and last frames with strigs.
        """
        menu_sur = pygame.Surface((rct[2], rct[3]))
        menu_sur.fill(GAME_CLR)
        menu_rct = menu_sur.get_rect()
        menu_rct.centerx = rct.centerx
        menu_rct.centery = rct.centery

        if strings:
            for i in strings:
                ob = strings[i]
                if i == 'title':
                    surface = self.DISPLAY
                else:
                    surface = menu_sur
                # add frame if selected
                if i == self.user and ob['framesize']:
                    rct = ob['framesize']
                    pygame.draw.rect(surface, FILLBUT, rct)
                self.make_txt(ob['text'],
                              ob['font'], surface,
                              ob['x'],
                              ob['y'], ob['anchor'],
                              ob['fg'], ob['bg'])
        self.blink_cursor(menu_sur)
        self.DISPLAY.blit(menu_sur, menu_rct)

    def make_input_menu(self):
        for e in pygame.event.get():
            if e.type == QUIT:
                self.make_exit()
            if e.type == KEYDOWN:
                if e.key == K_ESCAPE or (e.key == K_q and e.mod == 1024):
                    self.make_exit()

                if e.key == K_RETURN:
                    self.button_on(self.usr_men_butt['OK'])
                    self.user_edit = False
                    # select ok
                    return False

                # select with arrows by index
                if e.key == K_UP:
                    self.user_select_menu(-2)
                    self.user_edit = False
                if e.key == K_DOWN:
                    self.user_select_menu(2)
                    self.user_edit = False
                # ⌘ + N for new user
                if (e.key == K_n and e.mod == 1024):
                    self.button_on(self.usr_men_butt['NEW'])
                    self.new_user(edit=True)
                    # to prevent type N
                    return True
                # edit
                if (e.key == K_e and e.mod == 1024):
                    self.button_on(self.usr_men_butt['EDIT'])
                    self.user_edit = True
                    return True

                # edit main menu
                if self.user_edit:
                    self.edit_names(e)

            if e.type == KEYUP:
                self.button_blink(self.usr_men_butt)

            if e.type == MOUSEBUTTONUP:
                self.button_blink(self.usr_men_butt)

            if e.type == MOUSEBUTTONDOWN:
                # mouse selection
                user_mouse = (e.pos[0] - self.us_rct[0],
                              e.pos[1] - self.us_rct[1])

                ob = dict(**self.usr_str)
                for i in self.usr_str:
                    if i != 'title':
                        # check for delete
                        if (ob[i]['framesize'] and
                                self.us_rct.collidepoint(e.pos[0], e.pos[1])):
                            colider = pygame.Rect(ob[i]['framesize'])

                            if colider.collidepoint(*user_mouse):
                                if e.button == 1:
                                    self.user = i
                                    self.user_edit = False

                                if e.button == 3:
                                    self.user = i
                                    self.button_on(self.usr_men_butt['EDIT'])
                                    self.user_edit = True
                self.usr_str = dict(**ob)

                ob = dict(**self.usr_men_butt)
                for i in self.usr_men_butt:
                    if ob[i]['framesize']:
                        colider = pygame.Rect(ob[i]['framesize'])
                        if colider.collidepoint(e.pos[0], e.pos[1]):
                            if i == 'DEL' and self.user and e.button == 1:
                                self.button_on(ob[i])
                                self.delete_user_data()
                                self.user_edit = False
                            if i == 'EDIT' and self.user and e.button == 1:
                                self.button_on(ob[i])
                                self.user_edit = True
                            if i == 'NEW' and e.button == 1:
                                self.button_on(ob[i])
                                self.new_user(edit=True)
                            if i == 'OK' and self.user and e.button == 1:
                                self.user_edit = False
                                self.button_on(ob[i])
                                # select ok
                                return False

                # scrool in user menu
                if self.us_rct.collidepoint(e.pos[0], e.pos[1]):
                    if e.button == 4:
                        self.scrool_user_menu(16)
                    if e.button == 5:
                        self.scrool_user_menu(-16)

                self.usr_men_butt = dict(**ob)

        return True

    def make_input(self):
        for e in pygame.event.get():
            if e.type == QUIT:
                self.make_exit()
            if e.type == KEYDOWN:
                if e.key == K_ESCAPE or (e.key == K_q and e.mod == 1024):
                    self.make_exit()

                # run game
                if e.key == K_SPACE:
                    if self.start:
                        self.button_on(self.bottom_obj['STOP'])
                    else:
                        self.button_on(self.bottom_obj['START'])

                    self.start = not self.start

                # erase gliders in user menu
                if e.key == K_BACKSPACE:
                    self.overwrite_gliders()

            if e.type == KEYUP:
                if e.key == K_SPACE:
                    self.button_blink(self.bottom_obj)

            if e.type == MOUSEBUTTONUP:
                self.scroll = False
                self.GL.old_x, self.GL.old_y = None, None
                self.button_blink(self.bottom_obj)

            game_field = self.cell_matrix.get_rect()
            game_field.topright = (WID, 0)
            # invisible frame show in display coord
            gli_bor = self.create_border()

            # copy dict to make cleaner code and correctly show bottom buttons
            ob = dict(**self.bottom_obj)

            if e.type == MOUSEBUTTONDOWN:

                # for paint in editor
                mouse_glider = (e.pos[0] - gli_bor[0], e.pos[1] - gli_bor[1])
                # correction for mouse to paint in game field
                mouse_field = (e.pos[0] - WID - GAME_WID, e.pos[1])

                # return all bottom menu obj
                for num, obj in enumerate(self.side_menu(*self.menu_content)):
                    if pygame.Rect(obj).collidepoint(*mouse_glider):
                        if e.button == 1:
                            self.create_cursor(num, obj)
                        # erase gliders in user menu
                        if (e.button == 3 and
                                self.menu_content[1] == self.user_gliders):
                            self.overwrite_gliders()

                if self.edit and gli_bor.collidepoint(e.pos[0], e.pos[1]):
                    if e.button == 1:
                        self.made_creature_scheme(*mouse_glider)
                    else:
                        self.erase_creature_scheme(*mouse_glider)

                # use copy dict of all bottom but and after loop save changes
                for i in self.bottom_obj:
                    if ob[i]['framesize']:
                        colider = pygame.Rect(ob[i]['framesize'])
                        if colider.collidepoint(e.pos[0], e.pos[1]):
                            if i == 'STOP' and self.start:
                                self.start = False
                                self.button_on(ob[i])
                            if i == 'START' and not self.start:
                                self.start = True
                                self.button_on(ob[i])
                            if i == 'CLEAR' and not self.start:
                                self.button_on(ob[i])
                                self.clear()
                                self.bottom_obj = dict(**ob)
                                # to clear buttons
                                return True
                            if i == '>>':
                                self.change_fps(self.fps + 5)
                                self.button_on(ob[i])
                            if i == '<<':
                                self.change_fps(self.fps - 5)
                                self.button_on(ob[i])
                            if i == 'EDIT' and not self.start:
                                self.button_on(ob[i])
                                self.edit_but(ob, i,
                                              'MAKE', 'EDITOR',
                                              self.make_gliders)
                                self.edit = True

                            elif i == 'MAKE':
                                self.button_on(ob[i])
                                self.edit_but(ob, i,
                                              'EDIT',
                                              'CREATURES',
                                              self.user_gliders)
                                self.edit = False

                                if ob.get('USER'):
                                    self.edit_but(ob, 'USER',
                                                  'MAIN',
                                                  'CREATURES',
                                                  self.user_gliders)
                                self.made_glider()

                            elif i == 'USER':
                                self.button_on(ob[i])
                                self.edit_but(ob, i,
                                              'MAIN', 'CREATURES',
                                              self.user_gliders)
                                self.edit = False
                                # put all gliders in begining
                                for i in self.user_gliders:
                                    i.delta = 0

                                if ob.get('MAKE'):
                                    self.edit_but(ob, 'MAKE',
                                                  'EDIT',
                                                  'CREATURES',
                                                  self.user_gliders)
                            elif i == 'MAIN':
                                self.button_on(ob[i])
                                self.edit_but(ob, i,
                                              'USER', 'CREATURES',
                                              self.all_gliders)
                                self.edit = False

                                if ob.get('MAKE'):
                                    self.edit_but(ob, 'MAKE',
                                                  'EDIT',
                                                  'CREATURES',
                                                  self.all_gliders)
                            # prevent error in dictionary
                            break

                # make permanent changes
                self.bottom_obj = dict(**ob)

                # paint one dot or ship
                if game_field.collidepoint(e.pos[0], e.pos[1]):
                    # paint glider
                    if self.cursor and e.button == 1:
                        self.cursor.create_glider(*mouse_field)
                    # delete glider cursor
                    elif self.cursor and e.button == 3:
                        self.del_cursor()
                    else:
                        # paint cells
                        if e.button == 1:
                            self.GL.old_x, self.GL.old_y = mouse_field

                            self.GL.start_paint(*mouse_field)
                        if e.button == 3:
                            self.GL.erase = not self.GL.erase
                            # change cursor
                            if self.GL.erase:
                                curs = pygame.cursors.diamond
                            else:
                                curs = pygame.cursors.arrow
                            pygame.mouse.set_cursor(*curs)

            if e.type == MOUSEMOTION:
                self.button_blink(self.bottom_obj)

                # for paint in editor
                mouse_glider = (e.pos[0] - gli_bor[0], e.pos[1] - gli_bor[1])
                # for paint in game field
                mouse_field = (e.pos[0] - WID - GAME_WID, e.pos[1])
                # position of bottom menu
                bott_menu = pygame.Rect(0, 0, WID, GAME_HEI)

                if game_field.collidepoint(e.pos[0], e.pos[1]):
                    if self.cursor:
                        self.cursor.visible = True
                    # usual paint
                    if e.buttons[0] and not self.cursor:
                        self.GL.motion_paint(*mouse_field)
                    if self.GL.erase:
                        pygame.mouse.set_cursor(*pygame.cursors.diamond)
                else:
                    if self.cursor:
                        self.cursor.visible = False
                    pygame.mouse.set_cursor(*pygame.cursors.arrow)

                # delete cursor when enter bottom menu
                if not bott_menu.collidepoint(e.pos[0], e.pos[1]):
                    self.del_cursor()

                # paint in editor
                if self.edit and gli_bor.collidepoint(e.pos[0], e.pos[1]):
                    self.see_editor = True
                    if e.buttons[0]:
                        self.made_creature_scheme(*mouse_glider)
                    elif e.buttons[2]:
                        self.erase_creature_scheme(*mouse_glider)

                # scrool with drag in user menu
                elif (pygame.mouse.get_pressed()[0] and
                      gli_bor.collidepoint(e.pos[0], e.pos[1]) and
                      self.menu_content[1] == self.user_gliders):
                    obj = [i for i in (self.side_menu(*self.menu_content))]
                    obj.sort(key=lambda i: i[1])
                    min_ = obj[0]
                    max_ = obj[-1]
                    # e.rel show direction of move
                    if (min_.top <= GLIDEPAD and max_.bottom >= gli_bor[3]):
                        self.scroll = True
                    elif (min_.top <= GLIDEPAD and
                          max_.bottom <= gli_bor[3] and e.rel[1] > 0):
                        self.scroll = True
                    elif (min_.top >= GLIDEPAD and
                          max_.bottom >= gli_bor[3] and e.rel[1] < 0):
                        self.scroll = True
                    else:
                        self.scroll = False

                else:
                    self.see_editor = False

                # other way to make cursor
                self.edit_cursor.move_ip(e.pos[0] - self.edit_cursor.centerx,
                                         e.pos[1] - self.edit_cursor.centery)
        return True

    def make_input_end(self):
        for e in pygame.event.get():
            if e.type == QUIT:
                self.make_exit()
            if e.type == KEYUP:
                self.button_blink(self.fin_m_obj)
            if e.type == KEYDOWN:
                if e.key == K_ESCAPE or (e.key == K_q and e.mod == 1024):
                    self.make_exit()
                if e.key == K_SPACE:
                    self.button_on(self.fin_m_obj['RESTART LIFE'])
                    return False
                if e.key == K_RETURN:
                    self.button_on(self.fin_m_obj['SELECT USER'])
                    self.usr_str = []
                    self.user = False
                    return False
            if e.type == MOUSEBUTTONUP:
                self.button_blink(self.fin_m_obj)
            if e.type == MOUSEBUTTONDOWN:
                ob = dict(**self.fin_m_obj)
                for i in self.fin_m_obj:
                    if ob[i]['framesize']:
                        colider = pygame.Rect(ob[i]['framesize'])
                        if colider.collidepoint(e.pos[0], e.pos[1]):
                            if i == 'RESTART LIFE' and e.button == 1:
                                self.button_on(ob[i])
                                return False
                            if i == 'SELECT USER' and e.button == 1:
                                self.button_on(ob[i])
                                self.usr_str = []
                                self.user = False
                                return False
                self.fin_m_obj = dict(**ob)
        return True

    def edit_names(self, e):
        """
        Edit names of user accounts every iteration and correct same name.
        """
        edit_obj = self.usr_str[self.user]['text']
        self.color_cursor = TXTCOL
        self.blink_time = 10
        if e.unicode in ascii_lowercase:
            if edit_obj.startswith('NEW USER'):
                self.usr_str[self.user]['text'] = ''
            self.usr_str[self.user]['text'] += e.unicode.upper()

        if e.key == K_BACKSPACE:
            self.usr_str[self.user]['text'] = edit_obj[:-1]
        if e.key == K_SPACE:
            self.usr_str[self.user]['text'] += ' '
        # save account name every move
        with shelve.open('0_life.dat') as data:
            old_data = data[edit_obj]
            del data[edit_obj]
            if not self.usr_str[self.user]['text'] in data:
                data[self.usr_str[self.user]['text']] = old_data
            else:
                name = self.usr_str[self.user]['text']
                count = [i for i in data].count(name)
                self.usr_str[self.user]['text'] = name + f'{count+1}'
                data[self.usr_str[self.user]['text']] = old_data

    def blink_cursor(self, surface):
        if self.user_edit:
            if not self.blink_time and self.color_cursor == FILLBUT:
                self.color_cursor = TXTCOL
                self.blink_time = 10
            elif not self.blink_time and self.color_cursor == TXTCOL:
                self.color_cursor = FILLBUT
                self.blink_time = 10

            x = FONT_S.size(self.usr_str[self.user]['text'])[0] + 2
            y = STR_Y // 2 + self.usr_str[self.user]['y']
            self.text_cursor.midright = (STR_Y + x, y)
            pygame.draw.rect(surface, self.color_cursor,
                             self.text_cursor)

            self.blink_time -= 1

    def change_position(self):
        """
        Made selected string visible if it out of screen.
        """
        new_pos = 0
        obj = pygame.Rect(self.usr_str[self.user]['framesize'])
        if obj.top < 0:
            pos = obj.top
            new_pos = 0 - pos
        elif obj.bottom > self.us_rct[3]:
            pos = obj.bottom
            new_pos = self.us_rct[3] - pos

        self.scrool_user_menu(new_pos)

    def scrool_user_menu(self, mouse):
        """
        Use to select user account with scroll.
        """
        coord = self.sortred_str()

        delta = 0
        if coord:
            min_ = self.usr_str[coord[0][1]]['framesize']
            max_ = self.usr_str[coord[-2][1]]['framesize']
            if (min_.top <= 0 and max_.bottom >= self.us_rct[3]):
                delta = mouse
            elif (min_.top <= 0 and
                  max_.bottom <= self.us_rct[3]) and mouse > 0:
                delta = mouse
            elif (min_.top >= 0 and
                  max_.bottom >= self.us_rct[3]) and mouse < 0:
                delta = mouse

        for i in self.usr_str:
            if i != 'title':
                self.usr_str[i]['y'] += delta
                if self.usr_str[i]['framesize']:
                    self.usr_str[i]['framesize'].centery += delta

    def sortred_str(self):
        """
        List of coords for all strings in user menu.
        """
        coord = sorted([(self.usr_str[i]['y'], i)
                        for i in self.usr_str
                        if i != 'title'])
        return coord

    def user_select_menu(self, direct):
        """
        Use to select user account with arrows.
        """
        coord = self.sortred_str()
        lenght = len(coord)
        # current coord of object
        user_coord = self.usr_str[self.user]['y']

        # find nearest
        index = coord.index((user_coord, self.user))
        if index == 0 and direct < 0:
            direct = 0
        if index == lenght - 2 and direct > 0:
            direct = 0
        self.user = coord[index + direct][1]

        self.change_position()

    def delete_user_data(self):
        """
        Delete user accounts in first menu.
        """
        with shelve.open('0_life.dat') as data:
            del data[self.usr_str[self.user]['text']]
        # coords for select new user
        coord = self.sortred_str()

        take_old = coord.index(*[i for i in coord if i[1] == self.user])
        del self.usr_str[self.user]
        del self.usr_str['strht_%s' % self.user.split('_')[1]]

        self.update_position()
        # to find right position
        coord = self.sortred_str()

        if len(self.usr_str) > 1:
            # take a nearest or same
            if take_old >= len(coord):
                take_new = coord[take_old - 2][1]
            else:
                take_new = coord[take_old][1]
            self.user = take_new
            self.change_position()
        else:
            self.user = False

    def update_position(self):
        """
        Make default position after delete.
        """
        coord = self.sortred_str()
        info = []

        if coord:
            for i in range(0, len(coord), 2):
                left = coord[i][1]
                right = coord[i + 1][1]

                info.append((self.usr_str[left]['text'],
                             self.usr_str[right]['text']))

        self.us_rct, self.usr_str = self.make_labframe('GAME OF LIFE',
                                                       FONT_L, FONT_S,
                                                       None,
                                                       WID // 2, HEI // 2,
                                                       STR_TOT,
                                                       fram=True, inf=info)

    def made_glider(self):
        """
        Use to create gliders in editor.
        """
        matrix = []
        self.make_gliders.sort()
        if self.make_gliders:
            x0 = min(self.make_gliders)[0]
            x1 = max(self.make_gliders)[0]
            y0 = min(self.make_gliders, key=lambda i: i[1])[1]
            y1 = max(self.make_gliders, key=lambda i: i[1])[1]
            sizex = (x1 - x0) // BIGCELL
            sizey = (y1 - y0) // BIGCELL
            # add one to correct size and range
            for i in range(sizey + 1):
                row = []
                for j in range(sizex + 1):
                    goalx = j * BIGCELL + x0
                    goaly = i * BIGCELL + y0

                    if any([rect[0] == goalx and rect[1] == goaly
                            for rect in list(self.make_gliders)]):
                        row.append(1)
                    else:
                        row.append(0)
                matrix.append(row)
            self.make_gliders = []
            # save matrix not transpose matrix to database
            self.save_user_glider(matrix)

            matrix = list(zip(*matrix))
            self.user_gliders.append(Glider(matrix, BIGCELL, ENABLE, self))

    def save_user_glider(self, matr=False, menu=False):
        """
        Save matrix from editor to database
        """
        with shelve.open('0_life.dat') as data:
            if not menu and matr:
                if data.get(self.usr_str[self.user]['text']):
                    old_data = data[self.usr_str[self.user]['text']]
                    old_data.append(matr)
                    data[self.usr_str[self.user]['text']] = old_data
                else:
                    data[self.usr_str[self.user]['text']] = [matr]
            else:
                if data.get(self.usr_str[self.user]['text']):
                    old_data = data[self.usr_str[self.user]['text']]
                    data[self.usr_str[self.user]['text']] = old_data
                else:
                    data[self.usr_str[self.user]['text']] = []

    def overwrite_gliders(self):
        for i in self.user_gliders[:]:
            if i.selected:
                index = self.user_gliders.index(i)
                self.user_gliders.pop(index)
                with shelve.open('0_life.dat') as data:
                    old_data = data[self.usr_str[self.user]['text']]
                    old_data.pop(index)
                    data[self.usr_str[self.user]['text']] = old_data

    def made_creature_scheme(self, x, y):
        x = x // BIGCELL * BIGCELL
        y = y // BIGCELL * BIGCELL

        obj = pygame.Rect((x, y, BIGCELL, BIGCELL))

        if all([i[0] != x or i[1] != y for i in self.make_gliders]):
            self.make_gliders.append(obj)

    def erase_creature_scheme(self, x, y):
        x = x // BIGCELL * BIGCELL
        y = y // BIGCELL * BIGCELL
        for i in self.make_gliders[:]:
            if i[0] == x and i[1] == y:
                self.make_gliders.remove(i)

    def del_cursor(self):
        self.cursor = None
        # use two loops for prevent error with editor
        for i in self.all_gliders:
            i.set_color = ENABLE
            i.selected = False
        for i in self.user_gliders:
            i.set_color = ENABLE
            i.selected = False

    def create_cursor(self, num, obj):
        """
        Cursor for gliders in side menu.
        """
        if self.cursor:
            if self.menu_content[1][num].selected:
                # deselect glider if select same
                self.del_cursor()
                return
            self.del_cursor()
        self.erase = False
        self.menu_content[1][num].set_color = DISABLE
        # made cursor with image for game field
        self.cursor = Glider(self.menu_content[1][num].matrix,
                             SMALLCELL, ENABLE, self)

    def edit_but(self, menu, group, name, label, pack):
        """
        Change buttons labels.
        """
        menu[group]['text'] = name
        menu[name] = menu[group]
        del menu[group]
        self.menu_content = (label, pack)

    def button_blink(self, menu_pack):
        for i in menu_pack:
            self.button_off(menu_pack[i])
            # disable after click
            if self.start:
                if i == 'CLEAR' or i == 'START' or i == 'EDIT':
                    menu_pack[i]['fg'] = DISABLE
                elif i == 'STOP':
                    menu_pack[i]['fg'] = ENABLE
            else:
                if i == 'STOP':
                    menu_pack[i]['fg'] = DISABLE
                else:
                    menu_pack[i]['fg'] = ENABLE
            if not self.user:
                if i == 'OK' or i == 'EDIT' or i == 'DEL':
                    menu_pack[i]['fg'] = DISABLE

    def button_on(self, i):
        i['bdcol'] = FILLBUT
        i['bd'] = 0

    def button_off(self, i):
        i['bdcol'] = ENABLE
        i['bd'] = BORBUT

    def make_anchor(self, rect, x, y, anchor):
        if anchor == 'center':
            rect.centerx = x
            rect.centery = y
        elif anchor == 'n':
            rect.midtop = (x, y)
        elif anchor == 's':
            rect.midbottom = (x, y)
        elif anchor == 'w':
            rect.midleft = (x, y)
        elif anchor == 'e':
            rect.midright = (x, y)
        elif anchor == 'nw':
            rect.topleft = (x, y)
        elif anchor == 'ne':
            rect.topright = (x, y)
        elif anchor == 'se':
            rect.bottomright = (x, y)
        elif anchor == 'sw':
            rect.bottomleft = (x, y)
        return rect

    def make_txt(self, txt, font, surface, x, y, anchor, fg=TXTCOL, bg=None):
        obj = font.render(txt, 1, fg, bg)
        rect = obj.get_rect()
        rect = self.make_anchor(rect, x, y, anchor)
        surface.blit(obj, rect)

    def make_exit(self):
        pygame.quit()
        sysexit()


if __name__ == '__main__':
    print(__version__)
    print(__doc__)
    print(__file__)
    Main()
