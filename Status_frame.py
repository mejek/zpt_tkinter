#!/usr/bin/python
# -*- coding: utf-8 -*-
import tkinter as tk
import ZPT_Database
from datetime import datetime


class Status_frame(tk.Frame):  #ramka na dole programu przedstawia aktualne czasu aktualizacji z poszczególnych aptek
    def __init__(self, parent, controller):
        self.zpt_database = ZPT_Database.ZPT_base()
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.configure(bg='#6b685f')
        self.get_aktualizacja_time()
        self.show_aktualizacja_time()

    def get_aktualizacja_time(self):
        self.querry_aktualizacja_time = f'SELECT apteka, data FROM aktualizacja'
        self.aktualizacja_time_list = self.zpt_database.mysql_querry(self.querry_aktualizacja_time)
        self.aktualizacja_time_dict = dict(self.aktualizacja_time_list)
        return self.aktualizacja_time_dict

    def show_aktualizacja_time(self):
        self.bg_label = '#6b685f'
        self.font_type = 'Verdana'
        self.font_size = 8

        self.H4_label = tk.Label(self, text= f"H4: {self.aktualizacja_time_dict[2][0:19]}", bg=self.bg_label, justify='left' )
        self.H4_label.config(fg=self.change_color_if_deley(self.aktualizacja_time_dict[2][0:19],300),
                                font=(self.font_type, self.font_size))
        self.H4_label.place(relx=0.008, rely=0.15)

        self.H3_label = tk.Label(self, text=f"", bg=self.bg_label, justify='left')
        self.H3_label.config(font=(self.font_type, self.font_size))
        self.H3_label.place(relx=0.108, rely=0.15)

        self.H_label = tk.Label(self, text=f"H: {self.aktualizacja_time_dict[4][0:19]}", bg=self.bg_label, justify='left')
        self.H_label.config(fg=self.change_color_if_deley(self.aktualizacja_time_dict[4][0:19],300),
                                font=(self.font_type, self.font_size))
        self.H_label.place(relx=0.208, rely=0.15)

        self.P_label = tk.Label(self, text=f"P: {self.aktualizacja_time_dict[5][0:19]}", bg=self.bg_label, justify='left')
        self.P_label.config(fg=self.change_color_if_deley(self.aktualizacja_time_dict[5][0:19],300),
                                font=(self.font_type, self.font_size))
        self.P_label.place(relx=0.308, rely=0.15)

        self.W_label = tk.Label(self, text=f"W: {self.aktualizacja_time_dict[6][0:19]}", bg=self.bg_label, justify='left')
        self.W_label.config(fg=self.change_color_if_deley(self.aktualizacja_time_dict[6][0:19],300),
                                font=(self.font_type, self.font_size))
        self.W_label.place(relx=0.408, rely=0.15)

        self.Bi_label = tk.Label(self, text=f"B: {self.aktualizacja_time_dict[7][0:19]}", bg=self.bg_label, justify='left')
        self.Bi_label.config(fg=self.change_color_if_deley(self.aktualizacja_time_dict[7][0:19],300),
                                font=(self.font_type, self.font_size))
        self.Bi_label.place(relx=0.508, rely=0.15)

        self.Bz_label = tk.Label(self, text=f"Bz: {self.aktualizacja_time_dict[8][0:19]}", bg=self.bg_label, justify='left')
        self.Bz_label.config(fg=self.change_color_if_deley(self.aktualizacja_time_dict[8][0:19],300),
                                font=(self.font_type, self.font_size))
        self.Bz_label.place(relx=0.608, rely=0.15)

        self.Daty_label = tk.Label(self, text=f"KRÓTKIE DATY", bg=self.bg_label,justify='left')
        self.Daty_label.config(fg=self.change_color_if_deley(self.aktualizacja_time_dict[98][0:19],88000),
                                font=(self.font_type, self.font_size))
        self.Daty_label.place(relx=0.708, rely=0.15)

        self.Daty_label = tk.Label(self, text=f"PŁATNOŚCI",
                                   bg=self.bg_label, justify='left')
        self.Daty_label.config(fg=self.change_color_if_deley(self.aktualizacja_time_dict[90][0:19], 3900),
                                font=(self.font_type, self.font_size))
        self.Daty_label.place(relx=0.758, rely=0.15)

        self.Grupy_label = tk.Label(self, text=f"GRUPY ZAKUPOWE",
                                   bg=self.bg_label, justify='left')
        self.Grupy_label.config(fg=self.change_color_if_deley(self.aktualizacja_time_dict[91][0:19], 88000),
                                font=(self.font_type, self.font_size))
        self.Grupy_label.place(relx=0.798, rely=0.15)

    def change_color_if_deley(self, czas, spoznienie):
        self.czas_datetime = datetime.strptime(czas, "%Y-%m-%d %H:%M:%S")
        self.difference = (datetime.now() - self.czas_datetime).total_seconds()
        if self.difference > spoznienie:
            return '#a30018'
        return '#57ba16'



