#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# LIFE 3.0

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

import platform
from os import getpid, system
from tkinter import *


class Main(object):

    def __init__(self, master):
        self.master = master
        self.master.title('CONWAY\'S GAME OF LIFE')
        self.master.geometry('910x683+200+50')
        self.master.resizable(width=False, height=False)

        # create a main field
        can_width = 801
        can_height = 641

        # variable for stop or run game
        self.on_off = True
        # variable to continue with right number generation after stop game
        self.global_gen = None
        # start
        self.start_cell = 0
        # population
        self.score = 0
        # variable for max cells
        self.max_score = 0
        # for change speed
        self.timer = 50
        self.invert = None
        self.on = (0, 0)
        # cursor for place ships
        self.cur = None
        # erase seeds
        self.erase = True

        # images for ships
        self.glider = PhotoImage(file='data/1_ship.gif')
        self.glider_in = PhotoImage(file='data/1_ship_in.gif')
        self.lss = PhotoImage(file='data/2_lss.gif')
        self.lss_in = PhotoImage(file='data/2_lss_in.gif')
        self.sui = PhotoImage(file='data/3_sucide.gif')
        self.sui_in = PhotoImage(file='data/3_sucide_in.gif')
        self.f5 = PhotoImage(file='data/4_f5.gif')
        self.f5_in = PhotoImage(file='data/4_f5_in.gif')
        self.penta = PhotoImage(file='data/5_penta.gif')
        self.penta_in = PhotoImage(file='data/5_penta_in.gif')
        self.patern = PhotoImage(file='data/6_patern.gif')
        self.patern_in = PhotoImage(file='data/6_patern_in.gif')
        self.fireship = PhotoImage(file='data/7_fireship.gif')
        self.fireship_in = PhotoImage(file='data/7_fireship_in.gif')

        # GUI
        frameWin = Frame(master, bg='white', borderwidth=0)
        frameWin.pack(side=TOP, fill=BOTH)

        frameCanv = Frame(frameWin, bg='white', borderwidth=0)
        frameCanv.pack(side=RIGHT, fill=BOTH)

        # main canvas
        self.window = Canvas(frameCanv,
                             width=can_width,
                             height=can_height,
                             cursor='plus',
                             bg='white',
                             bd=0,
                             highlightthickness=0)
        self.window.pack(side=TOP)

        self.cell = 10
        self.w_field = can_width // self.cell
        self.h_field = can_height // self.cell

        # create a examples of class square
        self.cell_matrix = []
        for i in range(0, self.h_field):
            x = 0
            y = 0 + i * self.cell
            rows = []
            for i in range(0, self.w_field):
                rows.append(Square(self.window, x + i *
                                   self.cell, y, self.cell, self))
            self.cell_matrix.append(rows)

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

    def motion_paint(self, event):
        x = int(event.x)
        y = int(event.y)
        xcell = int(y / self.cell)
        ycell = int(x / self.cell)

        self.black_cell(xcell, ycell)

    def start_paint(self, event):
        self.window.bind('<B1-Motion>', self.motion_paint)
        for i in self.cell_matrix:
            for j in i:
                j.canvas.tag_bind(j.cel, '<ButtonPress-1>', j.paint)

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

    def creat_but(self, x, y, fnx, lnx, fny, lny, x_im, y_im, img_in, img, bind, al):
        self.window.unbind('<B1-Motion>')
        if self.cur:
            self.window.delete(self.cur)
            self.cur = None
        if self.on[0] not in range(fnx, lnx) or self.on[1] not in range(fny, lny):
            self.invert = self.creat.create_image(x_im, y_im, image=img_in)
            self.window.bind('<ButtonPress-1>', bind)
            self.on = (x, y)
            self.window.bind('<Motion>', lambda event, i=img,
                             a=al: self.cursor(event, i, a))

    def cursor(self, event, img, align):
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

        self.black_cell(xcell, ycell)
        self.black_cell(xcell - 1, ycell)
        self.black_cell(xcell, ycell - 1)
        self.black_cell(xcell, ycell - 2)
        self.black_cell(xcell - 2, ycell - 1)

    def ship_2(self, event):
        x = int(event.x)
        y = int(event.y)
        xcell = int(y / self.cell)
        ycell = int(x / self.cell)

        self.black_cell(xcell, ycell)
        self.black_cell(xcell - 1, ycell)
        self.black_cell(xcell - 2, ycell)
        self.black_cell(xcell - 3, ycell - 1)
        self.black_cell(xcell, ycell - 1)
        self.black_cell(xcell, ycell - 2)
        self.black_cell(xcell, ycell - 3)
        self.black_cell(xcell - 1, ycell - 4)
        self.black_cell(xcell - 3, ycell - 4)

    def fig_1(self, event):
        x = int(event.x)
        y = int(event.y)
        xcell = int(y / self.cell)
        ycell = int(x / self.cell)

        self.black_cell(xcell, ycell)
        self.black_cell(xcell, ycell - 1)
        self.black_cell(xcell - 1, ycell - 1)
        self.black_cell(xcell - 2, ycell - 1)
        self.black_cell(xcell - 3, ycell - 1)
        self.black_cell(xcell - 3, ycell - 2)

    def fig_2(self, event):
        x = int(event.x)
        y = int(event.y)
        xcell = int(y / self.cell)
        ycell = int(x / self.cell)

        self.black_cell(xcell, ycell)
        self.black_cell(xcell - 1, ycell)
        self.black_cell(xcell - 2, ycell)
        self.black_cell(xcell - 1, ycell - 1)
        self.black_cell(xcell - 2, ycell + 1)

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

    def black_cell(self, x, y):
        # could be an answer
        if self.cell_matrix[x % self.h_field][y % self.w_field].color_change:

            self.start_cell += 1
            self.window.itemconfigure(self.cell_matrix[x % self.h_field][y % self.w_field].cel,
                                      fill='black')
            self.cell_matrix[x % self.h_field][y %
                                               self.w_field].color_change = False

    def check_black(self, x, y, color):
        total = 8
        for i in [(-1, -1), (0, -1), (1, -1),
                  (-1, 0),        (1, 0),
                  (-1, 1), (0, 1), (1, 1)]:
            if self.cell_matrix[(x + i[0]) % self.h_field][(y + i[1]) % self.w_field].color_change == color:
                total -= 1

        return total

    def start_game(self):
        self.erase = False
        self.on_off = True
        self.button_Start.configure(state='disabled')
        self.button_Clear.configure(state='disabled')

        self.start_cycle()

    def start_cycle(self):
        if self.global_gen:
            gen = self.global_gen
        else:
            gen = 1

        tot = 0

        dead = []
        born = []
        for i in self.cell_matrix:
            x = self.cell_matrix.index(i)
            for j in i:
                y = i.index(j)
                if j.color_change == False:
                    tot += 1
                    total = self.check_black(x, y, True)

                    if total < 2:
                        dead.append(self.cell_matrix[x][y])

                    if total > 3:
                        dead.append(self.cell_matrix[x][y])

                    # check if new cell wass born
                    for xy in [(x - 1, y - 1), (x, y - 1), (x + 1, y - 1),
                               (x - 1, y),            (x + 1, y),
                               (x - 1, y + 1), (x, y + 1), (x + 1, y + 1)]:

                        total = self.check_black(xy[0], xy[1], False)

                    # my old very big and complicated answer with try and without %
                    # try:
                    #     if self.cell_matrix[x-1][y+1].color_change == False:
                    #         total +=1
                    # except:
                    #     if self.cell_matrix[x-1][(y-self.w_field)+1].color_change == False:
                    #         total +=1

                    # invert rule need 3 cells to born new
                        if total == 5:
                            born.append(self.cell_matrix[xy[0] % self.h_field][
                                        xy[1] % self.w_field])

        self.scrPop.configure(text=tot)
        self.scrGen.configure(text=gen)

        for i in dead:
            i.canvas.itemconfigure(i.cel, fill='#EEEEEE')
            i.color_change = True

        for i in born:
            i.canvas.itemconfigure(i.cel, fill='black')
            i.color_change = False

        # update screen
        # self.master.update_idletasks()

        # counters for maximum population
        if self.max_score == False:
            self.max_score = tot
        elif tot > self.max_score:
            self.max_score = tot
        else:
            self.max_score = self.max_score

        # for generation
        gen += 1
        self.global_gen = gen

        # after dead cells need to check how many stay alive
        tot += len(born) - len(dead)

        # count population
        self.score += tot

        # start goal for end message
        if tot == 0:
            self.game_over(tot, gen)
        # for stop button
        if self.on_off == True:
            self.window.after(self.timer, self.start_cycle)

    def stop_game(self):
        self.on_off = False
        self.button_Start.configure(state='normal')
        self.button_Clear.configure(state='normal')

    # better to use event=None
    # def clear_side(self):
    #     self.clear_side_menu()

    def clear_side_menu(self, event=None):
        self.window.unbind('<Motion>')
        self.creat.delete(self.invert)
        self.invert = None
        self.window.bind('<ButtonPress-1>', self.start_paint)
        self.window.configure(cursor='plus')
        if self.cur:
            self.window.delete(self.cur)

    def clear(self):
        for i in self.cell_matrix:
            for j in i:
                j.canvas.itemconfigure(j.cel, fill='#EEEEEE')
                j.color_change = True
        self.scrPop.configure(text=0)
        self.scrGen.configure(text=0)
        # clear menu with figures
        self.clear_side_menu()
        self.erase = True
        self.start_cell = 0
        self.score = 0
        self.max_score = 0
        self.global_gen = None

    def fast(self):
        self.timer -= 10
        if self.timer < 10:
            self.timer = 10
        self.speedVal.configure(text=int(self.timer))

    def slow(self):
        self.timer += 10
        if self.timer > 150:
            self.timer = 150
        self.speedVal.configure(text=int(self.timer))

    def game_over(self, tot, gen):

        self.erase = True
        self.on_off = False
        self.global_gen = 0
        self.scrPop.configure(text=tot)
        self.scrGen.configure(text=self.global_gen)
        self.creat.delete(self.invert)

        self.button_Stop.configure(state='disabled')
        end_menu = End(self.master, gen, self.start_cell,
                       self.score, self.max_score)
        self.window.configure(cursor='left_ptr')
        ans = end_menu.answer()

        if ans == True:
            self.button_Start.configure(state='normal')
            self.button_Clear.configure(state='normal')
            self.button_Stop.configure(state='normal')
            self.window.configure(cursor='plus')
            # start seeds
            self.start_cell = 0
            # population
            self.score = 0
            # variable for max cells
            self.max_score = 0

        elif ans == False:
            self.exit_life()

    def exit_life(self):
        self.master.quit()

# squares for build board


class Square(object):

    def __init__(self, canvas, x, y, size, main):
        self.canvas = canvas
        self.cel = self.canvas.create_rectangle(x, y, x + size, y + size,
                                                fill='#EEEEEE')
        self.main = main
        self.color_change = True

        self.canvas.tag_bind(self.cel, '<ButtonPress-1>', self.paint)

    def paint(self, event):
        if self.color_change == True:
            color = 'black'
            self.color_change = False
            # to know how many cells at the start and during game
            self.main.start_cell += 1

            self.canvas.itemconfigure(self.cel, fill=color)
        else:
            if self.main.erase:
                self.main.start_cell -= 1
                color = '#EEEEEE'
                self.color_change = True

                # important
                self.canvas.itemconfigure(self.cel, fill=color)


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

        # to hide buttons
        # need update if no transient window
        # self.end.update_idletasks()
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
