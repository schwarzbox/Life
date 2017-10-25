#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# LIFE 6.0

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

# no evolution
# no virt_matrix
# on/off clean screen

import math
import sys
from itertools import chain, product
from glob import glob

import pygame
from pygame.locals import *

WID = 910
HEI = 680

GAME_WID = 800
GAME_HEI = 640

LEFTMEN_WID = WID - GAME_WID
BOTMEN_HEI = HEI - GAME_HEI

GLIDEBORMARG = 6
GLIDEPAD = 10

RED = (255, 55, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255, 200)
GRAY = (208, 208, 208, 100)
DARKGRAY = (138, 138, 138)

TXTCOL = BLACK
BGCOL = WHITE
GAME_COLOR = DARKGRAY
CELL_COLOR = RED

BORDER = GRAY
ENABLE = TXTCOL
DISABLE = GRAY

TXTMARG = 12
PADDING = 4

FPS = 20


class Main(object):

    def __init__(self):

        pygame.init()

        self.CLOCK = pygame.time.Clock()
        self.DISPLAY = pygame.display.set_mode((WID, HEI), 0, 32)

        # set up icon in taskbar
        icon = pygame.image.load('data/icon.png')
        pygame.display.set_icon(icon)

        pygame.display.set_caption('CONWAY\'S GAME OF LIFE')

        pygame.mouse.set_visible(True)

        self.FONT_L = pygame.font.Font('/System/Library/Fonts/SFNSText.ttf',
                                       26)
        self.FONT_M = pygame.font.Font('/System/Library/Fonts/SFNSText.ttf',
                                       16)
        self.FONT_S = pygame.font.Font('/System/Library/Fonts/SFNSText.ttf',
                                       13)
        # field for cells
        self.cell_matrix = pygame.Surface((GAME_WID, GAME_HEI))

        # left menu
        # original images
        self.all_gliders = [pygame.image.load(i) for i in glob('data/*.gif')]

        self.def_gliders = [self.all_gliders[i]
                            for i in range(0, len(self.all_gliders), 2)]
        self.inv_gliders = [self.all_gliders[i]
                            for i in range(1, len(self.all_gliders), 2)]

        gliders_func = (self.ship_1, self.ship_2, self.fig_1, self.fig_2,
                        self.fig_3, self.fig_4, self.ship_3)
        self.glider_coords = {i: gliders_func[i]
                              for i in range(len(self.def_gliders))}

        self.fps = FPS

        self.live = set()

        self.start_cell = 0
        self.global_gen = 0
        self.score = 0
        self.max_score = 0

        # paint
        self.motion = False
        self.erase = True
        self.old_x, self.old_y = None, None
        self.cursor = None
        # button var
        self.start = False

        # made a scheme for menu
        self.made_bottom_menu()

        # main loop
        self.game()

    def made_bottom_menu(self):
        """ made blueprint for bottom menu """
        self.bottom_obj = {}
        menu_groups = [('SQUARE UNIVERSUM',),
                       ('CYCLE', 'EPOCHS', 'CELL', 'POPULUS'),
                       ('<<', 'FPS', '>>'),
                       ('CLEAR', 'STOP', 'START')]

        total_x = 0
        for group in menu_groups:
            items = len(group)
            all_margin = TXTMARG * (items + 1)
            total_x += max([self.FONT_S.size(i)[0]
                            for i in group]) * items

            total_x += all_margin

        group_dist = (GAME_WID - total_x) / (len(menu_groups) - 1)
        # start x for first obj
        start = WID - GAME_WID
        for group in menu_groups:
            # find biggest text in group
            xt = max([self.FONT_S.size(i)[0] for i in group])
            yt = max([self.FONT_S.size(i)[1] for i in group])

            for j in range(len(group)):

                cx = start + TXTMARG + xt / 2 + TXTMARG * j + xt * j
                cy = GAME_HEI + TXTMARG + yt / 2

                # label frame = False
                if group[j] in ('START', 'STOP', 'CLEAR', '<<', '>>'):
                    frame = (cx - xt / 2 - PADDING, cy - yt / 2 - PADDING,
                             xt + PADDING * 2, yt + PADDING * 2)
                else:
                    frame = False
                # set up counters
                if group[j] == 'POPULUS':
                    text = str(self.score)
                elif group[j] == 'EPOCHS':
                    text = str(self.global_gen)
                elif group[j] == 'FPS':
                    text = str(self.fps)
                else:
                    text = group[j]
                scheme = {
                    'x': cx, 'y': cy, 'text': text,
                    'textsize': (xt, yt),
                    'fg': ENABLE, 'bg': None, 'anchor': 'center',
                    'framesize': frame, 'bd': 2, 'bdcol': GRAY,
                    'pad': PADDING
                }
                self.bottom_obj[group[j]] = scheme

            # change next start point
            start = cx + xt / 2 + TXTMARG + group_dist

    def game(self):
        while True:
            # game loop
            self.start_game()
            # game over screen
            self.end_game()

            pygame.display.update()
            self.CLOCK.tick(self.fps)

    def bottom_menu(self):
        # count distanse beetween groups
        ob = dict(**self.bottom_obj)
        for i in self.bottom_obj:

            # frame show difference beetwen labels and buttons
            if ob[i]['framesize']:
                pygame.draw.rect(self.DISPLAY, ob[i]['bdcol'],
                                 ob[i]['framesize'], ob[i]['bd'])

            self.make_txt(ob[i]['text'],
                          self.FONT_S, self.DISPLAY,
                          ob[i]['x'], ob[i]['y'], ob[i]['anchor'],
                          fg=ob[i]['fg'], bg=ob[i]['bg'])

    def gliders_menu(self):
        txt = 'CREATURES'
        width, height = self.FONT_S.size(txt)
        self.make_txt(txt,
                      self.FONT_S, self.DISPLAY,
                      LEFTMEN_WID // 2, TXTMARG,
                      'n', fg=TXTCOL, bg=None)

        # rectangle
        sizex = LEFTMEN_WID - GLIDEBORMARG * 2
        sizey = GAME_HEI - BOTMEN_HEI
        rect = pygame.Rect(0, 0, sizex, sizey)
        rect.midtop = (LEFTMEN_WID // 2, TXTMARG * 2 + height)

        pygame.draw.rect(self.DISPLAY, BORDER, rect, 2)
        # images
        start_img = TXTMARG * 2 + height
        next_rect_top = start_img + GLIDEPAD
        # list consist from usual and inverted images
        rect = []
        for i in range(len(self.def_gliders)):
            img_rect = self.def_gliders[i].get_rect()
            img_rect.centerx = LEFTMEN_WID // 2
            img_rect.top = next_rect_top
            self.DISPLAY.blit(self.def_gliders[i], img_rect)
            next_rect_top = img_rect.bottom + GLIDEPAD

            rect.append(img_rect)

        return rect

    def ship_1(self, x, y):
        xcell = y
        ycell = x

        pack = [(xcell, ycell), (xcell - 1, ycell), (xcell, ycell - 1),
                (xcell, ycell - 2), (xcell - 2, ycell - 1)]
        for i in pack:
            self.black_cell(i[0], i[1])

    def ship_2(self, x, y):
        xcell = y
        ycell = x

        pack = [(xcell, ycell), (xcell - 1, ycell), (xcell - 2, ycell),
                (xcell - 3, ycell - 1), (xcell, ycell - 1),
                (xcell, ycell - 2), (xcell, ycell - 3),
                (xcell - 1, ycell - 4), (xcell - 3, ycell - 4)]
        for i in pack:
            self.black_cell(i[0], i[1])

    def fig_1(self, x, y):
        xcell = y
        ycell = x

        pack = [(xcell, ycell), (xcell, ycell - 1), (xcell - 1, ycell - 1),
                (xcell - 2, ycell - 1), (xcell - 3, ycell - 1),
                (xcell - 3, ycell - 2)]
        for i in pack:
            self.black_cell(i[0], i[1])

    def fig_2(self, x, y):
        xcell = y
        ycell = x

        pack = [(xcell, ycell), (xcell - 1, ycell), (xcell - 2, ycell),
                (xcell - 1, ycell - 1), (xcell - 2, ycell + 1)]
        for i in pack:
            self.black_cell(i[0], i[1])

    def fig_3(self, x, y):
        xcell = y
        ycell = x

        pack = [(xcell, ycell), (xcell - 1, ycell), (xcell - 2, ycell - 1),
                (xcell - 2, ycell + 1), (xcell - 3, ycell),
                (xcell - 4, ycell), (xcell - 5, ycell), (xcell - 6, ycell),
                (xcell - 7, ycell - 1), (xcell - 7, ycell + 1),
                (xcell - 8, ycell), (xcell - 9, ycell)]
        for i in pack:
            self.black_cell(i[0], i[1])

    def fig_4(self, x, y):
        xcell = y
        ycell = x

        pack = [(xcell, ycell), (xcell - 1, ycell), (xcell - 2, ycell),
                (xcell - 2, ycell - 1), (xcell - 4, ycell),
                (xcell - 4, ycell - 2), (xcell - 4, ycell - 3),
                (xcell - 4, ycell - 4), (xcell - 3, ycell - 4),
                (xcell - 1, ycell - 3), (xcell - 1, ycell - 2),
                (xcell, ycell - 2), (xcell, ycell - 4)]
        for i in pack:
            self.black_cell(i[0], i[1])

    def ship_3(self, x, y):
        xcell = y
        ycell = x

        pack = [(xcell, ycell), (xcell - 1, ycell), (xcell - 1, ycell + 1),
                (xcell - 2, ycell), (xcell - 2, ycell + 2),
                (xcell - 3, ycell + 2), (xcell - 4, ycell + 2),
                (xcell - 3, ycell + 3), (xcell - 6, ycell + 1),
                (xcell - 7, ycell), (xcell - 9, ycell),
                (xcell - 9, ycell + 1), (xcell - 10, ycell + 1),
                (xcell - 10, ycell + 2), (xcell - 11, ycell + 3),
                (xcell - 13, ycell + 3), (xcell - 14, ycell + 3),
                (xcell - 14, ycell + 1), (xcell - 15, ycell),
                (xcell - 16, ycell), (xcell - 17, ycell + 1),
                (xcell - 17, ycell + 2), (xcell, ycell - 1),
                (xcell - 1, ycell - 1), (xcell - 1, ycell - 2),
                (xcell - 2, ycell - 1), (xcell - 2, ycell - 3),
                (xcell - 3, ycell - 3), (xcell - 3, ycell - 4),
                (xcell - 4, ycell - 3), (xcell - 6, ycell - 2),
                (xcell - 7, ycell - 1), (xcell - 9, ycell - 1),
                (xcell - 9, ycell - 2), (xcell - 10, ycell - 2),
                (xcell - 10, ycell - 3), (xcell - 11, ycell - 4),
                (xcell - 13, ycell - 4), (xcell - 14, ycell - 4),
                (xcell - 14, ycell - 2), (xcell - 15, ycell - 1),
                (xcell - 16, ycell - 1), (xcell - 17, ycell - 2),
                (xcell - 17, ycell - 3)]
        for i in pack:
            self.black_cell(i[0], i[1])

    def add_pixels(self, x, y):
        pack = []
        dist_x = (x - self.old_x)
        dist_y = (y - self.old_y)
        hyp = int(math.hypot(dist_x, dist_y))

        for i in range(hyp):
            x = int(i * (dist_x / hyp) + self.old_x)
            y = int(i * (dist_y / hyp) + self.old_y)
            pack.append((x, y))
        return pack

    def motion_paint(self, x, y):
        self.erase = False
        xcell = int(x)
        ycell = int(y)
        pack = []
        if self.old_x and self.old_y:
            pack = self.add_pixels(xcell, ycell)
        # make smooth painting
        self.old_x, self.old_y = xcell, ycell
        self.black_cell(ycell, xcell)
        for i in pack:
            self.black_cell(i[1], i[0])

    def start_paint(self, x, y):
        self.erase = True
        self.black_cell(y, x)

    def black_cell(self, y, x):

        x = x % GAME_WID
        y = y % GAME_HEI

        if (x, y) not in self.live:

            self.fill_black((x, y), CELL_COLOR)

            self.start_cell += 1
            self.live.add((x, y))
        else:
            if self.erase:
                if (x, y) in self.live:

                    self.fill_black((x, y), GAME_COLOR)

                    self.start_cell -= 1
                    self.live.remove((x, y))

    def fill_black(self, coords, color):
        x, y = coords

        # show evolution
        self.cell_matrix.set_at((x, y), color)

    def check_black(self, x, y, live, wid, hei):
        tot = 0
        around = (((-1 + x) % wid, (-1 + y) % hei),
                  ((0 + x) % wid, (-1 + y) % hei),
                  ((1 + x) % wid, (-1 + y) % hei),
                  ((-1 + x) % wid, y % hei),
                  ((1 + x) % wid, y % hei),
                  ((-1 + x) % wid, (1 + y) % hei),
                  ((0 + x) % wid, (1 + y) % hei),
                  ((1 + x) % wid, (1 + y) % hei))

        for i in range(8):
            x, y = around[i]
            if (x, y) in live:
                tot += 1
            if tot == 4:
                return tot

        return tot

    def find_cells(self, cell):
        x, y = cell

        for i, j in product(range(-1, 2), repeat=2):
            if any((i, j)):
                yield ((x + i, y + j))

    def check_live(self, live, wid, hei):
        new_live = set()
        born_app = new_live.add

        # clean live
        fut_live = list(live | set(chain(*map(self.find_cells, live))))

        for cell_num in range(len(fut_live)):
            xx, yy = fut_live[cell_num]

            # slow
            # total = sum([((i[0] % wid, i[1] % hei) in live)
            #              for i in self.find_cells((xx, yy))])
            total = self.check_black(xx, yy, live, wid, hei)

            if total == 3 or (total == 2 and (xx, yy) in live):
                xx = xx % wid
                yy = yy % hei
                born_app((xx, yy))

        return new_live

    def start_life(self):
        # for generation
        self.global_gen += 1

        tot = len(self.live)

        # update screen counters
        self.update_counters(self.global_gen, tot)

        # check coords
        self.live = self.check_live(self.live, GAME_WID, GAME_HEI)

        # clean field for next iteration with live cells

        for i in self.live:
            self.fill_black(i, CELL_COLOR)

        # counters for maximum population
        if not self.max_score:
            self.max_score = tot
        elif tot > self.max_score:
            self.max_score = tot
        else:
            self.max_score = self.max_score

        # after dead cells need to check how many stay alive
        tot = len(self.live)
        # count population
        self.score += tot

        # start goal for end message
        if tot == 0:
            return False
        # for stop button
        else:
            return True

    def start_game(self):
        game = True
        self.cell_matrix.fill(GAME_COLOR)
        while game:

            # update screen
            self.DISPLAY.fill(BGCOL)
            # move in right place
            place = self.cell_matrix.get_rect()
            place.topright = (WID, 0)
            self.DISPLAY.blit(self.cell_matrix, place)

            # menu
            self.bottom_menu()

            # gliders menu
            self.gliders_menu()

            game = self.make_input()
            # game code
            if game and self.start:
                # clean screen
                # self.cell_matrix.fill(GAME_COLOR)
                game = self.start_life()

            # move glider cursor and switch to default
            if self.cursor and self.cursor[3]:
                pygame.mouse.set_visible(False)

                self.cursor[1].midbottom = pygame.mouse.get_pos()
                self.DISPLAY.blit(self.cursor[0], self.cursor[1])
            else:
                pygame.mouse.set_visible(True)

            pygame.display.update()
            self.CLOCK.tick(self.fps)

            real_fps = int(self.CLOCK.get_fps())
            if real_fps < self.fps:
                self.bottom_obj['FPS']['text'] = str(real_fps)

    def end_game(self):
        pygame.mouse.set_visible(True)
        pygame.mouse.set_cursor(*pygame.cursors.arrow)

        self.create_fin_info()

        self.clear()
        for i in self.bottom_obj:
            self.button_off(self.bottom_obj[i])
            self.bottom_obj[i]['fg'] = ENABLE

        self.make_stop()

    def create_fin_info(self):
        top = (HEI // 2) - 150
        # string padding y
        pady = 30
        # create trasparent field
        alpha = pygame.Surface((WID, HEI))
        alpha = alpha.convert_alpha()
        rect = alpha.get_rect()

        alpha.fill(BGCOL)
        self.DISPLAY.blit(alpha, rect)

        mess = 'EMPTY UNIVERSUM'
        xt = self.FONT_L.size('EMPTY UNIVERSUM')[0]
        yt = self.FONT_S.size('EMPTY UNIVERSUM')[1]

        self.make_txt(mess,
                      self.FONT_L, self.DISPLAY,
                      WID // 2, top, 'center',
                      fg=TXTCOL, bg=None)
        c_st = 'CYCLE'.rjust(9) if self.global_gen == 1 else 'CYCLES'.rjust(8)
        info = [('LIFE EXIST',
                 str(self.global_gen) + c_st),
                ('POPULATION',
                 str(self.score + self.start_cell) + 'CELLS'.rjust(9)),
                ('SEEDS',
                 str(self.start_cell) + 'CELLS'.rjust(9)),
                ('MAXIMUM',
                 str(self.max_score) + 'CELLS'.rjust(9))]

        menu_rct = pygame.Rect(0, 0, xt, len(info) * (yt + pady))
        menu_rct.left = WID // 2 - xt // 2
        menu_rct.top = top + yt * 3

        pygame.draw.rect(self.DISPLAY, GRAY, menu_rct)

        for i in range(len(info)):
            self.make_txt(info[i][0],
                          self.FONT_S, self.DISPLAY,
                          menu_rct.left + pady,
                          menu_rct.top + pady + pady * i, 'e',
                          fg=TXTCOL, bg=None)
            self.make_txt(info[i][1],
                          self.FONT_S, self.DISPLAY,
                          menu_rct.right - pady,
                          menu_rct.top + pady + pady * i, 'w',
                          fg=TXTCOL, bg=None)

        self.make_txt('PRESS ANY KEY',
                      self.FONT_M, self.DISPLAY,
                      (WID // 2), menu_rct.bottom - pady, 'center',
                      fg=TXTCOL, bg=None)

    def clear(self):
        # clear board
        self.cell_matrix.fill(GAME_COLOR)

        self.del_cursor()

        self.fps = FPS
        self.live = set()
        self.start_cell = 0
        self.score = 0
        self.max_score = 0
        self.global_gen = 0

        self.update_counters(0, 0)

        self.start = False

    def del_cursor(self):

        self.cursor = None
        self.def_gliders = [self.all_gliders[i]
                            for i in range(0, len(self.all_gliders), 2)]

    def change_size(self, collection, num, obj):
        # made smaller cursor
        size = (int(obj[2] / 8), int(obj[3] / 8))
        img_cursor = pygame.transform.scale(collection[num], size)
        cursor = img_cursor.get_rect()

        fin_cursor = [img_cursor, cursor, num, False]
        return fin_cursor

    def create_cursor(self, num, obj):
        # made clear menu if choose same
        if self.cursor:
            if self.cursor[2] == num:
                self.del_cursor()
                return
            self.del_cursor()

        # made cursor with image and rect obj
        self.cursor = self.change_size(self.def_gliders, num, obj)
        # num for chose right function

        self.def_gliders[num] = self.inv_gliders[num]

    def update_counters(self, gen, tot):
        self.bottom_obj['POPULUS']['text'] = str(tot)
        self.bottom_obj['EPOCHS']['text'] = str(gen)

    def change_fps(self, value):
        self.fps = value
        if self.fps >= 60:
            self.fps = 60
        if self.fps <= 0:
            self.fps = 1

        self.bottom_obj['FPS']['text'] = str(self.fps)

    def button_on(self, i):
        i['bdcol'] = DARKGRAY
        i['bd'] = 0

    def button_off(self, i):
        i['bdcol'] = GRAY
        i['bd'] = 2

    def make_input(self):
        for e in pygame.event.get():
            if e.type == QUIT:
                self.make_exit()

            if e.type == KEYDOWN:

                if e.key == K_ESCAPE or (e.key == K_q and e.mod == 1024):
                    self.make_exit()

                # exit game loop
                if e.key == ord('q'):
                    return False

                if e.key == K_SPACE:
                    self.start = not self.start

            game_field = self.cell_matrix.get_rect()
            game_field.topright = (WID, 0)

            ob = dict(**self.bottom_obj)

            if e.type == MOUSEBUTTONUP:
                self.motion = False
                self.old_x, self.old_y = None, None

                for i in self.bottom_obj:
                    self.button_off(self.bottom_obj[i])

                    if self.start:
                        if i == 'CLEAR' or i == 'START':
                            ob[i]['fg'] = DISABLE
                    else:
                        ob[i]['fg'] = ENABLE

            if e.type == MOUSEBUTTONDOWN:
                # menu

                for i in self.bottom_obj:
                    if ob[i]['framesize']:
                        colider = pygame.Rect(ob[i]['framesize'])
                        if colider.collidepoint(e.pos[0], e.pos[1]):

                            if i == 'STOP':
                                self.start = False
                                self.button_on(ob[i])
                            if i == 'START' and not self.start:
                                self.start = True
                                self.button_on(ob[i])
                            if i == 'CLEAR' and not self.start:
                                self.button_on(ob[i])
                                self.clear()
                            if i == '>>':
                                self.change_fps(self.fps + 5)
                                self.button_on(ob[i])
                            if i == '<<':
                                self.change_fps(self.fps - 5)
                                self.button_on(ob[i])

                for num, obj in enumerate(self.gliders_menu()):
                    colider = pygame.Rect(obj)
                    if colider.collidepoint(e.pos[0], e.pos[1]):
                        self.create_cursor(num, obj)

                # paint one dot or ship
                if game_field.collidepoint(e.pos[0], e.pos[1]):
                    self.motion = True
                    # correction for mouse in game field
                    mouse = (e.pos[0] - WID - GAME_WID, e.pos[1])
                    # solve problem with alone dot
                    self.old_x, self.old_y = mouse
                    # made a ship or paint dots
                    if self.cursor and e.button == 1:
                        # run function with glider coords
                        self.glider_coords[self.cursor[2]](*mouse)

                    else:
                        self.start_paint(*mouse)
                    # delete ship by second button
                    if e.button == 3:
                        self.del_cursor()

            if e.type == MOUSEMOTION:
                mouse = (e.pos[0] - WID - GAME_WID, e.pos[1])
                if game_field.collidepoint(e.pos[0], e.pos[1]):

                    if self.cursor:
                        # var for show cursor
                        self.cursor[3] = True
                        self.motion = False

                    if self.motion:
                        self.motion_paint(*mouse)

                    # set up cursor invisible when ship selected
                    pygame.mouse.set_cursor(*pygame.cursors.broken_x)

                else:
                    if self.cursor:
                        self.cursor[3] = False
                    pygame.mouse.set_cursor(*pygame.cursors.arrow)
                # check if mouse not in bottom menu
                colider = pygame.Rect(0, 0, WID, GAME_HEI)
                if not colider.collidepoint(e.pos[0], e.pos[1]):
                    self.del_cursor()

        return True

    def make_txt(self, txt, font, surface, x, y, anchor, fg=TXTCOL, bg=None):
        obj = font.render(txt, 1, fg, bg)
        rect = obj.get_rect()

        if anchor == 'center':
            rect.centerx = x
            rect.centery = y
        elif anchor == 'n':
            rect.midtop = (x, y)
        elif anchor == 's':
            rect.midbottom = (x, y)
        elif anchor == 'e':
            rect.midleft = (x, y)
        elif anchor == 'w':
            rect.midright = (x, y)
        elif anchor == 'nw':
            rect.topleft = (x, y)
        elif anchor == 'ne':
            rect.topright = (x, y)
        elif anchor == 'se':
            rect.bottomright = (x, y)
        elif anchor == 'sw':
            rect.bottomleft = (x, y)

        surface.blit(obj, rect)

    def make_stop(self):
        pygame.display.update()
        while True:
            for e in pygame.event.get():
                if e.type == QUIT:
                    self.make_exit()
                if e.type == KEYDOWN:
                    if e.key == K_ESCAPE:
                        self.make_exit()
                    return

    def make_exit(self):
        pygame.quit()
        sys.exit()


if __name__ == '__main__':
    Main()
