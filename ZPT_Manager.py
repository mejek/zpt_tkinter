#!/usr/bin/python
# -*- coding: utf-8 -*-

import tkinter as tk                # python 3
import Status_frame, Work_frame, Log_manager, Maile
from ahk import AHK
import logging, queue

class Main_Window(tk.Tk):

    def __init__(self, *args, **kwargs):
        self.frames = {}

        tk.Tk.__init__(self, *args, **kwargs)
        self.title(f'ZPT MANAGER')

        self.container = tk.Canvas()
        self.container.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.logger = logging.getLogger(__name__)
        self.log_queue = queue.Queue()
        self.queue_handler = Log_manager.QueueHandler(self.log_queue)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.queue_handler.setFormatter(formatter)
        self.logger.addHandler(self.queue_handler)
        logging.basicConfig(level=logging.ERROR)

        self.fh = logging.FileHandler('ZPT_Manager_log.log')
        self.fh.setLevel(level=logging.INFO)
        self.fh.setFormatter(formatter)
        self.logger.addHandler(self.fh)
        self.logger.setLevel(level=logging.INFO)

        #log start programu
        self.logger.log(logging.INFO, "Start programu")

        #główna ramka programu
        main_frame = Main_frame(self.container, self)
        main_frame.place(relx=0, rely=0,relwidth=1, relheight=0.97)

        #ramka status aktualizacji ZPT
        self.status_frame = Status_frame.Status_frame(self.container, self)
        self.status_frame.place(relx=0, rely=0.97, relwidth=1, relheight=0.03)
        self.status_frame.tkraise()
        self.status_frame_update()

        #ramka menu
        self.menu_frame = Menu_frame(main_frame, self)
        self.menu_frame.place(relx=0.001, rely=0.005, relwidth=0.08, relheight=0.99)
        self.menu_frame.tkraise()

        #modul maile
        self.maile = Work_frame.Maile(main_frame, self)

        #frames
        self.online_frame = Work_frame.Online_frame(main_frame, self)
        self.frames['online_frame'] = self.online_frame
        self.gotowki_frame = Work_frame.Gotowki_frame(main_frame, self)
        self.frames['gotowki_frame'] = self.gotowki_frame
        self.faktury_koszty_frame = Work_frame.Faktury_koszty_frame(main_frame, self)
        self.frames['faktury_koszty_frame'] = self.faktury_koszty_frame
        self.faktury_towar_frame = Work_frame.Faktury_towar_frame(main_frame, self)
        self.frames['faktury_towar_frame'] = self.faktury_towar_frame
        self.biala_lista_frame = Work_frame.Biala_lista_frame(main_frame, self)
        self.frames['biala_lista_frame'] = self.biala_lista_frame
        self.hurtownie_frame = Work_frame.Hurtownie_frame(main_frame, self)
        self.frames['hurtownie_frame'] = self.hurtownie_frame
        self.czynsze_frame = Work_frame.Czynsze_frame(main_frame, self)
        self.frames['czynsze_frame'] = self.czynsze_frame
        self.przelewy_frame = Work_frame.Przelewy_frame(main_frame, self)
        self.frames['przelewy_frame'] = self.przelewy_frame
        self.dane_archiwlane_frame = Work_frame.Dane_archiwalne_frame(main_frame, self)
        self.frames['dane_archiwalne_frame'] = self.dane_archiwlane_frame
        self.pracownicy_frame = Work_frame.Pracownicy_frame(main_frame, self)
        self.frames['pracownicy_frame'] = self.pracownicy_frame
        self.todo_frame = Work_frame.Todo_manager(main_frame, self)
        self.frames['todo_frame'] = self.todo_frame
        self.wyciagi_frame = Work_frame.Wyciagi_frame(main_frame, self)
        self.frames['wyciagi_frame'] = self.wyciagi_frame

        self.rozne_frame = Work_frame.Rozne_frame(main_frame, self)
        self.frames['rozne_frame'] = self.rozne_frame
        self.logi_frame = Log_manager.Log_manager(main_frame, self)
        self.frames['logi_frame'] = self.logi_frame



        self.show_frame('faktury_koszty_frame', 2)
        self.ahk = AHK(executable_path=r"C:\Program Files\AutoHotkey\AutoHotkey.exe")

    def show_frame(self, page_name, lista_index):
        frame = self.frames[page_name]
        frame.place(relx=0.084, rely=0.005, relwidth=0.914, relheight=0.99)
        if page_name == 'biala_lista_frame':
            self.biala_lista_frame.update_biala_lista_treeview()

        for n in range(len(self.menu_frame.menu_buttons_lista)):
            if n == lista_index:
                self.menu_frame.menu_buttons_lista[n].config(bg='#085420')
            else:
                self.menu_frame.menu_buttons_lista[n].config(bg='#544949')
        frame.tkraise()

    def status_frame_update(self):
        if self.status_frame:
            self.status_frame.destroy()
        self.status_frame = Status_frame.Status_frame(self.container, self)
        self.status_frame.place(relx=0, rely=0.97, relwidth=1, relheight=0.03)
        self.status_frame.tkraise()
        self.after(60000, lambda: self.status_frame_update())

class Main_frame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.configure(bg='#383232')

class Menu_frame(tk.Frame):  #ramka na dole programu przedstawia aktualne czasu aktualizacji z poszczególnych aptek
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.configure(bg='#383232')
        self.create_online_button()
        self.create_gotowki_button()
        self.create_platnosci_koszty_button()
        self.create_platnosci_towar_button()
        self.create_biala_lista_button()
        self.create_hurtownie_button()
        self.create_czynsze_button()
        self.create_przelewy_button()
        self.create_dane_archiwalne_button()
        self.create_pracownicy_button()
        self.create_todo_button()
        self.create_wyciagi_button()

        self.create_rozne_button()
        self.create_logi_button()
        self.set_menu_buttons_lista()

    def create_online_button(self):
        self.raporty_button =tk.Button(self, text="ONLINE", bg='#544949', fg='#b58b14',
                                       command = lambda: app.show_frame('online_frame', 0))
        self.raporty_button.place(relx=0.05, rely=0.02, relwidth=0.95, relheight= 0.03)

    def create_gotowki_button(self):
        self.gotowki_button =tk.Button(self, text="GOTÓWKI", bg='#544949', fg='#b58b14',
                                       command = lambda: app.show_frame('gotowki_frame', 1))
        self.gotowki_button.place(relx=0.05, rely=0.06, relwidth=0.95, relheight= 0.03)

    def create_platnosci_koszty_button(self):
        self.koszty_button =tk.Button(self, text="FAKTURY KOSZTY", bg='#544949', fg='#b58b14',
                                       command = lambda: app.show_frame('faktury_koszty_frame', 2))
        self.koszty_button.place(relx=0.05, rely=0.10, relwidth=0.95, relheight= 0.03)

    def create_platnosci_towar_button(self):
        self.towar_button =tk.Button(self, text="FAKTURY TOWAR", bg='#544949', fg='#b58b14',
                                       command = lambda: app.show_frame('faktury_towar_frame', 3))
        self.towar_button.place(relx=0.05, rely=0.14, relwidth=0.95, relheight= 0.03)

    def create_biala_lista_button(self):
        self.biala_lista_button =tk.Button(self, text="BIAŁA LISTA", bg='#544949', fg='#b58b14',
                                       command = lambda: app.show_frame('biala_lista_frame', 4))
        self.biala_lista_button.place(relx=0.05, rely=0.18, relwidth=0.95, relheight= 0.03)

    def create_hurtownie_button(self):
        self.hurtownie_button =tk.Button(self, text="HURTOWNIE", bg='#544949', fg='#b58b14',
                                       command = lambda: app.show_frame('hurtownie_frame', 5))
        self.hurtownie_button.place(relx=0.05, rely=0.22, relwidth=0.95, relheight= 0.03)

    def create_czynsze_button(self):
        self.czynsze_button =tk.Button(self, text="CZYNSZE", bg='#544949', fg='#b58b14',
                                       command = lambda: app.show_frame('czynsze_frame', 6))
        self.czynsze_button.place(relx=0.05, rely=0.26, relwidth=0.95, relheight= 0.03)

    def create_przelewy_button(self):
        self.przelewy_button =tk.Button(self, text="PRZELEWY", bg='#544949', fg='#b58b14',
                                       command = lambda: app.show_frame('przelewy_frame', 7))
        self.przelewy_button.place(relx=0.05, rely=0.30, relwidth=0.95, relheight= 0.03)

    def create_dane_archiwalne_button(self):
        self.dane_archiwalne_button =tk.Button(self, text="DANE ARCHIWALNE", bg='#544949', fg='#b58b14',
                                       command = lambda: app.show_frame('dane_archiwalne_frame', 8))
        self.dane_archiwalne_button.place(relx=0.05, rely=0.34, relwidth=0.95, relheight= 0.03)

    def create_pracownicy_button(self):
        self.pracownicy_button =tk.Button(self, text="PRACOWNICY", bg='#544949', fg='#b58b14',
                                       command = lambda: app.show_frame('pracownicy_frame', 9))
        self.pracownicy_button.place(relx=0.05, rely=0.38, relwidth=0.95, relheight= 0.03)

    def create_todo_button(self):
        self.todo_button =tk.Button(self, text="TODO", bg='#544949', fg='#b58b14',
                                       command = lambda: app.show_frame('todo_frame', 11))
        self.todo_button.place(relx=0.05, rely=0.42, relwidth=0.95, relheight= 0.03)

    def create_wyciagi_button(self):
        self.wyciagi_button =tk.Button(self, text="WYCIĄGI", bg='#544949', fg='#b58b14',
                                       command = lambda: app.show_frame('wyciagi_frame', 12))
        self.wyciagi_button.place(relx=0.05, rely=0.46, relwidth=0.95, relheight= 0.03)


    def create_rozne_button(self):
        self.rozne_button =tk.Button(self, text="RÓŻNE", bg='#544949', fg='#b58b14',
                                       command = lambda: app.show_frame('rozne_frame', 13))
        self.rozne_button.place(relx=0.05, rely=0.91, relwidth=0.95, relheight= 0.03)

    def create_logi_button(self):
        self.logi_button =tk.Button(self, text="LOGI", bg='#544949', fg='#b58b14',
                                       command = lambda: app.show_frame('logi_frame', 10))
        self.logi_button.place(relx=0.05, rely=0.95, relwidth=0.95, relheight= 0.03)

    def set_menu_buttons_lista(self):
        self.menu_buttons_lista = [self.raporty_button, self.gotowki_button, self.koszty_button, self.towar_button,
                                   self.biala_lista_button, self.hurtownie_button, self.czynsze_button,
                                   self.przelewy_button, self.dane_archiwalne_button, self.pracownicy_button,
                                   self.logi_button, self.todo_button, self.wyciagi_button, self.rozne_button]
        return self.menu_buttons_lista

if __name__ == "__main__":
    app = Main_Window()
    app.wm_state('zoomed')
    app.mainloop()
