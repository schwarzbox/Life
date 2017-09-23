#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# LIFE 4.5

# 1.0 (2016 - 3 days to build, but I am only start to code!)
# 3.0 (2017 - use signal flag to stop, many comments with old code)
# 3.5 (2017 – erase all time, after_cancel improve speed, pep-8)
# 4.0 (2017 – 4 px. very slow with fill pixels, after 200 epochs)
# 4.5 (2017 – 1 px. improve painting and syntax, slow with 600 pixels)
# 5.0 (2017 – 1 px, virtual matrix, slow 900 pix, del self.cell size)
# 5.1 (2017 – 1 px. virtual matrix, total update very slow)
# 5.2 (2017 - 1 px. thread pool executor, same perfomans)
# 6.0 (2017 - 1 px. use pygame, made simple GUI by pygame)

import math
from tkinter import (BOTH, BOTTOM, Button, CENTER, Canvas, Frame, LEFT, Label,
                     NW, PhotoImage, RIGHT, S, SE, TOP, Tk,
                     Toplevel, X, Y, YES)


class Main(object):

    def __init__(self, master):
        self.master = master
        self.master.title('CONWAY\'S GAME OF LIFE')
        self.master.geometry('910x680+200+50')
        self.master.resizable(width=False, height=False)

        # create a main field
        self.can_width = 800
        self.can_height = 640

        # variable to continue with right number generation after stop game
        self.global_gen = None
        # start
        self.cell = 1
        self.start_cell = 0
        self.live = set()
        # trick for rigth after_cancel
        self.game_on = (0, 0)
        # population
        self.score = 0
        # variable for max cells
        self.max_score = 0
        # for change speed
        self.timer = 15
        # cursor for place ships
        self.cur = None
        self.invert = None
        self.on = (0, 0)
        self.sample = {'1': 10, '2': 5, '4': 3}

        # erase seeds
        self.erase = True

        # images for ships
        self.glider = PhotoImage(file='1_ship.gif')
        self.glider_in = PhotoImage(file='1_ship_in.gif')
        self.lss = PhotoImage(file='2_lss.gif')
        self.lss_in = PhotoImage(file='2_lss_in.gif')
        self.sui = PhotoImage(file='3_sucide.gif')
        self.sui_in = PhotoImage(file='3_sucide_in.gif')
        self.f5 = PhotoImage(file='4_f5.gif')
        self.f5_in = PhotoImage(file='4_f5_in.gif')
        self.penta = PhotoImage(file='5_penta.gif')
        self.penta_in = PhotoImage(file='5_penta_in.gif')
        self.patern = PhotoImage(file='6_patern.gif')
        self.patern_in = PhotoImage(file='6_patern_in.gif')
        self.fireship = PhotoImage(file='7_fireship.gif')
        self.fireship_in = PhotoImage(file='7_fireship_in.gif')

        # GUI
        frameWin = Frame(master, bg='white', borderwidth=0)
        frameWin.pack(side=TOP, fill=BOTH)

        frameCanv = Frame(frameWin, bg='white', borderwidth=0)
        frameCanv.pack(side=RIGHT, fill=BOTH)

        # main canvas
        self.window = Canvas(frameCanv,
                             width=self.can_width,
                             height=self.can_height,
                             cursor='plus',
                             bg='white',
                             bd=0,
                             highlightthickness=0)
        self.window.pack(side=TOP)

        self.w_field = self.can_width // self.cell
        self.h_field = self.can_height // self.cell

        self.cell_matrix = PhotoImage(width=self.can_width,
                                      height=self.can_height)
        hor_line = '{' + ' '.join(['#EEEEEE'] * self.can_width) + '}'
        self.cell_matrix.put(' '.join([hor_line] * self.can_height))
        # make copy
        self.original = self.cell_matrix.copy()

        self.cell_img = self.window.create_image(0, 0,
                                                 image=self.cell_matrix,
                                                 anchor=NW)

        # side menu for images
        frameBorderCr = Frame(frameWin, bg='white', bd=3)
        frameBorderCr.pack(side=LEFT, fill=BOTH)
        mes_creat = Label(frameBorderCr, text='CREATURE',
                          height=2, bg='white')
        mes_creat.pack(side=TOP, fill=X)

        frameCreat = Frame(frameBorderCr, bg='gray', bd=2)
        frameCreat.pack(side=TOP, fill=BOTH)

        self.creat = Canvas(frameCreat,
                            height=596,
                            bg='white',
                            highlightthickness=0)
        self.creat.pack(side=TOP, expand=YES, fill=Y)

        # images for ships
        self.creat.create_image(48, 25, image=self.glider)
        self.creat.create_image(48, 73, image=self.lss)
        self.creat.create_image(48, 126, image=self.sui)
        self.creat.create_image(48, 175, image=self.f5)
        self.creat.create_image(48, 256, image=self.penta)
        self.creat.create_image(48, 349, image=self.patern)
        self.creat.create_image(49, 485, image=self.fireship)

        # menu for counters
        frameMB = Frame(frameCanv, bg='white', borderwidth=0)
        frameMB.pack(side=BOTTOM, fill=BOTH)

        message = Label(frameMB, text='SQUARE UNIVERSUM ',
                        height=2, bg='white')
        message.pack(side=LEFT, fill=X)

        # cell part
        frameBor1 = Frame(frameMB, bg='gray', borderwidth=2)
        frameBor1.pack(side=LEFT)
        name_pop = Label(frameBor1, text='CELL')
        name_pop.pack(side=LEFT)
        self.scrPop = Label(frameBor1, text=0, width=7)
        self.scrPop.pack(side=RIGHT)

        # separator
        sep = Frame(frameMB, width=4)
        sep.pack(side=LEFT)

        # cycle part
        frameBor2 = Frame(frameMB, bg='gray', borderwidth=2)
        frameBor2.pack(side=LEFT)
        name_gen = Label(frameBor2, text='CYCLE')
        name_gen.pack(side=LEFT)
        self.scrGen = Label(frameBor2, text=0, width=6)
        self.scrGen.pack(side=RIGHT)

        # buttons
        self.button_Start = Button(frameMB,
                                   text='START',
                                   width=6,
                                   command=self.start_game)

        self.button_Start.pack(side=RIGHT, padx=3)

        self.button_Stop = Button(frameMB,
                                  text='STOP',
                                  width=6,
                                  command=self.stop_game)
        self.button_Stop.pack(side=RIGHT, padx=3)

        self.button_Clear = Button(frameMB,
                                   text='CLEAR',
                                   width=6,
                                   command=self.clear)
        self.button_Clear.pack(side=RIGHT, padx=3)

        blockSpeed = Frame(frameMB, padx=25)
        blockSpeed.pack(side=RIGHT)

        button_Fast = Button(blockSpeed,
                             text='>>',
                             width=3,
                             command=self.fast)
        button_Fast.pack(side=RIGHT, padx=3)

        butSpeedFrame = Frame(blockSpeed, bg='gray', bd=2)
        butSpeedFrame.pack(side=RIGHT)

        self.speedVal = Label(butSpeedFrame, text=int(self.timer), width=3)
        self.speedVal.pack(side=RIGHT)

        button_Slow = Button(blockSpeed,
                             text='<<',
                             width=3,
                             command=self.slow)
        button_Slow.pack(side=RIGHT, padx=3)

        self.window.bind('<B1-Motion>', self.motion_paint)
        self.window.bind('<ButtonPress-1>', self.start_paint)
        self.window.bind('<ButtonPress-2>', self.clear_side_menu)

        self.window.bind('<Leave>', self.clear_side_menu)
        self.creat.bind('<ButtonPress-1>', self.creatures)

        self.master.mainloop()

    def add_pixels(self, x, y):
        pack = []
        dist_x = (x - self.fir_x)
        dist_y = (y - self.fir_y)
        hyp = int(math.hypot(dist_x, dist_y))

        for i in range(hyp):
            x = int(i * (dist_x / hyp) + self.fir_x)
            y = int(i * (dist_y / hyp) + self.fir_y)
            pack.append((x, y))
        return pack

    def motion_paint(self, event):
        self.erase = False
        xcell = int(event.x)
        ycell = int(event.y)
        # 1 pix
        # xcell = int(x // self.cell)
        # ycell = int(y // self.cell)
        # 1 pix
        pack = self.add_pixels(xcell, ycell)

        self.fir_x, self.fir_y = xcell, ycell
        self.black_cell(ycell, xcell)
        for i in pack:
            self.black_cell(i[1], i[0])

    def start_paint(self, event):
        self.erase = True
        # 1 pix
        # self.fir_x = event.x // self.cell
        # self.fir_y = event.y // self.cell

        self.fir_x = event.x
        self.fir_y = event.y

        self.black_cell(self.fir_y, self.fir_x)

    def creatures(self, event):
        # I can realize with standart buttons and compound
        x = int(event.x)
        y = int(event.y)

        if self.invert:
            # clear menu with figures
            self.clear_side_menu()
        else:
            self.on = (0, 0)

        if x in range(32, 65) and y in range(10, 45):
            self.creat_but(x, y, 32, 65, 10, 45, 48, 25,
                           self.glider_in, self.glider, self.ship_1, SE)

        if x in range(20, 75) and y in range(54, 96):
            self.creat_but(x, y, 20, 75, 54, 96, 48, 73,
                           self.lss_in, self.lss, self.ship_2, SE)

        if x in range(32, 65) and y in range(107, 149):
            self.creat_but(x, y, 32, 65, 107, 149, 48, 126,
                           self.sui_in, self.sui, self.fig_1, S)

        if x in range(32, 65) and y in range(161, 192):
            self.creat_but(x, y, 32, 65, 161, 192, 48, 175,
                           self.f5_in, self.f5, self.fig_2, CENTER)

        if x in range(32, 65) and y in range(203, 313):
            self.creat_but(x, y, 32, 65, 203, 313, 48, 256,
                           self.penta_in, self.penta, self.fig_3, S)

        if x in range(21, 75) and y in range(323, 377):
            self.creat_but(x, y, 21, 75, 323, 377, 48, 349,
                           self.patern_in, self.patern, self.fig_4, SE)

        if x in range(6, 93) and y in range(388, 588):
            self.creat_but(x, y, 6, 93, 388, 588, 48, 485,
                           self.fireship_in, self.fireship, self.ship_3, S)

    def creat_but(self, x, y, fnx, lnx, fny, lny,
                  x_im, y_im, img_in, img, bind, al):
        self.window.unbind('<B1-Motion>')
        if self.cur:
            self.window.delete(self.cur)
            self.cur = None
        if (self.on[0] not in range(fnx, lnx) or
                self.on[1] not in range(fny, lny)):

            self.invert = self.creat.create_image(x_im, y_im, image=img_in)
            self.window.bind('<ButtonPress-1>', bind)
            self.on = (x, y)
            # size of pictures depend of self.cell
            size = self.sample[str(self.cell)]
            img = img.subsample(size, size)
            self.window.bind('<Motion>', lambda event, i=img,
                             a=al: self.cursor(event, i, a))

    def cursor(self, event, img, align):
        self.erase = False
        self.window.configure(cursor='none')
        if not self.cur:
            self.cur = self.window.create_image(
                event.x, event.y, image=img, anchor=align)
        self.window.coords(self.cur, (event.x, event.y))

    def ship_1(self, event):
        x = int(event.x)
        y = int(event.y)
        xcell = int(y / self.cell)
        ycell = int(x / self.cell)
        pack = [(xcell, ycell), (xcell - 1, ycell), (xcell, ycell - 1),
                (xcell, ycell - 2), (xcell - 2, ycell - 1)]
        for i in pack:
            self.black_cell(i[0], i[1])

    def ship_2(self, event):
        x = int(event.x)
        y = int(event.y)
        xcell = int(y / self.cell)
        ycell = int(x / self.cell)

        pack = [(xcell, ycell), (xcell - 1, ycell), (xcell - 2, ycell),
                (xcell - 3, ycell - 1), (xcell, ycell - 1),
                (xcell, ycell - 2), (xcell, ycell - 3),
                (xcell - 1, ycell - 4), (xcell - 3, ycell - 4)]
        for i in pack:
            self.black_cell(i[0], i[1])

    def fig_1(self, event):
        x = int(event.x)
        y = int(event.y)
        xcell = int(y / self.cell)
        ycell = int(x / self.cell)

        pack = [(xcell, ycell), (xcell, ycell - 1), (xcell - 1, ycell - 1),
                (xcell - 2, ycell - 1), (xcell - 3, ycell - 1),
                (xcell - 3, ycell - 2)]
        for i in pack:
            self.black_cell(i[0], i[1])

    def fig_2(self, event):
        x = int(event.x)
        y = int(event.y)
        xcell = int(y / self.cell)
        ycell = int(x / self.cell)

        pack = [(xcell, ycell), (xcell - 1, ycell), (xcell - 2, ycell),
                (xcell - 1, ycell - 1), (xcell - 2, ycell + 1)]
        for i in pack:
            self.black_cell(i[0], i[1])

    def fig_3(self, event):
        x = int(event.x)
        y = int(event.y)
        xcell = int(y / self.cell)
        ycell = int(x / self.cell)

        self.black_cell(xcell, ycell)
        self.black_cell(xcell - 1, ycell)
        self.black_cell(xcell - 2, ycell - 1)
        self.black_cell(xcell - 2, ycell + 1)
        self.black_cell(xcell - 3, ycell)
        self.black_cell(xcell - 4, ycell)
        self.black_cell(xcell - 5, ycell)
        self.black_cell(xcell - 6, ycell)
        self.black_cell(xcell - 7, ycell - 1)
        self.black_cell(xcell - 7, ycell + 1)
        self.black_cell(xcell - 8, ycell)
        self.black_cell(xcell - 9, ycell)

    def fig_4(self, event):
        x = int(event.x)
        y = int(event.y)
        xcell = int(y / self.cell)
        ycell = int(x / self.cell)

        self.black_cell(xcell, ycell)
        self.black_cell(xcell - 1, ycell)
        self.black_cell(xcell - 2, ycell)
        self.black_cell(xcell - 2, ycell - 1)
        self.black_cell(xcell - 4, ycell)
        self.black_cell(xcell - 4, ycell - 2)
        self.black_cell(xcell - 4, ycell - 3)
        self.black_cell(xcell - 4, ycell - 4)
        self.black_cell(xcell - 3, ycell - 4)
        self.black_cell(xcell - 1, ycell - 3)
        self.black_cell(xcell - 1, ycell - 2)
        self.black_cell(xcell, ycell - 2)
        self.black_cell(xcell, ycell - 4)

    def ship_3(self, event):
        x = int(event.x)
        y = int(event.y)
        xcell = int(y / self.cell)
        ycell = int(x / self.cell)

        self.black_cell(xcell, ycell)
        self.black_cell(xcell - 1, ycell)
        self.black_cell(xcell - 1, ycell + 1)
        self.black_cell(xcell - 2, ycell)
        self.black_cell(xcell - 2, ycell + 2)
        self.black_cell(xcell - 3, ycell + 2)
        self.black_cell(xcell - 4, ycell + 2)
        self.black_cell(xcell - 3, ycell + 3)
        self.black_cell(xcell - 6, ycell + 1)
        self.black_cell(xcell - 7, ycell)
        self.black_cell(xcell - 9, ycell)
        self.black_cell(xcell - 9, ycell + 1)
        self.black_cell(xcell - 10, ycell + 1)
        self.black_cell(xcell - 10, ycell + 2)
        self.black_cell(xcell - 11, ycell + 3)
        self.black_cell(xcell - 13, ycell + 3)
        self.black_cell(xcell - 14, ycell + 3)
        self.black_cell(xcell - 14, ycell + 1)
        self.black_cell(xcell - 15, ycell)
        self.black_cell(xcell - 16, ycell)
        self.black_cell(xcell - 17, ycell + 1)
        self.black_cell(xcell - 17, ycell + 2)

        self.black_cell(xcell, ycell - 1)
        self.black_cell(xcell - 1, ycell - 1)
        self.black_cell(xcell - 1, ycell - 2)
        self.black_cell(xcell - 2, ycell - 1)
        self.black_cell(xcell - 2, ycell - 3)
        self.black_cell(xcell - 3, ycell - 3)
        self.black_cell(xcell - 3, ycell - 4)
        self.black_cell(xcell - 4, ycell - 3)
        self.black_cell(xcell - 6, ycell - 2)
        self.black_cell(xcell - 7, ycell - 1)
        self.black_cell(xcell - 9, ycell - 1)
        self.black_cell(xcell - 9, ycell - 2)
        self.black_cell(xcell - 10, ycell - 2)
        self.black_cell(xcell - 10, ycell - 3)
        self.black_cell(xcell - 11, ycell - 4)
        self.black_cell(xcell - 13, ycell - 4)
        self.black_cell(xcell - 14, ycell - 4)
        self.black_cell(xcell - 14, ycell - 2)
        self.black_cell(xcell - 15, ycell - 1)
        self.black_cell(xcell - 16, ycell - 1)
        self.black_cell(xcell - 17, ycell - 2)
        self.black_cell(xcell - 17, ycell - 3)

    def black_cell(self, y, x):

        x = x % self.w_field
        y = y % self.h_field
        # 1 pixel
        # x = x * self.cell + self.cell // 2
        # y = y * self.cell + self.cell // 2

        if self.cell_matrix.get(x, y) == '238 238 238':
            self.fill_black(x, y, '#000000')

            self.start_cell += 1
            self.live.add((x, y))
        else:
            if self.erase:
                if self.cell_matrix.get(x, y) == '0 0 0':
                    self.fill_black(x, y, '#EEEEEE')

                    self.start_cell -= 1
                    self.live.remove((x, y))

    def fill_black(self, x, y, color):
        # leave some borders for 4 px but it is to heavy task
        # for i in range((-self.cell // 2) - 1, (self.cell // 2) - 1):
        #     for j in range((-self.cell // 2) - 1, (self.cell // 2) - 1):
        #         xx = (x + i) % self.can_width
        #         yy = (y + j) % self.can_height
        self.cell_matrix.put(color, (x, y))

    def check_black(self, x, y, color):

        total = 8
        for i in [(-1, -1), (0, -1),
                  (1, -1), (-1, 0),
                  (1, 0), (-1, 1),
                  (0, 1), (1, 1)]:
            # xi = (x + i[0] * self.cell) % self.can_width
            # yi = (y + i[1] * self.cell) % self.can_height
            # 1 pixel
            xi = (x + i[0]) % self.can_width
            yi = (y + i[1]) % self.can_height

            if self.cell_matrix.get(xi, yi) == color:
                total -= 1

        return total

    def start_game(self):
        self.button_Start.configure(state='disabled')
        self.button_Clear.configure(state='disabled')

        self.start_cycle()

    def start_cycle(self):
        if self.global_gen:
            gen = self.global_gen
        else:
            gen = 1

        tot = len(self.live)
        # clean
        self.born = []
        self.dead = []

        for i, j in self.live:

            total = self.check_black(i, j, '238 238 238')

            if total < 2:
                self.dead.append((i, j))

            if total > 3:
                self.dead.append((i, j))

            # check if new cell wass born
            for xy in [(i - self.cell, j - self.cell), (i, j - self.cell),
                       (i + self.cell, j - self.cell), (i - self.cell, j),
                       (i + self.cell, j), (i - self.cell, j + self.cell),
                       (i, j + self.cell), (i + self.cell, j + self.cell)]:

                total = self.check_black(xy[0], xy[1], '0 0 0')

            # invert rule need 3 cells to born new
                if total == 5:
                    xy0 = xy[0] % self.can_width
                    xy1 = xy[1] % self.can_height
                    self.born.append((xy0, xy1))

        self.scrPop.configure(text=tot)
        self.scrGen.configure(text=gen)

        for i in self.dead:
            self.live.remove(i)
            xd, yd = i
            self.fill_black(xd, yd, '#EEEEEE')

        for i in self.born:
            self.live.add(i)
            xb, yb = i
            self.fill_black(xb, yb, '#000000')

        # counters for maximum population
        if self.max_score is False:
            self.max_score = tot
        elif tot > self.max_score:
            self.max_score = tot
        else:
            self.max_score = self.max_score

        # for generation
        gen += 1
        self.global_gen = gen

        # after dead cells need to check how many stay alive
        tot += len(self.born) - len(self.dead)
        # count population
        self.score += tot

        # start goal for end message
        if tot == 0:
            self.game_over(tot, gen)
        # for stop button
        else:
            self.game_on = self.window.after(self.timer, self.start_cycle)

    def stop_game(self):
        self.window.after_cancel(self.game_on)
        self.button_Start.configure(state='normal')
        self.button_Clear.configure(state='normal')

    def clear_side_menu(self, event=None):
        self.window.unbind('<Motion>')
        self.creat.delete(self.invert)
        self.invert = None
        self.window.bind('<ButtonPress-1>', self.start_paint)
        self.window.bind('<B1-Motion>', self.motion_paint)

        self.window.configure(cursor='plus')
        if self.cur:
            self.window.delete(self.cur)

    def clear(self):
        self.cell_matrix = self.original.copy()
        self.window.itemconfigure(self.cell_img, image=self.cell_matrix)

        self.scrPop.configure(text=0)
        self.scrGen.configure(text=0)
        # clear menu with figures
        self.clear_side_menu()
        self.start_cell = 0
        self.live = set()
        self.score = 0
        self.max_score = 0
        self.global_gen = None

    def fast(self):
        self.timer -= 1
        if self.timer < 1:
            self.timer = 1
        self.speedVal.configure(text=int(self.timer))

    def slow(self):
        self.timer += 1
        if self.timer > 15:
            self.timer = 15
        self.speedVal.configure(text=int(self.timer))

    def game_over(self, tot, gen):
        self.window.after_cancel(self.game_on)
        self.global_gen = 0
        self.scrPop.configure(text=tot)
        self.scrGen.configure(text=self.global_gen)
        self.creat.delete(self.invert)

        self.button_Stop.configure(state='disabled')
        end_menu = End(self.master, gen, self.start_cell,
                       self.score, self.max_score)
        self.window.configure(cursor='left_ptr')
        ans = end_menu.answer()

        if ans is True:
            self.button_Start.configure(state='normal')
            self.button_Clear.configure(state='normal')
            self.button_Stop.configure(state='normal')
            self.window.configure(cursor='plus')
            self.clear()

        elif ans is False:
            self.exit_life()

    def exit_life(self):
        self.master.quit()


class End(object):

    def __init__(self, master, gen, start_cell, score, max_score):
        self.end = Toplevel(master)
        self.end.transient(master)
        self.end.title('THE END')

        x = master.winfo_x()
        y = master.winfo_y()
        w_mid = master.winfo_width() // 2
        h_mid = master.winfo_height() // 2
        self.end.geometry(
            '200x170+{}+{}'.format(x + w_mid - 100, y + h_mid - 85))
        self.end.resizable(width=False, height=False)

        self.end.gen = str(gen - 1)
        self.end.start = str(start_cell)
        # because they are out of the cycle
        self.end.score = str(score + start_cell)
        self.end.max = str(max_score)

        self.end.label_univ = Label(self.end, text='EMPTY UNIVERSUM')
        self.end.label_univ.pack(side=TOP, fill=BOTH, pady=10)

        self.end.label_cyc = Label(
            self.end, text='LIFE EXIST ' + self.end.gen + ' CYCLES')
        self.end.label_cyc.pack(side=TOP, fill=BOTH)

        self.end.label_cell = Label(
            self.end, text='POPULATION ' + self.end.score + ' CELLS')
        self.end.label_cell.pack(side=TOP, fill=BOTH)

        self.end.label_cell = Label(
            self.end, text='SEEDS ' + self.end.start + ' CELLS')
        self.end.label_cell.pack(side=TOP, fill=BOTH)

        self.end.label_maxcell = Label(
            self.end, text='MAXIMUM ' + self.end.max + ' CELLS')
        self.end.label_maxcell.pack(side=TOP, fill=BOTH)

        self.end.frameButt = Frame(self.end, bd=5)
        self.end.frameButt.pack(side=BOTTOM)

        self.end.exit = Button(self.end.frameButt,
                               text='END LIFE',
                               width=7,
                               command=self.exit_life)
        self.end.exit.pack(side=LEFT, padx=5)

        self.end.new = Button(self.end.frameButt,
                              text='NEW LIFE',
                              width=7,
                              command=self.new_life)
        self.end.new.pack(side=LEFT, padx=5)

        self.end.overrideredirect(True)

    def answer(self):
        # to prevent error when close main window
        self.answer = None

        self.end.grab_set()
        self.end.wait_window()
        return self.answer

    def exit_life(self):
        self.answer = False
        self.end.destroy()

    def new_life(self):
        self.answer = True
        self.end.destroy()


# MAIN PROGRAMM
root = Tk()

if __name__ == '__main__':
    Main(root)
