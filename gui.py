# -*- coding: utf-8 -*-
import os
from tkinter import Frame, Entry, Button, Radiobutton, IntVar
import tkinter as tk
import configparser


class Application(Frame):
    """
    configure should only be changed here!
    """

    def __init__(self, master=None):
        self.cfg = configparser.ConfigParser()
        self.cfg.read('settings.ini')

        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()

    def createWidgets(self):
        v = IntVar()
        v.set(1)
        self.checkbutton_selection = Radiobutton(self, text='selection', value=1, variable=v,
                                                 command=self.choose_selection_mode)
        self.checkbutton_selection.pack()
        self.checkbutton_random_init = Radiobutton(self, text='random init', value=2, variable=v,
                                                   command=self.choose_random_init_mode)
        self.checkbutton_random_init.pack()
        self.checkbutton_readfile = Radiobutton(self, text='read file', value=3, variable=v,
                                                command=self.choose_readfile_mode)
        self.checkbutton_readfile.pack()

    def choose_selection_mode(self):
        self.cfg.set('MODE', 'mode', 'SELECTION')
        with open('settings.ini', 'w') as configfile:
            self.cfg.write(configfile)

    def choose_random_init_mode(self):
        self.cfg.set('MODE', 'mode', 'RANDOM_INIT')
        with open('settings.ini', 'w') as configfile:
            self.cfg.write(configfile)

    def choose_readfile_mode(self):
        self.cfg.set('MODE', 'mode', 'READFILE')
        with open('settings.ini', 'w') as configfile:
            self.cfg.write(configfile)


if __name__ == '__main__':
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()
