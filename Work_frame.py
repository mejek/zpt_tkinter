#!/usr/bin/python
# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, StringVar, scrolledtext
import datetime
from time import sleep
import ZPT_Database
import Kamsoft_Database
import slowniki
from dateutil import easter
from tkcalendar import DateEntry
import requests
import pandas as pd
import pdfkit
import glob
import keyring
from pandas_ods_reader import read_ods
import shutil
from tabula import read_pdf
import json
from ahk import AHK
import mt940  # parseowanie wyciągu MILLENNIUM
import xml.etree.ElementTree as ET  # parsowanie wyciagu PKO
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
import email.encoders as Encoders
import os
import zipfile
import threading
import ftplib
from simpledbf import Dbf5

class Online_frame(tk.Frame):
    def __init__(self, parent, controller):
        self.zpt_database = ZPT_Database.ZPT_base()
        self.kolor_legenda = '#383232'
        self.kolor_razem = '#b58b14'
        self.kolor_font = 'white'
        self.kolor_font_razem = 'black'
        self.czas_odswiezenia = self.data_dzien = str(datetime.datetime.now().time())[:5]
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.configure(bg='#383232')
        self.get_obroty_dzienne_data()
        self.get_obroty_miesieczne_data()
        self.get_dane_prognoza()
        self.get_zakupy_dane()
        self.create_obroty_f1()
        self.create_obroty_dzienne_legenda()
        self.create_obroty_miesieczne_frame()
        self.create_obroty_miesieczne_legenda()
        self.create_obroty_miesieczne_prognoza_frame()
        self.create_obroty_miesieczne_prognoza_legenda()
        self.create_oborty_dzienne_dane_frame()
        self.create_oborty_miesieczne_dane_frame()
        self.create_oborty_miesieczne_prognoza_dane_frame()
        self.create_zakupy_frame()
        self.create_zakupy_legenda()
        # self.create_odswiezenie_czas()
        self.update_obroty_dzienne_dane()
        self.update_obroty_miesieczne_dane()
        self.update_obroty_miesieczne_prognoza_dane()
        self.update_zakupy_dane()
        self.update_zakupy_hurtownie_dane()
        self.update_procenty_dane()
        # self.create_odswiez_button()

    def get_obroty_dzienne_data(self):
        self.obroty_dzienne_dict = {}
        self.all_pacjenci = 0
        self.all_brutto = 0
        self.all_netto = 0
        self.all_zysk = 0
        self.all_magazyn = 0

        for n in range(2, 9):
            self.guerry_obroty_dzienne = f'SELECT * FROM obroty_dzienne WHERE' \
                                         f' data = "{datetime.datetime.now().date()}"' \
                                         f' AND apteka = {n}'
            self.obroty_dzienne_dane = self.zpt_database.mysql_querry(self.guerry_obroty_dzienne)
            self.querry_magazyn_apteka = f'SELECT sum(cena_zak*ilakt) FROM rem_0{n}'
            self.magazyn_apteka = self.zpt_database.mysql_querry(self.querry_magazyn_apteka)
            if n == 3:
                self.magazyn = 0
            else:
                self.magazyn = round(self.magazyn_apteka[0][0], 2)

            if not self.obroty_dzienne_dane:
                self.obroty_dzienne_dict[f'{n}'] = [0, 0, 0, 0, self.magazyn]
                self.all_magazyn += self.magazyn

            else:
                self.obroty_dzienne_dict[f'{n}'] = [self.obroty_dzienne_dane[0][2],
                                                    self.obroty_dzienne_dane[0][3],
                                                    self.obroty_dzienne_dane[0][4],
                                                    self.obroty_dzienne_dane[0][5],
                                                    self.magazyn]
                self.all_pacjenci += self.obroty_dzienne_dane[0][2]
                self.all_brutto += self.obroty_dzienne_dane[0][3]
                self.all_netto += self.obroty_dzienne_dane[0][4]
                self.all_zysk += self.obroty_dzienne_dane[0][5]
                self.all_magazyn += self.magazyn
        self.obroty_dzienne_dict[f'razem'] = [self.all_pacjenci, round(self.all_brutto, 2),
                                              round(self.all_netto, 2), round(self.all_zysk, 2),
                                              round(self.all_magazyn, 2)]

        return self.obroty_dzienne_dict

    def get_obroty_miesieczne_data(self):
        self.obroty_miesieczne_dict = {}
        self.all_pacjenci = 0
        self.all_brutto = 0
        self.all_netto = 0
        self.all_zysk = 0

        for n in range(2, 9):
            self.guerry_obroty_miesieczne = f'SELECT SUM(pacjenci), SUM(obrot_brutto), SUM(obrot_netto),' \
                                            f' SUM(zysk_netto)' \
                                            f' FROM obroty_dzienne' \
                                            f' WHERE (data between  DATE_FORMAT(NOW() ,"%Y-%m-01") AND NOW())' \
                                            f' AND apteka = {n}'
            self.obroty_miesieczne_dane = self.zpt_database.mysql_querry(self.guerry_obroty_miesieczne)
            if self.obroty_miesieczne_dane == [(None, None, None, None)]:
                self.obroty_miesieczne_dict[f'{n}'] = [0, 0, 0, 0, 0]

            else:
                self.marza = round((self.obroty_miesieczne_dane[0][3] / self.obroty_miesieczne_dane[0][2]) * 100, 2)
                self.obroty_miesieczne_dict[f'{n}'] = [int(self.obroty_miesieczne_dane[0][0]),
                                                       round(self.obroty_miesieczne_dane[0][1], 2),
                                                       round(self.obroty_miesieczne_dane[0][2], 2),
                                                       round(self.obroty_miesieczne_dane[0][3], 2),
                                                       self.marza]
                self.all_pacjenci += self.obroty_miesieczne_dane[0][0]
                self.all_brutto += self.obroty_miesieczne_dane[0][1]
                self.all_netto += self.obroty_miesieczne_dane[0][2]
                self.all_zysk += self.obroty_miesieczne_dane[0][3]
            if self.all_netto != 0:
                self.marza_all = round((self.all_zysk / self.all_netto) * 100, 2)
            else:
                self.marza_all = 0
            self.obroty_miesieczne_dict[f'razem'] = [int(self.all_pacjenci), round(self.all_brutto, 2),
                                                     round(self.all_netto, 2), round(self.all_zysk, 2),
                                                     round(self.marza_all, 2)]
        return self.obroty_miesieczne_dict

    def get_dni_robocze(self):
        self.rok_now = datetime.datetime.now().year
        self.miesiac_now = datetime.datetime.now().month
        self.pierwszy_dzien = datetime.date(self.rok_now, self.miesiac_now, 1)
        self.holidays = [f'{self.rok_now}-01-01', f'{self.rok_now}-01-06', f'{self.rok_now}-05-01',
                         f'{self.rok_now}-05-03',
                         f'{self.rok_now}-08-15', f'{self.rok_now}-11-01', f'{self.rok_now}-11-11',
                         f'{self.rok_now}-12-25', f'{self.rok_now}-12-26']
        easter_date = easter.easter(self.rok_now)
        easter_monday = easter_date + datetime.timedelta(days=1)
        cc_date = easter_date + datetime.timedelta(days=60)
        self.holidays.append(str(easter_date))
        self.holidays.append(str(easter_monday))
        self.holidays.append(str(cc_date))

        self.dni_robocze_lista = []
        self.soboty_lista = []
        self.dni_robocze = 0
        self.soboty = 0

        for n_day in range(31):
            data_n = self.pierwszy_dzien + datetime.timedelta(days=n_day)
            if data_n.month != self.miesiac_now:
                break
            elif str(data_n) in self.holidays or data_n.weekday() == 6:
                continue
            elif data_n.weekday() < 5:
                if data_n < datetime.datetime.now().date():
                    self.dni_robocze_lista.append(str(data_n))
                self.dni_robocze += 1
            elif data_n.weekday() == 5:
                if data_n < datetime.datetime.now().date():
                    self.soboty_lista.append(str(data_n))
                self.soboty += 1

        return [self.dni_robocze_lista, self.soboty_lista, self.dni_robocze, self.soboty]

    def get_dane_prognoza(self):
        self.dni = self.get_dni_robocze()
        self.dane_prognoza = {}
        pacjenci_prognoza_all = 0
        brutto_prognoza_all = 0
        netto_prognoza_all = 0
        zysk_prognoza_all = 0

        if self.dni[0] == [] or self.dni[1] == []:
            for apteka in range(2, 9):
                self.dane_prognoza[f'{apteka}'] = [0, 0, 0, 0]
            self.dane_prognoza['razem'] = [0, 0, 0, 0]
            return self.dane_prognoza

        for apteka in range(2, 9):
            pacjenci_prognoza = 0
            brutto_prognoza = 0
            netto_prognoza = 0
            zysk_prognoza = 0
            pacjenci_prognoza_sob = 0
            brutto_prognoza_sob = 0
            netto_prognoza_sob = 0
            zysk_prognoza_sob = 0

            for dzien_roboczy in self.dni[0]:
                querry_dane_dzien_roboczy = f'SELECT * FROM obroty_dzienne WHERE' \
                                            f' apteka = {apteka} and data = "{dzien_roboczy}"'
                dane_dzien_roboczy = self.zpt_database.mysql_querry(querry_dane_dzien_roboczy)
                if dane_dzien_roboczy:
                    pacjenci_prognoza += dane_dzien_roboczy[0][2]
                    brutto_prognoza += dane_dzien_roboczy[0][3]
                    netto_prognoza += dane_dzien_roboczy[0][4]
                    zysk_prognoza += dane_dzien_roboczy[0][5]

            for sobota in self.dni[1]:
                querry_dane_sobota = f'SELECT * FROM obroty_dzienne WHERE apteka = {apteka} and data = "{sobota}"'
                dane_sobota = self.zpt_database.mysql_querry(querry_dane_sobota)
                if dane_sobota:
                    pacjenci_prognoza_sob += dane_sobota[0][2]
                    brutto_prognoza_sob += dane_sobota[0][3]
                    netto_prognoza_sob += dane_sobota[0][4]
                    zysk_prognoza_sob += dane_sobota[0][5]

            self.dane_prognoza[f'{apteka}'] = [
                (pacjenci_prognoza / len(self.dni[0])) * self.dni[2] + (pacjenci_prognoza_sob / len(self.dni[1])) *
                self.dni[3],
                round((brutto_prognoza / len(self.dni[0])) * self.dni[2] + (brutto_prognoza_sob / len(self.dni[1])) *
                      self.dni[3], 2),
                round((netto_prognoza / len(self.dni[0])) * self.dni[2] + (netto_prognoza_sob / len(self.dni[1])) *
                      self.dni[3], 2),
                round((zysk_prognoza / len(self.dni[0])) * self.dni[2] + (zysk_prognoza_sob / len(self.dni[1])) *
                      self.dni[3], 2)]

            pacjenci_prognoza_all += (pacjenci_prognoza / len(self.dni[0])) * self.dni[2] + (
                        pacjenci_prognoza_sob / len(self.dni[1])) * self.dni[3]
            brutto_prognoza_all += (brutto_prognoza / len(self.dni[0])) * self.dni[2] + (
                        brutto_prognoza_sob / len(self.dni[1])) * self.dni[3]
            netto_prognoza_all += (netto_prognoza / len(self.dni[0])) * self.dni[2] + (
                        netto_prognoza_sob / len(self.dni[1])) * self.dni[3]
            zysk_prognoza_all += (zysk_prognoza / len(self.dni[0])) * self.dni[2] + (
                        zysk_prognoza_sob / len(self.dni[1])) * self.dni[3]
        self.dane_prognoza['razem'] = [pacjenci_prognoza_all, round(brutto_prognoza_all, 2),
                                       round(netto_prognoza_all, 2), round(zysk_prognoza_all, 2)]

        return self.dane_prognoza

    def get_zakupy_dane(self):
        self.zakupy_dane_dict = {}
        zakupy_all = 0

        for apteka in range(2, 9):
            querry_zakupy_dane = f'SELECT sum(wartosc) FROM zakupy_0{apteka} where dat_zak_fv BETWEEN' \
                                 f'  DATE_FORMAT(CURDATE() ,"%Y-%m-01")  AND CURDATE() '
            zakupy_dane = self.zpt_database.mysql_querry(querry_zakupy_dane)
            if zakupy_dane == [(None,)]:
                self.zakupy_dane_dict[f'{apteka}'] = 0
            else:
                self.zakupy_dane_dict[f'{apteka}'] = round(zakupy_dane[0][0], 2)
                zakupy_all += zakupy_dane[0][0]
        self.zakupy_dane_dict['razem'] = round(zakupy_all, 2)

        return self.zakupy_dane_dict

    def get_zakupy_hurtownie_dane(self):
        miesiac_dzis = str(datetime.date.today())[:7]
        lista_zakupy_hurtownie = []
        for apteka in range(2, 9):
            if apteka == 3:
                continue
            querry_zakupy_hurtownie_dane = f'SELECT kwoty FROM zakupy_hurtownie WHERE apteka = {apteka} AND' \
                                   f' miesiac LIKE "{miesiac_dzis}"'
            zakupy_hurtownie_dane = self.zpt_database.mysql_querry(querry_zakupy_hurtownie_dane)
            if zakupy_hurtownie_dane:
                dane = json.loads(zakupy_hurtownie_dane[0][0], encoding='utf-8')
                lista_zakupy_hurtownie.append(round(sum(dane.values()),2))
            else:
                lista_zakupy_hurtownie = []
        return lista_zakupy_hurtownie

    def get_procenty_dane(self):
        miesiac_dzis = str(datetime.date.today())[:7]
        lista_procentow = []
        for apteka in range(2, 9):
            if apteka == 3:
                continue
            querry_procenty_dane = f'SELECT procenty FROM zakupy_hurtownie WHERE apteka = {apteka} AND' \
                                   f' miesiac LIKE "{miesiac_dzis}"'
            procenty_dane = self.zpt_database.mysql_querry(querry_procenty_dane)
            if procenty_dane:
                dane = json.loads(procenty_dane[0][0], encoding='utf-8')
                lista_procentow.append(dane['NEUCA'])
            else:
                lista_procentow = []
        return lista_procentow

    @staticmethod
    def currency_format(i):
        currency = str(i)
        if currency == '0':
            return currency

        if currency[-3] == '.':
            pass
        else:
            currency += '0'

        if len(currency) > 6:
            sep_number = int(len(currency) / 3) - 1
            m = 0
            for n in range(sep_number):
                currency = currency[:-(6 + (3 * n) + m)] + ' ' + currency[-(6 + (3 * n) + m):]
                m += 1
        return currency

    def create_odswiez_button(self):
        self.odswiez_button = tk.Button(self, text="ODŚWIEŻ", bg='#544949', fg=f'{self.kolor_razem}',
                                        command=self.odswiez_dane)
        self.odswiez_button.place(relx=0.01, rely=0.02, relwidth=0.12, relheight=0.03)

    def create_odswiezenie_czas(self):
        self.odswiezenie_czas = tk.Label(self, text=f'DANE NA CZAS: {self.czas_odswiezenia}', bg=f'#383232',
                                         fg=f'{self.kolor_font}')
        self.odswiezenie_czas.place(relx=0.15, rely=0.03, relwidth=0.12, relheight=0.03)

    def odswiez_dane(self):
        # self.odswiez_button.configure(state='disabled')
        self.update_obroty_dzienne_dane()
        self.update_obroty_miesieczne_dane()
        self.update_zakupy_dane()
        self.update_zakupy_hurtownie_dane()
        self.update_procenty_dane()
        self.czas_odswiezenia = str(datetime.datetime.now().time())[:5]
        self.odswiezenie_czas.config(text=f'DANE NA CZAS: {self.czas_odswiezenia}')
        self.odswiez_button.configure(state='normal')

    # obroty dzienne
    def create_obroty_f1(self):
        self.obroty_dzienne_frame = tk.Frame(self)
        self.obroty_dzienne_frame.configure(bg='#383232', relief='groove', bd=1)
        self.obroty_dzienne_frame.place(relx=0.01, rely=0.06, relwidth=0.98, relheight=0.22)

    def create_obroty_dzienne_legenda(self):
        self.data_dzien = str(datetime.datetime.now())[0:16]
        self.obroty_dzienne_label = tk.Label(self, text=f'OBROTY DZIENNE: {self.data_dzien}', bg=f'#383232',
                                             fg=f'{self.kolor_font}')
        self.obroty_dzienne_label.place(relx=0.01, rely=0.03, relwidth=0.98, relheight=0.03)

        self.obroty_dzienne_legenda_apteka = tk.Label(self.obroty_dzienne_frame, text='APTEKA', relief='groove',
                                                      bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.obroty_dzienne_legenda_apteka.place(relwidth=1 / 6, relheight=1 / 8)
        self.obroty_dzienne_legenda_pacjenci = tk.Label(self.obroty_dzienne_frame, text='PACJENCI', relief='groove',
                                                        bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.obroty_dzienne_legenda_pacjenci.place(relx=1 / 6, relwidth=1 / 6, relheight=1 / 8)
        self.obroty_dzienne_legenda_brutto = tk.Label(self.obroty_dzienne_frame, text='OBROTY BRUTTO', relief='groove',
                                                      bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.obroty_dzienne_legenda_brutto.place(relx=2 / 6, relwidth=1 / 6, relheight=1 / 8)
        self.obroty_dzienne_legenda_netto = tk.Label(self.obroty_dzienne_frame, text='OBROTY NETTO', relief='groove',
                                                     bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.obroty_dzienne_legenda_netto.place(relx=3 / 6, relwidth=1 / 6, relheight=1 / 8)
        self.obroty_dzienne_legenda_zysk = tk.Label(self.obroty_dzienne_frame, text='ZYSK NETTO', relief='groove',
                                                    bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.obroty_dzienne_legenda_zysk.place(relx=4 / 6, relwidth=1 / 6, relheight=1 / 8)
        self.obroty_dzienne_legenda_magazyn = tk.Label(self.obroty_dzienne_frame, text='MAGAZYN', relief='groove',
                                                       bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.obroty_dzienne_legenda_magazyn.place(relx=5 / 6, relwidth=1 / 6, relheight=1 / 8)

        self.obroty_dzienne_legenda_nazwa_02 = tk.Label(self.obroty_dzienne_frame, text='HIPOKRATES 4', relief='groove',
                                                        bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.obroty_dzienne_legenda_nazwa_02.place(rely=1 / 8, relwidth=1 / 6, relheight=1 / 8)
        self.obroty_dzienne_legenda_nazwa_04 = tk.Label(self.obroty_dzienne_frame, text='HALLERA', relief='groove',
                                                        bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.obroty_dzienne_legenda_nazwa_04.place(rely=2 / 8, relwidth=1 / 6, relheight=1 / 8)
        self.obroty_dzienne_legenda_nazwa_05 = tk.Label(self.obroty_dzienne_frame, text='PIELGRZYMOWICE',
                                                        relief='groove',
                                                        bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.obroty_dzienne_legenda_nazwa_05.place(rely=3 / 8, relwidth=1 / 6, relheight=1 / 8)
        self.obroty_dzienne_legenda_nazwa_06 = tk.Label(self.obroty_dzienne_frame, text='WISŁA', relief='groove',
                                                        bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.obroty_dzienne_legenda_nazwa_06.place(rely=4 / 8, relwidth=1 / 6, relheight=1 / 8)
        self.obroty_dzienne_legenda_nazwa_07 = tk.Label(self.obroty_dzienne_frame, text='BIEDRONKA', relief='groove',
                                                        bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.obroty_dzienne_legenda_nazwa_07.place(rely=5 / 8, relwidth=1 / 6, relheight=1 / 8)
        self.obroty_dzienne_legenda_nazwa_08 = tk.Label(self.obroty_dzienne_frame, text='BZIE', relief='groove',
                                                        bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.obroty_dzienne_legenda_nazwa_08.place(rely=6 / 8, relwidth=1 / 6, relheight=1 / 8)

        self.obroty_dzienne_legenda_razem = tk.Label(self.obroty_dzienne_frame, text='RAZEM', relief='groove',
                                                     bg=f'{self.kolor_razem}', fg=f'{self.kolor_font_razem}')
        self.obroty_dzienne_legenda_razem.place(rely=7 / 8, relwidth=1 / 6, relheight=1 / 8)

    def create_oborty_dzienne_dane_frame(self):
        self.obroty_dzienne_dane_frame = tk.Frame(self.obroty_dzienne_frame)
        self.obroty_dzienne_dane_frame.configure(bg='white')
        self.obroty_dzienne_dane_frame.place(relx=1 / 6, rely=1 / 8, relwidth=5 / 6, relheight=7 / 8)

    def update_obroty_dzienne_dane(self):
        self.get_obroty_dzienne_data()
        if self.obroty_dzienne_dane_frame:
            self.obroty_dzienne_dane_frame.destroy()
        self.create_oborty_dzienne_dane_frame()

        self.obroty_dzienne_legenda_razem_pacjeci = tk.Label(self.obroty_dzienne_dane_frame,
                                                             text=f'{self.obroty_dzienne_dict[f"razem"][0]}',
                                                             relief='groove', bg=f'{self.kolor_razem}',
                                                             fg=f'{self.kolor_font_razem}')
        self.obroty_dzienne_legenda_razem_pacjeci.place(rely=6 / 7, relwidth=1 / 5, relheight=1 / 7)
        self.obroty_dzienne_legenda_razem_brutto = tk.Label(self.obroty_dzienne_dane_frame,
                                            text=f'{self.currency_format(self.obroty_dzienne_dict[f"razem"][1])} zł',
                                                            relief='groove', bg=f'{self.kolor_razem}',
                                            fg=f'{self.kolor_font_razem}')
        self.obroty_dzienne_legenda_razem_brutto.place(relx=1 / 5, rely=6 / 7, relwidth=1 / 5, relheight=1 / 7)
        self.obroty_dzienne_legenda_razem_netto = tk.Label(self.obroty_dzienne_dane_frame,
                                            text=f'{self.currency_format(self.obroty_dzienne_dict[f"razem"][2])} zł',
                                            relief='groove', bg=f'{self.kolor_razem}',
                                            fg=f'{self.kolor_font_razem}')
        self.obroty_dzienne_legenda_razem_netto.place(relx=2 / 5, rely=6 / 7, relwidth=1 / 5, relheight=1 / 7)
        self.obroty_dzienne_legenda_razem_zysk = tk.Label(self.obroty_dzienne_dane_frame,
                                            text=f'{self.currency_format(self.obroty_dzienne_dict[f"razem"][3])} zł',
                                            relief='groove', bg=f'{self.kolor_razem}',
                                            fg=f'{self.kolor_font_razem}')
        self.obroty_dzienne_legenda_razem_zysk.place(relx=3 / 5, rely=6 / 7, relwidth=1 / 5, relheight=1 / 7)
        self.obroty_dzienne_legenda_razem_magazyn = tk.Label(self.obroty_dzienne_dane_frame,
                                            text=f'{self.currency_format(self.obroty_dzienne_dict[f"razem"][4])} zł',
                                            relief='groove', bg=f'{self.kolor_razem}',
                                            fg=f'{self.kolor_font_razem}')
        self.obroty_dzienne_legenda_razem_magazyn.place(relx=4 / 5, rely=6 / 7, relwidth=1 / 5, relheight=1 / 7)

        for n in range(2, 9):
            if n == 3:
                continue

            if n > 3:
                m = n - 1
            else:
                m = n

            self.obroty_dzienne_pacjenci = tk.Label(self.obroty_dzienne_dane_frame,
                                                    text=f'{self.obroty_dzienne_dict[f"{n}"][0]}', relief='groove',
                                                    bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
            self.obroty_dzienne_pacjenci.place(rely=(m - 2) / 7, relwidth=1 / 5, relheight=1 / 7)
            self.obroty_dzienne_brutto = tk.Label(self.obroty_dzienne_dane_frame,
                                                  text=f'{self.currency_format(self.obroty_dzienne_dict[f"{n}"][1])} zł',
                                                  relief='groove',
                                                  bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
            self.obroty_dzienne_brutto.place(relx=1 / 5, rely=(m - 2) / 7, relwidth=1 / 5, relheight=1 / 7)
            self.obroty_dzienne_netto = tk.Label(self.obroty_dzienne_dane_frame,
                                                 text=f'{self.currency_format(self.obroty_dzienne_dict[f"{n}"][2])} zł',
                                                 relief='groove',
                                                 bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
            self.obroty_dzienne_netto.place(relx=2 / 5, rely=(m - 2) / 7, relwidth=1 / 5, relheight=1 / 7)
            self.obroty_dzienne_zysk = tk.Label(self.obroty_dzienne_dane_frame,
                                                text=f'{self.currency_format(self.obroty_dzienne_dict[f"{n}"][3])} zł',
                                                relief='groove',
                                                bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
            self.obroty_dzienne_zysk.place(relx=3 / 5, rely=(m - 2) / 7, relwidth=1 / 5, relheight=1 / 7)
            self.obroty_dzienne_magazyn = tk.Label(self.obroty_dzienne_dane_frame,
                                                   text=f'{self.currency_format(self.obroty_dzienne_dict[f"{n}"][4])} zł',
                                                   relief='groove',
                                                   bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
            self.obroty_dzienne_magazyn.place(relx=4 / 5, rely=(m - 2) / 7, relwidth=1 / 5, relheight=1 / 7)

        self.data_dzien = str(datetime.datetime.now())[0:16]
        self.obroty_dzienne_label.config(text=f'OBROTY DZIENNE: {self.data_dzien}')
        self.after(60000, lambda: self.update_obroty_dzienne_dane())

    # obroty miesięczne
    def create_obroty_miesieczne_frame(self):
        self.obroty_miesieczne_frame = tk.Frame(self)
        self.obroty_miesieczne_frame.configure(bg='#383232', relief='groove', bd=1)
        self.obroty_miesieczne_frame.place(relx=0.01, rely=0.32, relwidth=0.98, relheight=0.22)

    def create_obroty_miesieczne_legenda(self):
        self.data_miesiac = str(datetime.datetime.now())[0:16]
        self.obroty_miesieczne_label = tk.Label(self, text=f'OBROTY MIESIĘCZNE: {self.data_miesiac}', bg=f'#383232'
                                                , fg=f'{self.kolor_font}')
        self.obroty_miesieczne_label.place(relx=0.01, rely=0.29, relwidth=0.98, relheight=0.03)

        self.obroty_miesieczne_legenda_apteka = tk.Label(self.obroty_miesieczne_frame, text='APTEKA', relief='groove',
                                                         bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.obroty_miesieczne_legenda_apteka.place(relwidth=1 / 6, relheight=1 / 8)
        self.obroty_miesieczne_legenda_pacjenci = tk.Label(self.obroty_miesieczne_frame, text='PACJENCI',
                                                           relief='groove',
                                                           bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.obroty_miesieczne_legenda_pacjenci.place(relx=1 / 6, relwidth=1 / 6, relheight=1 / 8)
        self.obroty_miesieczne_legenda_brutto = tk.Label(self.obroty_miesieczne_frame, text='OBROTY BRUTTO',
                                                         relief='groove',
                                                         bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.obroty_miesieczne_legenda_brutto.place(relx=2 / 6, relwidth=1 / 6, relheight=1 / 8)
        self.obroty_miesieczne_legenda_netto = tk.Label(self.obroty_miesieczne_frame, text='OBROTY NETTO',
                                                        relief='groove',
                                                        bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.obroty_miesieczne_legenda_netto.place(relx=3 / 6, relwidth=1 / 6, relheight=1 / 8)
        self.obroty_miesieczne_legenda_zysk = tk.Label(self.obroty_miesieczne_frame, text='ZYSK NETTO', relief='groove',
                                                       bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.obroty_miesieczne_legenda_zysk.place(relx=4 / 6, relwidth=1 / 6, relheight=1 / 8)
        self.obroty_miesieczne_legenda_magazyn = tk.Label(self.obroty_miesieczne_frame, text='MARŻA', relief='groove',
                                                          bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.obroty_miesieczne_legenda_magazyn.place(relx=5 / 6, relwidth=1 / 6, relheight=1 / 8)

        self.obroty_miesieczne_legenda_nazwa_02 = tk.Label(self.obroty_miesieczne_frame, text='HIPOKRATES 4',
                                                           relief='groove',
                                                           bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.obroty_miesieczne_legenda_nazwa_02.place(rely=1 / 8, relwidth=1 / 6, relheight=1 / 8)
        self.obroty_miesieczne_legenda_nazwa_04 = tk.Label(self.obroty_miesieczne_frame, text='HALLERA',
                                                           relief='groove',
                                                           bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.obroty_miesieczne_legenda_nazwa_04.place(rely=2 / 8, relwidth=1 / 6, relheight=1 / 8)
        self.obroty_miesieczne_legenda_nazwa_05 = tk.Label(self.obroty_miesieczne_frame, text='PIELGRZYMOWICE',
                                                           relief='groove',
                                                           bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.obroty_miesieczne_legenda_nazwa_05.place(rely=3 / 8, relwidth=1 / 6, relheight=1 / 8)
        self.obroty_miesieczne_legenda_nazwa_06 = tk.Label(self.obroty_miesieczne_frame, text='WISŁA', relief='groove',
                                                           bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.obroty_miesieczne_legenda_nazwa_06.place(rely=4 / 8, relwidth=1 / 6, relheight=1 / 8)
        self.obroty_miesieczne_legenda_nazwa_07 = tk.Label(self.obroty_miesieczne_frame, text='BIEDRONKA',
                                                           relief='groove',
                                                           bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.obroty_miesieczne_legenda_nazwa_07.place(rely=5 / 8, relwidth=1 / 6, relheight=1 / 8)
        self.obroty_miesieczne_legenda_nazwa_08 = tk.Label(self.obroty_miesieczne_frame, text='BZIE', relief='groove',
                                                           bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.obroty_miesieczne_legenda_nazwa_08.place(rely=6 / 8, relwidth=1 / 6, relheight=1 / 8)

        self.obroty_miesieczne_legenda_razem = tk.Label(self.obroty_miesieczne_frame, text='RAZEM', relief='groove',
                                                        bg=f'{self.kolor_razem}', fg=f'{self.kolor_font_razem}')
        self.obroty_miesieczne_legenda_razem.place(rely=7 / 8, relwidth=1 / 6, relheight=1 / 8)

    def create_oborty_miesieczne_dane_frame(self):
        self.oborty_miesieczne_dane_frame = tk.Frame(self.obroty_miesieczne_frame)
        self.oborty_miesieczne_dane_frame.configure(bg='white')
        self.oborty_miesieczne_dane_frame.place(relx=1 / 6, rely=1 / 8, relwidth=5 / 6, relheight=7 / 8)

    def update_obroty_miesieczne_dane(self):
        self.get_obroty_miesieczne_data()
        if self.oborty_miesieczne_dane_frame:
            self.oborty_miesieczne_dane_frame.destroy()
        self.create_oborty_miesieczne_dane_frame()
        self.obroty_miesieczne_legenda_razem_pacjeci = tk.Label(self.obroty_miesieczne_frame,
                                                                text=f'{self.obroty_miesieczne_dict["razem"][0]}',
                                                                relief='groove',
                                                                bg=f'{self.kolor_razem}', fg=f'{self.kolor_font_razem}')
        self.obroty_miesieczne_legenda_razem_pacjeci.place(relx=1 / 6, rely=7 / 8, relwidth=1 / 6, relheight=1 / 8)
        self.obroty_miesieczne_legenda_razem_brutto = tk.Label(self.obroty_miesieczne_frame,
                                                               text=f'{self.currency_format(self.obroty_miesieczne_dict["razem"][1])} zł',
                                                               relief='groove',
                                                               bg=f'{self.kolor_razem}', fg=f'{self.kolor_font_razem}')
        self.obroty_miesieczne_legenda_razem_brutto.place(relx=2 / 6, rely=7 / 8, relwidth=1 / 6, relheight=1 / 8)
        self.obroty_miesieczne_legenda_razem_netto = tk.Label(self.obroty_miesieczne_frame,
                                                              text=f'{self.currency_format(self.obroty_miesieczne_dict["razem"][2])} zł',
                                                              relief='groove',
                                                              bg=f'{self.kolor_razem}', fg=f'{self.kolor_font_razem}')
        self.obroty_miesieczne_legenda_razem_netto.place(relx=3 / 6, rely=7 / 8, relwidth=1 / 6, relheight=1 / 8)
        self.obroty_miesieczne_legenda_razem_zysk = tk.Label(self.obroty_miesieczne_frame,
                                                             text=f'{self.currency_format(self.obroty_miesieczne_dict["razem"][3])} zł',
                                                             relief='groove',
                                                             bg=f'{self.kolor_razem}', fg=f'{self.kolor_font_razem}')
        self.obroty_miesieczne_legenda_razem_zysk.place(relx=4 / 6, rely=7 / 8, relwidth=1 / 6, relheight=1 / 8)
        self.obroty_miesieczne_legenda_razem_marza = tk.Label(self.obroty_miesieczne_frame,
                                                              text=f'{self.obroty_miesieczne_dict["razem"][4]} %',
                                                              relief='groove',
                                                              bg=f'{self.kolor_razem}', fg=f'{self.kolor_font_razem}')
        self.obroty_miesieczne_legenda_razem_marza.place(relx=5 / 6, rely=7 / 8, relwidth=1 / 6, relheight=1 / 8)

        for n in range(2, 9):
            m = 0
            if n == 3:
                continue

            if n > 3:
                m = n - 1
            else:
                m = n
            self.obroty_miesieczne_pacjenci = tk.Label(self.obroty_miesieczne_frame,
                                                       text=f'{self.obroty_miesieczne_dict[f"{n}"][0]}',
                                                       relief='groove',
                                                       bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
            self.obroty_miesieczne_pacjenci.place(relx=1 / 6, rely=(m - 1) / 8, relwidth=1 / 6, relheight=1 / 8)
            self.obroty_miesieczne_brutto = tk.Label(self.obroty_miesieczne_frame,
                                                     text=f'{self.currency_format(self.obroty_miesieczne_dict[f"{n}"][1])} zł',
                                                     relief='groove',
                                                     bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
            self.obroty_miesieczne_brutto.place(relx=2 / 6, rely=(m - 1) / 8, relwidth=1 / 6, relheight=1 / 8)
            self.obroty_miesieczne_netto = tk.Label(self.obroty_miesieczne_frame,
                                                    text=f'{self.currency_format(self.obroty_miesieczne_dict[f"{n}"][2])}',
                                                    relief='groove',
                                                    bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
            self.obroty_miesieczne_netto.place(relx=3 / 6, rely=(m - 1) / 8, relwidth=1 / 6, relheight=1 / 8)
            self.obroty_miesieczne_zysk = tk.Label(self.obroty_miesieczne_frame,
                                                   text=f'{self.currency_format(self.obroty_miesieczne_dict[f"{n}"][3])}',
                                                   relief='groove',
                                                   bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
            self.obroty_miesieczne_zysk.place(relx=4 / 6, rely=(m - 1) / 8, relwidth=1 / 6, relheight=1 / 8)
            self.obroty_miesieczne_marza = tk.Label(self.obroty_miesieczne_frame,
                                                    text=f'{self.obroty_miesieczne_dict[f"{n}"][4]} %', relief='groove',
                                                    bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
            self.obroty_miesieczne_marza.place(relx=5 / 6, rely=(m - 1) / 8, relwidth=1 / 6, relheight=1 / 8)

        self.data_miesiac = str(datetime.datetime.now())[0:16]
        self.obroty_miesieczne_label.config(text=f'OBROTY MIESIĘCZNE: {self.data_miesiac}')
        self.controller.logger.log(20, f'Aktualizacja obrotów miesięcznych.')
        self.after(1800000, lambda: self.update_obroty_miesieczne_dane())

    # obroty miesięczne prognoza
    def create_obroty_miesieczne_prognoza_frame(self):
        self.obroty_miesieczne_prognoza_frame = tk.Frame(self)
        self.obroty_miesieczne_prognoza_frame.configure(bg='#383232', relief='groove', bd=1)
        self.obroty_miesieczne_prognoza_frame.place(relx=0.01, rely=0.58, relwidth=0.98, relheight=0.22)

    def create_obroty_miesieczne_prognoza_legenda(self):
        self.data_miesiac_prog = str(datetime.datetime.now().date())[0:7]
        self.obroty_miesieczne_prognoza_label = tk.Label(self,
                                                         text=f'OBROTY MIESIĘCZNE PROGNOZA: {self.data_miesiac_prog}',
                                                         bg=f'#383232', fg=f'{self.kolor_font}')
        self.obroty_miesieczne_prognoza_label.place(relx=0.01, rely=0.55, relwidth=0.98, relheight=0.03)

        self.obroty_miesieczne_prognoza_legenda_apteka = tk.Label(self.obroty_miesieczne_prognoza_frame, text='APTEKA',
                                                                  relief='groove',
                                                                  bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.obroty_miesieczne_prognoza_legenda_apteka.place(relwidth=1 / 5, relheight=1 / 8)
        self.obroty_miesieczne_prognoza_legenda_pacjenci = tk.Label(self.obroty_miesieczne_prognoza_frame,
                                                                    text='PACJENCI',
                                                                    relief='groove',
                                                                    bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.obroty_miesieczne_prognoza_legenda_pacjenci.place(relx=1 / 5, relwidth=1 / 5, relheight=1 / 8)
        self.obroty_miesieczne_prognoza_legenda_brutto = tk.Label(self.obroty_miesieczne_prognoza_frame,
                                                                  text='OBROTY BRUTTO',
                                                                  relief='groove',
                                                                  bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.obroty_miesieczne_prognoza_legenda_brutto.place(relx=2 / 5, relwidth=1 / 5, relheight=1 / 8)
        self.obroty_miesieczne_prognoza_legenda_netto = tk.Label(self.obroty_miesieczne_prognoza_frame,
                                                                 text='OBROTY NETTO',
                                                                 relief='groove',
                                                                 bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.obroty_miesieczne_prognoza_legenda_netto.place(relx=3 / 5, relwidth=1 / 5, relheight=1 / 8)
        self.obroty_miesieczne_prognoza_legenda_zysk = tk.Label(self.obroty_miesieczne_prognoza_frame,
                                                                text='ZYSK NETTO',
                                                                relief='groove',
                                                                bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.obroty_miesieczne_prognoza_legenda_zysk.place(relx=4 / 5, relwidth=1 / 5, relheight=1 / 8)

        self.obroty_miesieczne_prognoza_legenda_nazwa_02 = tk.Label(self.obroty_miesieczne_prognoza_frame,
                                                                    text='HIPOKRATES 4',
                                                                    relief='groove',
                                                                    bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.obroty_miesieczne_prognoza_legenda_nazwa_02.place(rely=1 / 8, relwidth=1 / 5, relheight=1 / 8)
        self.obroty_miesieczne_prognoza_legenda_nazwa_04 = tk.Label(self.obroty_miesieczne_prognoza_frame,
                                                                    text='HALLERA',
                                                                    relief='groove',
                                                                    bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.obroty_miesieczne_prognoza_legenda_nazwa_04.place(rely=2 / 8, relwidth=1 / 5, relheight=1 / 8)
        self.obroty_miesieczne_prognoza_legenda_nazwa_05 = tk.Label(self.obroty_miesieczne_prognoza_frame,
                                                                    text='PIELGRZYMOWICE',
                                                                    relief='groove',
                                                                    bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.obroty_miesieczne_prognoza_legenda_nazwa_05.place(rely=3 / 8, relwidth=1 / 5, relheight=1 / 8)
        self.obroty_miesieczne_prognoza_legenda_nazwa_06 = tk.Label(self.obroty_miesieczne_prognoza_frame, text='WISŁA',
                                                                    relief='groove',
                                                                    bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.obroty_miesieczne_prognoza_legenda_nazwa_06.place(rely=4 / 8, relwidth=1 / 5, relheight=1 / 8)
        self.obroty_miesieczne_prognoza_legenda_nazwa_07 = tk.Label(self.obroty_miesieczne_prognoza_frame,
                                                                    text='BIEDRONKA',
                                                                    relief='groove',
                                                                    bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.obroty_miesieczne_prognoza_legenda_nazwa_07.place(rely=5 / 8, relwidth=1 / 5, relheight=1 / 8)
        self.obroty_miesieczne_prognoza_legenda_nazwa_08 = tk.Label(self.obroty_miesieczne_prognoza_frame, text='BZIE',
                                                                    relief='groove',
                                                                    bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.obroty_miesieczne_prognoza_legenda_nazwa_08.place(rely=6 / 8, relwidth=1 / 5, relheight=1 / 8)

        self.obroty_miesieczne_prognoza_legenda_razem = tk.Label(self.obroty_miesieczne_prognoza_frame, text='RAZEM',
                                                                 relief='groove',
                                                                 bg=f'{self.kolor_razem}')
        self.obroty_miesieczne_prognoza_legenda_razem.place(rely=7 / 8, relwidth=1 / 5, relheight=1 / 8)

    def create_oborty_miesieczne_prognoza_dane_frame(self):
        self.oborty_miesieczne_prognoza_dane_frame = tk.Frame(self.obroty_miesieczne_prognoza_frame)
        self.oborty_miesieczne_prognoza_dane_frame.configure(bg='white')
        self.oborty_miesieczne_prognoza_dane_frame.place(relx=1 / 5, rely=1 / 8, relwidth=4 / 5, relheight=7 / 8)

    def update_obroty_miesieczne_prognoza_dane(self):
        self.obroty_miesieczne_prognoza_legenda_razem_pacjeci = tk.Label(self.oborty_miesieczne_prognoza_dane_frame,
                                                                         text=f'{int(self.dane_prognoza["razem"][0])}',
                                                                         relief='groove',
                                                                         bg=f'{self.kolor_razem}')
        self.obroty_miesieczne_prognoza_legenda_razem_pacjeci.place(rely=6 / 7, relwidth=1 / 4, relheight=1 / 7)
        self.obroty_miesieczne_prognoza_legenda_razem_brutto = tk.Label(self.oborty_miesieczne_prognoza_dane_frame,
                                                                        text=f'{self.currency_format(self.dane_prognoza["razem"][1])} zł',
                                                                        relief='groove',
                                                                        bg=f'{self.kolor_razem}')
        self.obroty_miesieczne_prognoza_legenda_razem_brutto.place(relx=1 / 4, rely=6 / 7, relwidth=1 / 4,
                                                                   relheight=1 / 7)
        self.obroty_miesieczne_prognoza_legenda_razem_netto = tk.Label(self.oborty_miesieczne_prognoza_dane_frame,
                                                                       text=f'{self.currency_format(self.dane_prognoza["razem"][2])} zł',
                                                                       relief='groove',
                                                                       bg=f'{self.kolor_razem}')
        self.obroty_miesieczne_prognoza_legenda_razem_netto.place(relx=2 / 4, rely=6 / 7, relwidth=1 / 4,
                                                                  relheight=1 / 7)
        self.obroty_miesieczne_prognoza_legenda_razem_zysk = tk.Label(self.oborty_miesieczne_prognoza_dane_frame,
                                                                      text=f'{self.currency_format(self.dane_prognoza["razem"][3])} zł',
                                                                      relief='groove',
                                                                      bg=f'{self.kolor_razem}')
        self.obroty_miesieczne_prognoza_legenda_razem_zysk.place(relx=3 / 4, rely=6 / 7, relwidth=1 / 4,
                                                                 relheight=1 / 7)

        for n in range(2, 9):
            m = 0
            if n == 3:
                continue

            if n > 3:
                m = n - 1
            else:
                m = n
            self.obroty_miesieczne_prognoza_pacjenci = tk.Label(self.oborty_miesieczne_prognoza_dane_frame,
                                                                text=f'{int(self.dane_prognoza[f"{n}"][0])}',
                                                                relief='groove',
                                                                bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
            self.obroty_miesieczne_prognoza_pacjenci.place(rely=(m - 2) / 7, relwidth=1 / 4, relheight=1 / 7)
            self.obroty_miesieczne_prognoza_brutto = tk.Label(self.oborty_miesieczne_prognoza_dane_frame,
                                                              text=f'{self.currency_format(self.dane_prognoza[f"{n}"][1])} zł',
                                                              relief='groove',
                                                              bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
            self.obroty_miesieczne_prognoza_brutto.place(relx=1 / 4, rely=(m - 2) / 7, relwidth=1 / 4, relheight=1 / 7)
            self.obroty_miesieczne_prognoza_netto = tk.Label(self.oborty_miesieczne_prognoza_dane_frame,
                                                             text=f'{self.currency_format(self.dane_prognoza[f"{n}"][2])} zł',
                                                             relief='groove',
                                                             bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
            self.obroty_miesieczne_prognoza_netto.place(relx=2 / 4, rely=(m - 2) / 7, relwidth=1 / 4, relheight=1 / 7)
            self.obroty_miesieczne_prognoza_zysk = tk.Label(self.oborty_miesieczne_prognoza_dane_frame,
                                                            text=f'{self.currency_format(self.dane_prognoza[f"{n}"][3])} zł',
                                                            relief='groove',
                                                            bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
            self.obroty_miesieczne_prognoza_zysk.place(relx=3 / 4, rely=(m - 2) / 7, relwidth=1 / 4, relheight=1 / 7)

        self.controller.logger.log(20, f'Aktualizacja prognozy obrotów.')

    # zakupy
    def create_zakupy_frame(self):
        self.obroty_zakupy_frame = tk.Frame(self)
        self.obroty_zakupy_frame.configure(bg='#383232', relief='groove', bd=1)
        self.obroty_zakupy_frame.place(relx=0.01, rely=0.84, relwidth=0.98, relheight=60 / 450)

    def create_zakupy_legenda(self):
        data_miesiac_prog = str(datetime.datetime.now().date())[0:7]
        obroty_zakupy_label = tk.Label(self, text=f'ZAKUPY W MIESIĄCU: {data_miesiac_prog}',
                                       bg=f'#383232', fg=f'{self.kolor_font}')
        obroty_zakupy_label.place(relx=0.01, rely=0.81, relwidth=0.98, relheight=0.03)
        obroty_zakupy_legenda_apteka = tk.Label(self.obroty_zakupy_frame, text='',
                                                relief='groove',
                                                bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        obroty_zakupy_legenda_apteka.place(relwidth=1 / 8, relheight=1 / 4)
        obroty_zakupy_legenda_apteka_02 = tk.Label(self.obroty_zakupy_frame, text='HIPOKRATES 4',
                                                   relief='groove',
                                                   bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        obroty_zakupy_legenda_apteka_02.place(relx=1 / 8, relwidth=1 / 8, relheight=1 / 4)
        obroty_zakupy_legenda_apteka_04 = tk.Label(self.obroty_zakupy_frame, text='HALLERA',
                                                   relief='groove',
                                                   bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        obroty_zakupy_legenda_apteka_04.place(relx=2 / 8, relwidth=1 / 8, relheight=1 / 4)
        obroty_zakupy_legenda_apteka_05 = tk.Label(self.obroty_zakupy_frame, text='PIELGRZYMOWICE',
                                                   relief='groove',
                                                   bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        obroty_zakupy_legenda_apteka_05.place(relx=3 / 8, relwidth=1 / 8, relheight=1 / 4)
        obroty_zakupy_legenda_apteka_06 = tk.Label(self.obroty_zakupy_frame, text='WISŁA',
                                                   relief='groove',
                                                   bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        obroty_zakupy_legenda_apteka_06.place(relx=4 / 8, relwidth=1 / 8, relheight=1 / 4)
        obroty_zakupy_legenda_apteka_07 = tk.Label(self.obroty_zakupy_frame, text='BIEDRONKA',
                                                   relief='groove',
                                                   bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        obroty_zakupy_legenda_apteka_07.place(relx=5 / 8, relwidth=1 / 8, relheight=1 / 4)
        obroty_zakupy_legenda_apteka_07 = tk.Label(self.obroty_zakupy_frame, text='BZIE',
                                                   relief='groove',
                                                   bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        obroty_zakupy_legenda_apteka_07.place(relx=6 / 8, relwidth=1 / 8, relheight=1 / 4)
        obroty_zakupy_legenda_apteka_razem = tk.Label(self.obroty_zakupy_frame, text='RAZEM',
                                                      relief='groove',
                                                      bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        obroty_zakupy_legenda_apteka_razem.place(relx=7 / 8, relwidth=1 / 8, relheight=1 / 4)
        obroty_zakupy_legenda_apteka_opis = tk.Label(self.obroty_zakupy_frame, text='WSZYSCY DOSTAWCY',
                                                     relief='groove',
                                                     bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        obroty_zakupy_legenda_apteka_opis.place(relx=0 / 8, rely=1 / 4, relwidth=1 / 8, relheight=1 / 4)
        procenty_zakupy_legenda_apteka_opis = tk.Label(self.obroty_zakupy_frame, text='ZAKUPY HURTOWNIE',
                                                       relief='groove',
                                                       bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        procenty_zakupy_legenda_apteka_opis.place(relx=0 / 8, rely=2 / 4, relwidth=1 / 8, relheight=1 / 4)
        procenty_zakupy_legenda_apteka_opis = tk.Label(self.obroty_zakupy_frame, text='PROCENTY NEUCA',
                                                       relief='groove',
                                                       bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        procenty_zakupy_legenda_apteka_opis.place(relx=0 / 8, rely=3 / 4, relwidth=1 / 8, relheight=1 / 4)

    def update_zakupy_dane(self):
        self.dane_zakupy = self.get_zakupy_dane()
        for apteka in range(2, 9):
            m = 0
            if apteka == 3:
                continue

            if apteka > 3:
                m = apteka - 1
            else:
                m = apteka

            obroty_zakupy_apteka_dane = tk.Label(self.obroty_zakupy_frame,
                                                 text=f'{self.currency_format(self.dane_zakupy[f"{apteka}"])} zł',
                                                 relief='groove',
                                                 bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
            obroty_zakupy_apteka_dane.place(relx=(m - 1) / 8, rely=1 / 4, relwidth=1 / 8, relheight=1 / 4)
        obroty_zakupy_razem_apteka_dane = tk.Label(self.obroty_zakupy_frame,
                                                   text=f'{self.currency_format(self.dane_zakupy["razem"])} zł',
                                                   relief='groove',
                                                   bg=f'{self.kolor_razem}', fg=f'{self.kolor_font_razem}')
        obroty_zakupy_razem_apteka_dane.place(relx=7 / 8, rely=1 / 4, relwidth=1 / 8, relheight=1 / 4)

        self.controller.logger.log(20, f'Aktualizacja danych zakupowych.')
        self.after(3600000, lambda: self.update_zakupy_dane())

    def update_zakupy_hurtownie_dane(self):
        dane_zakupy_hurtownie = self.get_zakupy_hurtownie_dane()
        for m in range(6):
            if dane_zakupy_hurtownie != [] and len(dane_zakupy_hurtownie) == 6:
                zakupy_hurtownie_apteka_dane = tk.Label(self.obroty_zakupy_frame,
                                                     text=f'{self.currency_format(dane_zakupy_hurtownie[m])} zł',
                                                     relief='groove',
                                                     bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
                zakupy_hurtownie_apteka_dane.place(relx=(m + 1) / 8, rely=2 / 4, relwidth=1 / 8, relheight=1 / 4)
            else:
                zakupy_hurtownie_apteka_dane = tk.Label(self.obroty_zakupy_frame,
                                                        text=f'BRAK DANYCH',
                                                        relief='groove',
                                                        bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
                zakupy_hurtownie_apteka_dane.place(relx=(m + 1) / 8, rely=2 / 4, relwidth=1 / 8, relheight=1 / 4)

        self.controller.logger.log(20, f'Aktualizacja danych zakupowych hurtowni.')
        self.after(3600000, lambda: self.update_zakupy_hurtownie_dane())


    def update_procenty_dane(self):
        lista_procentow = self.get_procenty_dane()
        for m in range(6):
            kolor_procent = 'green'
            if lista_procentow != [] and len(lista_procentow) == 6:
                if lista_procentow[m] < 80:
                    kolor_procent = 'red'
                procenty_zakupy_apteka_dane = tk.Label(self.obroty_zakupy_frame,
                                                       text=f'{lista_procentow[m]} %',
                                                       relief='groove',
                                                       bg=f'{self.kolor_legenda}', fg=kolor_procent)
                procenty_zakupy_apteka_dane.place(relx=(m + 1) / 8, rely=3 / 4, relwidth=1 / 8, relheight=1 / 4)
            else:
                procenty_zakupy_apteka_dane = tk.Label(self.obroty_zakupy_frame,
                                                       text=f'BRAK DANYCH',
                                                       relief='groove',
                                                       bg=f'{self.kolor_legenda}', fg=kolor_procent)
                procenty_zakupy_apteka_dane.place(relx=(m + 1) / 8, rely=3 / 4, relwidth=1 / 8, relheight=1 / 4)

        self.controller.logger.log(20, f'Aktualizacja danych zakupowych - procenty NEUCA.')
        self.after(3600000, lambda: self.update_procenty_dane())

class Gotowki_frame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.configure(bg='#383232')
        self.zpt_database = ZPT_Database.ZPT_base()
        self.kolor_razem = '#b58b14'
        self.apteki_dict = {'1': 'WSZYSCY', '2': 'HIPOKRATES 4', '3': 'HIPOKRATES 3', '4': 'HALLERA',
                            '5': 'PIELGRZYMOWICE',
                            '6': 'WISŁA', '7': 'BIEDRONKA', '8': 'BZIE', '9': 'BANK', '10': 'INNE'}
        self.create_gotowki_frame()
        self.create_gotowki_treeview()
        self.create_gotowki_L_2lf()
        self.create_gotowki_saldo_frame()
        self.create_gotowki_L_1f()
        self.create_gotowki_R_1f()

    def create_gotowki_frame(self):
        self.gotowki_main_frame = tk.Frame(self)
        self.gotowki_main_frame.configure(bg='#383232', relief='groove', bd=1)
        self.gotowki_main_frame.place(relx=0.01, rely=0.02, relwidth=0.46, relheight=0.96)

    def create_gotowki_L_2lf(self):
        self.gotowki_L_2lf = tk.LabelFrame(self.gotowki_main_frame, text='   FILTR   ', bg='#383232',
                                           relief='groove', bd=1, fg='white')
        self.gotowki_L_2lf.place(relx=0.02, rely=0.14, relwidth=0.47, relheight=0.05)

        apteki = ['WSZYSCY', 'HIPOKRATES 4', 'HIPOKRATES 3', 'HALLERA', 'PIELGRZYMOWICE', 'WISŁA', 'BIEDRONKA', 'BZIE',
                  'BANK', 'INNE']

        self.filtr_options = ttk.Combobox(self.gotowki_L_2lf, values=apteki, state='readonly')
        self.filtr_options.place(relx=0.15, rely=0.06, relwidth=0.7)
        self.filtr_options.current(0)
        self.get_apteka_wybor(self.filtr_options.get())
        self.filtr_options.bind("<<ComboboxSelected>>", self.get_apteka_wybor)

    def create_gotowki_treeview(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', fieldbackground="#383232", background="#383232", foreground='white')
        style.configure("Treeview.Heading", background="#383232", foreground="white")
        style.map('Treeview.Heading', background=[('disabled', '#383232')])

        def fixed_map(option):  # naprawa buga wersji dla Python 3.7 przy wyświetlaniu koloru linii w treeview
            return [elm for elm in style.map("Treeview", query_opt=option)
                    if elm[:2] != ("!disabled", "!selected")]

        style.map("Treeview", foreground=fixed_map("foreground"),
                  background=fixed_map("background"))

        self.gotowki_L_3f = tk.Frame(self.gotowki_main_frame)
        self.gotowki_L_3f.configure(bg='#383232', relief='groove', bd=1)
        self.gotowki_L_3f.place(relx=0.02, rely=0.20, relwidth=0.96, relheight=0.79)

        self.columns_gotowki = ('ID', 'DATA', 'MIEJSCE', 'KWOTA', 'OPIS')
        self.treeview_gotowki = ttk.Treeview(self.gotowki_L_3f, columns=self.columns_gotowki, show='headings',
                                             style="Treeview", selectmode="browse")

        self.treeview_gotowki.heading('ID', text='ID')
        self.treeview_gotowki.column('ID', minwidth=0, width=50, stretch='no', anchor='center')
        self.treeview_gotowki.heading('DATA', text='DATA')
        self.treeview_gotowki.column('DATA', minwidth=0, width=150, stretch='no', anchor='center')
        self.treeview_gotowki.heading('MIEJSCE', text='MIEJSCE')
        self.treeview_gotowki.column('MIEJSCE', minwidth=0, width=150, stretch='no', anchor='center')
        self.treeview_gotowki.heading('KWOTA', text='KWOTA')
        self.treeview_gotowki.column('KWOTA', minwidth=200, stretch='no', anchor='center')
        self.treeview_gotowki.heading('OPIS', text='OPIS')
        self.treeview_gotowki.column('OPIS', minwidth=200, stretch='yes', anchor='center')

        self.scrolly = ttk.Scrollbar(self.treeview_gotowki, orient='vertical', command=self.treeview_gotowki.yview)
        self.treeview_gotowki.configure(yscrollcommand=self.scrolly.set)
        map(lambda col: col.configure(yscrollcommand=self.scrolly.set), self.columns_gotowki)
        self.scrolly.pack(side=tk.RIGHT, fill=tk.Y)
        map(lambda col: col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True), self.columns_gotowki)
        self.treeview_gotowki.pack(expand='yes', fill='both')
        self.treeview_gotowki.bind("<Double-1>", self.poprawa_wpisu)

    def create_gotowki_saldo_frame(self):
        self.gotowki_L_2rf = tk.LabelFrame(self.gotowki_main_frame, text='   SALDO   ', bg='#383232',
                                           relief='groove', bd=1, fg='white')
        self.gotowki_L_2rf.place(relx=0.51, rely=0.14, relwidth=0.47, relheight=0.05)
        saldo = self.get_gotowki_saldo()
        self.saldo_display = tk.Label(self.gotowki_L_2rf, text=f'{saldo} zł', bg='#383232',
                                      font=("Verdena", "14", "bold"), fg='green')
        self.saldo_display.place(relwidth=1, relheight=1)

    def get_gotowki_saldo(self):
        self.querry_saldo = f'SELECT SUM(kwota) FROM gotowki'
        self.saldo = self.zpt_database.mysql_querry(self.querry_saldo)
        return self.saldo[0][0]

    def update_saldo_display(self):
        saldo = self.get_gotowki_saldo()
        self.saldo_display.config(text=f'{saldo} zł')
        self.get_apteka_wybor_after_change()

    def get_apteka_wybor(self, event):
        apteka_wybor = self.filtr_options.get()
        for key, val in self.apteki_dict.items():
            if val == apteka_wybor:
                apteka_wybor = key
        self.get_gotowki_dane(apteka_wybor)

    def get_apteka_wybor_after_change(self):
        apteka_wybor = self.filtr_options.get()
        for key, val in self.apteki_dict.items():
            if val == apteka_wybor:
                apteka_wybor = key
        self.get_gotowki_dane(apteka_wybor)

    def get_gotowki_dane(self, apteka_wybor):
        if apteka_wybor == "1":
            self.guerry_gotowki_dane = f'SELECT * FROM gotowki WHERE data > DATE_SUB(NOW(), INTERVAL 20 DAY) ORDER BY id_got DESC'
        else:
            self.guerry_gotowki_dane = f'SELECT * FROM gotowki WHERE id_apteka = {apteka_wybor} ORDER BY id_got DESC'
        self.gotowki_dane = self.zpt_database.mysql_querry(self.guerry_gotowki_dane)
        self.update_gotowki_treeview(self.gotowki_dane)

    def update_gotowki_treeview(self, dane):
        self.treeview_gotowki.delete(*self.treeview_gotowki.get_children())
        i = 0
        for n in dane:
            i += 1
            gotowki_id = n[0]
            gotowki_data = n[1]
            gotowki_apteka_id = str(n[2])
            gotowki_apteka = self.apteki_dict[f'{gotowki_apteka_id}']
            gotowki_kwota = n[3]
            gotowki_opis = n[4]

            if i % 2 == 0:
                background_gotowki = 'background_dark'
            else:
                background_gotowki = 'background_light'

            if gotowki_kwota < 0:
                foreground_gotowki = 'foreground_bank'
            else:
                foreground_gotowki = 'foreground_plus'

            self.treeview_gotowki.tag_configure('background_dark', background='#383232')
            self.treeview_gotowki.tag_configure('background_light', background='#262424')
            self.treeview_gotowki.tag_configure('foreground_bank', foreground='red')
            self.treeview_gotowki.tag_configure('foreground_plus', foreground='white')

            self.treeview_gotowki.insert('', 'end', values=(gotowki_id, gotowki_data, gotowki_apteka, gotowki_kwota,
                                                            gotowki_opis),
                                         tags=(background_gotowki, foreground_gotowki))

    def create_gotowki_L_1f(self):
        self.gotowki_L_1f = tk.Frame(self.gotowki_main_frame, bg='#383232',
                                     relief='groove', bd=1)
        self.gotowki_L_1f.place(relx=0.02, rely=0.01, relwidth=0.96, relheight=0.12)
        self.create_dodaj_combobox_apteka()

    def create_dodaj_combobox_apteka(self):
        # wybór apteki
        self.dodaj_combobox_apteka_label = tk.Label(self.gotowki_L_1f, text='WYBIERZ APTEKĘ',
                                                    foreground='white', background='#383232', anchor='w')
        self.dodaj_combobox_apteka_label.place(relx=0.02, rely=0.12, relwidth=0.15)
        apteki = ['HIPOKRATES 4', 'HIPOKRATES 3', 'HALLERA', 'PIELGRZYMOWICE',
                  'WISŁA', 'BIEDRONKA', 'BZIE', 'BANK', 'INNE']
        self.dodaj_combobox_apteka = ttk.Combobox(self.gotowki_L_1f, values=apteki, state='readonly')
        self.dodaj_combobox_apteka.place(relx=0.17, rely=0.12, relwidth=0.15)
        self.dodaj_combobox_apteka.current(0)

        # wybór daty
        self.dodaj_data_label = tk.Label(self.gotowki_L_1f, text='WYBIERZ DATĘ',
                                         foreground='white', background='#383232', anchor='w')
        self.dodaj_data_label.place(relx=0.35, rely=0.12, relwidth=0.15)
        self.dodaj_data_picker = DateEntry(self.gotowki_L_1f, width=12, background='#383232',
                                           foreground='white', borderwidth=2, date_pattern='y-mm-dd',
                                           locale='pl_PL')
        self.dodaj_data_picker.place(relx=0.5, rely=0.12, relwidth=0.15)

        # kwota
        self.dodaj_kwota_label = tk.Label(self.gotowki_L_1f, text='KWOTA',
                                          foreground='white', background='#383232', anchor='w')
        self.dodaj_kwota_label.place(relx=0.68, rely=0.12, relwidth=0.10)
        self.dodaj_kwota_entry = tk.Entry(self.gotowki_L_1f, justify='center', bg='#6b685f', fg='white')
        self.dodaj_kwota_entry.place(relx=0.78, rely=0.12, relwidth=0.15)

        # opis
        self.dodaj_opis_label = tk.Label(self.gotowki_L_1f, text='OPIS',
                                         foreground='white', background='#383232', anchor='w')
        self.dodaj_opis_label.place(relx=0.02, rely=0.52, relwidth=0.10)
        self.dodaj_opis_entry = tk.Entry(self.gotowki_L_1f, justify='center', bg='#6b685f', fg='white')
        self.dodaj_opis_entry.place(relx=0.12, rely=0.52, relwidth=0.43)

        # dodaj button
        self.dodaj_button = tk.Button(self.gotowki_L_1f, text="DODAJ", bg='#544949', fg=f'{self.kolor_razem}',
                                      command=self.dodaj_wpis_do_bazy)
        self.dodaj_button.place(relx=0.60, rely=0.52, relwidth=0.25)

        # odświerz button
        self.odswierz_button = tk.Button(self.gotowki_L_1f, text="\uD83D\uDDD8", bg='#544949', fg=f'{self.kolor_razem}',
                                         command=self.update_saldo_display)
        self.odswierz_button.place(relx=0.88, rely=0.52, relwidth=0.05)
        self.dodaj_opis_entry.bind('<Return>', (lambda event: self.dodaj_wpis_do_bazy()))
        self.dodaj_kwota_entry.bind('<Return>', (lambda event: self.dodaj_wpis_do_bazy()))

    @staticmethod
    def if_kwota_number(kwota):
        try:
            int(kwota)
        except ValueError:
            return False
        return True

    def dodaj_wpis_do_bazy(self):
        apteka_wybor = self.dodaj_combobox_apteka.get()
        for key, val in self.apteki_dict.items():
            if val == apteka_wybor:
                apteka_wybor = key
        data_wybor = self.dodaj_data_picker.get()
        kwota = self.dodaj_kwota_entry.get()
        opis = self.dodaj_opis_entry.get()

        # zapis do bazy
        if kwota != '' and self.if_kwota_number(kwota):
            querry_inset_text = f'INSERT INTO gotowki( data, id_apteka, kwota, opis)' \
                                f' VALUES("{data_wybor}",{apteka_wybor},{int(kwota)},"{opis}")'
            self.zpt_database.mysql_no_fetch_querry(querry_inset_text)
            self.get_apteka_wybor_after_change()
            self.saldo_display.config(text=f'{self.get_gotowki_saldo()} zł')

        else:
            messagebox.showerror('UWAGA', 'Kwota musi być liczbą całkowitą. Podaj poprawną kwotę')
            self.dodaj_kwota_entry.delete(0, 'end')
            return False

        self.controller.logger.log(20, f'Dodano zapis do: GOTÓWKI. Apteka: {self.dodaj_combobox_apteka.get()}'
                                       f', Kwota: {kwota} zł, Opis: {opis}')
        self.dodaj_data_picker.set_date(f'{datetime.date.today()}')
        self.dodaj_kwota_entry.delete(0, 'end')
        self.dodaj_opis_entry.delete(0, 'end')

    def poprawa_wpisu(self, event):
        self.item = self.treeview_gotowki.selection()
        id = self.treeview_gotowki.item(self.item, 'values')[0]
        data = self.treeview_gotowki.item(self.item, 'values')[1]
        apteka = self.treeview_gotowki.item(self.item, 'values')[2]
        kwota = self.treeview_gotowki.item(self.item, 'values')[3]
        opis = self.treeview_gotowki.item(self.item, 'values')[4]

        self.popraw_usun_toplevel = tk.Toplevel(self.gotowki_L_1f, background='#383232',
                                                highlightthickness=2)
        self.popraw_usun_toplevel.grab_set()
        self.popraw_usun_toplevel.geometry(f'400x200+200+100')

        self.id_label = tk.Label(self.popraw_usun_toplevel, text=f'ID',
                                 foreground='white', background='#383232', anchor='w')
        self.id_label.place(relx=0.03, rely=0.05, relwidth=0.12)
        self.apteka_label = tk.Label(self.popraw_usun_toplevel, text=f'APTEKA',
                                     foreground='white', background='#383232', anchor='w')
        self.apteka_label.place(relx=0.03, rely=0.2, relwidth=0.12)
        self.data_label = tk.Label(self.popraw_usun_toplevel, text=f'DATA',
                                   foreground='white', background='#383232', anchor='w')
        self.data_label.place(relx=0.03, rely=0.38, relwidth=0.12)
        self.kwota_label = tk.Label(self.popraw_usun_toplevel, text=f'KWOTA',
                                    foreground='white', background='#383232', anchor='w')
        self.kwota_label.place(relx=0.03, rely=0.56, relwidth=0.12)
        self.opis_label = tk.Label(self.popraw_usun_toplevel, text=f'OPIS',
                                   foreground='white', background='#383232', anchor='w')
        self.opis_label.place(relx=0.03, rely=0.74, relwidth=0.12)

        self.poprawa_id_entry = tk.Entry(self.popraw_usun_toplevel, justify='center', bg='#6b685f', fg='white')
        self.poprawa_id_entry.insert(0, id)
        self.poprawa_id_entry.place(relx=0.18, rely=0.05, relwidth=0.35)

        apteki = ['HIPOKRATES 4', 'HIPOKRATES 3', 'HALLERA', 'PIELGRZYMOWICE',
                  'WISŁA', 'BIEDRONKA', 'BZIE', 'BANK', 'INNE']
        self.poprawa_combobox_apteka = ttk.Combobox(self.popraw_usun_toplevel, values=apteki, state='readonly')
        self.poprawa_combobox_apteka.place(relx=0.18, rely=0.2, relwidth=0.35)
        self.poprawa_combobox_apteka.current(apteki.index(f'{apteka}'))

        self.poprawa_data_entry = DateEntry(self.popraw_usun_toplevel, width=12, background='#383232',
                                            foreground='white', borderwidth=2, date_pattern='y-mm-dd',
                                            locale='pl_PL')
        self.poprawa_data_entry.set_date(f'{data}')
        self.poprawa_data_entry.place(relx=0.18, rely=0.38, relwidth=0.35)

        self.poprawa_kwota_entry = tk.Entry(self.popraw_usun_toplevel, justify='center', bg='#6b685f', fg='white')
        self.poprawa_kwota_entry.insert(0, kwota)
        self.poprawa_kwota_entry.place(relx=0.18, rely=0.56, relwidth=0.35)

        self.poprawa_opis_entry = tk.Entry(self.popraw_usun_toplevel, justify='center', bg='#6b685f', fg='white')
        self.poprawa_opis_entry.insert(0, opis)
        self.poprawa_opis_entry.place(relx=0.18, rely=0.74, relwidth=0.35)

        self.usun_wpis_button = tk.Button(self.popraw_usun_toplevel, text='USUN', bg='#544949',
                                          fg=f'{self.kolor_razem}', command=self.usun_wpis)
        self.usun_wpis_button.place(relx=0.6, rely=0.56, relwidth=0.35)

        self.popraw_wpis_button = tk.Button(self.popraw_usun_toplevel, text='POPRAW', bg='#544949',
                                            fg=f'{self.kolor_razem}', command=self.popraw_wpis)
        self.popraw_wpis_button.place(relx=0.6, rely=0.74, relwidth=0.35)

    def usun_wpis(self):
        id = self.poprawa_id_entry.get()
        delete_querry = f'DELETE FROM gotowki WHERE id_got = {id}'
        self.zpt_database.mysql_no_fetch_querry(delete_querry)
        self.get_apteka_wybor_after_change()
        self.popraw_usun_toplevel.destroy()
        self.saldo_display.config(text=f'{self.get_gotowki_saldo()} zł')
        self.controller.logger.log(20,
                                   f'Usunięto zapis do: GOTÓWKI. Id: {id}')

    def popraw_wpis(self):
        id = self.poprawa_id_entry.get()
        apteka_nazwa = self.poprawa_combobox_apteka.get()
        apteka_id = ''
        for key, val in self.apteki_dict.items():
            if val == apteka_nazwa:
                apteka_id = key
        data = self.poprawa_data_entry.get()
        kwota = self.poprawa_kwota_entry.get()
        opis = self.poprawa_opis_entry.get()

        if kwota != '' and self.if_kwota_number(kwota):
            update_querry = f'UPDATE gotowki SET data = "{data}", id_apteka = {apteka_id},' \
                            f'kwota = {kwota}, opis = "{opis}" WHERE id_got = {id}'
            self.zpt_database.mysql_no_fetch_querry(update_querry)
            self.get_apteka_wybor_after_change()
            self.saldo_display.config(text=f'{self.get_gotowki_saldo()} zł')
            self.popraw_usun_toplevel.destroy()
            self.controller.logger.log(20,
                                       f'Poprawiono zapis do: GOTÓWKI. Id: {id}, Apteka: {apteka_nazwa},'
                                       f' Kwota: {kwota} zł, Opis: {opis}')
        else:
            messagebox.showerror('UWAGA', 'Kwota musi być liczbą całkowitą. Podaj poprawną kwotę')
            self.poprawa_kwota_entry.delete(0, 'end')
            return False

    def create_gotowki_R_1f(self):
        self.gotowki_R_1f = tk.Frame(self)
        self.gotowki_R_1f.configure(bg='#383232', relief='groove', bd=1)
        self.gotowki_R_1f.place(relx=0.49, rely=0.02, relwidth=0.5, relheight=0.3)
        self.create_gotowki_R_1lf()
        self.create_gotowki_R_1rf()

    def create_gotowki_R_1lf(self):
        self.gotowki_R_1lf = tk.Frame(self.gotowki_R_1f)
        self.gotowki_R_1lf.configure(bg='#383232', relief='groove', bd=1)
        self.gotowki_R_1lf.place(relx=0.01, rely=0.02, relwidth=0.48, relheight=0.96)

        nominaly_50 = tk.Label(self.gotowki_R_1lf, text=f'50    x ', foreground='white', background='#383232',
                               anchor='w')
        nominaly_50.place(relx=0.05, rely=0.1, relwidth=0.1)
        nominaly_100 = tk.Label(self.gotowki_R_1lf, text=f'100   x ', foreground='white', background='#383232',
                                anchor='w')
        nominaly_100.place(relx=0.05, rely=0.25, relwidth=0.1)
        nominaly_200 = tk.Label(self.gotowki_R_1lf, text=f'200   x ', foreground='white', background='#383232',
                                anchor='w')
        nominaly_200.place(relx=0.05, rely=0.4, relwidth=0.1)
        nominaly_500 = tk.Label(self.gotowki_R_1lf, text=f'500   x ', foreground='white', background='#383232',
                                anchor='w')
        nominaly_500.place(relx=0.05, rely=0.55, relwidth=0.1)
        self.nominaly_50_entry = tk.Entry(self.gotowki_R_1lf, justify='center', bg='#6b685f', fg='white')
        self.nominaly_50_entry.place(relx=0.15, rely=0.1, relwidth=0.3)
        self.nominaly_100_entry = tk.Entry(self.gotowki_R_1lf, justify='center', bg='#6b685f', fg='white')
        self.nominaly_100_entry.place(relx=0.15, rely=0.25, relwidth=0.3)
        self.nominaly_200_entry = tk.Entry(self.gotowki_R_1lf, justify='center', bg='#6b685f', fg='white')
        self.nominaly_200_entry.place(relx=0.15, rely=0.4, relwidth=0.3)
        self.nominaly_500_entry = tk.Entry(self.gotowki_R_1lf, justify='center', bg='#6b685f', fg='white')
        self.nominaly_500_entry.place(relx=0.15, rely=0.55, relwidth=0.3)
        for n in range(4):
            znak_rownosci = tk.Label(self.gotowki_R_1lf, text=f'  = ', foreground='white', background='#383232',
                                     anchor='w')
            znak_rownosci.place(relx=0.45, rely=0.1 + (0.15 * n), relwidth=0.05)

        self.suma_nominal_50_label = tk.Label(self.gotowki_R_1lf, text=f'0.00 zł', foreground='white',
                                              background='#383232',
                                              anchor='w')
        self.suma_nominal_50_label.place(relx=0.5, rely=0.1, relwidth=0.2)
        self.suma_nominal_100_label = tk.Label(self.gotowki_R_1lf, text=f'0.00 zł', foreground='white',
                                               background='#383232',
                                               anchor='w')
        self.suma_nominal_100_label.place(relx=0.5, rely=0.25, relwidth=0.2)
        self.suma_nominal_200_label = tk.Label(self.gotowki_R_1lf, text=f'0.00 zł', foreground='white',
                                               background='#383232',
                                               anchor='w')
        self.suma_nominal_200_label.place(relx=0.5, rely=0.4, relwidth=0.2)
        self.suma_nominal_500_label = tk.Label(self.gotowki_R_1lf, text=f'0.00 zł', foreground='white',
                                               background='#383232',
                                               anchor='w')
        self.suma_nominal_500_label.place(relx=0.5, rely=0.55, relwidth=0.2)
        self.break_frame = tk.Frame(self.gotowki_R_1lf)
        self.break_frame.config(bg='white', relief='groove', bd=1)
        self.break_frame.place(relx=0.5, rely=0.65, relwidth=0.35, relheight=0.01)
        self.suma_nominal_all_label = tk.Label(self.gotowki_R_1lf, text=f'0.00 zł', foreground='white',
                                               background='#383232',
                                               anchor='w', font=("Verdena", "12", "bold"))
        self.suma_nominal_all_label.place(relx=0.5, rely=0.68, relwidth=0.35)

        self.nominaly_50_entry.insert(0, 0)
        self.nominaly_100_entry.insert(0, 0)
        self.nominaly_200_entry.insert(0, 0)
        self.nominaly_500_entry.insert(0, 0)

        self.nominaly_50_entry.bind('<Return>', self.przelicz_nominaly)
        self.nominaly_100_entry.bind('<Return>', self.przelicz_nominaly)
        self.nominaly_200_entry.bind('<Return>', self.przelicz_nominaly)
        self.nominaly_500_entry.bind('<Return>', self.przelicz_nominaly)

        self.zeruj_button = tk.Button(self.gotowki_R_1lf, text="ZERUJ", bg='#544949', fg=f'{self.kolor_razem}',
                                      command=self.zeruj_nominaly)
        self.zeruj_button.place(relx=0.1, rely=0.85, relwidth=0.8)

    def przelicz_nominaly(self, event):
        ilosc_50 = self.nominaly_50_entry.get()
        ilosc_100 = self.nominaly_100_entry.get()
        ilosc_200 = self.nominaly_200_entry.get()
        ilosc_500 = self.nominaly_500_entry.get()

        self.check_if_numeric(ilosc_50)
        self.check_if_numeric(ilosc_100)
        self.check_if_numeric(ilosc_200)
        self.check_if_numeric(ilosc_500)

        self.suma_nominal_50_label.config(text=f'{int(ilosc_50) * 50} zł')
        self.suma_nominal_100_label.config(text=f'{int(ilosc_100) * 100} zł')
        self.suma_nominal_200_label.config(text=f'{int(ilosc_200) * 200} zł')
        self.suma_nominal_500_label.config(text=f'{int(ilosc_500) * 500} zł')
        suma_all = (int(ilosc_50) * 50) + (int(ilosc_100) * 100) + (int(ilosc_200) * 200) + (int(ilosc_500) * 500)
        self.suma_nominal_all_label.config(text=f'{suma_all} zł')

    def check_if_numeric(self, number):
        if number.isnumeric():
            return True
        else:
            messagebox.showwarning('UWAGA', 'ILOŚĆ BANKNOTÓW MUSI BYĆ LICZNĄ NATURALNĄ')
            self.nominaly_50_entry.delete(0, 'end')
            self.nominaly_50_entry.insert(0, 0)
            self.nominaly_100_entry.delete(0, 'end')
            self.nominaly_100_entry.insert(0, 0)
            self.nominaly_200_entry.delete(0, 'end')
            self.nominaly_200_entry.insert(0, 0)
            self.nominaly_500_entry.delete(0, 'end')
            self.nominaly_500_entry.insert(0, 0)

            return False

    def zeruj_nominaly(self):
        self.nominaly_50_entry.delete(0, 'end')
        self.nominaly_50_entry.insert(0, 0)
        self.nominaly_100_entry.delete(0, 'end')
        self.nominaly_100_entry.insert(0, 0)
        self.nominaly_200_entry.delete(0, 'end')
        self.nominaly_200_entry.insert(0, 0)
        self.nominaly_500_entry.delete(0, 'end')
        self.nominaly_500_entry.insert(0, 0)
        self.suma_nominal_50_label.config(text='0.00 zł')
        self.suma_nominal_100_label.config(text='0.00 zł')
        self.suma_nominal_200_label.config(text='0.00 zł')
        self.suma_nominal_500_label.config(text='0.00 zł')
        self.suma_nominal_all_label.config(text='0.00 zł')

    def create_gotowki_R_1rf(self):
        self.gotowki_R_1rf = tk.Frame(self.gotowki_R_1f)
        self.gotowki_R_1rf.configure(bg='#383232', relief='groove', bd=1)
        self.gotowki_R_1rf.place(relx=0.51, rely=0.02, relwidth=0.48, relheight=0.96)

        pgf_label = tk.Label(self.gotowki_R_1rf, text=f'PGF', foreground='white',
                             background='#383232', anchor='w')
        pgf_label.place(relx=0.05, rely=0.1, relwidth=0.17)
        neuca_label = tk.Label(self.gotowki_R_1rf, text=f'NEUCA', foreground='white',
                               background='#383232', anchor='w')
        neuca_label.place(relx=0.05, rely=0.2, relwidth=0.17)
        hurtap_label = tk.Label(self.gotowki_R_1rf, text=f'HURTAP', foreground='white',
                                background='#383232', anchor='w')
        hurtap_label.place(relx=0.05, rely=0.3, relwidth=0.17)
        novo_label = tk.Label(self.gotowki_R_1rf, text=f'NOVO', foreground='white',
                              background='#383232', anchor='w')
        novo_label.place(relx=0.05, rely=0.4, relwidth=0.17)
        salus_label = tk.Label(self.gotowki_R_1rf, text=f'SALUS', foreground='white',
                               background='#383232', anchor='w')
        salus_label.place(relx=0.05, rely=0.5, relwidth=0.17)
        farmacol_label = tk.Label(self.gotowki_R_1rf, text=f'FARAMCOL', foreground='white',
                                  background='#383232', anchor='w')
        farmacol_label.place(relx=0.05, rely=0.6, relwidth=0.17)
        astellas_label = tk.Label(self.gotowki_R_1rf, text=f'ASTELLAS', foreground='white',
                                  background='#383232', anchor='w')
        astellas_label.place(relx=0.05, rely=0.7, relwidth=0.17)

        self.pgf_entry = tk.Entry(self.gotowki_R_1rf, justify='center', bg='#6b685f', fg='white')
        self.pgf_entry.place(relx=0.23, rely=0.1, relwidth=0.2)
        self.neuca_entry = tk.Entry(self.gotowki_R_1rf, justify='center', bg='#6b685f', fg='white')
        self.neuca_entry.place(relx=0.23, rely=0.2, relwidth=0.2)
        self.hurtap_entry = tk.Entry(self.gotowki_R_1rf, justify='center', bg='#6b685f', fg='white')
        self.hurtap_entry.place(relx=0.23, rely=0.3, relwidth=0.2)
        self.novo_entry = tk.Entry(self.gotowki_R_1rf, justify='center', bg='#6b685f', fg='white')
        self.novo_entry.place(relx=0.23, rely=0.4, relwidth=0.2)
        self.salus_entry = tk.Entry(self.gotowki_R_1rf, justify='center', bg='#6b685f', fg='white')
        self.salus_entry.place(relx=0.23, rely=0.5, relwidth=0.2)
        self.farmacol_entry = tk.Entry(self.gotowki_R_1rf, justify='center', bg='#6b685f', fg='white')
        self.farmacol_entry.place(relx=0.23, rely=0.6, relwidth=0.2)
        self.astellas_entry = tk.Entry(self.gotowki_R_1rf, justify='center', bg='#6b685f', fg='white')
        self.astellas_entry.place(relx=0.23, rely=0.7, relwidth=0.2)

        bank_label = tk.Label(self.gotowki_R_1rf, text=f'BANK', foreground='white',
                              background='#383232', anchor='w')
        bank_label.place(relx=0.5, rely=0.1, relwidth=0.10)
        self.bank_entry = tk.Entry(self.gotowki_R_1rf, justify='center', bg='#6b685f', fg='white')
        self.bank_entry.place(relx=0.61, rely=0.1, relwidth=0.2)

        self.pgf_entry.insert(0, 0)
        self.neuca_entry.insert(0, 0)
        self.hurtap_entry.insert(0, 0)
        self.novo_entry.insert(0, 0)
        self.salus_entry.insert(0, 0)
        self.farmacol_entry.insert(0, 0)
        self.astellas_entry.insert(0, 0)
        self.bank_entry.insert(0, 0)

        self.pgf_entry.bind('<Return>', self.przelicz_hurtownie)
        self.neuca_entry.bind('<Return>', self.przelicz_hurtownie)
        self.hurtap_entry.bind('<Return>', self.przelicz_hurtownie)
        self.novo_entry.bind('<Return>', self.przelicz_hurtownie)
        self.salus_entry.bind('<Return>', self.przelicz_hurtownie)
        self.farmacol_entry.bind('<Return>', self.przelicz_hurtownie)
        self.astellas_entry.bind('<Return>', self.przelicz_hurtownie)
        self.bank_entry.bind('<Return>', self.przelicz_hurtownie)

        self.bank_wynik_label = tk.Label(self.gotowki_R_1rf, text=f'0.00', foreground='white',
                                         background='#383232',
                                         anchor='e', font=("Verdena", "12", "bold"))
        self.bank_wynik_label.place(relx=0.5, rely=0.3, relwidth=0.31)
        self.hurtownie_wynik_label = tk.Label(self.gotowki_R_1rf, text=f'-  0.00', foreground='white',
                                              background='#383232',
                                              anchor='e', font=("Verdena", "12", "bold"))
        self.hurtownie_wynik_label.place(relx=0.5, rely=0.4, relwidth=0.31)
        break_frame = tk.Frame(self.gotowki_R_1rf)
        break_frame.config(bg='white', relief='groove', bd=1)
        break_frame.place(relx=0.5, rely=0.5, relwidth=0.31, relheight=0.01)
        self.saldo_label = tk.Label(self.gotowki_R_1rf, text=f'0.00', foreground='white',
                                    background='#383232',
                                    anchor='e', font=("Verdena", "12", "bold"))
        self.saldo_label.place(relx=0.5, rely=0.55, relwidth=0.31)

        self.zeruj_hurtownie_button = tk.Button(self.gotowki_R_1rf, text="ZERUJ", bg='#544949',
                                                fg=f'{self.kolor_razem}',
                                                command=self.zeruj_hurtownie)
        self.zeruj_hurtownie_button.place(relx=0.1, rely=0.85, relwidth=0.8)

    def przelicz_hurtownie(self, event):
        # todo: sprawdz czy float
        e1 = float(self.pgf_entry.get().replace(',', '.'))
        e2 = float(self.neuca_entry.get().replace(',', '.'))
        e3 = float(self.hurtap_entry.get().replace(',', '.'))
        e4 = float(self.novo_entry.get().replace(',', '.'))
        e5 = float(self.salus_entry.get().replace(',', '.'))
        e6 = float(self.farmacol_entry.get().replace(',', '.'))
        e7 = float(self.astellas_entry.get().replace(',', '.'))

        suma_hurtownie = round((e1 + e2 + e3 + e4 + e5 + e6 + e7), 2)
        bank = round(float(self.bank_entry.get().replace(',', '.')), 2)
        saldo = bank - suma_hurtownie

        self.bank_wynik_label.config(text=f'{bank:.2f}')
        self.hurtownie_wynik_label.config(text=f'-  {suma_hurtownie:.2f}')
        self.saldo_label.config(text=f'{saldo:.2f}')

        if saldo > 0:
            self.saldo_label.config(foreground='green')
        elif saldo < 0:
            self.saldo_label.config(foreground='red')
        elif saldo == 0:
            self.saldo_label.config(foreground='white')

    def zeruj_hurtownie(self):
        self.pgf_entry.delete(0, 'end')
        self.neuca_entry.delete(0, 'end')
        self.hurtap_entry.delete(0, 'end')
        self.novo_entry.delete(0, 'end')
        self.salus_entry.delete(0, 'end')
        self.farmacol_entry.delete(0, 'end')
        self.astellas_entry.delete(0, 'end')
        self.bank_entry.delete(0, 'end')

        self.pgf_entry.insert(0, 0)
        self.neuca_entry.insert(0, 0)
        self.hurtap_entry.insert(0, 0)
        self.novo_entry.insert(0, 0)
        self.salus_entry.insert(0, 0)
        self.farmacol_entry.insert(0, 0)
        self.astellas_entry.insert(0, 0)
        self.bank_entry.insert(0, 0)

        self.przelicz_hurtownie('')

class Faktury_koszty_frame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.configure(bg='#383232')
        self.zpt_database = ZPT_Database.ZPT_base()
        self.kolor_razem = '#b58b14'
        self.create_koszty_LF()
        self.create_koszty_RF()

    def create_koszty_LF(self):
        self.koszty_LF = tk.Frame(self)
        self.koszty_LF.configure(bg='#383232', relief='groove', bd=1)
        self.koszty_LF.place(relx=0.01, rely=0.02, relwidth=0.48, relheight=0.96)
        self.create_koszty_L_1f()
        self.create_koszty_L_3f()
        self.create_faktury_frame_treeview()
        self.update_faktury_treeview()

    def create_koszty_L_1f(self):
        self.koszty_L_1f = tk.Frame(self.koszty_LF, bg='#383232',
                                    relief='groove', bd=1)
        self.koszty_L_1f.place(relx=0.02, rely=0.01, relwidth=0.96, relheight=0.12)

        kontrahenci_lista = self.get_kontrahenci_dane()

        faktura_combobox_label = tk.Label(self.koszty_L_1f, text='KONTRAHENT',
                                          foreground='white', background='#383232', anchor='w')
        faktura_combobox_label.place(relx=0.02, rely=0.12, relwidth=0.14)
        self.fakruta_combobox_kontrahenci = ttk.Combobox(self.koszty_L_1f, values=kontrahenci_lista,
                                                         height=30, state='readonly')
        self.fakruta_combobox_kontrahenci.place(relx=0.15, rely=0.12, relwidth=0.82)
        faktura_nr_label = tk.Label(self.koszty_L_1f, text='FAKRUTA',
                                    foreground='white', background='#383232', anchor='w')
        faktura_nr_label.place(relx=0.02, rely=0.52, relwidth=0.10)
        self.faktura_nr_entry = tk.Entry(self.koszty_L_1f, justify='center', bg='#6b685f', fg='white')
        self.faktura_nr_entry.place(relx=0.12, rely=0.52, relwidth=0.15)
        faktura_kwota_label = tk.Label(self.koszty_L_1f, text='KWOTA',
                                       foreground='white', background='#383232')
        faktura_kwota_label.place(relx=0.28, rely=0.52, relwidth=0.07)
        self.faktura_kwota_entry = tk.Entry(self.koszty_L_1f, justify='center', bg='#6b685f', fg='white')
        self.faktura_kwota_entry.place(relx=0.35, rely=0.52, relwidth=0.15)
        faktura_data_label = tk.Label(self.koszty_L_1f, text='DATA',
                                      foreground='white', background='#383232')
        faktura_data_label.place(relx=0.5, rely=0.52, relwidth=0.07)
        self.faktura_data_entry = DateEntry(self.koszty_L_1f, width=12, background='#383232',
                                            foreground='white', borderwidth=2, date_pattern='y-mm-dd',
                                            locale='pl_PL')
        self.faktura_data_entry.place(relx=0.57, rely=0.52, relwidth=0.15)
        self.faktura_dodaj_button = tk.Button(self.koszty_L_1f, text='DODAJ', bg='#544949',
                                              fg=f'{self.kolor_razem}', command=self.dodaj_faktura_koszty)
        self.faktura_dodaj_button.place(relx=0.75, rely=0.52, relwidth=0.23)

    def dodaj_faktura_koszty(self):
        nazwa_kontrahenta = self.fakruta_combobox_kontrahenci.get()
        id_kontrahenta = self.get_kontrhent_id(nazwa_kontrahenta)
        nr_fakruty = self.faktura_nr_entry.get()
        kwota_faktury = self.faktura_kwota_entry.get().replace(',', '.')
        data_platnosci = self.faktura_data_entry.get()

        if kwota_faktury != '' and self.if_kwota_float(kwota_faktury):
            querry_inset_text = f'INSERT INTO platnosci_fv( id_kont, nr_fv, kwota, data_platnosci, data_zaplaty, zaplacone)' \
                                f' VALUES("{id_kontrahenta}","{nr_fakruty}",{float(kwota_faktury)},' \
                                f'"{data_platnosci}", "", 0)'
            self.zpt_database.mysql_no_fetch_querry(querry_inset_text)
            self.faktura_kwota_entry.delete(0, 'end')
            self.faktura_nr_entry.delete(0, 'end')
            self.faktura_data_entry.set_date(datetime.date.today())
            self.fakruta_combobox_kontrahenci.set('')
            self.update_faktury_treeview()
            self.controller.logger.log(20, f'Dodano fakturę kosztową: {nr_fakruty}, data płatności: {data_platnosci}, '
                                           f'kwota: {kwota_faktury}')
        else:
            messagebox.showerror('UWAGA', 'Podaj poprawną kwotę')
            self.faktura_kwota_entry.delete(0, 'end')
            return False

    @staticmethod
    def if_kwota_float(kwota):
        try:
            float(kwota)
        except ValueError:
            return False
        return True

    def get_kontrhent_id(self, nazwa_kontrhenta):
        id_kontrahenta_querry = f'SELECT id_kont FROM platnosci_kontrahenci WHERE nazwa = "{nazwa_kontrhenta}"'
        id_kontrahenta = self.zpt_database.mysql_querry(id_kontrahenta_querry)
        return id_kontrahenta[0][0]

    def get_kontrahenci_dane(self):
        kontrahenci_querry = f'SELECT DISTINCT nazwa FROM platnosci_kontrahenci ORDER BY nazwa ASC'
        kontrahenci = self.zpt_database.mysql_querry(kontrahenci_querry)
        kontrahenci_lista = [x[0] for x in kontrahenci]
        return kontrahenci_lista

    def create_faktury_frame_treeview(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', fieldbackground="#383232", background="#383232", foreground='white')
        style.configure("Treeview.Heading", background="#383232", foreground="white")
        style.map('Treeview.Heading', background=[('disabled', '#383232')])

        def fixed_map(option):  # naprawa buga wersji dla Python 3.7 przy wyświetlaniu koloru linii w treeview
            return [elm for elm in style.map("Treeview", query_opt=option)
                    if elm[:2] != ("!disabled", "!selected")]

        style.map("Treeview", foreground=fixed_map("foreground"),
                  background=fixed_map("background"))

        self.koszty_L_2f = tk.Frame(self.koszty_LF)
        self.koszty_L_2f.configure(bg='#383232', relief='groove', bd=1)
        self.koszty_L_2f.place(relx=0.02, rely=0.15, relwidth=0.96, relheight=0.60)

        self.columns_faktury = ('ID', 'KONTRAHENT', 'FV', 'KWOTA', 'TERMIN')
        self.faktury_treeview = ttk.Treeview(self.koszty_L_2f, columns=self.columns_faktury, show='headings',
                                             style="Treeview")

        self.faktury_treeview.heading('ID', text='ID')
        self.faktury_treeview.column('ID', width=50, stretch='no', anchor='center')
        self.faktury_treeview.heading('KONTRAHENT', text='KONTRAHENT')
        self.faktury_treeview.column('KONTRAHENT', minwidth=0, stretch='yes', anchor='center')
        self.faktury_treeview.heading('FV', text='FV')
        self.faktury_treeview.column('FV', width=170, stretch='no', anchor='center')
        self.faktury_treeview.heading('KWOTA', text='KWOTA')
        self.faktury_treeview.column('KWOTA', width=100, stretch='no', anchor='center')
        self.faktury_treeview.heading('TERMIN', text='TERMIN')
        self.faktury_treeview.column('TERMIN', width=100, stretch='no', anchor='center')

        self.scrolly = ttk.Scrollbar(self.faktury_treeview, orient='vertical', command=self.faktury_treeview.yview)
        self.faktury_treeview.configure(yscrollcommand=self.scrolly.set)
        map(lambda col: col.configure(yscrollcommand=self.scrolly.set), self.columns_faktury)
        self.scrolly.pack(side=tk.RIGHT, fill=tk.Y)
        map(lambda col: col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True), self.columns_faktury)
        self.faktury_treeview.pack(expand='yes', fill='both')
        self.faktury_treeview.bind("<Double-1>", self.poprawa_wpisu)
        self.faktury_treeview.bind('<<TreeviewSelect>>', self.wybrane_faktury_analizuj)

    def wybrane_faktury_analizuj(self, event):
        self.tytul_przelewu_entry.delete(0, 'end')
        self.suma_przelewu_kwota_label.config(text='0.00 zł')
        tytul_przelewu = ''
        suma_przelewu = 0
        nazwa = []
        nip = ''
        konto = ''

        for item in event.widget.selection():
            nazwa_wybor = self.faktury_treeview.item(item, 'values')[1]
            if len(event.widget.selection()) == 1:
                dane_nip_konto = self.get_konto_nip_kontrahent(nazwa_wybor)
                nip = dane_nip_konto[0]
                konto = dane_nip_konto[1]
                self.dane_kontrahent_konto_nip_label.config(text=f'NIP: {nip}\t\t KONTO: {konto}')
                self.sprawdz_konto_biala_lista(konto)

            if len(event.widget.selection()) > 1:
                if nazwa_wybor not in nazwa:
                    nazwa.append(nazwa_wybor)
                if len(nazwa) > 1:
                    messagebox.showerror('UWAGA', 'Wybrano dwóch różnych kontrahentów')
                    self.tytul_przelewu_entry.delete(0, 'end')
                    self.suma_przelewu_kwota_label.config(text=f'0.00 zł')
                    self.dane_kontrahent_konto_nip_label.config(text=f'')
                    self.update_faktury_treeview()
                    self.zaplac_button.config(state='disable')
                    tytul_przelewu = ''
                    suma_przelewu = 0
                    break
            tytul_przelewu += self.faktury_treeview.item(item, 'values')[2] + ', '
            suma_przelewu += float(self.faktury_treeview.item(item, 'values')[3])

        self.tytul_przelewu_entry.insert(0, tytul_przelewu[:-2])
        self.suma_przelewu_kwota_label.config(text=f'{suma_przelewu:.2f} zł')

    def sprawdz_konto_biala_lista(self, konto):
        dane_do_zapisu = {}

        if len(self.faktury_treeview.selection()) == 1:
            selected = self.faktury_treeview.selection()
            nazwa = self.faktury_treeview.item(selected, 'values')[1]
            if nazwa == 'ZUS' or nazwa == 'US PIT4' or nazwa == 'US CIT' or nazwa == 'US VAT' \
                    or nazwa == 'PEKAO S.A.' or nazwa == 'MARIA KAPPEL-ZIOŁA':
                self.dane_kontrahent_konto_nip_label.config(fg='white')
                self.zaplac_button.config(state='normal')
                self.przelew_button.config(state='normal')
                return dane_do_zapisu

        data_param = datetime.date.today()
        konto_26 = konto.replace(' ', '')
        dane = requests.get(f'https://wl-api.mf.gov.pl/api/search/bank-account/{konto_26}?date={data_param}')
        dane = dane.json()

        if 'code' in dane:
            self.dane_kontrahent_konto_nip_label.config(text=f'BŁĄD SPRAWDZENIA KONTRAHENTA NA BIEAŁEJ LIŚCIE',
                                                        fg='red')
            self.zaplac_button.config(state='disable')
            self.przelew_button.config(state='disable')
            return dane_do_zapisu

        elif 'result' in dane and dane['result']['subjects'] != []:
            self.dane_kontrahent_konto_nip_label.config(fg='green')
            self.zaplac_button.config(state='normal')
            self.przelew_button.config(state='normal')
            dane_do_zapisu.update({'czas': dane['result']['requestDateTime']})
            dane_do_zapisu.update({'nazwa': dane['result']['subjects'][0]['name'].replace('"', '')})
            dane_do_zapisu.update({'konto': dane['result']['subjects'][0]['accountNumbers']})
            dane_do_zapisu.update({'nip': dane['result']['subjects'][0]['nip']})
            dane_do_zapisu.update({'status': dane['result']['subjects'][0]['statusVat']})
            dane_do_zapisu.update({'kod_potwierdzenia': dane['result']['requestId']})
            nazwa = dane['result']['subjects'][0]['name'].replace('"', '')
            status = dane['result']['subjects'][0]['statusVat']
            kod_potwierdzenia = dane['result']['requestId']
            self.controller.logger.log(20, f'Sprawdzono konto {konto} na Białej Liście: {nazwa},'
                                           f' status: {status}, '
                                           f'kod potwierdzenia: {kod_potwierdzenia}')
            return dane_do_zapisu
        # todo: sprawdzić zgodność NIP

    def get_konto_nip_kontrahent(self, nazwa):
        dane_querry = f'SELECT nip, konto FROM platnosci_kontrahenci WHERE nazwa = "{nazwa}"'
        dane = self.zpt_database.mysql_querry(dane_querry)
        return dane[0]

    def poprawa_wpisu(self, event):
        self.item = self.faktury_treeview.selection()
        id = self.faktury_treeview.item(self.item, 'values')[0]
        kontrahent = self.faktury_treeview.item(self.item, 'values')[1]
        nr_faktury = self.faktury_treeview.item(self.item, 'values')[2]
        kwota_faktury = self.faktury_treeview.item(self.item, 'values')[3]
        termin = self.faktury_treeview.item(self.item, 'values')[4]

        kontrahenci_lista = self.get_kontrahenci_dane()
        self.popraw_usun_toplevel = tk.Toplevel(self.koszty_L_2f, background='#383232',
                                                highlightthickness=2)
        self.popraw_usun_toplevel.grab_set()
        self.popraw_usun_toplevel.geometry(f'400x200+200+100')

        self.id_label = tk.Label(self.popraw_usun_toplevel, text=f'ID',
                                 foreground='white', background='#383232', anchor='w')
        self.id_label.place(relx=0.03, rely=0.05, relwidth=0.12)
        self.kontrahent_label = tk.Label(self.popraw_usun_toplevel, text=f'KONTRAHENT',
                                         foreground='white', background='#383232', anchor='w')
        self.kontrahent_label.place(relx=0.03, rely=0.2, relwidth=0.12)
        self.nr_faktury_label = tk.Label(self.popraw_usun_toplevel, text=f'NR FAKRUTY',
                                         foreground='white', background='#383232', anchor='w')
        self.nr_faktury_label.place(relx=0.03, rely=0.38, relwidth=0.12)
        self.kwota_faktury_label = tk.Label(self.popraw_usun_toplevel, text=f'KWOTA',
                                            foreground='white', background='#383232', anchor='w')
        self.kwota_faktury_label.place(relx=0.03, rely=0.56, relwidth=0.12)
        self.termin_label = tk.Label(self.popraw_usun_toplevel, text=f'TERMIN',
                                     foreground='white', background='#383232', anchor='w')
        self.termin_label.place(relx=0.03, rely=0.74, relwidth=0.12)

        self.poprawa_id_entry = tk.Entry(self.popraw_usun_toplevel, justify='center', bg='#6b685f', fg='white')
        self.poprawa_id_entry.insert(0, id)
        self.poprawa_id_entry.place(relx=0.18, rely=0.05, relwidth=0.35)
        self.poprawa_combobox_kontrahenci = ttk.Combobox(self.popraw_usun_toplevel, values=kontrahenci_lista,
                                                         state='readonly', height=30)
        self.poprawa_combobox_kontrahenci.place(relx=0.18, rely=0.2, relwidth=0.6)
        self.poprawa_combobox_kontrahenci.current(kontrahenci_lista.index(f'{kontrahent}'))

        self.poprawa_nr_faktury_entry = tk.Entry(self.popraw_usun_toplevel, justify='center',
                                                 bg='#6b685f', fg='white')
        self.poprawa_nr_faktury_entry.insert(0, nr_faktury)
        self.poprawa_nr_faktury_entry.place(relx=0.18, rely=0.38, relwidth=0.35)

        self.poprawa_kwota_entry = tk.Entry(self.popraw_usun_toplevel, justify='center',
                                            bg='#6b685f', fg='white')
        self.poprawa_kwota_entry.insert(0, kwota_faktury)
        self.poprawa_kwota_entry.place(relx=0.18, rely=0.56, relwidth=0.35)

        self.poprawa_termin_entry = DateEntry(self.popraw_usun_toplevel, width=12, background='#383232',
                                              foreground='white', borderwidth=2, date_pattern='y-mm-dd',
                                              locale='pl_PL')
        self.poprawa_termin_entry.set_date(f'{termin}')
        self.poprawa_termin_entry.place(relx=0.18, rely=0.74, relwidth=0.35)

        self.usun_wpis_button = tk.Button(self.popraw_usun_toplevel, text='USUN', bg='#544949',
                                          fg=f'{self.kolor_razem}', command=self.usun_wpis_faktury_koszty)
        self.usun_wpis_button.place(relx=0.6, rely=0.56, relwidth=0.35)

        self.popraw_wpis_button = tk.Button(self.popraw_usun_toplevel, text='POPRAW', bg='#544949',
                                            fg=f'{self.kolor_razem}', command=self.popraw_wpis_faktury_koszty)
        self.popraw_wpis_button.place(relx=0.6, rely=0.74, relwidth=0.35)

    def usun_wpis_faktury_koszty(self):
        id = self.poprawa_id_entry.get()
        delete_querry = f'DELETE FROM platnosci_fv WHERE id_fv = {id}'
        self.zpt_database.mysql_no_fetch_querry(delete_querry)
        self.popraw_usun_toplevel.destroy()
        self.tytul_przelewu_entry.delete(0, 'end')
        self.suma_przelewu_kwota_label.config(text='0.00 zł')
        self.dane_kontrahent_konto_nip_label.config(text='')
        self.update_faktury_treeview()

    def popraw_wpis_faktury_koszty(self):
        id = self.poprawa_id_entry.get()
        kontrahent = self.poprawa_combobox_kontrahenci.get()
        kontrahent_id = self.get_kontrhent_id(kontrahent)
        nr_faktury = self.poprawa_nr_faktury_entry.get()
        kwota_faktury = self.poprawa_kwota_entry.get().replace(',', '.')
        termin = self.poprawa_termin_entry.get()

        if kwota_faktury != '' and self.if_kwota_float(kwota_faktury):
            update_querry = f'UPDATE platnosci_fv SET id_kont = {kontrahent_id}, nr_fv = "{nr_faktury}",' \
                            f'kwota = {kwota_faktury}, data_platnosci = "{termin}" WHERE id_fv = {id}'
            self.zpt_database.mysql_no_fetch_querry(update_querry)
            self.popraw_usun_toplevel.destroy()
            self.update_faktury_treeview()
            self.tytul_przelewu_entry.delete(0, 'end')
            self.suma_przelewu_kwota_label.config(text='0.00 zł')
        else:
            messagebox.showerror('UWAGA', 'Podaj poprawną kwotę')
            self.poprawa_kwota_entry.delete(0, 'end')
            return False

    def get_dane_faktury_koszty(self):
        dane_fakruty_koszty_querry = f'SELECT f.id_fv, k.nazwa, f.nr_fv, f.kwota, f.data_platnosci FROM ' \
                                     f'platnosci_kontrahenci k, platnosci_fv f WHERE ' \
                                     f'f.id_kont=k.id_kont AND f.zaplacone = 0 ORDER BY data_platnosci'
        dane_fakruty_koszty = self.zpt_database.mysql_querry(dane_fakruty_koszty_querry)
        return dane_fakruty_koszty

    def create_koszty_L_3f(self):
        self.koszty_L_3f = tk.Frame(self.koszty_LF, bg='#383232',
                                    relief='groove', bd=1)
        self.koszty_L_3f.place(relx=0.02, rely=0.77, relwidth=0.96, relheight=0.21)

        tytul_przelewu_label = tk.Label(self.koszty_L_3f, text='TYTUŁ PRZELEWU',
                                        foreground='white', background='#383232', anchor='w')
        tytul_przelewu_label.place(relx=0.02, rely=0.06, relwidth=0.14)
        suma_przelewu_label = tk.Label(self.koszty_L_3f, text='SUMA PRZELEWU',
                                       foreground='white', background='#383232', anchor='w')
        suma_przelewu_label.place(relx=0.02, rely=0.26, relwidth=0.14)

        self.tytul_przelewu_entry = tk.Entry(self.koszty_L_3f, justify='center',
                                             bg='#6b685f', fg='white')
        self.tytul_przelewu_entry.place(relx=0.16, rely=0.06, relwidth=0.54)
        self.suma_przelewu_kwota_label = tk.Label(self.koszty_L_3f, text='0.00 zł',
                                                  foreground='white', background='#383232', anchor='w')
        self.suma_przelewu_kwota_label.place(relx=0.16, rely=0.26, relwidth=0.54)
        self.kopiuj_tytul_przelwu_buton = tk.Button(self.koszty_L_3f, text='KOPIUJ TYTUŁ', bg='#544949',
                                                    fg=f'{self.kolor_razem}', command=self.kopiuj_tytul_przelwu)
        self.kopiuj_tytul_przelwu_buton.place(relx=0.72, rely=0.06, relwidth=0.26)
        self.kopiuj_sume_przelwu_buton = tk.Button(self.koszty_L_3f, text='KOPIUJ KWOTĘ',
                                                   bg='#544949',
                                                   fg=f'{self.kolor_razem}', command=self.kopiuj_sume_przelwu)
        self.kopiuj_sume_przelwu_buton.place(relx=0.72, rely=0.26, relwidth=0.26)

        self.zaplac_button = tk.Button(self.koszty_L_3f, text='ZAPŁAĆ',
                                       bg='#544949', fg=f'{self.kolor_razem}', state='disable',
                                       command=self.zaplac_faktury_wybrane)
        self.zaplac_button.place(relx=0.02, rely=0.8, relwidth=0.47)
        self.przelew_button = tk.Button(self.koszty_L_3f, text='DODAJ DO PRZELEWÓW',
                                        bg='#544949', fg=f'{self.kolor_razem}', state='disable',
                                        command=self.dodaj_do_listy_przelewow)
        self.przelew_button.place(relx=0.51, rely=0.8, relwidth=0.47)
        # sprawdzanie biała lista
        self.dane_kontrahent_konto_nip_label = tk.Label(self.koszty_L_3f, text='',
                                                        foreground='white', background='#383232')
        self.dane_kontrahent_konto_nip_label.place(relx=0.02, rely=0.56, relwidth=0.88)

    def dodaj_do_listy_przelewow(self):
        kontrahent = f'"{self.controller.przelewy_frame.podziel_tytul(self.faktury_treeview.item(self.faktury_treeview.selection()[0], "values")[1])}"'
        nr_konta = f'"{self.get_konto_nip_kontrahent(kontrahent[1:-1].replace("|", ""))[1].replace(" ", "")}"'
        kwota = self.suma_przelewu_kwota_label.cget('text')[:-3]
        data = str(datetime.datetime.now().date())
        tytul = f'(K) {self.tytul_przelewu_entry.get()}'
        self.controller.przelewy_frame.dodaj_do_listy_przelewow(kontrahent, nr_konta, kwota, data, tytul)

    def update_faktury_treeview(self):
        dane = self.get_dane_faktury_koszty()
        self.faktury_treeview.delete(*self.faktury_treeview.get_children())
        i = 0
        for n in dane:
            i += 1
            id_faktury = n[0]
            nazwa_kotrahenta = n[1]
            nr_faktury = n[2]
            kwota_fakruty = f'{float(n[3]):.2f}'
            data_platnowci = n[4]

            if i % 2 == 0:
                background_gotowki = 'background_dark'
            else:
                background_gotowki = 'background_light'

            if self.check_date_deley(data_platnowci):
                foreground_gotowki = 'foreground_plus'
            else:
                foreground_gotowki = 'foreground_bank'

            self.faktury_treeview.tag_configure('background_dark', background='#383232')
            self.faktury_treeview.tag_configure('background_light', background='#262424')
            self.faktury_treeview.tag_configure('foreground_bank', foreground='red')
            self.faktury_treeview.tag_configure('foreground_plus', foreground='white')

            self.faktury_treeview.insert('', 'end', values=(id_faktury, nazwa_kotrahenta, nr_faktury, kwota_fakruty,
                                                            data_platnowci),
                                         tags=(background_gotowki, foreground_gotowki))
            self.tytul_przelewu_entry.delete(0, 'end')
            self.suma_przelewu_kwota_label.config(text='0.00 zł')
            self.dane_kontrahent_konto_nip_label.config(text='')

    @staticmethod
    def check_date_deley(date):
        date_1 = datetime.datetime.strptime(date, '%Y-%m-%d')
        date_now = datetime.datetime.strptime(str(datetime.date.today()), '%Y-%m-%d')
        if date_1 <= date_now:
            return False
        return True

    def zaplac_faktury_wybrane(self):
        self.id_wybrane_fv = []
        nazwa = ''
        for item in self.faktury_treeview.selection():
            id_faktury = self.faktury_treeview.item(item, 'values')[0]
            nazwa = self.faktury_treeview.item(item, 'values')[1]
            zaplac_querry = f'UPDATE platnosci_fv SET zaplacone = 1, data_zaplaty = "{datetime.date.today()}"  WHERE id_fv = {id_faktury}'
            self.zpt_database.mysql_no_fetch_querry(zaplac_querry)
        konto = self.get_konto_nip_kontrahent(nazwa)[1]
        if nazwa != 'ZUS' and nazwa != 'US PIT4' and nazwa != 'US CIT' and nazwa != 'US VAT' and nazwa != 'PPK PKO' \
                and nazwa != 'MARIA KAPPEL-ZIOŁA':
            self.zapisz_biala_lista(konto)

        self.update_faktury_treeview()
        self.tytul_przelewu_entry.delete(0, 'end')
        self.suma_przelewu_kwota_label.config(text='0.00 zł')
        self.update_faktury_zaplacone_treeview()

    def zapisz_biala_lista(self, konto):
        dane_do_zapisu = self.sprawdz_konto_biala_lista(konto)
        konto_26 = konto.replace(' ', '')
        if dane_do_zapisu != {}:
            self.dane_kontrahent_konto_nip_label.config(text='')
            zapisz_biala_lista_querry = f'INSERT INTO biala_lista VALUES(NULL, "{dane_do_zapisu["czas"]}", ' \
                                        f'"{dane_do_zapisu["nazwa"]}", "{konto_26}", ' \
                                        f'"{dane_do_zapisu["nip"]}", "{dane_do_zapisu["status"]}", ' \
                                        f'"{dane_do_zapisu["kod_potwierdzenia"]}")'
            self.zpt_database.mysql_no_fetch_querry(zapisz_biala_lista_querry)

    def kopiuj_tytul_przelwu(self):
        cboard = tk.Tk()
        cboard.withdraw()
        cboard.clipboard_clear()
        cboard.clipboard_append(self.tytul_przelewu_entry.get())
        cboard.update()
        cboard.destroy()

    def kopiuj_sume_przelwu(self):
        cboard = tk.Tk()
        cboard.withdraw()
        cboard.clipboard_clear()
        cboard.clipboard_append(self.suma_przelewu_kwota_label.cget('text')[:-3])
        cboard.update()
        cboard.destroy()

    def create_koszty_RF(self):
        self.koszty_RF = tk.Frame(self)
        self.koszty_RF.configure(bg='#383232', relief='groove', bd=1)
        self.koszty_RF.place(relx=0.51, rely=0.02, relwidth=0.48, relheight=0.96)
        self.create_koszty_R_0f()
        self.create_koszty_R_1f()
        self.create_zaplacone_faktury_treeview()
        self.update_faktury_zaplacone_treeview()
        self.create_koszty_R_2f()
        self.create_koszty_R_3f()
        self.update_kontrahenci_treeview()

    def create_koszty_R_0f(self):
        self.szukany_kontrahent_ = StringVar()
        self.szukany_kontrahent_.trace('w', lambda name, index, mode: self.update_faktury_zaplacone_treeview())
        self.koszty_szukanie_kontrahenta_entry = tk.Entry(self.koszty_RF, justify='center',
                                                          bg='#6b685f', fg='white',
                                                          textvariable=self.szukany_kontrahent_)

        self.koszty_szukanie_kontrahenta_entry.place(relx=0.02, rely=0.01, relwidth=0.96, relheight=0.03)

    def create_koszty_R_1f(self):  # zapłacone faktury
        self.koszty_R_1f = tk.Frame(self.koszty_RF, bg='#383232',
                                    relief='groove', bd=1)
        self.koszty_R_1f.place(relx=0.02, rely=0.05, relwidth=0.96, relheight=0.56)

    def create_zaplacone_faktury_treeview(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', fieldbackground="#383232", background="#383232", foreground='white')
        style.configure("Treeview.Heading", background="#383232", foreground="white")
        style.map('Treeview.Heading', background=[('disabled', '#383232')])

        def fixed_map(option):  # naprawa buga wersji dla Python 3.7 przy wyświetlaniu koloru linii w treeview
            return [elm for elm in style.map("Treeview", query_opt=option)
                    if elm[:2] != ("!disabled", "!selected")]

        style.map("Treeview", foreground=fixed_map("foreground"),
                  background=fixed_map("background"))

        self.columns_faktury_zaplacone = ('ID', 'KONTRAHENT', 'FV', 'KWOTA', 'TERMIN', 'ZAPŁACONE')
        self.zaplacone_faktury_treeview = ttk.Treeview(self.koszty_R_1f,
                                                       columns=self.columns_faktury_zaplacone, show='headings',
                                                       style="Treeview")

        self.zaplacone_faktury_treeview.heading('ID', text='ID')
        self.zaplacone_faktury_treeview.column('ID', width=50, stretch='no', anchor='center')
        self.zaplacone_faktury_treeview.heading('KONTRAHENT', text='KONTRAHENT')
        self.zaplacone_faktury_treeview.column('KONTRAHENT', minwidth=0, stretch='yes', anchor='center')
        self.zaplacone_faktury_treeview.heading('FV', text='FV')
        self.zaplacone_faktury_treeview.column('FV', width=170, stretch='no', anchor='center')
        self.zaplacone_faktury_treeview.heading('KWOTA', text='KWOTA')
        self.zaplacone_faktury_treeview.column('KWOTA', width=100, stretch='no', anchor='center')
        self.zaplacone_faktury_treeview.heading('TERMIN', text='TERMIN')
        self.zaplacone_faktury_treeview.column('TERMIN', width=100, stretch='no', anchor='center')
        self.zaplacone_faktury_treeview.heading('ZAPŁACONE', text='ZAPŁACONE')
        self.zaplacone_faktury_treeview.column('ZAPŁACONE', width=100, stretch='no', anchor='center')

        self.scrolly = ttk.Scrollbar(self.zaplacone_faktury_treeview, orient='vertical',
                                     command=self.zaplacone_faktury_treeview.yview)
        self.zaplacone_faktury_treeview.configure(yscrollcommand=self.scrolly.set)
        map(lambda col: col.configure(yscrollcommand=self.scrolly.set), self.columns_faktury_zaplacone)
        self.scrolly.pack(side=tk.RIGHT, fill=tk.Y)
        map(lambda col: col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True), self.columns_faktury_zaplacone)
        self.zaplacone_faktury_treeview.pack(expand='yes', fill='both')
        self.zaplacone_faktury_treeview.bind("<Double-1>", self.anuluj_zaplate_faktury)

    def get_dane_faktury_zaplacone(self):
        lista_filtrowana = []
        text = self.szukany_kontrahent_.get()

        dane_fakruty_zaplacone_querry = f'SELECT f.id_fv, k.nazwa, f.nr_fv,f.kwota, f.data_platnosci, f.data_zaplaty ' \
                                        f'FROM platnosci_kontrahenci k, platnosci_fv f WHERE f.id_kont=k.id_kont ' \
                                        f'AND f.zaplacone = 1 ' \
                                        f'AND data_zaplaty > DATE_SUB(NOW(), INTERVAL 5 MONTH)' \
                                        f'ORDER BY data_zaplaty DESC'
        dane_fakruty_zaplacone = self.zpt_database.mysql_querry(dane_fakruty_zaplacone_querry)

        if len(text) < 3:
            return dane_fakruty_zaplacone
        else:
            for d in dane_fakruty_zaplacone:
                if text.lower() in d[1].lower():
                    lista_filtrowana.append(d)
            return lista_filtrowana

    def update_faktury_zaplacone_treeview(self):
        dane = self.get_dane_faktury_zaplacone()
        self.zaplacone_faktury_treeview.delete(*self.zaplacone_faktury_treeview.get_children())
        i = 0
        for n in dane:
            i += 1
            id_faktury = n[0]
            nazwa_kotrahenta = n[1]
            nr_faktury = n[2]
            kwota_fakruty = f'{float(n[3]):.2f}'
            data_platnowci = n[4]
            data_zaplaty = n[5]

            if i % 2 == 0:
                background_gotowki = 'background_dark'
            else:
                background_gotowki = 'background_light'

            self.zaplacone_faktury_treeview.tag_configure('background_dark', background='#383232')
            self.zaplacone_faktury_treeview.tag_configure('background_light', background='#262424')

            self.zaplacone_faktury_treeview.insert('', 'end',
                                                   values=(id_faktury, nazwa_kotrahenta, nr_faktury, kwota_fakruty,
                                                           data_platnowci, data_zaplaty), tags=background_gotowki)

    def anuluj_zaplate_faktury(self, event):
        for item in self.zaplacone_faktury_treeview.selection():
            id_faktury = self.zaplacone_faktury_treeview.item(item, 'values')[0]
            zaplac_querry = f'UPDATE platnosci_fv SET zaplacone = 0, data_zaplaty = ""  WHERE id_fv = {id_faktury}'
            self.zpt_database.mysql_no_fetch_querry(zaplac_querry)
        self.update_faktury_zaplacone_treeview()
        self.update_faktury_treeview()

    def create_koszty_R_2f(self):  # dodaj kontrahentów
        self.koszty_R_2f = tk.Frame(self.koszty_RF, bg='#383232',
                                    relief='groove', bd=1)
        self.koszty_R_2f.place(relx=0.02, rely=0.62, relwidth=0.96, relheight=0.12)
        kontrahent_nazwa_label = tk.Label(self.koszty_R_2f, text='KONTRAHENT',
                                          foreground='white', background='#383232', anchor='w')
        kontrahent_nazwa_label.place(relx=0.02, rely=0.12, relwidth=0.14)
        kontrahent_nip_label = tk.Label(self.koszty_R_2f, text='NIP',
                                        foreground='white', background='#383232', anchor='w')
        kontrahent_nip_label.place(relx=0.02, rely=0.52, relwidth=0.05)
        kontrahent_konto_label = tk.Label(self.koszty_R_2f, text='KONTO',
                                          foreground='white', background='#383232', anchor='w')
        kontrahent_konto_label.place(relx=0.3, rely=0.52, relwidth=0.07)
        self.kontrahent_nazwa_entry = tk.Entry(self.koszty_R_2f, justify='center',
                                               bg='#6b685f', fg='white')
        self.kontrahent_nazwa_entry.place(relx=0.16, rely=0.12, relwidth=0.82)
        self.kontrahent_nip_entry = tk.Entry(self.koszty_R_2f, justify='center',
                                             bg='#6b685f', fg='white')
        self.kontrahent_nip_entry.place(relx=0.07, rely=0.52, relwidth=0.21)
        self.kontrahent_konto_entry = tk.Entry(self.koszty_R_2f, justify='center',
                                               bg='#6b685f', fg='white')
        self.kontrahent_konto_entry.place(relx=0.37, rely=0.52, relwidth=0.35)
        self.kontrahent_dodaj_button = tk.Button(self.koszty_R_2f, text='DODAJ', bg='#544949',
                                                 fg=f'{self.kolor_razem}', command=self.dodaj_kontrahenta_koszty)
        self.kontrahent_dodaj_button.place(relx=0.75, rely=0.52, relwidth=0.23)

    def dodaj_kontrahenta_koszty(self):
        nazwa = self.kontrahent_nazwa_entry.get()
        nip = self.kontrahent_nip_entry.get()
        konto = self.kontrahent_konto_entry.get()

        if nazwa != '' and nip != '' and konto != '':
            dodaj_querry = f'INSERT INTO platnosci_kontrahenci(nazwa, nip, konto) VALUES ("{nazwa}","{nip}","{konto}")'
            self.zpt_database.mysql_no_fetch_querry(dodaj_querry)
            self.update_kontrahenci_treeview()
            self.kontrahent_nazwa_entry.delete(0, 'end')
            self.kontrahent_nip_entry.delete(0, 'end')
            self.kontrahent_konto_entry.delete(0, 'end')
            kontrahenci_lista = self.get_kontrahenci_dane()
            self.fakruta_combobox_kontrahenci = ttk.Combobox(self.koszty_L_1f, values=kontrahenci_lista,
                                                             height=30, state='readonly')
            self.fakruta_combobox_kontrahenci.place(relx=0.15, rely=0.12, relwidth=0.82)
        else:
            messagebox.showerror('UWAGA', 'Podaj wszystkie dane')

    def create_koszty_R_3f(self):  # lista kontrahentów
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', fieldbackground="#383232", background="#383232", foreground='white')
        style.configure("Treeview.Heading", background="#383232", foreground="white")
        style.map('Treeview.Heading', background=[('disabled', '#383232')])

        def fixed_map(option):  # naprawa buga wersji dla Python 3.7 przy wyświetlaniu koloru linii w treeview
            return [elm for elm in style.map("Treeview", query_opt=option)
                    if elm[:2] != ("!disabled", "!selected")]

        style.map("Treeview", foreground=fixed_map("foreground"),
                  background=fixed_map("background"))

        self.koszty_R_3f = tk.Frame(self.koszty_RF)
        self.koszty_R_3f.configure(bg='#383232', relief='groove', bd=1)
        self.koszty_R_3f.place(relx=0.02, rely=0.75, relwidth=0.96, relheight=0.23)

        self.columns_kontrahenci = ('ID', 'KONTRAHENT', 'NIP', 'KONTO')
        self.kontrahenci_treeview = ttk.Treeview(self.koszty_R_3f, columns=self.columns_kontrahenci, show='headings',
                                                 style="Treeview")

        self.kontrahenci_treeview.heading('ID', text='ID')
        self.kontrahenci_treeview.column('ID', width=50, stretch='no', anchor='center')
        self.kontrahenci_treeview.heading('KONTRAHENT', text='KONTRAHENT')
        self.kontrahenci_treeview.column('KONTRAHENT', minwidth=0, stretch='yes', anchor='center')
        self.kontrahenci_treeview.heading('NIP', text='NIP')
        self.kontrahenci_treeview.column('NIP', width=170, stretch='no', anchor='center')
        self.kontrahenci_treeview.heading('KONTO', text='KONTO')
        self.kontrahenci_treeview.column('KONTO', width=250, stretch='no', anchor='center')

        self.scrolly = ttk.Scrollbar(self.kontrahenci_treeview, orient='vertical',
                                     command=self.kontrahenci_treeview.yview)
        self.kontrahenci_treeview.configure(yscrollcommand=self.scrolly.set)
        map(lambda col: col.configure(yscrollcommand=self.scrolly.set), self.columns_kontrahenci)
        self.scrolly.pack(side=tk.RIGHT, fill=tk.Y)
        map(lambda col: col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True), self.columns_kontrahenci)
        self.kontrahenci_treeview.pack(expand='yes', fill='both')
        self.kontrahenci_treeview.bind("<Double-1>", self.poprawa_wpisu_kontrahenci)

    def update_kontrahenci_treeview(self):
        dane = self.get_kontraheci_treeview_dane()
        self.kontrahenci_treeview.delete(*self.kontrahenci_treeview.get_children())
        i = 0
        for n in dane:
            i += 1
            id_kontrahenta = n[0]
            nazwa_kotrahenta = n[1]
            nip = n[2]
            konto = n[3]

            if i % 2 == 0:
                background_gotowki = 'background_dark'
            else:
                background_gotowki = 'background_light'

            self.kontrahenci_treeview.tag_configure('background_dark', background='#383232')
            self.kontrahenci_treeview.tag_configure('background_light', background='#262424')

            self.kontrahenci_treeview.insert('', 'end', values=(id_kontrahenta, nazwa_kotrahenta, nip, konto),
                                             tags=background_gotowki)

    def get_kontraheci_treeview_dane(self):
        kontrahenci_querry = f'SELECT * FROM platnosci_kontrahenci ORDER BY nazwa'
        kontrahenci = self.zpt_database.mysql_querry(kontrahenci_querry)
        return kontrahenci

    def poprawa_wpisu_kontrahenci(self, event):
        self.item = self.kontrahenci_treeview.selection()
        id = self.kontrahenci_treeview.item(self.item, 'values')[0]
        kontrahent = self.kontrahenci_treeview.item(self.item, 'values')[1]
        nip = self.kontrahenci_treeview.item(self.item, 'values')[2]
        konto = self.kontrahenci_treeview.item(self.item, 'values')[3]

        self.popraw_usun_kontrahencji_toplevel = tk.Toplevel(self.koszty_R_3f, background='#383232',
                                                             highlightthickness=2)
        self.popraw_usun_kontrahencji_toplevel.grab_set()
        self.popraw_usun_kontrahencji_toplevel.geometry(f'400x200+800+600')

        id_popraw_label = tk.Label(self.popraw_usun_kontrahencji_toplevel, text=f'ID',
                                   foreground='white', background='#383232', anchor='w')
        id_popraw_label.place(relx=0.03, rely=0.05, relwidth=0.22)
        kontrahent_popraw_label = tk.Label(self.popraw_usun_kontrahencji_toplevel, text=f'KONTRAHENT',
                                           foreground='white', background='#383232', anchor='w')
        kontrahent_popraw_label.place(relx=0.03, rely=0.2, relwidth=0.22)
        nip_popraw_label = tk.Label(self.popraw_usun_kontrahencji_toplevel, text=f'NIP',
                                    foreground='white', background='#383232', anchor='w')
        nip_popraw_label.place(relx=0.03, rely=0.38, relwidth=0.22)
        konto_popraw_label = tk.Label(self.popraw_usun_kontrahencji_toplevel, text=f'KONTO',
                                      foreground='white', background='#383232', anchor='w')
        konto_popraw_label.place(relx=0.03, rely=0.56, relwidth=0.22)

        self.poprawa_id_entry = tk.Entry(self.popraw_usun_kontrahencji_toplevel, justify='center',
                                         bg='#6b685f', fg='white')
        self.poprawa_id_entry.insert(0, id)
        self.poprawa_id_entry.place(relx=0.25, rely=0.05, relwidth=0.72)
        self.poprawa_kontrahent_entry = tk.Entry(self.popraw_usun_kontrahencji_toplevel, justify='center',
                                                 bg='#6b685f', fg='white')
        self.poprawa_kontrahent_entry.insert(0, kontrahent)
        self.poprawa_kontrahent_entry.place(relx=0.25, rely=0.2, relwidth=0.72)
        self.poprawa_nip_entry = tk.Entry(self.popraw_usun_kontrahencji_toplevel, justify='center',
                                          bg='#6b685f', fg='white')
        self.poprawa_nip_entry.insert(0, nip)
        self.poprawa_nip_entry.place(relx=0.25, rely=0.38, relwidth=0.72)
        self.poprawa_konto_entry = tk.Entry(self.popraw_usun_kontrahencji_toplevel, justify='center',
                                            bg='#6b685f', fg='white')
        self.poprawa_konto_entry.insert(0, konto)
        self.poprawa_konto_entry.place(relx=0.25, rely=0.56, relwidth=0.72)

        self.usun_wpis_button = tk.Button(self.popraw_usun_kontrahencji_toplevel, text='USUN', bg='#544949',
                                          fg=f'{self.kolor_razem}', command=self.usun_wpis_kontrahenci)
        self.usun_wpis_button.place(relx=0.03, rely=0.74, relwidth=0.44)

        self.popraw_wpis_button = tk.Button(self.popraw_usun_kontrahencji_toplevel, text='POPRAW', bg='#544949',
                                            fg=f'{self.kolor_razem}', command=self.popraw_wpis_kontrahenci)
        self.popraw_wpis_button.place(relx=0.53, rely=0.74, relwidth=0.44)

    def usun_wpis_kontrahenci(self):
        id = self.poprawa_id_entry.get()
        delete_querry = f'DELETE FROM platnosci_kontrahenci WHERE id_kont = {id}'
        self.zpt_database.mysql_no_fetch_querry(delete_querry)
        self.popraw_usun_kontrahencji_toplevel.destroy()
        self.update_kontrahenci_treeview()
        self.fakruta_combobox_kontrahenci.destroy()
        kontrahenci_lista = self.get_kontrahenci_dane()
        self.fakruta_combobox_kontrahenci = ttk.Combobox(self.koszty_L_1f, values=kontrahenci_lista,
                                                         height=30, state='readonly')
        self.fakruta_combobox_kontrahenci.place(relx=0.15, rely=0.12, relwidth=0.82)

    def popraw_wpis_kontrahenci(self):
        id = self.poprawa_id_entry.get()
        nip = self.poprawa_nip_entry.get()
        konto = self.poprawa_konto_entry.get()
        update_querry = f'UPDATE platnosci_kontrahenci SET nip = "{nip}",' \
                        f'konto = "{konto}" WHERE id_kont = {id}'
        self.zpt_database.mysql_no_fetch_querry(update_querry)
        self.update_kontrahenci_treeview()
        self.popraw_usun_kontrahencji_toplevel.destroy()
        kontrahenci_lista = self.get_kontrahenci_dane()
        self.fakruta_combobox_kontrahenci = ttk.Combobox(self.koszty_L_1f, values=kontrahenci_lista,
                                                         height=30, state='readonly')
        self.fakruta_combobox_kontrahenci.place(relx=0.15, rely=0.12, relwidth=0.82)

class Faktury_towar_frame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.configure(bg='#383232')
        self.zpt_database = ZPT_Database.ZPT_base()
        self.kolor_razem = '#b58b14'
        self.biala_lista_dane_do_zapisu = {}
        self.create_towar_LF()
        self.create_towar_RF()

    @staticmethod
    def start_new_thread(target):
        threading.Thread(target=target).start()

    def create_towar_LF(self):
        self.towar_LF = tk.Frame(self)
        self.towar_LF.configure(bg='#383232', relief='groove', bd=1)
        self.towar_LF.place(relx=0.01, rely=0.02, relwidth=0.48, relheight=0.96)
        self.create_faktury_towar_frame_treeview()
        self.create_towar_L_2f()
        self.update_faktury_towar_treeview()

    def create_towar_RF(self):
        self.towar_RF = tk.Frame(self)
        self.towar_RF.configure(bg='#383232', relief='groove', bd=1)
        self.towar_RF.place(relx=0.51, rely=0.02, relwidth=0.48, relheight=0.96)
        self.create_towar_R_1f()
        self.create_wybrane_dosatwca_faktury_treeview()
        self.create_towar_R_3f()
        self.ustaw_stan_button_admin_dostawcy()

    def create_faktury_towar_frame_treeview(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', fieldbackground="#383232", background="#383232", foreground='white')
        style.configure("Treeview.Heading", background="#383232", foreground="white")
        style.map('Treeview.Heading', background=[('disabled', '#383232')])

        def fixed_map(option):  # naprawa buga wersji dla Python 3.7 przy wyświetlaniu koloru linii w treeview
            return [elm for elm in style.map("Treeview", query_opt=option)
                    if elm[:2] != ("!disabled", "!selected")]

        style.map("Treeview", foreground=fixed_map("foreground"),
                  background=fixed_map("background"))

        self.faktury_L_1f = tk.Frame(self.towar_LF)
        self.faktury_L_1f.configure(bg='#383232', relief='groove', bd=1)
        self.faktury_L_1f.place(relx=0.02, rely=0.01, relwidth=0.96, relheight=0.80)

        self.columns_faktury = ('APTEKA', 'FAKTURA', 'DATA ZAKUPU', 'TERMIN', 'KWOTA')
        self.faktury_treeview = ttk.Treeview(self.faktury_L_1f, columns=self.columns_faktury, show='headings',
                                             style="Treeview")

        self.faktury_treeview.heading('APTEKA', text='APTEKA')
        self.faktury_treeview.column('APTEKA', width=70, stretch='no', anchor='center')
        self.faktury_treeview.heading('FAKTURA', text='FAKTURA')
        self.faktury_treeview.column('FAKTURA', minwidth=0, stretch='yes', anchor='center')
        self.faktury_treeview.heading('DATA ZAKUPU', text='DATA ZAKUPU')
        self.faktury_treeview.column('DATA ZAKUPU', width=120, stretch='no', anchor='center')
        self.faktury_treeview.heading('TERMIN', text='TERMIN')
        self.faktury_treeview.column('TERMIN', width=120, stretch='no', anchor='center')
        self.faktury_treeview.heading('KWOTA', text='KWOTA')
        self.faktury_treeview.column('KWOTA', width=120, stretch='no', anchor='center')

        self.scrolly = ttk.Scrollbar(self.faktury_treeview, orient='vertical', command=self.faktury_treeview.yview)
        self.faktury_treeview.configure(yscrollcommand=self.scrolly.set)
        map(lambda col: col.configure(yscrollcommand=self.scrolly.set), self.columns_faktury)
        self.scrolly.pack(side=tk.RIGHT, fill=tk.Y)
        map(lambda col: col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True), self.columns_faktury)
        self.faktury_treeview.pack(expand='yes', fill='both')
        self.faktury_treeview.bind("<Double-1>", self.poprawa_wpisu)
        self.faktury_treeview.bind('<<TreeviewSelect>>', self.wybrane_faktury_analizuj)

    def create_towar_L_2f(self):  # szczególy faktur
        self.towar_L_2f = tk.Frame(self.towar_LF)
        self.towar_L_2f.configure(bg='#383232', relief='groove', bd=1)
        self.towar_L_2f.place(relx=0.02, rely=0.82, relwidth=0.96, relheight=0.17)

        tytul_przelewu_label = tk.Label(self.towar_L_2f, text='TYTUŁ PRZELEWU',
                                        foreground='white', background='#383232', anchor='w')
        tytul_przelewu_label.place(relx=0.02, rely=0.06, relwidth=0.14)
        suma_przelewu_label = tk.Label(self.towar_L_2f, text='SUMA PRZELEWU',
                                       foreground='white', background='#383232', anchor='w')
        suma_przelewu_label.place(relx=0.02, rely=0.26, relwidth=0.14)

        self.tytul_przelewu_entry = tk.Entry(self.towar_L_2f, justify='center', bg='#6b685f', fg='white')
        self.tytul_przelewu_entry.place(relx=0.16, rely=0.06, relwidth=0.54)
        self.suma_przelewu_kwota_label = tk.Label(self.towar_L_2f, text='0.00 zł',
                                                  foreground='white', background='#383232', anchor='w')
        self.suma_przelewu_kwota_label.place(relx=0.16, rely=0.26, relwidth=0.54)
        self.kopiuj_tytul_przelwu_buton = tk.Button(self.towar_L_2f, text='KOPIUJ TYTUŁ',
                                                    bg='#544949',
                                                    fg=f'{self.kolor_razem}', command=self.kopiuj_tytul_przelwu)
        self.kopiuj_tytul_przelwu_buton.place(relx=0.72, rely=0.06, relwidth=0.26)
        self.kopiuj_sume_przelwu_buton = tk.Button(self.towar_L_2f, text='KOPIUJ KWOTĘ',
                                                   bg='#544949',
                                                   fg=f'{self.kolor_razem}', command=self.kopiuj_sume_przelwu)
        self.kopiuj_sume_przelwu_buton.place(relx=0.72, rely=0.26, relwidth=0.26)

        self.gotowki_toplevel_buton = tk.Button(self.towar_L_2f, text='GOTÓWKI',
                                                bg='#544949', command=self.create_gotowki_toplevel,
                                                fg=f'{self.kolor_razem}')
        self.gotowki_toplevel_buton.place(relx=0.72, rely=0.46, relwidth=0.26)

        # sprawdzanie biała lista
        self.dane_kontrahent_konto_nip_label = tk.Label(self.towar_L_2f, text='',
                                                        foreground='white', background='#383232')
        self.dane_kontrahent_konto_nip_label.place(relx=0.02, rely=0.56, relwidth=0.7)

        self.zaplac_button = tk.Button(self.towar_L_2f, text='ZAPŁAĆ',
                                       bg='#544949', fg=f'{self.kolor_razem}', state='disable',
                                       command=self.zaplac_faktury_wybrane)
        self.zaplac_button.place(relx=0.02, rely=0.8, relwidth=0.3)

        self.przelew_button = tk.Button(self.towar_L_2f, text='DODAJ DO PRZELEWÓW',
                                        bg='#544949', fg=f'{self.kolor_razem}', state='disable',
                                        command=self.dodaj_do_listy_przelewow)
        self.przelew_button.place(relx=0.33, rely=0.8, relwidth=0.3)

        self.update_dane_button = tk.Button(self.towar_L_2f, text='ODŚWIEŻ DANE',
                                            bg='#544949', fg=f'{self.kolor_razem}',
                                            command=self.start_new_thread(self.update_dane_towar))
        self.update_dane_button.place(relx=0.64, rely=0.8, relwidth=0.25)

        self.odswierz_button = tk.Button(self.towar_L_2f, text='\uD83D\uDDD8',
                                         bg='#544949', fg=f'{self.kolor_razem}',
                                         command=self.update_faktury_towar_treeview)
        self.odswierz_button.place(relx=0.9, rely=0.8, relwidth=0.08)

    def update_dane_towar(self):
        today = datetime.datetime.today().date() + datetime.timedelta(days=1)
        data_start = today - datetime.timedelta(days=61)

        for n in range(2, 9):
            self.zpt_database = ZPT_Database.ZPT_base()
            tabela_zakupy = "zakupy_0" + str(n)
            kolumna_dostawcy = "id_0" + str(n)

            querry = f"SELECT d.id, z.nrfv, z.dat_zak_fv, z.datap, z.wartosc, d.nazwa FROM" \
                     f" {tabela_zakupy} z, dostawcy d where {kolumna_dostawcy} = z.dostawca " \
                     f"AND dat_zak_fv BETWEEN '{data_start}' AND '{today}' ORDER BY z.dat_zak_fv"
            wynik_lista_fv = self.zpt_database.mysql_querry(querry)

            for row in wynik_lista_fv:
                dostawca = row[0]
                nrfv = row[1]
                data_zak = row[2][0:10]
                data_platnosci = row[3][0:10]
                kwota = row[4]
                zaplacone = 0
                data_zaplaty = ''
                dost_nazwa = row[5]

                if dostawca > 18 and dostawca != 34 and dostawca != 121 and dostawca != 157:
                    querry_update = f"INSERT INTO platnosci_towar VALUES(" \
                                    f"{n}, {dostawca},'{nrfv}','{data_zak}','{data_platnosci}', {kwota}, {zaplacone}," \
                                    f" '{data_zaplaty}','{dost_nazwa}' ) ON DUPLICATE KEY UPDATE " \
                                    f"`dostawca` = {dostawca}, `data_zak` = '{data_zak}',`kwota`= {kwota}," \
                                    f" `dost_nazwa` = '{dost_nazwa}'"
                    self.zpt_database.mysql_no_fetch_querry(querry_update)

        now = str(datetime.datetime.now())[0:19]
        querry_akt = f"UPDATE aktualizacja SET data='{now}' WHERE apteka = 90"
        self.zpt_database.mysql_no_fetch_querry(querry_akt)

        self.controller.logger.log(20, f'Wykonano UPDATE faktur towarowych do płatności')

    def get_nazwy_dostacow(self):
        dostawcy_nazwa_querry = f'SELECT DISTINCT(nazwa), id FROM dostawcy ORDER BY nazwa'
        dostawcy_nazwa = self.zpt_database.mysql_querry(dostawcy_nazwa_querry)
        return dostawcy_nazwa

    def get_dane_faktury_towar(self):
        lista_faktur_niezaplaconych = []
        faktury_niezplacone_querry = f'SELECT apteka, nrfv, data_zak, data_platnosci, kwota, dost_nazwa ' \
                                     f'FROM platnosci_towar WHERE zaplacone = 0 ' \
                                     ' ORDER BY data_platnosci'
        faktury_niezaplacone = self.zpt_database.mysql_querry(faktury_niezplacone_querry)

        dostawcy_nazwa = self.get_nazwy_dostacow()

        for d in dostawcy_nazwa:
            d_nazwa = d[0]
            d_id = d[1]
            faktury_dla_dostawcy = []
            for f in faktury_niezaplacone:
                if f[5] == d_nazwa:
                    faktury_dla_dostawcy.append(f)
                    continue
            if faktury_dla_dostawcy != []:
                lista_faktur_niezaplaconych.append((d_nazwa, d_id, faktury_dla_dostawcy))
        return lista_faktur_niezaplaconych

    def update_faktury_towar_treeview(self):
        dane = self.get_dane_faktury_towar()
        self.faktury_treeview.delete(*self.faktury_treeview.get_children())

        for n in dane:
            nazwa = n[0]
            suma = 0
            d = 0
            pierwszy_termin = ''
            for f in n[2]:
                suma += float(f[4])
                if d == 0:
                    pierwszy_termin = f[3]
                    d = 1

            dostawca = self.faktury_treeview.insert('', 'end', values=('', f'{nazwa}', '', f'{pierwszy_termin}',
                                                                       f'{round(suma, 2)} zł'), open=True,
                                                    tags=('background_dostawca', 'foreground_dostawca'))
            i = 0
            for f in n[2]:
                i += 1
                apteka = f[0]
                nr_faktury = f[1]
                data_zakupu = f[2]
                termin = f[3]
                kwota = f'{float(f[4]):.2f}'

                if i % 2 == 0:
                    background = 'background_dark'
                else:
                    background = 'background_light'

                if self.check_date_deley(termin):
                    foreground = 'foreground_dobry_termin'
                else:
                    foreground = 'foreground_zly_termin'

                self.faktury_treeview.insert(dostawca, 'end',
                                             values=(apteka, nr_faktury, data_zakupu, termin, f'{kwota} zł'),
                                             tags=(background, foreground))

            self.faktury_treeview.insert('', 'end', values=('', '', '', '', ''),
                                         tags=('background_dostawca', 'foreground_dostawca'))

            self.faktury_treeview.tag_configure('background_dark', background='#383232')
            self.faktury_treeview.tag_configure('background_dostawca', background='#1a1717')
            self.faktury_treeview.tag_configure('background_light', background='#262424')
            self.faktury_treeview.tag_configure('foreground_dostawca', foreground=f'{self.kolor_razem}')
            self.faktury_treeview.tag_configure('foreground_zly_termin', foreground='red')
            self.faktury_treeview.tag_configure('foreground_dobry_termin', foreground='white')

            self.tytul_przelewu_entry.delete(0, 'end')
            self.suma_przelewu_kwota_label.config(text='0.00 zł')
            self.dane_kontrahent_konto_nip_label.config(text='')

    @staticmethod
    def check_date_deley(date):
        if date == 'None':
            return False
        date_1 = datetime.datetime.strptime(date, '%Y-%m-%d')
        date_now = datetime.datetime.strptime(str(datetime.date.today()), '%Y-%m-%d')
        if date_1 <= date_now:
            return False
        return True

    def poprawa_wpisu(self, event):
        pass

    def wybrane_faktury_analizuj(self, event):
        self.tytul_przelewu_entry.delete(0, 'end')
        self.suma_przelewu_kwota_label.config(text='0.00 zł')
        tytul_przelewu = ''
        suma_przelewu = 0
        parents_list = []

        for item in event.widget.selection():
            if self.faktury_treeview.item(item, 'values')[0] == '' \
                    and self.faktury_treeview.item(item, 'values')[1] == '':
                self.wyczysc_wszystkie_pola()
                self.dostawcy_filtr_combobox.set('')
                self.update_wybrane_dosatwca_faktury_treeview('')
                self.ustaw_stan_button_admin_dostawcy()
                self.update_dostawca_admin()
                return False
            elif self.faktury_treeview.item(item, 'values')[0] == '' \
                    and self.faktury_treeview.item(item, 'values')[1] != '':
                self.dostawcy_filtr_combobox.set(f'{self.faktury_treeview.item(item, "values")[1]}')
                self.update_wybrane_dosatwca_faktury_treeview('')
                self.update_dostawca_admin()
                self.ustaw_stan_button_admin_dostawcy()
            else:
                if len(event.widget.selection()) == 1:
                    parent = self.faktury_treeview.parent(event.widget.selection()[0])
                    parent_name = self.faktury_treeview.item(parent, 'values')[1]
                    self.dostawcy_filtr_combobox.set(f'{parent_name}')
                    self.update_wybrane_dosatwca_faktury_treeview('')
                    self.update_dostawca_admin()
                    self.ustaw_stan_button_admin_dostawcy()
                    self.ustaw_button_stan_poczatek()

                if len(event.widget.selection()) > 1:
                    if parents_list == []:
                        parents_list.append(self.faktury_treeview.parent(event.widget.selection()[0]))
                    for item_ in event.widget.selection():
                        if self.faktury_treeview.parent(item_) not in parents_list:
                            self.wyczysc_wszystkie_pola()
                            self.ustaw_button_stan_poczatek()
                            messagebox.showerror('UWAGA', 'Wybrano dwóch różnych kontrahentów')
                            return False

                tytul_przelewu += self.faktury_treeview.item(item, 'values')[1] + ', '
                suma_przelewu += float(self.faktury_treeview.item(item, 'values')[4][:-3])

        self.tytul_przelewu_entry.insert(0, tytul_przelewu[:-2])
        self.suma_przelewu_kwota_label.config(text=f'{suma_przelewu:.2f} zł')

    def ustaw_button_stan_poczatek(self):
        self.id_02_entry.config(background='#6b685f')
        self.id_03_entry.config(background='#6b685f')
        self.id_04_entry.config(background='#6b685f')
        self.id_05_entry.config(background='#6b685f')
        self.id_06_entry.config(background='#6b685f')
        self.id_07_entry.config(background='#6b685f')
        self.id_08_entry.config(background='#6b685f')
        self.nip_entry.config(background='#6b685f')
        self.konto_entry.config(background='#6b685f')
        self.popraw_dostawca_button.place_forget()
        self.edytuj_dostawca_button.place_forget()
        self.edytuj_dostawca_button.place(relx=0.54, rely=0.78, relwidth=0.23)

    def wyczysc_wszystkie_pola(self):
        self.tytul_przelewu_entry.delete(0, 'end')
        self.suma_przelewu_kwota_label.config(text=f'0.00 zł')
        self.dostawcy_filtr_combobox.set('')
        self.update_wybrane_dosatwca_faktury_treeview('')
        self.dane_kontrahent_konto_nip_label.config(text='')
        self.zaplac_button.config(state='disable')
        self.przelew_button.config(state='disable')

        # odznaczenie elementów drzewa
        for item in self.faktury_treeview.selection():
            self.faktury_treeview.selection_remove(item)

    def kopiuj_tytul_przelwu(self):
        cboard = tk.Tk()
        cboard.withdraw()
        cboard.clipboard_clear()
        cboard.clipboard_append(self.tytul_przelewu_entry.get())
        cboard.update()
        cboard.destroy()

    def kopiuj_sume_przelwu(self):
        cboard = tk.Tk()
        cboard.withdraw()
        cboard.clipboard_clear()
        cboard.clipboard_append(self.suma_przelewu_kwota_label.cget('text')[:-3])
        cboard.update()
        cboard.destroy()

    def zaplac_faktury_wybrane(self):
        today = datetime.date.today()
        for item_ in self.faktury_treeview.selection():
            faktura_nr = self.faktury_treeview.item(item_, 'values')[1]
            zaplac_querry = f'UPDATE platnosci_towar SET zaplacone = 1, data_zaplaty = "{today}" WHERE ' \
                            f'nrfv = "{faktura_nr}"'
            self.zpt_database.mysql_no_fetch_querry(zaplac_querry)

        konto_26 = self.konto_entry.get().replace(' ', '')
        if self.biala_lista_dane_do_zapisu != {}:
            zapisz_biala_lista_querry = f'INSERT INTO biala_lista VALUES(NULL, "{self.biala_lista_dane_do_zapisu["czas"]}", ' \
                                        f'"{self.biala_lista_dane_do_zapisu["nazwa"]}", "{konto_26}", ' \
                                        f'"{self.biala_lista_dane_do_zapisu["nip"]}", ' \
                                        f'"{self.biala_lista_dane_do_zapisu["status"]}", ' \
                                        f'"{self.biala_lista_dane_do_zapisu["kod_potwierdzenia"]}")'
            self.zpt_database.mysql_no_fetch_querry(zapisz_biala_lista_querry)
        self.update_wybrane_dosatwca_faktury_treeview(self.dostawcy_filtr_combobox.get())
        self.update_faktury_towar_treeview()
        self.tytul_przelewu_entry.delete(0, 'end')
        self.suma_przelewu_kwota_label.config(text='0.00 zł')
        self.dane_kontrahent_konto_nip_label.config(text='')

    def create_towar_R_1f(self):  # filtr dostawców
        self.towar_R_1f = tk.Frame(self.towar_RF)
        self.towar_R_1f.configure(bg='#383232', relief='groove', bd=1)
        self.towar_R_1f.place(relx=0.02, rely=0.01, relwidth=0.96, relheight=0.08)
        self.dostawcy_filtr_combobox = ttk.Combobox(self.towar_R_1f, values=self.update_lista_dostawcow(),
                                                    height=30, state='readonly')
        self.dostawcy_filtr_combobox.place(relx=0.02, rely=0.3, relwidth=0.96)
        self.dostawcy_filtr_combobox.bind("<<ComboboxSelected>>", self.update_wybrane_dosatwca_faktury_treeview)

    def update_lista_dostawcow(self):
        dostawcy = ['']
        for d in self.get_nazwy_dostacow():
            dostawcy.append(d[0])
        return dostawcy

    def create_wybrane_dosatwca_faktury_treeview(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', fieldbackground="#383232", background="#383232", foreground='white')
        style.configure("Treeview.Heading", background="#383232", foreground="white")
        style.map('Treeview.Heading', background=[('disabled', '#383232')])

        def fixed_map(option):  # naprawa buga wersji dla Python 3.7 przy wyświetlaniu koloru linii w treeview
            return [elm for elm in style.map("Treeview", query_opt=option)
                    if elm[:2] != ("!disabled", "!selected")]

        style.map("Treeview", foreground=fixed_map("foreground"),
                  background=fixed_map("background"))

        self.wybrane_towar_R_2f = tk.Frame(self.towar_RF)
        self.wybrane_towar_R_2f.configure(bg='#383232', relief='groove', bd=1)
        self.wybrane_towar_R_2f.place(relx=0.02, rely=0.10, relwidth=0.96, relheight=0.71)

        self.columns_faktury_wybrany_dostawca = ('APTEKA', 'FAKTURA', 'DATA ZAKUPU', 'TERMIN', 'KWOTA', 'DATA ZAPLATY')
        self.faktury_wybrany_dostawca_treeview = ttk.Treeview(self.wybrane_towar_R_2f,
                                                              columns=self.columns_faktury_wybrany_dostawca,
                                                              show='headings',
                                                              style="Treeview")

        self.faktury_wybrany_dostawca_treeview.heading('APTEKA', text='APTEKA')
        self.faktury_wybrany_dostawca_treeview.column('APTEKA', width=70, stretch='no', anchor='center')
        self.faktury_wybrany_dostawca_treeview.heading('FAKTURA', text='FAKTURA')
        self.faktury_wybrany_dostawca_treeview.column('FAKTURA', minwidth=0, stretch='yes', anchor='center')
        self.faktury_wybrany_dostawca_treeview.heading('DATA ZAKUPU', text='DATA ZAKUPU')
        self.faktury_wybrany_dostawca_treeview.column('DATA ZAKUPU', width=120, stretch='no', anchor='center')
        self.faktury_wybrany_dostawca_treeview.heading('TERMIN', text='TERMIN')
        self.faktury_wybrany_dostawca_treeview.column('TERMIN', width=120, stretch='no', anchor='center')
        self.faktury_wybrany_dostawca_treeview.heading('KWOTA', text='KWOTA')
        self.faktury_wybrany_dostawca_treeview.column('KWOTA', width=120, stretch='no', anchor='center')
        self.faktury_wybrany_dostawca_treeview.heading('DATA ZAPLATY', text='DATA ZAPŁATY')
        self.faktury_wybrany_dostawca_treeview.column('DATA ZAPLATY', width=120, stretch='no', anchor='center')

        self.scrolly = ttk.Scrollbar(self.faktury_wybrany_dostawca_treeview, orient='vertical',
                                     command=self.faktury_wybrany_dostawca_treeview.yview)
        self.faktury_wybrany_dostawca_treeview.configure(yscrollcommand=self.scrolly.set)
        map(lambda col: col.configure(yscrollcommand=self.scrolly.set), self.columns_faktury_wybrany_dostawca)
        self.scrolly.pack(side=tk.RIGHT, fill=tk.Y)
        map(lambda col: col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True), self.columns_faktury_wybrany_dostawca)
        self.faktury_wybrany_dostawca_treeview.pack(expand='yes', fill='both')

    def update_wybrane_dosatwca_faktury_treeview(self, event):
        self.update_dostawca_admin()
        wybrany_dostawca = self.dostawcy_filtr_combobox.get()
        dane_faktur = self.get_dane_wybrany_dostawca_faktury(wybrany_dostawca)
        self.faktury_wybrany_dostawca_treeview.delete(*self.faktury_wybrany_dostawca_treeview.get_children())

        i = 0
        for n in dane_faktur:
            i += 1
            apteka = n[0]
            nr_fv = n[1]
            data_zak = n[2]
            data_platnosci = n[3]
            kwota = n[4]
            data_zaplaty = n[5]

            if n[6] == 2:
                data_zaplaty = 'GOTÓWKA'

            if i % 2 == 0:
                background = 'background_dark'
            else:
                background = 'background_light'

            self.faktury_wybrany_dostawca_treeview.insert('', 'end', values=(apteka, nr_fv, data_zak, data_platnosci,
                                                                             f'{kwota} zł', data_zaplaty),
                                                          tags=background)

            self.faktury_wybrany_dostawca_treeview.tag_configure('background_dark', background='#383232')
            self.faktury_wybrany_dostawca_treeview.tag_configure('background_light', background='#262424')
            self.faktury_wybrany_dostawca_treeview.bind("<Double-1>", self.poprawa_wpisu_faktura_towar)

    def get_dane_wybrany_dostawca_faktury(self, wybrany_dostawca):
        dane_querry = f'SELECT apteka, nrfv, data_zak, data_platnosci, kwota, data_zaplaty, zaplacone FROM platnosci_towar ' \
                      f'WHERE dost_nazwa = "{wybrany_dostawca}" ORDER BY data_platnosci DESC'
        dane = self.zpt_database.mysql_querry(dane_querry)
        return dane

    def create_towar_R_3f(self):
        self.towar_R_3f = tk.Frame(self.towar_RF)
        self.towar_R_3f.configure(bg='#383232', relief='groove', bd=1)
        self.towar_R_3f.place(relx=0.02, rely=0.82, relwidth=0.96, relheight=0.17)

        nazwa_dostawcy_label = tk.Label(self.towar_R_3f, text='DOSTAWCA',
                                        foreground='white', background='#383232', anchor='w')
        nazwa_dostawcy_label.place(relx=0.04, rely=0.06, relwidth=0.10)

        self.dostawca_id_frame = tk.Frame(self.towar_R_3f)
        self.dostawca_id_frame.configure(bg='#383232', relief='groove', bd=1)
        self.dostawca_id_frame.place(relx=0.04, rely=0.23, relwidth=0.92, relheight=0.3)

        frame_width = self.dostawca_id_frame.winfo_width()
        frame_height = self.dostawca_id_frame.winfo_height()

        id_02_label = tk.Label(self.dostawca_id_frame, text='ID 02', relief="groove",
                               foreground='white', background='#383232')
        id_02_label.place(relx=0, rely=0, relwidth=1 / 7, relheight=1 / 2)
        id_03_label = tk.Label(self.dostawca_id_frame, text='ID 03', relief="groove",
                               foreground='white', background='#383232')
        id_03_label.place(relx=frame_width * (1 / 7), rely=0, relwidth=1 / 7, relheight=1 / 2)
        id_04_label = tk.Label(self.dostawca_id_frame, text='ID 04', relief="groove",
                               foreground='white', background='#383232')
        id_04_label.place(relx=frame_width * (2 / 7), rely=0, relwidth=1 / 7, relheight=1 / 2)
        id_05_label = tk.Label(self.dostawca_id_frame, text='ID 05', relief="groove",
                               foreground='white', background='#383232')
        id_05_label.place(relx=frame_width * (3 / 7), rely=0, relwidth=1 / 7, relheight=1 / 2)
        id_06_label = tk.Label(self.dostawca_id_frame, text='ID 06', relief="groove",
                               foreground='white', background='#383232')
        id_06_label.place(relx=frame_width * (4 / 7), rely=0, relwidth=1 / 7, relheight=1 / 2)
        id_07_label = tk.Label(self.dostawca_id_frame, text='ID 07', relief="groove",
                               foreground='white', background='#383232')
        id_07_label.place(relx=frame_width * (5 / 7), rely=0, relwidth=1 / 7, relheight=1 / 2)
        id_08_label = tk.Label(self.dostawca_id_frame, text='ID 08', relief="groove",
                               foreground='white', background='#383232')
        id_08_label.place(relx=frame_width * (6 / 7), rely=0, relwidth=1 / 7, relheight=1 / 2)

        nip_label = tk.Label(self.towar_R_3f, text='NIP',
                             foreground='white', background='#383232', anchor='w')
        nip_label.place(relx=0.04, rely=0.57, relwidth=0.05)
        konto_label = tk.Label(self.towar_R_3f, text='KONTO',
                               foreground='white', background='#383232', anchor='w')
        konto_label.place(relx=0.41, rely=0.57, relwidth=0.07)
        biala_lista_label = tk.Label(self.towar_R_3f, text='BIAŁA LISTA',
                                     foreground='white', background='#383232', anchor='w')
        biala_lista_label.place(relx=0.78, rely=0.78, relwidth=0.10)

        self.nazwa_dostawca_entry = tk.Entry(self.towar_R_3f, justify='center', bg='#6b685f', fg='white')
        self.nazwa_dostawca_entry.place(relx=0.14, rely=0.06, relwidth=0.82)

        self.id_02_entry = tk.Entry(self.dostawca_id_frame, justify='center', bg='#6b685f', fg='white')
        self.id_02_entry.place(relx=0, rely=frame_height / 2, relwidth=1 / 7, relheight=1 / 2)
        self.id_03_entry = tk.Entry(self.dostawca_id_frame, justify='center', bg='#6b685f', fg='white')
        self.id_03_entry.place(relx=frame_width * (1 / 7), rely=frame_height / 2, relwidth=1 / 7, relheight=1 / 2)
        self.id_04_entry = tk.Entry(self.dostawca_id_frame, justify='center', bg='#6b685f', fg='white')
        self.id_04_entry.place(relx=frame_width * (2 / 7), rely=frame_height / 2, relwidth=1 / 7, relheight=1 / 2)
        self.id_05_entry = tk.Entry(self.dostawca_id_frame, justify='center', bg='#6b685f', fg='white')
        self.id_05_entry.place(relx=frame_width * (3 / 7), rely=frame_height / 2, relwidth=1 / 7, relheight=1 / 2)
        self.id_06_entry = tk.Entry(self.dostawca_id_frame, justify='center', bg='#6b685f', fg='white')
        self.id_06_entry.place(relx=frame_width * (4 / 7), rely=frame_height / 2, relwidth=1 / 7, relheight=1 / 2)
        self.id_07_entry = tk.Entry(self.dostawca_id_frame, justify='center', bg='#6b685f', fg='white')
        self.id_07_entry.place(relx=frame_width * (5 / 7), rely=frame_height / 2, relwidth=1 / 7, relheight=1 / 2)
        self.id_08_entry = tk.Entry(self.dostawca_id_frame, justify='center', bg='#6b685f', fg='white')
        self.id_08_entry.place(relx=frame_width * (6 / 7), rely=frame_height / 2, relwidth=1 / 7, relheight=1 / 2)

        self.nip_entry = tk.Entry(self.towar_R_3f, justify='center', bg='#6b685f', fg='white')
        self.nip_entry.place(relx=0.08, rely=0.57, relwidth=0.3)
        self.konto_entry = tk.Entry(self.towar_R_3f, justify='center', bg='#6b685f', fg='white')
        self.konto_entry.place(relx=0.48, rely=0.57, relwidth=0.48)

        self.id_02_entry.insert(0, '0')
        self.id_03_entry.insert(0, '0')
        self.id_04_entry.insert(0, '0')
        self.id_05_entry.insert(0, '0')
        self.id_06_entry.insert(0, '0')
        self.id_07_entry.insert(0, '0')
        self.id_08_entry.insert(0, '0')

        self.dodaj_dostawca_button = tk.Button(self.towar_R_3f, text='DODAJ',
                                               bg='#544949', fg=f'{self.kolor_razem}',
                                               command=self.dodaj_dostawca)
        self.dodaj_dostawca_button.place(relx=0.04, rely=0.78, relwidth=0.23)
        self.usun_dostawca_button = tk.Button(self.towar_R_3f, text='USUŃ',
                                              bg='#544949', fg=f'{self.kolor_razem}',
                                              command=self.usun_dostawca)
        self.usun_dostawca_button.place(relx=0.29, rely=0.78, relwidth=0.23)
        self.edytuj_dostawca_button = tk.Button(self.towar_R_3f, text='EDYTUJ',
                                                bg='#544949', fg=f'{self.kolor_razem}',
                                                command=self.edytuj_dostawca)
        self.edytuj_dostawca_button.place(relx=0.54, rely=0.78, relwidth=0.23)
        self.popraw_dostawca_button = tk.Button(self.towar_R_3f, text='POPRAW',
                                                bg='#544949', fg=f'{self.kolor_razem}',
                                                command=self.popraw_dostawca)
        self.dioda_biala_lista = tk.Label(self.towar_R_3f, relief="raised",
                                          background='green')
        self.dioda_biala_lista.place(relx=0.88, rely=0.78, relwidth=0.08)

        # todo:
        #   sprawdz czy nie ma juz takiego nipu
        #   pobierz nazwe po nipie

    def update_dostawca_admin(self):
        nazwa = self.dostawcy_filtr_combobox.get()
        dane_dostawca = self.get_dane_dostawca_admin(nazwa)

        if dane_dostawca == []:
            self.nazwa_dostawca_entry.delete(0, 'end')
            self.id_02_entry.delete(0, 'end')
            self.id_03_entry.delete(0, 'end')
            self.id_04_entry.delete(0, 'end')
            self.id_05_entry.delete(0, 'end')
            self.id_06_entry.delete(0, 'end')
            self.id_07_entry.delete(0, 'end')
            self.id_08_entry.delete(0, 'end')
            self.nip_entry.delete(0, 'end')
            self.konto_entry.delete(0, 'end')

            self.nazwa_dostawca_entry.insert(0, '')
            self.id_02_entry.insert(0, '0')
            self.id_03_entry.insert(0, '0')
            self.id_04_entry.insert(0, '0')
            self.id_05_entry.insert(0, '0')
            self.id_06_entry.insert(0, '0')
            self.id_07_entry.insert(0, '0')
            self.id_08_entry.insert(0, '0')
            self.nip_entry.insert(0, '')
            self.konto_entry.insert(0, '')


        else:
            self.nazwa_dostawca_entry.delete(0, 'end')
            self.id_02_entry.delete(0, 'end')
            self.id_03_entry.delete(0, 'end')
            self.id_04_entry.delete(0, 'end')
            self.id_05_entry.delete(0, 'end')
            self.id_06_entry.delete(0, 'end')
            self.id_07_entry.delete(0, 'end')
            self.id_08_entry.delete(0, 'end')
            self.nip_entry.delete(0, 'end')
            self.konto_entry.delete(0, 'end')

            self.nazwa_dostawca_entry.insert(0, f'{nazwa}')
            self.id_02_entry.insert(0, f'{dane_dostawca[2]}')
            self.id_03_entry.insert(0, f'{dane_dostawca[3]}')
            self.id_04_entry.insert(0, f'{dane_dostawca[4]}')
            self.id_05_entry.insert(0, f'{dane_dostawca[5]}')
            self.id_06_entry.insert(0, f'{dane_dostawca[6]}')
            self.id_07_entry.insert(0, f'{dane_dostawca[7]}')
            self.id_08_entry.insert(0, f'{dane_dostawca[8]}')
            if dane_dostawca[9] != '':
                self.nip_entry.insert(0, f'{dane_dostawca[9]}')
            else:
                self.nip_entry.insert(0, 'BRAK')

            if dane_dostawca[10] != '':
                self.konto_entry.insert(0, f'{dane_dostawca[10]}')
            else:
                self.konto_entry.insert(0, 'BRAK')

        self.ustaw_stan_button_admin_dostawcy()

    def get_dane_dostawca_admin(self, nazwa):
        dane_dostawca_querry = f'SELECT * FROM dostawcy WHERE nazwa = "{nazwa}"'
        dane_dostawca = self.zpt_database.mysql_querry(dane_dostawca_querry)
        if dane_dostawca != []:
            return dane_dostawca[0]
        return []

    def usun_dostawca(self):
        result = messagebox.askyesno("USUŃ", "CZY NA PEWNO USUNĄĆ")
        if result == True:
            delete_querry = f'DELETE FROM dostawcy WHERE nazwa = "{self.nazwa_dostawca_entry.get()}"'
            self.zpt_database.mysql_no_fetch_querry(delete_querry)
            self.dostawcy_filtr_combobox.config(values=self.update_lista_dostawcow())
            self.wyczysc_wszystkie_pola()
        else:
            pass

    def dodaj_dostawca(self):
        nazwa = self.nazwa_dostawca_entry.get()
        if nazwa == '':
            messagebox.showwarning('UWAGA', 'WPISZ NAZWĘ DOSTAWCY')
            return False
        else:
            add_querry = f'INSERT INTO dostawcy VALUES(NULL, "{nazwa}", {self.id_02_entry.get()},' \
                         f'{self.id_03_entry.get()}, {self.id_04_entry.get()}, {self.id_05_entry.get()},' \
                         f'{self.id_06_entry.get()}, {self.id_07_entry.get()}, {self.id_08_entry.get()},' \
                         f'"{self.nip_entry.get()}", "{self.konto_entry.get()}")'
            self.zpt_database.mysql_no_fetch_querry(add_querry)
            self.dostawcy_filtr_combobox.config(values=self.update_lista_dostawcow())
            self.wyczysc_wszystkie_pola()

    def edytuj_dostawca(self):
        self.id_02_entry.config(background='grey')
        self.id_03_entry.config(background='grey')
        self.id_04_entry.config(background='grey')
        self.id_05_entry.config(background='grey')
        self.id_06_entry.config(background='grey')
        self.id_07_entry.config(background='grey')
        self.id_08_entry.config(background='grey')
        self.nip_entry.config(background='grey')
        self.konto_entry.config(background='grey')

        self.edytuj_dostawca_button.place_forget()
        self.popraw_dostawca_button.place(relx=0.54, rely=0.78, relwidth=0.23)

    def popraw_dostawca(self):
        self.nazwa_dostawca_entry.config(background='#6b685f')
        self.id_02_entry.config(background='#6b685f')
        self.id_03_entry.config(background='#6b685f')
        self.id_04_entry.config(background='#6b685f')
        self.id_05_entry.config(background='#6b685f')
        self.id_06_entry.config(background='#6b685f')
        self.id_07_entry.config(background='#6b685f')
        self.id_08_entry.config(background='#6b685f')
        self.nip_entry.config(background='#6b685f')
        self.konto_entry.config(background='#6b685f')

        nazwa_dostawcy = self.nazwa_dostawca_entry.get()
        update_querry = f'UPDATE dostawcy SET nazwa = "{nazwa_dostawcy}", id_02 = {self.id_02_entry.get()}, ' \
                        f'id_03 = {self.id_03_entry.get()}, id_04 = {self.id_04_entry.get()}, ' \
                        f'id_05 = {self.id_05_entry.get()}, id_06 = {self.id_06_entry.get()}, ' \
                        f'id_07 = {self.id_07_entry.get()}, id_08 = {self.id_08_entry.get()}, ' \
                        f'nip = "{self.nip_entry.get()}", konto = "{self.konto_entry.get()}" ' \
                        f'WHERE nazwa = "{self.aktualna_nazwa}"'
        self.zpt_database.mysql_no_fetch_querry(update_querry)
        update_platnosci_querry = f'UPDATE platnosci_towar SET dost_nazwa = "{nazwa_dostawcy}" ' \
                                  f'WHERE dost_nazwa = "{self.aktualna_nazwa}"'
        self.zpt_database.mysql_no_fetch_querry(update_platnosci_querry)

        self.update_dostawca_admin()
        self.sprawdz_biala_lista(self.konto_entry.get())
        self.update_faktury_towar_treeview()
        lista_dostawcow = self.update_lista_dostawcow()
        self.dostawcy_filtr_combobox['values'] = lista_dostawcow
        self.dostawcy_filtr_combobox.set(nazwa_dostawcy)
        self.update_wybrane_dosatwca_faktury_treeview(event='')
        self.popraw_dostawca_button.place_forget()
        self.edytuj_dostawca_button.place(relx=0.54, rely=0.78, relwidth=0.23)

    def ustaw_stan_button_admin_dostawcy(self):
        dostawca = self.dostawcy_filtr_combobox.get()
        if dostawca == '':
            self.dodaj_dostawca_button.config(state='normal')
            self.usun_dostawca_button.config(state='disabled')
            self.edytuj_dostawca_button.config(state='disabled')
            self.dioda_biala_lista.config(background='grey')
        else:
            self.aktualna_nazwa = self.nazwa_dostawca_entry.get()
            print(self.aktualna_nazwa)
            self.dodaj_dostawca_button.config(state='disabled')
            self.edytuj_dostawca_button.config(state='normal')
            self.usun_dostawca_button.config(state='normal')
            if self.konto_entry.get() == 'BRAK':
                self.dioda_biala_lista.config(background='grey')
                self.zaplac_button.config(state='disabled')
                self.przelew_button.config(state='disabled')
                self.dane_kontrahent_konto_nip_label.config(text='')
            else:
                self.sprawdz_biala_lista(self.konto_entry.get())

    def sprawdz_biala_lista(self, konto):
        data_param = datetime.date.today()
        konto_26 = konto.replace(' ', '')
        dane = requests.get(f'https://wl-api.mf.gov.pl/api/search/bank-account/{konto_26}?date={data_param}')
        dane = dane.json()
        self.biala_lista_dane_do_zapisu = {}

        if 'code' in dane:
            self.dioda_biala_lista.config(background='red')
            return False

        elif 'result' in dane and dane['result']['subjects'] != []:
            self.dioda_biala_lista.config(background='green')
            self.dane_kontrahent_konto_nip_label.config(text=f"'{dane['result']['subjects'][0]['name']}' \t"
                                                             f"NIP: {dane['result']['subjects'][0]['nip']}",
                                                        fg='green')
            self.zaplac_button.config(state='normal')
            self.przelew_button.config(state='normal')
            self.biala_lista_dane_do_zapisu.update({'czas': dane['result']['requestDateTime']})
            self.biala_lista_dane_do_zapisu.update({'nazwa': dane['result']['subjects'][0]['name'].replace('"', '')})
            self.biala_lista_dane_do_zapisu.update({'konto': dane['result']['subjects'][0]['accountNumbers']})
            self.biala_lista_dane_do_zapisu.update({'nip': dane['result']['subjects'][0]['nip']})
            self.biala_lista_dane_do_zapisu.update({'status': dane['result']['subjects'][0]['statusVat']})
            self.biala_lista_dane_do_zapisu.update({'kod_potwierdzenia': dane['result']['requestId']})
            print(dane['result']['subjects'][0]['nip'])
            return self.biala_lista_dane_do_zapisu

    def poprawa_wpisu_faktura_towar(self, event):
        self.item = self.faktury_wybrany_dostawca_treeview.selection()
        apteka = self.faktury_wybrany_dostawca_treeview.item(self.item, 'values')[0]
        faktura = self.faktury_wybrany_dostawca_treeview.item(self.item, 'values')[1]
        data_zakupu = self.faktury_wybrany_dostawca_treeview.item(self.item, 'values')[2]
        termin = self.faktury_wybrany_dostawca_treeview.item(self.item, 'values')[3]
        kwota = self.faktury_wybrany_dostawca_treeview.item(self.item, 'values')[4]
        zaplata = self.faktury_wybrany_dostawca_treeview.item(self.item, 'values')[5]

        self.popraw_faktura_towar_toplevel = tk.Toplevel(self.wybrane_towar_R_2f, background='#383232',
                                                         highlightthickness=2)
        self.popraw_faktura_towar_toplevel.grab_set()
        self.popraw_faktura_towar_toplevel.geometry(f'500x200+800+600')

        apteka_label = tk.Label(self.popraw_faktura_towar_toplevel, text=f'APTEKA',
                                foreground='white', background='#383232', anchor='w')
        apteka_label.place(relx=0.03, rely=0.05, relwidth=0.22)
        faktura_label = tk.Label(self.popraw_faktura_towar_toplevel, text=f'FAKTURA',
                                 foreground='white', background='#383232', anchor='w')
        faktura_label.place(relx=0.03, rely=0.18, relwidth=0.22)
        data_zakupu_label = tk.Label(self.popraw_faktura_towar_toplevel, text=f'DATA ZAKUPU',
                                     foreground='white', background='#383232', anchor='w')
        data_zakupu_label.place(relx=0.03, rely=0.31, relwidth=0.22)
        termin_label = tk.Label(self.popraw_faktura_towar_toplevel, text=f'TERMIN',
                                foreground='white', background='#383232', anchor='w')
        termin_label.place(relx=0.03, rely=0.44, relwidth=0.22)
        kwota_label = tk.Label(self.popraw_faktura_towar_toplevel, text=f'KWOTA',
                               foreground='white', background='#383232', anchor='w')
        kwota_label.place(relx=0.03, rely=0.57, relwidth=0.22)
        zaplata_label = tk.Label(self.popraw_faktura_towar_toplevel, text=f'DATA ZAPŁATY',
                                 foreground='white', background='#383232', anchor='w')
        zaplata_label.place(relx=0.03, rely=0.70, relwidth=0.22)

        self.poprawa_apteka_ft_entry = tk.Entry(self.popraw_faktura_towar_toplevel, justify='center',
                                                bg='#6b685f', fg='white')
        self.poprawa_apteka_ft_entry.insert(0, apteka)
        self.poprawa_apteka_ft_entry.place(relx=0.25, rely=0.05, relwidth=0.72)
        self.poprawa_faktura_ft_entry = tk.Entry(self.popraw_faktura_towar_toplevel, justify='center',
                                                 bg='#6b685f', fg='white')
        self.poprawa_faktura_ft_entry.insert(0, faktura)
        self.poprawa_faktura_ft_entry.place(relx=0.25, rely=0.18, relwidth=0.72)
        self.poprawa_data_zakupu_ft_entry = tk.Entry(self.popraw_faktura_towar_toplevel, justify='center',
                                                     bg='#6b685f', fg='white')
        self.poprawa_data_zakupu_ft_entry.insert(0, data_zakupu)
        self.poprawa_data_zakupu_ft_entry.place(relx=0.25, rely=0.31, relwidth=0.72)
        self.poprawa_termin_ft_entry = tk.Entry(self.popraw_faktura_towar_toplevel, justify='center',
                                                bg='#6b685f', fg='white')
        self.poprawa_termin_ft_entry.insert(0, termin)
        self.poprawa_termin_ft_entry.place(relx=0.25, rely=0.44, relwidth=0.72)
        self.poprawa_kwota_ft_entry = tk.Entry(self.popraw_faktura_towar_toplevel, justify='center',
                                               bg='#6b685f', fg='white')
        self.poprawa_kwota_ft_entry.insert(0, kwota[:-3])
        self.poprawa_kwota_ft_entry.place(relx=0.25, rely=0.57, relwidth=0.72)
        self.poprawa_zaplata_ft_entry = tk.Entry(self.popraw_faktura_towar_toplevel, justify='center',
                                                 bg='#6b685f', fg='white')
        self.poprawa_zaplata_ft_entry.insert(0, zaplata)
        self.poprawa_zaplata_ft_entry.place(relx=0.25, rely=0.70, relwidth=0.72)

        self.gotowka_button = tk.Button(self.popraw_faktura_towar_toplevel, text='GOTÓWKA', bg='#544949',
                                        fg=f'{self.kolor_razem}', command=self.popraw_wpis_faktura_towar_gotowka)
        self.gotowka_button.place(relx=0.03, rely=0.84, relwidth=0.3)
        self.gotowka_button = tk.Button(self.popraw_faktura_towar_toplevel, text='NIEZAPŁACONE', bg='#544949',
                                        fg=f'{self.kolor_razem}', command=self.popraw_wpis_faktura_niezaplaone)
        self.gotowka_button.place(relx=0.35, rely=0.84, relwidth=0.3)
        self.popraw_wpis_button = tk.Button(self.popraw_faktura_towar_toplevel, text='POPRAW', bg='#544949',
                                            fg=f'{self.kolor_razem}',
                                            command=lambda: self.popraw_wpis_faktura_towar(faktura))
        self.popraw_wpis_button.place(relx=0.67, rely=0.84, relwidth=0.3)

    def popraw_wpis_faktura_niezaplaone(self):
        update_niezaplacone_querry = f'UPDATE platnosci_towar SET zaplacone = 0, data_zaplaty = "" WHERE ' \
                                     f'apteka = {self.poprawa_apteka_ft_entry.get()} AND ' \
                                     f'nrfv = "{self.poprawa_faktura_ft_entry.get()}"'
        self.zpt_database.mysql_no_fetch_querry(update_niezaplacone_querry)
        self.popraw_faktura_towar_toplevel.destroy()
        self.update_wybrane_dosatwca_faktury_treeview(self.dostawcy_filtr_combobox.get())
        self.update_faktury_towar_treeview()

    def popraw_wpis_faktura_towar(self, faktura):
        update_faktury_querry = f'UPDATE platnosci_towar SET apteka = {self.poprawa_apteka_ft_entry.get()}, ' \
                                f'nrfv = "{self.poprawa_faktura_ft_entry.get()}", ' \
                                f'data_zak = "{self.poprawa_data_zakupu_ft_entry.get()}", ' \
                                f'data_platnosci = "{self.poprawa_termin_ft_entry.get()}", ' \
                                f'kwota = {self.poprawa_kwota_ft_entry.get()}, ' \
                                f'data_zaplaty = "{self.poprawa_zaplata_ft_entry.get()}" WHERE ' \
                                f'platnosci_towar.nrfv = "{faktura}"'
        self.zpt_database.mysql_no_fetch_querry(update_faktury_querry)
        self.popraw_faktura_towar_toplevel.destroy()
        self.update_wybrane_dosatwca_faktury_treeview(self.dostawcy_filtr_combobox.get())
        self.update_faktury_towar_treeview()

    def popraw_wpis_faktura_towar_gotowka(self):
        update_gotowka_querry = f'UPDATE platnosci_towar SET zaplacone = 2 WHERE ' \
                                f'apteka = {self.poprawa_apteka_ft_entry.get()} AND ' \
                                f'nrfv = "{self.poprawa_faktura_ft_entry.get()}"'
        self.zpt_database.mysql_no_fetch_querry(update_gotowka_querry)
        self.popraw_faktura_towar_toplevel.destroy()
        self.update_wybrane_dosatwca_faktury_treeview(self.dostawcy_filtr_combobox.get())
        self.update_faktury_towar_treeview()

    def dodaj_do_listy_przelewow(self):
        kontrahent = f'"{self.controller.przelewy_frame.podziel_tytul(self.nazwa_dostawca_entry.get())}"'
        nr_konta = f'"{self.konto_entry.get().replace(" ", "")}"'
        kwota = self.suma_przelewu_kwota_label.cget('text')[:-3]
        data = str(datetime.datetime.now().date())
        tytul = f'(T) {self.tytul_przelewu_entry.get()}'

        self.controller.przelewy_frame.dodaj_do_listy_przelewow(kontrahent, nr_konta, kwota, data, tytul)

    def create_gotowki_toplevel(self):
        self.gotowki_toplevel = tk.Toplevel(self.towar_LF, background='#383232',
                                            highlightthickness=2)
        self.gotowki_toplevel.grab_set()
        self.gotowki_toplevel.geometry(f'700x700+900+100')

        self.create_gotowki_toplevel_treeview()
        self.create_gotowki_toplevel_remotes()
        self.update_gotowki_toplevel_treeview()

    def create_gotowki_toplevel_treeview(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', fieldbackground="#383232", background="#383232", foreground='white')
        style.configure("Treeview.Heading", background="#383232", foreground="white")
        style.map('Treeview.Heading', background=[('disabled', '#383232')])

        def fixed_map(option):  # naprawa buga wersji dla Python 3.7 przy wyświetlaniu koloru linii w treeview
            return [elm for elm in style.map("Treeview", query_opt=option)
                    if elm[:2] != ("!disabled", "!selected")]

        style.map("Treeview", foreground=fixed_map("foreground"),
                  background=fixed_map("background"))

        self.gotowki_treeview_frame = tk.Frame(self.gotowki_toplevel)
        self.gotowki_treeview_frame.configure(bg='#383232', relief='groove', bd=1)
        self.gotowki_treeview_frame.place(relx=0.01, rely=0.01, relwidth=0.98, relheight=0.9)

        self.columns_gotowki_treeview = ('DOSTWACA', 'FAKTURA', 'DATA ZAKUPU', 'KWOTA')
        self.gotowki_treeview = ttk.Treeview(self.gotowki_treeview_frame,
                                             columns=self.columns_gotowki_treeview,
                                             show='headings',
                                             style="Treeview")

        self.gotowki_treeview.heading('DOSTWACA', text='DOSTWACA')
        self.gotowki_treeview.column('DOSTWACA', minwidth=100, stretch='yes', anchor='center')
        self.gotowki_treeview.heading('FAKTURA', text='FAKTURA')
        self.gotowki_treeview.column('FAKTURA', minwidth=100, stretch='yes', anchor='center')
        self.gotowki_treeview.heading('DATA ZAKUPU', text='DATA ZAKUPU')
        self.gotowki_treeview.column('DATA ZAKUPU', width=100, stretch='no', anchor='center')
        self.gotowki_treeview.heading('KWOTA', text='KWOTA')
        self.gotowki_treeview.column('KWOTA', minwidth=100, stretch='yes', anchor='center')

        self.scrolly = ttk.Scrollbar(self.gotowki_treeview, orient='vertical',
                                     command=self.gotowki_treeview.yview)
        self.gotowki_treeview.configure(yscrollcommand=self.scrolly.set)
        map(lambda col: col.configure(yscrollcommand=self.scrolly.set), self.columns_gotowki_treeview)
        self.scrolly.pack(side=tk.RIGHT, fill=tk.Y)
        map(lambda col: col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True), self.columns_gotowki_treeview)
        self.gotowki_treeview.pack(expand='yes', fill='both')

    def create_gotowki_toplevel_remotes(self):
        self.gotowki_data_od = DateEntry(self.gotowki_toplevel, width=12, background='#383232',
                                         foreground='white', borderwidth=2, date_pattern='y-mm-dd',
                                         locale='pl_PL')
        self.gotowki_data_od.place(relx=0.01, rely=0.92, relwidth=0.9 / 4)
        line_label = tk.Label(self.gotowki_toplevel, text='-', foreground='white', background='#383232')
        line_label.place(relx=(0.9 / 4) + 0.01, rely=0.92, relwidth=0.02)
        self.gotowki_data_do = DateEntry(self.gotowki_toplevel, width=12, background='#383232',
                                         foreground='white', borderwidth=2, date_pattern='y-mm-dd',
                                         locale='pl_PL')
        self.gotowki_data_do.place(relx=(0.9 / 4) + 0.03, rely=0.92, relwidth=0.9 / 4)

        self.set_gotowki_data_od()

        self.gotowki_odswiez_button = tk.Button(self.gotowki_toplevel, text='\uD83D\uDDD8',
                                                bg='#544949', fg=f'{self.kolor_razem}',
                                                command=self.update_gotowki_toplevel_treeview)
        self.gotowki_odswiez_button.place(relx=0.68, rely=0.92, relwidth=0.15)
        self.gotowki_eksportuj_button = tk.Button(self.gotowki_toplevel, text='EKSPORTUJ',
                                                  bg='#544949', fg=f'{self.kolor_razem}',
                                                  command=self.eksportuj_gotowki_dane)
        self.gotowki_eksportuj_button.place(relx=0.84, rely=0.92, relwidth=0.15)

    def set_gotowki_data_od(self):
        data = datetime.date.today()
        data = data.replace(day=1)
        self.gotowki_data_od.set_date(data)

    def get_data_gotowki_toplevel_treeview(self):
        data_od = self.gotowki_data_od.get()
        data_do = self.gotowki_data_do.get()

        querry = f'SELECT dost_nazwa, nrfv, data_zak, kwota FROM platnosci_towar WHERE zaplacone = 2 and data_zak BETWEEN' \
                 f'"{data_od}" AND "{data_do}"'
        dane = self.zpt_database.mysql_querry(querry)

        return dane

    def update_gotowki_toplevel_treeview(self):
        dane = self.get_data_gotowki_toplevel_treeview()
        if dane == []:
            messagebox.showerror('INFO', f'BRAK FAKTUR GOTÓWKOWYCH W OKRESIE OD {self.gotowki_data_od.get()}'
                                         f' DO {self.gotowki_data_do.get()}')
        else:
            self.gotowki_treeview.delete(*self.gotowki_treeview.get_children())
            i = 0
            for n in dane:
                i += 1

                if i % 2 == 0:
                    background = 'background_dark'
                else:
                    background = 'background_light'

                self.gotowki_treeview.tag_configure('background_dark', background='#383232')
                self.gotowki_treeview.tag_configure('background_light', background='#262424')

                self.gotowki_treeview.insert('', 'end', values=(n[0], n[1], n[2], n[3]),
                                             tags=background)

    def eksportuj_gotowki_dane(self):
        dane = self.get_data_gotowki_toplevel_treeview()
        df = pd.DataFrame(dane)

        df.columns = ['KONTRAHENT', 'FAKTURA', 'DATA ZAKUPU', 'KWOTA']

        eksport_file = fr'C:\Users\dell\Desktop\faktury_gotowkowe_{self.gotowki_data_od.get()}___' \
                       fr'{self.gotowki_data_do.get()}.csv'
        df.to_csv(eksport_file, index=False)
        # print(df)

class Biala_lista_frame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.configure(bg='#383232')
        self.zpt_database = ZPT_Database.ZPT_base()
        self.kolor_razem = '#b58b14'
        self.create_biala_lista_F()

    def create_biala_lista_F(self):
        self.biala_lista_F = tk.Frame(self)
        self.biala_lista_F.configure(bg='#383232', relief='groove', bd=1)
        self.biala_lista_F.place(relx=0.01, rely=0.02, relwidth=0.98, relheight=0.96)
        self.create_biala_lista_1f()
        self.create_biala_lista_treeview()

    def create_biala_lista_1f(self):
        self.biala_lista_1f = tk.Frame(self.biala_lista_F)
        self.biala_lista_1f.configure(bg='#383232', relief='groove', bd=1)
        self.biala_lista_1f.place(relx=0.02, rely=0.01, relwidth=0.96, relheight=0.06)

        konto_label = tk.Label(self.biala_lista_1f, text='KONTO',
                               foreground='white', background='#383232', anchor='w')
        konto_label.place(relx=0.02, rely=0.3, relwidth=0.05)
        self.konto_entry = tk.Entry(self.biala_lista_1f, justify='center', bg='#6b685f', fg='white')
        self.konto_entry.place(relx=0.07, rely=0.3, relwidth=0.63)
        self.konto_entry.focus()
        self.sprawdz_konto_button = tk.Button(self.biala_lista_1f, text='SPRAWDŹ KONTO',
                                              bg='#544949', command=lambda: self.zapisz_biala_lista(''),
                                              fg=f'{self.kolor_razem}')
        self.sprawdz_konto_button.place(relx=0.73, rely=0.3, relwidth=0.25)
        self.konto_entry.bind('<Return>', self.zapisz_biala_lista)

    def sprawdz_biala_lista(self):
        dane_do_zapisu = {}
        data_param = datetime.date.today()
        konto_26 = self.konto_entry.get().replace(' ', '')
        dane = requests.get(f'https://wl-api.mf.gov.pl/api/search/bank-account/{konto_26}?date={data_param}')
        dane = dane.json()

        if 'code' in dane:
            messagebox.showerror('UWAGA', 'BŁĄD SPRWDZANIA KONTA')
            self.konto_entry.delete(0, 'end')
            self.konto_entry.focus()
            print(dane_do_zapisu)
            return dane_do_zapisu

        elif 'result' in dane and dane['result']['subjects'] != []:
            dane_do_zapisu.update({'czas': dane['result']['requestDateTime']})
            dane_do_zapisu.update({'nazwa': dane['result']['subjects'][0]['name'].replace('"', '')})
            dane_do_zapisu.update({'konto': dane['result']['subjects'][0]['accountNumbers']})
            dane_do_zapisu.update({'nip': dane['result']['subjects'][0]['nip']})
            dane_do_zapisu.update({'status': dane['result']['subjects'][0]['statusVat']})
            dane_do_zapisu.update({'kod_potwierdzenia': dane['result']['requestId']})
            konto = self.konto_entry.get()
            nazwa = dane['result']['subjects'][0]['name'].replace('"', '')
            status = dane['result']['subjects'][0]['statusVat']
            kod_potwierdzenia = dane['result']['requestId']
            self.controller.logger.log(20, f'Sprawdzono konto {konto} na Białej Liście: {nazwa},'
                                           f' status: {status}, '
                                           f'kod potwierdzenia: {kod_potwierdzenia}')
            return dane_do_zapisu

    def zapisz_biala_lista(self, event):
        dane = self.sprawdz_biala_lista()
        konto_26 = self.konto_entry.get().replace(' ', '')
        print(dane)
        if dane != {} and dane != None:
            zapisz_biala_lista_querry = f'INSERT INTO biala_lista VALUES(NULL, "{dane["czas"]}", ' \
                                        f'"{dane["nazwa"]}", "{konto_26}", ' \
                                        f'"{dane["nip"]}", ' \
                                        f'"{dane["status"]}", ' \
                                        f'"{dane["kod_potwierdzenia"]}")'
            self.zpt_database.mysql_no_fetch_querry(zapisz_biala_lista_querry)
            self.konto_entry.delete(0, 'end')
            self.konto_entry.focus()
            self.update_biala_lista_treeview()

        else:
            self.konto_entry.delete(0, 'end')
            self.konto_entry.focus()

    def create_biala_lista_treeview(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', fieldbackground="#383232", background="#383232", foreground='white')
        style.configure("Treeview.Heading", background="#383232", foreground="white")
        style.map('Treeview.Heading', background=[('disabled', '#383232')])

        def fixed_map(option):  # naprawa buga wersji dla Python 3.7 przy wyświetlaniu koloru linii w treeview
            return [elm for elm in style.map("Treeview", query_opt=option)
                    if elm[:2] != ("!disabled", "!selected")]

        style.map("Treeview", foreground=fixed_map("foreground"),
                  background=fixed_map("background"))

        self.biala_lista_2f = tk.Frame(self.biala_lista_F)
        self.biala_lista_2f.configure(bg='#383232', relief='groove', bd=1)
        self.biala_lista_2f.place(relx=0.02, rely=0.08, relwidth=0.96, relheight=0.91)

        self.columns_biala_lista = ('DATA', 'NAZWA', 'NR KONTA', 'NIP', 'STATUS', 'KOD', 'SCROLL')
        self.biala_lista_treeview = ttk.Treeview(self.biala_lista_2f, columns=self.columns_biala_lista,
                                                 show='headings', style="Treeview")
        self.biala_lista_treeview.heading('DATA', text='DATA')
        self.biala_lista_treeview.column('DATA', width=120, stretch='no', anchor='center')
        self.biala_lista_treeview.heading('NAZWA', text='NAZWA')
        self.biala_lista_treeview.column('NAZWA', minwidth=0, stretch='yes', anchor='center')
        self.biala_lista_treeview.heading('NR KONTA', text='NR KONTA')
        self.biala_lista_treeview.column('NR KONTA', width=230, stretch='no', anchor='center')
        self.biala_lista_treeview.heading('NIP', text='NIP')
        self.biala_lista_treeview.column('NIP', width=120, stretch='no', anchor='center')
        self.biala_lista_treeview.heading('STATUS', text='STATUS')
        self.biala_lista_treeview.column('STATUS', width=120, stretch='no', anchor='center')
        self.biala_lista_treeview.heading('KOD', text='KOD POTWIERDZENIA')
        self.biala_lista_treeview.column('KOD', width=200, stretch='no', anchor='center')
        self.biala_lista_treeview.heading("SCROLL", text='')
        self.biala_lista_treeview.column('SCROLL', minwidth=0, width=12, stretch='no')

        self.scrolly = ttk.Scrollbar(self.biala_lista_treeview, orient='vertical',
                                     command=self.biala_lista_treeview.yview)
        self.biala_lista_treeview.configure(yscrollcommand=self.scrolly.set)
        map(lambda col: col.configure(yscrollcommand=self.scrolly.set), self.columns_biala_lista)
        self.scrolly.pack(side=tk.RIGHT, fill=tk.Y)
        map(lambda col: col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True), self.columns_biala_lista)
        self.biala_lista_treeview.pack(expand='yes', fill='both')

    def get_dane_biala_lista(self):
        biala_lista_querry = 'SELECT * FROM biala_lista ORDER BY id desc'
        biala_lista = self.zpt_database.mysql_querry(biala_lista_querry)
        return biala_lista

    def update_biala_lista_treeview(self):
        dane = self.get_dane_biala_lista()
        self.biala_lista_treeview.delete(*self.biala_lista_treeview.get_children())

        i = 0
        for n in dane:
            i += 1

            if i % 2 == 0:
                background = 'background_dark'
            else:
                background = 'background_light'

            self.biala_lista_treeview.tag_configure('background_dark', background='#383232')
            self.biala_lista_treeview.tag_configure('background_light', background='#262424')

            self.biala_lista_treeview.insert('', 'end', values=(n[1], n[2], n[3], n[4], n[5], n[6], ''),
                                             tags=background)

class Hurtownie_frame(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.configure(bg='#383232')
        self.zpt_database = ZPT_Database.ZPT_base()
        self.kolor_razem = '#b58b14'
        self.hurtownie = ['', 'PGF', 'NEUCA', 'HURTAP', 'NOVO', 'FARMACOL', 'ASTRA']
        self.slownik_hurtownie = slowniki.slownik_hurtownie
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)
        self.create_hurtownie_LF()
        self.create_hurtownie_RF()

    def create_hurtownie_LF(self):
        self.hurtownie_LF = tk.Frame(self)
        self.hurtownie_LF.configure(bg='#383232', relief='groove', bd=1)
        self.hurtownie_LF.place(relx=0.01, rely=0.02, relwidth=0.48, relheight=0.96)
        self.create_hurtownie_L_0f()
        self.create_hurtownie_L_1f()
        self.create_hurtownie_L_2f()
        self.create_hurtownia_L_3f()
        self.create_hurtownia_treeview()
        self.create_hurtownie_L_5f()

    def create_hurtownie_L_0f(self):
        self.hurtownie_L_0f = tk.Frame(self.hurtownie_LF)
        self.hurtownie_L_0f.configure(bg='#383232', relief='groove', bd=1)
        self.hurtownie_L_0f.place(relx=0.01, rely=0.01, relwidth=0.98, relheight=0.04)
        pobierz_button = tk.Button(self.hurtownie_L_0f, text='POBIERZ ZESTAWIENIA',
                                   bg='#544949', command=self.pobierz_zestawienia,
                                   fg=f'{self.kolor_razem}')
        pobierz_button.place(relx=0.02, rely=0.17, relwidth=0.47)
        wyslij_button = tk.Button(self.hurtownie_L_0f, text='WYŚLIJ ZESTAWIENIA',
                                  bg='#544949', command=self.wyslij_zestawienia,
                                  fg=f'{self.kolor_razem}')
        wyslij_button.place(relx=0.51, rely=0.17, relwidth=0.47)

    def create_hurtownie_L_1f(self):
        self.hurtownie_L_1f = tk.Frame(self.hurtownie_LF)
        self.hurtownie_L_1f.configure(bg='#383232', relief='groove', bd=1)
        self.hurtownie_L_1f.place(relx=0.01, rely=0.06, relwidth=0.98, relheight=0.04)

        update_novo_button = tk.Button(self.hurtownie_L_1f, text='NOVO',
                                       bg='#544949',
                                       fg=f'{self.kolor_razem}', command=lambda: self.wybierz_plik('NOVO'))
        update_novo_button.place(relx=0.02, rely=0.17, relwidth=0.15)
        update_neuca_button = tk.Button(self.hurtownie_L_1f, text='NEUCA',
                                        bg='#544949',
                                        fg=f'{self.kolor_razem}', command=lambda: self.wybierz_plik('NEUCA'))
        update_neuca_button.place(relx=0.18, rely=0.17, relwidth=0.15)
        update_hurtap_button = tk.Button(self.hurtownie_L_1f, text='HURTAP',
                                         bg='#544949',
                                         fg=f'{self.kolor_razem}', command=lambda: self.wybierz_plik('HURTAP'))
        update_hurtap_button.place(relx=0.34, rely=0.17, relwidth=0.15)
        update_farmacol_button = tk.Button(self.hurtownie_L_1f, text='FARMACOL',
                                           bg='#544949',
                                           fg=f'{self.kolor_razem}', command=lambda: self.wybierz_plik('FARMACOL'))
        update_farmacol_button.place(relx=0.50, rely=0.17, relwidth=0.15)
        update_pgf_button = tk.Button(self.hurtownie_L_1f, text='PGF',
                                      bg='#544949',
                                      fg=f'{self.kolor_razem}', command=lambda: self.wybierz_plik('PGF'))
        update_pgf_button.place(relx=0.66, rely=0.17, relwidth=0.15)
        update_salus_button = tk.Button(self.hurtownie_L_1f, text='ASTRA',
                                        bg='#544949',
                                        fg=f'{self.kolor_razem}', command=lambda: self.wybierz_plik('ASTRA'))
        update_salus_button.place(relx=0.82, rely=0.17, relwidth=0.15)

    def create_hurtownie_L_2f(self):
        self.hurtownie_L_2f = tk.Frame(self.hurtownie_LF)
        self.hurtownie_L_2f.configure(bg='#383232', relief='groove', bd=1)
        self.hurtownie_L_2f.place(relx=0.01, rely=0.11, relwidth=0.98, relheight=0.04)

        self.hurtownia_wybrany_plik_label = tk.Label(self.hurtownie_L_2f, text='',
                                                     foreground='white', background='#383232', anchor='w')
        self.hurtownia_wybrany_plik_label.place(relx=0.03, rely=0.16, relwidth=0.65)

        self.polacz_button = tk.Button(self.hurtownie_L_2f, text='DODAJ DO PLIKU GŁÓWNEGO',
                                       bg='#544949',
                                       fg=f'{self.kolor_razem}', command=self.polacz_pliki)
        self.polacz_button.place(relx=0.69, rely=0.16, relwidth=0.3)
        self.polacz_button.config(state='disabled')

    def create_hurtownia_L_3f(self):
        self.hurtownia_L_3f = tk.Frame(self.hurtownie_LF)
        self.hurtownia_L_3f.configure(bg='#383232', relief='groove', bd=1)
        self.hurtownia_L_3f.place(relx=0.01, rely=0.16, relwidth=0.98, relheight=0.04)

        self.hurtownia_combobx = ttk.Combobox(self.hurtownia_L_3f, values=self.hurtownie, state='readonly')
        self.hurtownia_combobx.place(relx=0.01, rely=0.17, relwidth=0.4)
        self.hurtownia_combobx.current(0)
        self.hurtownia_combobx.bind("<<ComboboxSelected>>", self.update_hurtownie_platnosci_treeview)

        self.zaplac_do_datownik = DateEntry(self.hurtownia_L_3f, width=12, background='#383232',
                                            foreground='white', borderwidth=2, date_pattern='y-mm-dd',
                                            locale='pl_PL')
        self.zaplac_do_datownik.place(relx=0.5, rely=0.12, relwidth=0.35)
        self.zaplac_do_datownik.bind("<<DateEntrySelected>>", self.update_hurtownie_platnosci_treeview)

    def create_hurtownia_treeview(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', fieldbackground="#383232", background="#383232", foreground='white')
        style.configure("Treeview.Heading", background="#383232", foreground="white")
        style.map('Treeview.Heading', background=[('disabled', '#383232')])

        def fixed_map(option):  # naprawa buga wersji dla Python 3.7 przy wyświetlaniu koloru linii w treeview
            return [elm for elm in style.map("Treeview", query_opt=option)
                    if elm[:2] != ("!disabled", "!selected")]

        style.map("Treeview", foreground=fixed_map("foreground"),
                  background=fixed_map("background"))

        self.hurtownia_L_4f = tk.Frame(self.hurtownie_LF)
        self.hurtownia_L_4f.configure(bg='#383232', relief='groove', bd=1)
        self.hurtownia_L_4f.place(relx=0.01, rely=0.21, relwidth=0.98, relheight=0.70)

        self.hurtownie_columns = ('NR DOKUMENTU', 'TERMIN', 'WYSTAWIONA', 'WARTOŚĆ', 'DO ZAPŁATY')
        self.hurtownie_platnosci_treeview = ttk.Treeview(self.hurtownia_L_4f, columns=self.hurtownie_columns,
                                                         show='headings',
                                                         style="Treeview", selectmode="browse")

        self.hurtownie_platnosci_treeview.heading('NR DOKUMENTU', text='NR DOKUMENTU')
        self.hurtownie_platnosci_treeview.column('NR DOKUMENTU', minwidth=200, stretch='yes', anchor='center')
        self.hurtownie_platnosci_treeview.heading('TERMIN', text='TERMIN')
        self.hurtownie_platnosci_treeview.column('TERMIN', width=150, stretch='no', anchor='center')
        self.hurtownie_platnosci_treeview.heading('WYSTAWIONA', text='WYSTAWIONA')
        self.hurtownie_platnosci_treeview.column('WYSTAWIONA', width=150, stretch='no', anchor='center')
        self.hurtownie_platnosci_treeview.heading('WARTOŚĆ', text='WARTOŚĆ')
        self.hurtownie_platnosci_treeview.column('WARTOŚĆ', width=150, stretch='no', anchor='center')
        self.hurtownie_platnosci_treeview.heading('DO ZAPŁATY', text='DO ZAPŁATY')
        self.hurtownie_platnosci_treeview.column('DO ZAPŁATY', width=150, stretch='no', anchor='center')

        self.scrolly = ttk.Scrollbar(self.hurtownie_platnosci_treeview, orient='vertical',
                                     command=self.hurtownie_platnosci_treeview.yview)
        self.hurtownie_platnosci_treeview.configure(yscrollcommand=self.scrolly.set)
        map(lambda col: col.configure(yscrollcommand=self.scrolly.set), self.hurtownie_columns)
        self.scrolly.pack(side=tk.RIGHT, fill=tk.Y)
        map(lambda col: col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True), self.hurtownie_columns)
        self.hurtownie_platnosci_treeview.pack(expand='yes', fill='both')

    def create_hurtownie_L_5f(self):
        self.hurtownie_L_5f = tk.Frame(self.hurtownie_LF)
        self.hurtownie_L_5f.configure(bg='#383232', relief='groove', bd=1)
        self.hurtownie_L_5f.place(relx=0.01, rely=0.92, relwidth=0.98, relheight=0.07)

        self.eksport_button = tk.Button(self.hurtownie_L_5f, text='EKSPORT ZESTAWIENIA',
                                        bg='#544949',
                                        fg=f'{self.kolor_razem}', command=self.eksport_zestawienia)
        self.eksport_button.place(relx=0.05, rely=0.3, relwidth=0.25)
        self.eksport_button.config(state='disabled')

        self.summary_kwota_label = tk.Label(self.hurtownie_L_5f, text='',
                                            foreground='white', background='#383232', anchor='e',
                                            font=("Verdena", "14", "bold"))
        self.summary_kwota_label.place(relx=0.6, rely=0.3, relwidth=0.35)
        self.przelew_button = tk.Button(self.hurtownie_L_5f, text='DODAJ DO PRZELEWOW',
                                        bg='#544949',
                                        fg=f'{self.kolor_razem}', command=self.dodaj_do_listy_przelewow)
        self.przelew_button.place(relx=0.32, rely=0.3, relwidth=0.25)
        self.przelew_button.config(state='disabled')

    def wybierz_plik(self, hurtownia):
        pliki_typ = ("wszystkie pliki", "*.*")

        self.filename = tk.filedialog.askopenfilename(initialdir=r'C:\Users\dell\Desktop', title="Wybierz plik",
                                                      filetypes=(pliki_typ, ("wszystkie pliki", "*.*")))
        self.hurtownia_wybrany_plik_label.config(text=f'WYBRANO: {hurtownia} \t\t {self.filename}')
        self.polacz_button.config(state='normal')
        self.hurtownia_combobx.current(f'{self.hurtownie.index(hurtownia)}')
        self.update_hurtownie_platnosci_treeview('')
        return self.filename

    def update_hurtownie_platnosci_treeview(self, event):
        hurtownia = self.hurtownia_combobx.get()
        self.data_zaplac_do = self.zaplac_do_datownik.get()
        self.suma_do_zaplaty = 0.00
        self.faktury_niezaplacone = ''

        if self.data_zaplac_do == str(datetime.date.today()):
            self.data_zaplac_do = str(datetime.datetime.strptime(self.data_zaplac_do, '%Y-%m-%d') +
                                      datetime.timedelta(days=365))[:10]

        if hurtownia != '':
            faktury_niezaplacone_lista = self.update_hurtownie_platnosci_treeview_dane()

            self.hurtownie_platnosci_treeview.delete(*self.hurtownie_platnosci_treeview.get_children())
            i = 0
            for n in faktury_niezaplacone_lista:
                i += 1
                nr_faktury = n[1]
                termin = str(n[2])[0:10]
                przyjecie = str(n[3])[0:10]
                wartosc = f'{n[4]:.2f}'
                do_zaplaty = f'{n[5]:.2f}'

                if i % 2 == 0:
                    background_gotowki = 'background_dark'
                else:
                    background_gotowki = 'background_light'

                self.hurtownie_platnosci_treeview.tag_configure('background_dark', background='#383232')
                self.hurtownie_platnosci_treeview.tag_configure('background_light', background='#262424')

                self.hurtownie_platnosci_treeview.insert('', 'end', values=(nr_faktury, termin, przyjecie, wartosc,
                                                                            do_zaplaty),
                                                         tags=(background_gotowki))
            self.eksport_button.config(state='normal')
            self.przelew_button.config(state='normal')

        else:
            self.hurtownie_platnosci_treeview.delete(*self.hurtownie_platnosci_treeview.get_children())
            self.eksport_button.config(state='disabled')
            self.przelew_button.config(state='disabled')
            self.summary_kwota_label.config(text='')

    def update_hurtownie_platnosci_treeview_dane(self):
        hurtownia = self.hurtownia_combobx.get()
        if hurtownia in slowniki.hurtownie_foldery.keys():
            plik_glowny = open(slowniki.hurtownie_foldery[f'{hurtownia}'], 'rb')
        else:
            self.hurtownie_platnosci_treeview.delete(*self.hurtownie_platnosci_treeview.get_children())
            self.eksport_button.config(state='disabled')
            self.przelew_button.config(state='disabled')
            self.summary_kwota_label.config(text='')
            return []

        dane_glowne = pd.read_excel(plik_glowny)
        niezaplacone_filtr = dane_glowne[(dane_glowne['Data płatności'] <= f'{self.data_zaplac_do}') &
                                         (dane_glowne['Data zapłaty'].isnull() == True)].index
        self.faktury_niezaplacone = dane_glowne.loc[niezaplacone_filtr]
        self.faktury_niezaplacone.sort_values(by=['Data płatności'], inplace=True, ascending=True)
        self.suma_do_zaplaty = f"{self.faktury_niezaplacone['Do zapłaty'].sum():.2f}"
        self.summary_kwota_label.config(text=f'RAZEM: {self.suma_do_zaplaty} zł')
        faktury_niezaplacone_lista = self.faktury_niezaplacone.values.tolist()
        return faktury_niezaplacone_lista

    def eksport_zestawienia(self):
        nazwa_hurtowni = self.hurtownia_combobx.get()
        data_generacji = str(datetime.date.today()).replace('-', '')
        if nazwa_hurtowni == "NEUCA":
            nazwa_pliku = f'129551_NEUCA_{data_generacji}_{self.suma_do_zaplaty}'
        else:
            nazwa_pliku = f'5472110371_{nazwa_hurtowni}_{data_generacji}_{self.suma_do_zaplaty}'

        dane_do_html = self.faktury_niezaplacone.drop(columns=['Data zapłaty']).to_html(index=False)
        dane_do_html = dane_do_html.replace('<table border="1" class="dataframe">',
                                            '<table border="1" cellspacing="0" cellpadding="4" style="text-align: center; width:100%;">')

        dane_do_html = dane_do_html.replace('</table>', '')
        dane_do_html = dane_do_html.replace('</tbody>', '')
        dane_do_html = dane_do_html.replace('<thead>', '')
        dane_do_html = dane_do_html.replace('</thead>', '')
        dane_do_html = dane_do_html.replace('<tbody>', '')
        dane_do_html = dane_do_html.replace('</tbody>', '')
        dane_do_html = dane_do_html.replace('<tr>', '<tr class="keeptogether">')
        dane_do_html = dane_do_html.replace('<tr style="text-align: right;">', '<tr style="text-align: center;">')

        text_start = '''<!DOCTYPE html>
        <html>
        <head>
        <title></title>
        <meta charset="utf-8">
        <style type="text/css"><!--
            .keeptogether {page-break-inside:avoid;}
        --></style>
        </head>'''

        text_zamkniecie = f'<tr>' \
                          f'<td colspan="4">RAZEM &emsp;&emsp;&emsp;</td>' \
                          f'<td colspan="2">{self.suma_do_zaplaty} zł</td>' \
                          f'</tr></tbody></table></body></html>'

        text_dane_firmy = f'ZESTAWIENIE DO PŁATNOŚCI - {nazwa_pliku} </br>' \
                          f'MARIA-PHARM Sp. z o.o.</br>' \
                          f'ul. Hallera 13, 43-200 Pszczyna </br>' \
                          f'NIP: 5472110371</br></br>'

        # konwertowanie pliku do PDF
        config = pdfkit.configuration(wkhtmltopdf='c:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')
        pdf_path = rf'C:\Users\dell\Desktop\{nazwa_pliku}.pdf'
        pdfkit.from_string(text_start + text_dane_firmy + dane_do_html + text_zamkniecie, pdf_path,
                           configuration=config)

        self.oznacz_zaplacone()
        self.hurtownia_right_combobx.set(self.hurtownia_combobx.get())
        self.zaplac_do_datownik.set_date(datetime.datetime.now().date())
        self.update_zestawienia_platnosci_treeview(event=None)
        self.update_hurtownie_platnosci_treeview_dane()
        self.update_zestawienia_platnosci_treeview(event=None)
        self.info_brakujace_faktury(self.faktury_niezaplacone)

    def sprawdz_wprowadzenie_fv_eksportowanych(self, zestawienie):
        faktury_zestawienie = zestawienie['Nr dokumentu'].astype(str).values.tolist()
        lista_zakupow_apteki = self.get_lista_faktur_wszystkie_apteki()
        lista_brakow = []
        for faktura in faktury_zestawienie:
            if faktura not in lista_zakupow_apteki:
                lista_brakow.append(faktura)
        print(lista_brakow)
        return lista_brakow

    def info_brakujace_faktury(self, zestawienie):
        braki_lista = self.sprawdz_wprowadzenie_fv_eksportowanych(zestawienie)
        if braki_lista == []:
            messagebox.showinfo('WSZYSKO OK', 'Wszystkie faktury są wprowadzone w aptekach')
        else:
            text = ''
            for f in braki_lista:
                text += f'{f}, '
            messagebox.showerror('BŁĄD', f'BRAKUJE FAKTUR: {text}')

    def get_faktury_zakupy_dane(self, apteka):
        querry_text = f'SELECT nrfv from zakupy_0{apteka} WHERE dat_zak_fv >= DATE_SUB(NOW(), INTERVAL 6 MONTH)'
        dane = self.zpt_database.mysql_querry(querry_text)
        return dane

    def get_lista_faktur_wszystkie_apteki(self):
        lista_wszystkich_faktur = []
        for apteka in range(2, 9):
            dane = self.get_faktury_zakupy_dane(apteka)
            for m in dane:
                lista_wszystkich_faktur.append(m[0])
        return lista_wszystkich_faktur

    def oznacz_zaplacone(self):
        hurtownia = self.hurtownia_combobx.get()
        if hurtownia in slowniki.hurtownie_foldery.keys():
            plik_path = slowniki.hurtownie_foldery[f'{hurtownia}']
        else:
            return False

        plik_glowny = open(plik_path, 'rb')
        dane_glowne = pd.read_excel(plik_glowny)
        data_zaplacone_do = self.zaplac_do_datownik.get()
        zaplac_do_filtr = dane_glowne[
            (dane_glowne['Data płatności'] <= f'{data_zaplacone_do}') & (
                        dane_glowne['Data zapłaty'].isnull() == True)].index
        dane_glowne.loc[zaplac_do_filtr, 'Data zapłaty'] = str(datetime.date.today())
        dane_glowne.sort_values(by=['Data płatności'], inplace=True, ascending=True)
        dane_glowne.to_excel(plik_path, index=False)
        self.update_hurtownie_platnosci_treeview('')

    def polacz_pliki(self):
        hurtownia = self.hurtownia_combobx.get()
        if hurtownia == 'NOVO':
            self.polacz_plik_novo()
        if hurtownia == 'NEUCA':
            self.polacz_plik_neuca()
        if hurtownia == 'HURTAP':
            self.polacz_plik_hurtap()
        if hurtownia == 'FARMACOL':
            self.polacz_plik_farmacol()
        if hurtownia == 'PGF':
            self.polacz_plik_pgf()
        if hurtownia == 'ASTRA':
            self.polacz_plik_astra()
        else:
            pass

        self.filename = ''
        self.polacz_button.config(state='disabled')
        self.hurtownia_wybrany_plik_label.config(text='')
        self.update_hurtownie_platnosci_treeview('')

    def polacz_plik_novo(self):
        nowe_dane = pd.read_excel(self.filename)
        nowe_dane.drop(['Skrót nazwy', 'Spóźn.', 'Data sprzedaży', 'Okres pł.', 'Zaliczka', 'Waluta'],
                       axis=1, inplace=True)
        puste_linie_filtr = nowe_dane[nowe_dane['Nr dokumentu'].isnull() != False].index
        nowe_dane.drop(puste_linie_filtr, inplace=True)
        plik_glowny = open(r'C:\Users\dell\Dysk Google\ZPT_DATA\5472110371_NOVO.xlsx', 'rb')
        dane_glowne = pd.read_excel(plik_glowny)
        filtr_pusta_data_zaplaty = dane_glowne[dane_glowne['Data zapłaty'].isnull() == True].index
        dane_glowne.drop(filtr_pusta_data_zaplaty, inplace=True)
        dane_polaczone = pd.concat([dane_glowne, nowe_dane]).reset_index(drop=True)
        dane_polaczone = dane_polaczone.sort_values('Data zapłaty', ascending=False)
        dane_polaczone = dane_polaczone.drop_duplicates(subset='Nr dokumentu', keep='first')
        dane_polaczone = dane_polaczone.sort_values('Data płatności', ascending=True)
        dane_polaczone.to_excel(r'C:\Users\dell\Dysk Google\ZPT_DATA\5472110371_NOVO.xlsx', index=False)

    def polacz_plik_neuca(self):
        nowe_dane = pd.read_excel(self.filename, skiprows=26, header=1)
        nowe_dane.drop(['Apteka', 'Indywidualny numer zamówienia', 'Typ', 'Po terminie', 'Data rozliczenia',
                        'Przedstawicielstwo'], axis=1, inplace=True)
        nowe_dane = nowe_dane[['Kod kontrahenta', 'Numer dokumentu', 'Termin zapłaty', 'Data wystawienia',
                               'Wartość brutto', 'Do zapłaty']]
        nowe_dane['Data zapłaty'] = ''
        nowe_dane.rename(columns={'Kod kontrahenta': 'Nr kontr.',
                                  'Numer dokumentu': 'Nr dokumentu',
                                  'Termin zapłaty': 'Data płatności',
                                  'Data wystawienia': 'Data wystawienia',
                                  'Wartość brutto': 'Wartość brutto',
                                  'Do zapłaty': 'Do zapłaty',
                                  }, inplace=True)
        nowe_dane['Data wystawienia'].dt.strftime('%Y-%m-%d')
        nowe_dane['Data płatności'].dt.strftime('%Y-%m-%d')
        plik_glowny = open(r'C:\Users\dell\Dysk Google\ZPT_DATA\5472110371_NEUCA.xlsx', 'rb')
        dane_glowne = pd.read_excel(plik_glowny)
        filtr_pusta_data_zaplaty = dane_glowne[dane_glowne['Data zapłaty'].isnull() == True].index
        dane_glowne.drop(filtr_pusta_data_zaplaty, inplace=True)
        dane_polaczone = pd.concat([dane_glowne, nowe_dane]).reset_index(drop=True)
        dane_polaczone = dane_polaczone.sort_values('Data zapłaty', ascending=False)
        dane_polaczone = dane_polaczone.drop_duplicates(subset='Nr dokumentu', keep='first')
        dane_polaczone = dane_polaczone.sort_values('Data płatności', ascending=True)
        dane_polaczone.to_excel(r'C:\Users\dell\Dysk Google\ZPT_DATA\5472110371_NEUCA.xlsx', index=False)

    def polacz_plik_hurtap(self):
        plik_glowny = open(self.filename, 'r')
        dane_z_pliku = []
        df = read_ods(self.filename, 'Sheet1')
        dane = df.values.tolist()
        for d in dane:
            dane_z_pliku.append([str(d[7])[:-2], d[1], str(d[3]), str(d[2]), d[6], d[6], ''])

        nowe_dane = pd.DataFrame(dane_z_pliku,
                                 columns=['Nr kontr.', 'Nr dokumentu', 'Data płatności', 'Data wystawienia',
                                          'Wartość brutto', 'Do zapłaty', 'Data zapłaty'])

        plik_glowny = open(r'C:\Users\dell\Dysk Google\ZPT_DATA\5472110371_HURTAP.xlsx', 'rb')
        dane_glowne = pd.read_excel(plik_glowny)
        filtr_pusta_data_zaplaty = dane_glowne[dane_glowne['Data zapłaty'].isnull() == True].index
        dane_glowne.drop(filtr_pusta_data_zaplaty, inplace=True)
        dane_polaczone = pd.concat([dane_glowne, nowe_dane]).reset_index(drop=True)
        dane_polaczone = dane_polaczone.sort_values('Data zapłaty', ascending=False)
        dane_polaczone = dane_polaczone.drop_duplicates(subset='Nr dokumentu', keep='first')
        dane_polaczone = dane_polaczone.sort_values('Data płatności', ascending=True)
        dane_polaczone.to_excel(r'C:\Users\dell\Dysk Google\ZPT_DATA\5472110371_HURTAP.xlsx', index=False)

    def polacz_plik_farmacol(self):
        plik_glowny = open(self.filename, 'rb')
        nowe_dane = read_pdf(plik_glowny, pages='all')
        dane = str(nowe_dane[0]).split('\n')
        dane_koncowe = []
        dz = ''
        for d in dane:
            if 'GT' in d or 'GM' in d:
                faktura = ['39505']
                for f in d.split(' '):
                    if len(f) > 1:
                        if f.endswith('-'):
                            f = f'-{f[:-1]}'
                        faktura.append(f)
                        dz = f
                faktura.append(dz)
                faktura.append('')
                dane_koncowe.append(faktura)

        nowa_lista = []
        for d in dane_koncowe:
            data_1 = d[3][6:] + '-' + d[3][3:5] + '-' + d[3][0:2]
            data_2 = d[2][6:] + '-' + d[2][3:5] + '-' + d[2][0:2]
            kwota = float(d[4].replace('.', '').replace(',', '.'))
            nowa_lista.append([d[0], d[1], data_1, data_2, kwota, kwota, ''])
        nowe_dane_ = pd.DataFrame(nowa_lista,
                                  columns=['Nr kontr.', 'Nr dokumentu', 'Data płatności', 'Data wystawienia',
                                           'Wartość brutto', 'Do zapłaty', 'Data zapłaty'])
        plik_glowny = open(r'C:\Users\dell\Dysk Google\ZPT_DATA\5472110371_FARMACOL.xlsx', 'rb')
        dane_glowne = pd.read_excel(plik_glowny)
        filtr_pusta_data_zaplaty = dane_glowne[dane_glowne['Data zapłaty'].isnull() == True].index
        dane_glowne.drop(filtr_pusta_data_zaplaty, inplace=True)
        dane_polaczone = pd.concat([dane_glowne, nowe_dane_]).reset_index(drop=True)
        dane_polaczone = dane_polaczone.sort_values('Data zapłaty', ascending=False)
        dane_polaczone = dane_polaczone.drop_duplicates(subset='Nr dokumentu', keep='first')
        dane_polaczone = dane_polaczone.sort_values('Data płatności', ascending=True)
        dane_polaczone.to_excel(r'C:\Users\dell\Dysk Google\ZPT_DATA\5472110371_FARMACOL.xlsx', index=False)

    def polacz_plik_pgf(self):
        df = pd.read_excel(self.filename, skiprows=10, skipfooter=5)

        dane_z_pliku = []

        dane = df.values.tolist()
        for d in dane:
            dane_z_pliku.append(['33114', d[0], d[2], d[1], d[3], d[5], ''])

        nowe_dane = pd.DataFrame(dane_z_pliku,
                                 columns=['Nr kontr.', 'Nr dokumentu', 'Data płatności', 'Data wystawienia',
                                          'Wartość brutto', 'Do zapłaty', 'Data zapłaty'])
        plik_glowny = open(r'C:\Users\dell\Dysk Google\ZPT_DATA\5472110371_PGF.xlsx', 'rb')
        dane_glowne = pd.read_excel(plik_glowny)
        filtr_pusta_data_zaplaty = dane_glowne[dane_glowne['Data zapłaty'].isnull() == True].index
        dane_glowne.drop(filtr_pusta_data_zaplaty, inplace=True)
        dane_polaczone = pd.concat([dane_glowne, nowe_dane]).reset_index(drop=True)
        dane_polaczone = dane_polaczone.sort_values('Data zapłaty', ascending=False)
        # dane_polaczone = dane_polaczone.drop_duplicates(subset='Nr dokumentu', keep='first')
        dane_polaczone = dane_polaczone.sort_values('Data płatności', ascending=True)
        dane_polaczone.to_excel(r'C:\Users\dell\Dysk Google\ZPT_DATA\5472110371_PGF.xlsx', index=False)

    def polacz_plik_astra(self):
        df = pd.read_excel(self.filename, skiprows=6)
        dane_z_pliku = []

        dane = df.values.tolist()
        for d in dane:
            # dane_z_pliku.append(['33114', d[0], d[2], d[1], d[3], d[5], ''])
            print(d)
            data_zaplaty = f'{str(d[4])[6:10]}-{str(d[4])[3:5]}-{str(d[4])[0:2]}'
            data_faktury = f'{str(d[3])[6:10]}-{str(d[3])[3:5]}-{str(d[3])[0:2]}'
            dane_z_pliku.append(['', str(d[1]), str(d[4]), str(d[3]), d[6], d[6], ''])

        nowe_dane = pd.DataFrame(dane_z_pliku,
                                 columns=['Nr kontr.', 'Nr dokumentu', 'Data płatności', 'Data wystawienia',
                                          'Wartość brutto', 'Do zapłaty', 'Data zapłaty'])
        plik_glowny = open(r'C:\Users\dell\Dysk Google\ZPT_DATA\5472110371_ASTRA.xlsx', 'rb')
        dane_glowne = pd.read_excel(plik_glowny)
        filtr_pusta_data_zaplaty = dane_glowne[dane_glowne['Data zapłaty'].isnull() == True].index
        dane_glowne.drop(filtr_pusta_data_zaplaty, inplace=True)
        dane_polaczone = pd.concat([dane_glowne, nowe_dane]).reset_index(drop=True)
        dane_polaczone = dane_polaczone.sort_values('Data zapłaty', ascending=False)
        # dane_polaczone = dane_polaczone.drop_duplicates(subset='Nr dokumentu', keep='first')
        dane_polaczone = dane_polaczone.sort_values('Data płatności', ascending=True)
        dane_polaczone.to_excel(r'C:\Users\dell\Dysk Google\ZPT_DATA\5472110371_ASTRA.xlsx', index=False)

    def create_hurtownie_RF(self):
        self.hurtownie_RF = tk.Frame(self)
        self.hurtownie_RF.configure(bg='#383232', relief='groove', bd=1)
        self.hurtownie_RF.place(relx=0.51, rely=0.02, relwidth=0.48, relheight=0.96)
        self.create_hurtownie_R_1f()
        self.create_zestawienia_platnosci_treeview()
        self.create_szczegoly_zestawienia_treeview()

    def create_hurtownie_R_1f(self):
        self.hurtownie_R_1f = tk.Frame(self.hurtownie_RF)
        self.hurtownie_R_1f.configure(bg='#383232', relief='groove', bd=1)
        self.hurtownie_R_1f.place(relx=0.01, rely=0.01, relwidth=0.98, relheight=0.04)

        self.hurtownia_right_combobx = ttk.Combobox(self.hurtownie_R_1f, values=self.hurtownie, state='readonly')
        self.hurtownia_right_combobx.place(relx=0.01, rely=0.17, relwidth=0.4)
        self.hurtownia_right_combobx.current(0)
        self.hurtownia_right_combobx.bind("<<ComboboxSelected>>", self.update_zestawienia_platnosci_treeview)

    def definiuj_plik_glowny(self):
        hurtownia = self.hurtownia_right_combobx.get()
        if hurtownia in slowniki.hurtownie_foldery.keys():
            plik_glowny = slowniki.hurtownie_foldery[f'{hurtownia}']
        else:
            return ''
        return plik_glowny

    def get_dane_zestawienia_platnosci(self):
        plik_glowny = self.definiuj_plik_glowny()
        if plik_glowny == '':
            return []
        dane_plik = pd.read_excel(plik_glowny)
        unique_dates = dane_plik['Data zapłaty'].unique().tolist()

        lista_platnosci = []
        for u_date in unique_dates:
            if u_date != '-' and str(u_date) != 'nan':
                data_filtr = dane_plik[dane_plik['Data zapłaty'] == u_date].index
                suma = dane_plik.loc[data_filtr, 'Do zapłaty'].sum()
                lista_platnosci.append([u_date, suma])
                lista_platnosci.sort(key=lambda x: x[0], reverse=True)
        return lista_platnosci

    def create_zestawienia_platnosci_treeview(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', fieldbackground="#383232", background="#383232", foreground='white')
        style.configure("Treeview.Heading", background="#383232", foreground="white")
        style.map('Treeview.Heading', background=[('disabled', '#383232')])

        def fixed_map(option):  # naprawa buga wersji dla Python 3.7 przy wyświetlaniu koloru linii w treeview
            return [elm for elm in style.map("Treeview", query_opt=option)
                    if elm[:2] != ("!disabled", "!selected")]

        style.map("Treeview", foreground=fixed_map("foreground"),
                  background=fixed_map("background"))

        self.hurtownie_R_2f = tk.Frame(self.hurtownie_RF)
        self.hurtownie_R_2f.configure(bg='#383232', relief='groove', bd=1)
        self.hurtownie_R_2f.place(relx=0.01, rely=0.06, relwidth=0.98, relheight=0.3)

        columns = ('DATA', 'KWOTA')
        self.zestawienia_platnosci_treeview = ttk.Treeview(self.hurtownie_R_2f,
                                                           columns=columns,
                                                           show='headings',
                                                           style="Treeview", selectmode="browse")

        self.zestawienia_platnosci_treeview.heading('DATA', text='DATA')
        self.zestawienia_platnosci_treeview.column('DATA', minwidth=200, stretch='yes', anchor='center')
        self.zestawienia_platnosci_treeview.heading('KWOTA', text='KWOTA')
        self.zestawienia_platnosci_treeview.column('KWOTA', minwidth=150, stretch='yes', anchor='center')

        self.scrolly = ttk.Scrollbar(self.zestawienia_platnosci_treeview, orient='vertical',
                                     command=self.zestawienia_platnosci_treeview.yview)
        self.zestawienia_platnosci_treeview.configure(yscrollcommand=self.scrolly.set)
        map(lambda col: col.configure(yscrollcommand=self.scrolly.set), columns)
        self.scrolly.pack(side=tk.RIGHT, fill=tk.Y)
        map(lambda col: col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True), columns)
        self.zestawienia_platnosci_treeview.pack(expand='yes', fill='both')
        self.zestawienia_platnosci_treeview.bind('<<TreeviewSelect>>', self.update_szczegoly_zestawienia_treeview)

    def update_zestawienia_platnosci_treeview(self, event):
        lista_platnosci = self.get_dane_zestawienia_platnosci()

        self.zestawienia_platnosci_treeview.delete(*self.zestawienia_platnosci_treeview.get_children())
        i = 0
        for n in lista_platnosci:
            i += 1
            data = n[0]
            kwota = f'{n[1]:.2f}'

            if i % 2 == 0:
                background_gotowki = 'background_dark'
            else:
                background_gotowki = 'background_light'

            self.zestawienia_platnosci_treeview.tag_configure('background_dark', background='#383232')
            self.zestawienia_platnosci_treeview.tag_configure('background_light', background='#262424')

            self.zestawienia_platnosci_treeview.insert('', 'end', values=(data, kwota),
                                                       tags=(background_gotowki))
        self.szczegoly_zestawienia_treeview.delete(*self.szczegoly_zestawienia_treeview.get_children())

    def create_szczegoly_zestawienia_treeview(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', fieldbackground="#383232", background="#383232", foreground='white')
        style.configure("Treeview.Heading", background="#383232", foreground="white")
        style.map('Treeview.Heading', background=[('disabled', '#383232')])

        def fixed_map(option):  # naprawa buga wersji dla Python 3.7 przy wyświetlaniu koloru linii w treeview
            return [elm for elm in style.map("Treeview", query_opt=option)
                    if elm[:2] != ("!disabled", "!selected")]

        style.map("Treeview", foreground=fixed_map("foreground"),
                  background=fixed_map("background"))

        self.hurtownie_R_3f = tk.Frame(self.hurtownie_RF)
        self.hurtownie_R_3f.configure(bg='#383232', relief='groove', bd=1)
        self.hurtownie_R_3f.place(relx=0.01, rely=0.37, relwidth=0.98, relheight=0.62)

        columns = ('NR DOKUMENTU', 'TERMIN', 'WYSTAWIONA', 'WARTOŚĆ')
        self.szczegoly_zestawienia_treeview = ttk.Treeview(self.hurtownie_R_3f,
                                                           columns=columns,
                                                           show='headings',
                                                           style="Treeview", selectmode="browse")

        self.szczegoly_zestawienia_treeview.heading('NR DOKUMENTU', text='NR DOKUMENTU')
        self.szczegoly_zestawienia_treeview.column('NR DOKUMENTU', minwidth=200, stretch='yes', anchor='center')
        self.szczegoly_zestawienia_treeview.heading('TERMIN', text='TERMIN')
        self.szczegoly_zestawienia_treeview.column('TERMIN', minwidth=150, stretch='yes', anchor='center')
        self.szczegoly_zestawienia_treeview.heading('WYSTAWIONA', text='WYSTAWIONA')
        self.szczegoly_zestawienia_treeview.column('WYSTAWIONA', minwidth=150, stretch='yes', anchor='center')
        self.szczegoly_zestawienia_treeview.heading('WARTOŚĆ', text='WARTOŚĆ')
        self.szczegoly_zestawienia_treeview.column('WARTOŚĆ', minwidth=150, stretch='yes', anchor='center')

        self.scrolly = ttk.Scrollbar(self.szczegoly_zestawienia_treeview, orient='vertical',
                                     command=self.szczegoly_zestawienia_treeview.yview)
        self.szczegoly_zestawienia_treeview.configure(yscrollcommand=self.scrolly.set)
        map(lambda col: col.configure(yscrollcommand=self.scrolly.set), columns)
        self.scrolly.pack(side=tk.RIGHT, fill=tk.Y)
        map(lambda col: col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True), columns)
        self.szczegoly_zestawienia_treeview.pack(expand='yes', fill='both')

    def update_szczegoly_zestawienia_treeview(self, event):
        data = ''
        for item in event.widget.selection():
            data = self.zestawienia_platnosci_treeview.item(item, 'values')[0]
        plik_glowny = self.definiuj_plik_glowny()
        lista_faktur = self.get_dane_szczegoly_zestawienia_platnosci(data, plik_glowny)
        self.szczegoly_zestawienia_treeview.delete(*self.szczegoly_zestawienia_treeview.get_children())
        i = 0
        for n in lista_faktur:
            i += 1
            nr_faktury = n[1]
            data_platnosci = n[2]
            data_faktury = str(n[3])[0:10]
            kwota = f'{n[4]:.2f}'

            if i % 2 == 0:
                background_gotowki = 'background_dark'
            else:
                background_gotowki = 'background_light'

            self.szczegoly_zestawienia_treeview.tag_configure('background_dark', background='#383232')
            self.szczegoly_zestawienia_treeview.tag_configure('background_light', background='#262424')

            self.szczegoly_zestawienia_treeview.insert('', 'end', values=(nr_faktury, data_platnosci, data_faktury
                                                                          , kwota),
                                                       tags=(background_gotowki))

    @staticmethod
    def get_dane_szczegoly_zestawienia_platnosci(data, plik_glowny):
        if plik_glowny == '':
            return []
        dane_plik = pd.read_excel(plik_glowny)
        data_filtr = dane_plik[dane_plik['Data zapłaty'] == data].index
        lista_platnosci = dane_plik.loc[data_filtr].values.tolist()
        return lista_platnosci

    def dodaj_do_listy_przelewow(self):
        kontrahent_nazwa = self.hurtownia_combobx.get()
        kontrahent = self.slownik_hurtownie[kontrahent_nazwa]['nazwa']
        nr_konta = self.slownik_hurtownie[kontrahent_nazwa]['konto']
        kwota = str(self.suma_do_zaplaty)
        if kwota[-3] == '.':
            pass
        else:
            kwota = kwota + '0'
        data = str(datetime.datetime.now().date())
        tytul = f'(H) {self.slownik_hurtownie[kontrahent_nazwa]["tytul"]}'
        self.controller.biala_lista_frame.konto_entry.delete(0, 'end')
        self.controller.biala_lista_frame.konto_entry.insert(0, nr_konta.replace('"', ''))
        self.controller.biala_lista_frame.zapisz_biala_lista('')
        self.controller.przelewy_frame.dodaj_do_listy_przelewow(kontrahent, nr_konta, kwota, data, tytul)

    def pobierz_zestawienia(self):
        subject = '5472110371 poproszę o zestawienie do patnosci'
        text = 'Pozdrawiam' \
               '' \
               'Tomasz Zembok'

        for key in slowniki.maile_pobierz_zestawienia:
            self.controller.maile.mail_text(slowniki.maile_pobierz_zestawienia[key], subject, text,
                                            keyring.get_password("mejek_mail", "mejek_mail"))
            self.controller.logger.log(20, f'Wysłano prośbę o zestawienie do płatności do:'
                                           f' {slowniki.maile_pobierz_zestawienia[key]}')

    def wyslij_zestawienia(self):
        # znajdz pliki
        lista_plikow = glob.glob(rf'C:\Users\dell\Desktop\*.pdf')
        print(lista_plikow)

        text = 'Pozdrawiam' \
               '' \
               'Tomasz Zembok'

        for f in lista_plikow:
            if '5472110371' in f or '129551' in f:
                if f.split('_')[1] in slowniki.maile_wyslij_zestawienia.keys():
                    hurtownia = f.split('_')[1]
                    nazwa_pliku = f.split('\\')[-1]
                    data = nazwa_pliku.split("_")[2][0:4] + '-' + nazwa_pliku.split("_")[2][4:6] \
                           + '-' + nazwa_pliku.split("_")[2][6:8]
                    subject = f'{nazwa_pliku.split("_")[0]} - zestawienie do płatności ' \
                              f'z dnia {data} - {nazwa_pliku.split("_")[3][0:-4]} zł'
                    email_hurtowni = slowniki.maile_wyslij_zestawienia[hurtownia]
                    zestawienie_folder = slowniki.foldery_zestawienia[hurtownia] + nazwa_pliku

                    self.controller.maile.mail_text_attachmen(email_hurtowni, subject, text,
                                                              f, keyring.get_password("mejek_mail", "mejek_mail"))

                    shutil.move(f, zestawienie_folder)
                    self.controller.logger.log(20, f'Wysłano e-mail do: {email_hurtowni}, {subject}')
                else:
                    pass

class Czynsze_frame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.configure(bg='#383232')
        self.kolor_razem = '#b58b14'
        self.najemcy = ['', 'HALLERA', 'PIELGRZYMOWICE', 'FART', 'DUDA', 'JASIEK', 'BANK']
        self.create_czynsze_LF()
        self.create_czynsze_RF()

    def create_czynsze_LF(self):
        self.czynsze_LF = tk.Frame(self)
        self.czynsze_LF.configure(bg='#383232', relief='groove', bd=1)
        self.czynsze_LF.place(relx=0.01, rely=0.02, relwidth=0.48, relheight=0.96)
        self.create_czynsze_treeview()
        self.update_czynsze_treeview()
        self.create_czynsze_L_3f()
        self.create_czynsze_L_2f()

    def create_czynsze_RF(self):
        self.czynsze_RF = tk.Frame(self)
        self.czynsze_RF.configure(bg='#383232', relief='groove', bd=1)
        self.czynsze_RF.place(relx=0.51, rely=0.02, relwidth=0.48, relheight=0.96)

    def create_czynsze_treeview(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', fieldbackground="#383232", background="#383232", foreground='white')
        style.configure("Treeview.Heading", background="#383232", foreground="white")
        style.map('Treeview.Heading', background=[('disabled', '#383232')])

        def fixed_map(option):  # naprawa buga wersji dla Python 3.7 przy wyświetlaniu koloru linii w treeview
            return [elm for elm in style.map("Treeview", query_opt=option)
                    if elm[:2] != ("!disabled", "!selected")]

        style.map("Treeview", foreground=fixed_map("foreground"),
                  background=fixed_map("background"))

        self.czynsze_L_1f = tk.Frame(self.czynsze_LF)
        self.czynsze_L_1f.configure(bg='#383232', relief='groove', bd=1)
        self.czynsze_L_1f.place(relx=0.01, rely=0.01, relwidth=0.98, relheight=0.4)

        self.czynsze_columns = ('NR RACHUNKU', 'DATA', 'NAJEMCA', 'WARTOŚĆ')
        self.czynsze_treeview = ttk.Treeview(self.czynsze_L_1f, columns=self.czynsze_columns,
                                             show='headings',
                                             style="Treeview", selectmode="browse")

        self.czynsze_treeview.heading('NR RACHUNKU', text='NR RACHUNKU')
        self.czynsze_treeview.column('NR RACHUNKU', minwidth=200, stretch='yes', anchor='center')
        self.czynsze_treeview.heading('DATA', text='DATA')
        self.czynsze_treeview.column('DATA', width=150, stretch='no', anchor='center')
        self.czynsze_treeview.heading('NAJEMCA', text='NAJEMCA')
        self.czynsze_treeview.column('NAJEMCA', width=150, stretch='no', anchor='center')
        self.czynsze_treeview.heading('WARTOŚĆ', text='WARTOŚĆ')
        self.czynsze_treeview.column('WARTOŚĆ', width=150, stretch='no', anchor='center')

        self.scrolly = ttk.Scrollbar(self.czynsze_treeview, orient='vertical',
                                     command=self.czynsze_treeview.yview)
        self.czynsze_treeview.configure(yscrollcommand=self.scrolly.set)
        map(lambda col: col.configure(yscrollcommand=self.scrolly.set), self.czynsze_columns)
        self.scrolly.pack(side=tk.RIGHT, fill=tk.Y)
        map(lambda col: col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True), self.czynsze_columns)
        self.czynsze_treeview.pack(expand='yes', fill='both')
        self.czynsze_treeview.bind("<Double-1>", self.kopiuj_dane)

    def update_czynsze_treeview(self):
        # dane_plik = pd.read_excel(r'C:\Users\dell\Dysk Google\ZPT_DATA\Czynsze\rachunki_dane.xlsx')
        # dane = dane_plik.values.tolist()
        # dane.sort(key=lambda x: x[0], reverse=True)
        dane = []
        with open('czynsze.json', encoding='utf-8') as json_file:
            data = json.load(json_file)

        for key in data:
            dane.append([int(key), data[key]['nr'], data[key]['data'], data[key]['najemca'], data[key]['suma']])
        dane.sort(key=lambda x: x[0], reverse=True)

        self.czynsze_treeview.delete(*self.czynsze_treeview.get_children())
        i = 0
        for n in dane:
            i += 1
            nr_rachunku = n[1]
            data = n[2]
            najemca = n[3]
            wartosc = f'{n[4]:.2f}'

            if i % 2 == 0:
                background_gotowki = 'background_dark'
            else:
                background_gotowki = 'background_light'

            self.czynsze_treeview.tag_configure('background_dark', background='#383232')
            self.czynsze_treeview.tag_configure('background_light', background='#262424')

            self.czynsze_treeview.insert('', 'end', values=(nr_rachunku, data, najemca, wartosc),
                                         tags=(background_gotowki))

    def create_czynsze_L_2f(self):
        self.czynsze_L_2f = tk.Frame(self.czynsze_LF)
        self.czynsze_L_2f.configure(bg='#383232', relief='groove', bd=1)
        self.czynsze_L_2f.place(relx=0.01, rely=0.42, relwidth=0.98, relheight=0.05)

        self.kopiuj_dane_button = tk.Button(self.czynsze_L_2f, text='KASUJ RACHUNEK',
                                            bg='#544949',
                                            fg=f'{self.kolor_razem}', command=self.delete_rachunek)
        self.kopiuj_dane_button.place(relx=0.05, rely=0.2, relwidth=0.25)
        self.ekdportuj_button = tk.Button(self.czynsze_L_2f, text='EKSPORTUJ DO PDF',
                                          bg='#544949',
                                          fg=f'{self.kolor_razem}', command=self.eksportuj_do_pdf)
        self.ekdportuj_button.place(relx=0.35, rely=0.2, relwidth=0.25)
        self.wyslij_button = tk.Button(self.czynsze_L_2f, text='WYŚLIJ MAILEM',
                                       bg='#544949',
                                       fg=f'{self.kolor_razem}', command=self.wyslij_rachunek)
        self.wyslij_button.place(relx=0.65, rely=0.2, relwidth=0.25)

    def kopiuj_dane(self, event):
        curItem = self.czynsze_treeview.focus()
        if curItem != '':
            dane_rachunku = self.czynsze_treeview.item(curItem)
            nr_rachunku = dane_rachunku['values'][0]

            # dane_glowne = pd.read_excel(r'C:\Users\dell\Dysk Google\ZPT_DATA\Czynsze\rachunki_dane.xlsx')
            # rachunek_dane = dane_glowne[dane_glowne['Nr_rachunku'] == f'{nr_rachunku}'].values.tolist()[0]
            # dane_koncowe = []
            # for n in rachunek_dane:
            #     if str(n) != 'nan':
            #         dane_koncowe.append(n)
            #     else:
            #         dane_koncowe.append('')
            with open('czynsze.json', encoding='utf-8') as json_file:
                data = json.load(json_file)
            dane_koncowe = {}
            for key in data:
                if data[key]['nr'] == nr_rachunku:
                    dane_koncowe = data[key]

            najemca_index = self.najemcy.index(dane_koncowe['najemca'])
            self.najemcy_options.current(najemca_index)

            self.czysc_pola_nowy_rachunek()
            self.opis_1_text.insert('1.0', f'{dane_koncowe["pole_1"]}')
            self.opis_2_text.insert('1.0', f'{dane_koncowe["pole_2"]}')
            self.opis_3_text.insert('1.0', f'{dane_koncowe["pole_3"]}')
            self.opis_4_text.insert('1.0', f'{dane_koncowe["pole_4"]}')
            self.opis_5_text.insert('1.0', f'{dane_koncowe["pole_5"]}')
            self.kwota_1_entry.insert(0, f'{dane_koncowe["kwota_1"]}')
            self.kwota_2_entry.insert(0, f'{dane_koncowe["kwota_2"]}')
            self.kwota_3_entry.insert(0, f'{dane_koncowe["kwota_3"]}')
            self.kwota_4_entry.insert(0, f'{dane_koncowe["kwota_4"]}')
            self.kwota_5_entry.insert(0, f'{dane_koncowe["kwota_5"]}')
            self.razem_entry.insert(0, f'{dane_koncowe["suma"]}')
            self.licznik_poprzedni_entry.insert(0, f'{dane_koncowe["licznik"]}')
            self.set_nr_nowe_zamowienie()

    def czysc_pola_nowy_rachunek(self):
        self.opis_1_text.delete('1.0', 'end')
        self.opis_2_text.delete('1.0', 'end')
        self.opis_3_text.delete('1.0', 'end')
        self.opis_4_text.delete('1.0', 'end')
        self.opis_5_text.delete('1.0', 'end')
        self.kwota_1_entry.delete(0, 'end')
        self.kwota_2_entry.delete(0, 'end')
        self.kwota_3_entry.delete(0, 'end')
        self.kwota_4_entry.delete(0, 'end')
        self.kwota_5_entry.delete(0, 'end')
        self.licznik_poprzedni_entry.delete(0, 'end')
        self.licznik_obecny_entry.delete(0, 'end')
        self.licznik_zuzycie_entry.delete(0, 'end')
        self.razem_entry.delete(0, 'end')
        self.kwota_energia_entry.delete(0, 'end')
        self.nr_rachunku_entry.delete(0, 'end')

    def przelicz_energie(self):
        self.licznik_zuzycie_entry.delete(0, 'end')
        self.kwota_energia_entry.delete(0, 'end')
        licznik_1 = self.licznik_poprzedni_entry.get()
        licznik_2 = self.licznik_obecny_entry.get()
        zuzycie = int(licznik_2) - int(licznik_1[0:-2])
        self.licznik_zuzycie_entry.insert(0, zuzycie)
        stawka_kwh = self.stawka_kwh_entry.get()
        kwota_energia = zuzycie * float(stawka_kwh)
        self.kwota_energia_entry.insert(0, kwota_energia)

    def set_nr_nowe_zamowienie(self):
        dzieci = self.czynsze_treeview.get_children()
        row_1 = self.czynsze_treeview.item(dzieci[0])['values']
        numer = int(row_1[0][:row_1[0].index('/')]) + 1
        nowy_numer = str(numer) + f'/{str(datetime.date.today().year)}'
        self.nr_rachunku_entry.insert(0, nowy_numer)

    def wyslij_rachunek(self):
        # pobierz dane z drzewa
        curItem = self.czynsze_treeview.focus()
        if curItem != '':
            dane_rachunku = self.czynsze_treeview.item(curItem)
            nr_rachunku = dane_rachunku['values'][0].replace('/', '_')
            kwota = dane_rachunku['values'][3]
            odbiorca = dane_rachunku['values'][2]
            miesiac_rachunku = dane_rachunku['values'][1][0:-3]

        else:
            nr_rachunku = ''
            kwota = ''
            odbiorca = ''
            miesiac_rachunku = ''

        # znajdz plik z rachunkiem
        lista_plikow = glob.glob(rf'C:\Users\dell\Dysk Google\ZPT_DATA\CZYNSZE\*.pdf')
        plik_rachunek = ''
        for f in lista_plikow:
            if nr_rachunku in f and kwota in f:
                plik_rachunek = f
                break

        # znjadz mail odbiorcy
        mail_odbiorca = slowniki.maile_czynsze[odbiorca]

        # zapytaj o hasło
        password = keyring.get_password("mejek_mail", "mejek_mail")

        # tekst wiadomości
        tutul_wiadomosci = f'Rachunek Pielgrzymowice {miesiac_rachunku}'
        text_wiadomosci = 'Pozdrawiam'

        # wyslij

        self.controller.maile.mail_text_attachmen(mail_odbiorca, tutul_wiadomosci, text_wiadomosci, plik_rachunek,
                                                  password)

        # zapis log
        self.controller.logger.log(20, f'Wysłano rachunek za {miesiac_rachunku} do {mail_odbiorca}')

    def create_czynsze_L_3f(self):
        self.czynsze_L_3f = tk.Frame(self.czynsze_LF)
        self.czynsze_L_3f.configure(bg='#383232', relief='groove', bd=1)
        self.czynsze_L_3f.place(relx=0.01, rely=0.48, relwidth=0.98, relheight=0.51)

        self.data_wystawienia_dateentry = DateEntry(self.czynsze_L_3f, width=12, background='#383232',
                                                    foreground='white', borderwidth=2, date_pattern='y-mm-dd',
                                                    locale='pl_PL')
        self.data_wystawienia_dateentry.place(relx=0.7, rely=0.02, relwidth=0.25)
        self.najemcy_options = ttk.Combobox(self.czynsze_L_3f, values=self.najemcy, state='readonly')
        self.najemcy_options.place(relx=0.7, rely=0.08, relwidth=0.25)
        self.najemcy_options.current(0)
        self.nr_rachunku_label = tk.Label(self.czynsze_L_3f, text='RACHUNEK',
                                          foreground='white', background='#383232', anchor='center')
        self.nr_rachunku_label.place(relx=0.05, rely=0.02, relwidth=0.6)
        self.nr_rachunku_entry = tk.Entry(self.czynsze_L_3f, justify='center', bg='#6b685f', fg='white')
        self.nr_rachunku_entry.place(relx=0.05, rely=0.08, relwidth=0.6)
        self.opis_1_text = tk.Text(self.czynsze_L_3f, bg='#6b685f', fg='white', wrap='word')
        self.opis_1_text.place(relx=0.05, rely=0.2, relwidth=0.6, relheight=0.07)
        self.opis_2_text = tk.Text(self.czynsze_L_3f, bg='#6b685f', fg='white')
        self.opis_2_text.place(relx=0.05, rely=0.3, relwidth=0.6, relheight=0.07)
        self.opis_3_text = tk.Text(self.czynsze_L_3f, bg='#6b685f', fg='white')
        self.opis_3_text.place(relx=0.05, rely=0.4, relwidth=0.6, relheight=0.07)
        self.opis_4_text = tk.Text(self.czynsze_L_3f, bg='#6b685f', fg='white')
        self.opis_4_text.place(relx=0.05, rely=0.5, relwidth=0.6, relheight=0.07)
        self.opis_5_text = tk.Text(self.czynsze_L_3f, bg='#6b685f', fg='white')
        self.opis_5_text.place(relx=0.05, rely=0.6, relwidth=0.6, relheight=0.07)
        self.kwota_1_entry = tk.Entry(self.czynsze_L_3f, justify='center', bg='#6b685f', fg='white')
        self.kwota_1_entry.place(relx=0.7, rely=0.2, relwidth=0.25, relheight=0.07)
        self.kwota_2_entry = tk.Entry(self.czynsze_L_3f, justify='center', bg='#6b685f', fg='white')
        self.kwota_2_entry.place(relx=0.7, rely=0.3, relwidth=0.25, relheight=0.07)
        self.kwota_3_entry = tk.Entry(self.czynsze_L_3f, justify='center', bg='#6b685f', fg='white')
        self.kwota_3_entry.place(relx=0.7, rely=0.4, relwidth=0.25, relheight=0.07)
        self.kwota_4_entry = tk.Entry(self.czynsze_L_3f, justify='center', bg='#6b685f', fg='white')
        self.kwota_4_entry.place(relx=0.7, rely=0.5, relwidth=0.25, relheight=0.07)
        self.kwota_5_entry = tk.Entry(self.czynsze_L_3f, justify='center', bg='#6b685f', fg='white')
        self.kwota_5_entry.place(relx=0.7, rely=0.6, relwidth=0.25, relheight=0.07)
        self.razem_entry = tk.Entry(self.czynsze_L_3f, justify='center', bg='#6b685f', fg='white')
        self.razem_entry.place(relx=0.7, rely=0.7, relwidth=0.2, relheight=0.07)
        self.sumuj_button = tk.Button(self.czynsze_L_3f, text=u"\u2211",
                                      bg='#544949',
                                      fg=f'{self.kolor_razem}', command=self.sumuj_rachunek)
        self.sumuj_button.place(relx=0.91, rely=0.7, relwidth=0.04, relheight=0.07)
        self.licznik_poprzedni_entry = tk.Entry(self.czynsze_L_3f, justify='center', bg='#6b685f', fg='white')
        self.licznik_poprzedni_entry.place(relx=0.05, rely=0.85, relwidth=0.13)
        self.licznik_obecny_entry = tk.Entry(self.czynsze_L_3f, justify='center', bg='#6b685f', fg='white')
        self.licznik_obecny_entry.place(relx=0.2, rely=0.85, relwidth=0.13)
        self.licznik_zuzycie_entry = tk.Entry(self.czynsze_L_3f, justify='center', bg='#6b685f', fg='white')
        self.licznik_zuzycie_entry.place(relx=0.35, rely=0.85, relwidth=0.13)
        self.stawka_kwh_entry = tk.Entry(self.czynsze_L_3f, justify='center', bg='#6b685f', fg='white')
        self.stawka_kwh_entry.place(relx=0.5, rely=0.85, relwidth=0.13)
        self.stawka_kwh_entry.insert(0, '0.86')
        self.kwota_energia_entry = tk.Entry(self.czynsze_L_3f, justify='center', bg='#6b685f', fg='white')
        self.kwota_energia_entry.place(relx=0.65, rely=0.85, relwidth=0.13)
        self.przelicz_energie_button = tk.Button(self.czynsze_L_3f, text='PRZELICZ',
                                                 bg='#544949',
                                                 fg=f'{self.kolor_razem}', command=self.przelicz_energie)
        self.przelicz_energie_button.place(relx=0.8, rely=0.85, relwidth=0.15)
        licznik_poprzedni_label = tk.Label(self.czynsze_L_3f, text='OSTATNI ODCZYT',
                                           foreground='white', background='#383232', anchor='w')
        licznik_poprzedni_label.place(relx=0.05, rely=0.8, relwidth=0.13)
        licznik_aktualny_label = tk.Label(self.czynsze_L_3f, text='ODCZYT DZIŚ',
                                          foreground='white', background='#383232', anchor='w')
        licznik_aktualny_label.place(relx=0.2, rely=0.8, relwidth=0.13)
        licznik_zuzycie_label = tk.Label(self.czynsze_L_3f, text='ZUZYCIE',
                                         foreground='white', background='#383232', anchor='w')
        licznik_zuzycie_label.place(relx=0.35, rely=0.8, relwidth=0.13)
        stawka_label = tk.Label(self.czynsze_L_3f, text='STAWKA kWh',
                                foreground='white', background='#383232', anchor='w')
        stawka_label.place(relx=0.5, rely=0.8, relwidth=0.13)
        suma_energia_label = tk.Label(self.czynsze_L_3f, text='NALEŻNOŚĆ',
                                      foreground='white', background='#383232', anchor='w')
        suma_energia_label.place(relx=0.65, rely=0.8, relwidth=0.13)
        opis_label = tk.Label(self.czynsze_L_3f, text='OPIS',
                              foreground='white', background='#383232', anchor='center')
        opis_label.place(relx=0.05, rely=0.15, relwidth=0.6)
        kwota_label = tk.Label(self.czynsze_L_3f, text='KWOTA',
                               foreground='white', background='#383232', anchor='center')
        kwota_label.place(relx=0.7, rely=0.15, relwidth=0.25)
        razem_label = tk.Label(self.czynsze_L_3f, text='RAZEM: ',
                               foreground='white', background='#383232', anchor='e')
        razem_label.place(relx=0.05, rely=0.7, relwidth=0.6)
        self.dodaj_rachunek_button = tk.Button(self.czynsze_L_3f, text='DODAJ RACHUNEK',
                                               bg='#544949',
                                               fg=f'{self.kolor_razem}', command=self.dodaj_rachunek)
        self.dodaj_rachunek_button.place(relx=0.05, rely=0.92, relwidth=0.9)

    def sumuj_rachunek(self):
        if self.kwota_1_entry.get() != '':
            kwota_1 = float(self.kwota_1_entry.get().replace(',', '.'))
        else:
            kwota_1 = 0
        if self.kwota_2_entry.get() != '':
            kwota_2 = float(self.kwota_2_entry.get().replace(',', '.'))
        else:
            kwota_2 = 0
        if self.kwota_3_entry.get() != '':
            kwota_3 = float(self.kwota_3_entry.get().replace(',', '.'))
        else:
            kwota_3 = 0
        if self.kwota_4_entry.get() != '':
            kwota_4 = float(self.kwota_4_entry.get().replace(',', '.'))
        else:
            kwota_4 = 0
        if self.kwota_5_entry.get() != '':
            kwota_5 = float(self.kwota_5_entry.get().replace(',', '.'))
        else:
            kwota_5 = 0
        suma = kwota_1 + kwota_2 + kwota_3 + kwota_4 + kwota_5
        self.razem_entry.delete(0, 'end')
        self.razem_entry.insert(0, f'{suma:.2f}')

    def dodaj_rachunek(self):
        self.sumuj_rachunek()
        nr_rachunku = self.nr_rachunku_entry.get()
        data_rachunek = self.data_wystawienia_dateentry.get()
        najemca = self.najemcy_options.get()
        opis_1 = self.opis_1_text.get('1.0', 'end').strip('\n')
        opis_2 = self.opis_2_text.get('1.0', 'end').strip('\n')
        opis_3 = self.opis_3_text.get('1.0', 'end').strip('\n')
        opis_4 = self.opis_4_text.get('1.0', 'end').strip('\n')
        opis_5 = self.opis_5_text.get('1.0', 'end').strip('\n')
        if self.kwota_1_entry.get() != '':
            kwota_1 = float(self.kwota_1_entry.get().replace(',', '.'))
        else:
            kwota_1 = ''
        if self.kwota_2_entry.get() != '':
            kwota_2 = float(self.kwota_2_entry.get().replace(',', '.'))
        else:
            kwota_2 = ''
        if self.kwota_3_entry.get() != '':
            kwota_3 = float(self.kwota_3_entry.get().replace(',', '.'))
        else:
            kwota_3 = ''
        if self.kwota_4_entry.get() != '':
            kwota_4 = float(self.kwota_4_entry.get().replace(',', '.'))
        else:
            kwota_4 = ''
        if self.kwota_5_entry.get() != '':
            kwota_5 = float(self.kwota_5_entry.get().replace(',', '.'))
        else:
            kwota_5 = ''
        razem = float(self.razem_entry.get().replace(',', '.'))
        if self.licznik_obecny_entry.get() != '':
            licznik = float(self.licznik_obecny_entry.get())
        else:
            licznik = ''

        with open('czynsze.json', encoding='utf-8') as json_file:
            data = json.load(json_file)

        data[self.get_last_rachunek_id() + 1] = {'nr': nr_rachunku, 'data': str(data_rachunek), 'najemca': najemca,
                                                 'pole_1': opis_1,
                                                 'pole_2': opis_2, 'pole_3': opis_3, 'pole_4': opis_4, 'pole_5': opis_5,
                                                 'kwota_1': kwota_1, 'kwota_2': kwota_2, 'kwota_3': kwota_3,
                                                 'kwota_4': kwota_4, 'kwota_5': kwota_5, 'suma': razem,
                                                 'licznik': licznik}

        with open('czynsze.json', 'w', encoding='utf-8') as outfile:
            json.dump(data, outfile)

        self.update_czynsze_treeview()
        self.czysc_pola_nowy_rachunek()

    def delete_rachunek(self):
        self.item = self.czynsze_treeview.selection()
        nr_rachunku = self.czynsze_treeview.item(self.item, 'values')[0]
        with open('czynsze.json', encoding='utf-8') as json_file:
            data = json.load(json_file)

        for element in data:
            if data[element]['nr'] == nr_rachunku:
                del data[element]
                break

        with open('czynsze.json', 'w') as outfile:
            json.dump(data, outfile)

        self.update_czynsze_treeview()
        self.czysc_pola_nowy_rachunek()

    def eksportuj_do_pdf(self):
        key = ''
        config = pdfkit.configuration(wkhtmltopdf='c:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')
        file_html = 'wzor_rachunek.html'
        with open(file_html, "r", encoding='utf-8') as f:
            text = f.read()
        curItem = self.czynsze_treeview.focus()
        if curItem != '':
            dane_rachunku = self.czynsze_treeview.item(curItem)
            nr_rachunku = dane_rachunku['values'][0]
            with open('czynsze.json', encoding='utf-8') as json_file:
                data = json.load(json_file)
            for element in data:
                if data[element]['nr'] == nr_rachunku:
                    key = element

            data_rachunku = data[key]['data']
            najemca = data[key]['najemca']
            nr_rachunku = data[key]['nr']
            opis_1 = data[key]['pole_1']
            opis_2 = data[key]['pole_2']
            opis_3 = data[key]['pole_3']
            opis_4 = data[key]['pole_4']
            opis_5 = data[key]['pole_5']
            if data[key]['kwota_1'] != 0:
                kwota_1 = float(data[key]['kwota_1'])
            else:
                kwota_1 = ''
            if data[key]['kwota_2'] != 0:
                kwota_2 = float(data[key]['kwota_2'])
            else:
                kwota_2 = 0
            if data[key]['kwota_3'] != 0:
                kwota_3 = float(data[key]['kwota_3'])
            else:
                kwota_3 = 0
            if data[key]['kwota_4'] != 0:
                kwota_4 = float(data[key]['kwota_4'])
            else:
                kwota_4 = 0
            if data[key]['kwota_5'] != 0:
                kwota_5 = float(data[key]['kwota_5'])
            else:
                kwota_5 = 0

            suma_rachunku = data[key]['suma']
            licznik = data[key]['licznik']

            text = text.replace('data_wystawienia_rachunku', f'{data_rachunku}')
            najemca_dane = self.get_dane_najemcy(najemca)
            text = text.replace('nazwa_odbiorcy_rachunku', f'{najemca_dane[0]}')
            text = text.replace('adres_odbiorcy_rachunku', f'{najemca_dane[1]}')
            text = text.replace('nip_odbiorcy_rachunku', f'{najemca_dane[2]}')
            text = text.replace('numer_rachunku', f'{nr_rachunku}')
            text = text.replace('opis_1', f'{opis_1}')
            text = text.replace('opis_2', f'{opis_2}')
            text = text.replace('opis_3', f'{opis_3}')
            text = text.replace('opis_4', f'{opis_4}')
            text = text.replace('opis_5', f'{opis_5}')
            if kwota_1 != 0:
                text = text.replace('kwota_1', f'{kwota_1:.2f} zł')
            else:
                text = text.replace('kwota_1', f'')
            if kwota_2 != 0:
                text = text.replace('kwota_2', f'{kwota_2:.2f} zł')
            else:
                text = text.replace('kwota_2', f'')
            if kwota_3 != 0:
                text = text.replace('kwota_3', f'{kwota_3:.2f} zł')
            else:
                text = text.replace('kwota_3', f'')
            if kwota_4 != 0:
                text = text.replace('kwota_4', f'{kwota_4:.2f} zł')
            else:
                text = text.replace('kwota_4', f'')
            if kwota_5 != 0:
                text = text.replace('kwota_5', f'{kwota_5:.2f} zł')
            else:
                text = text.replace('kwota_5', f'')

            text = text.replace('suma_rachunku', f'{suma_rachunku:.2f} zł')

            nazwa_pliku = f'{nr_rachunku.replace("/", "_")}_{data_rachunku.replace("-", "")}_{najemca}_{suma_rachunku:.2f}'
            plik_wyjsciowy = rf'C:\Users\dell\Dysk Google\ZPT_DATA\Czynsze\{nazwa_pliku}.pdf'
            pdfkit.from_string(text, plik_wyjsciowy, configuration=config)

    @staticmethod
    def get_dane_najemcy(najemca):
        nazwa = ''
        adres = ''
        nip = ''

        if najemca == 'BANK':
            nazwa = 'BANK SPÓŁDZIELCZY W PAWŁOWICACH'
            adres = '43-250 PAWŁOWICE, ZJEDNOCZENIA 62B'
            nip = '6331015145'
        if najemca == 'JASIEK':
            nazwa = 'Piekarnia Ciastkarnia “JASIEK” Sp. jawna Marian, Ewa Jasiek'
            adres = '43-200 PSZCZYNA, PARTYZANTÓW 17'
            nip = '638-15-87-576'
        if najemca == 'DUDA':
            nazwa = 'INDYWIDUALNA PRAKTYKA DENTYSTYCZNA AGNIESZKA DUDA-NAWROCKA'
            adres = '43-252 PIELGRZYMOWICE, GOLASOWICKA 4'
            nip = '6331935644'
        if najemca == 'FART':
            nazwa = 'FART UBEZPIECZENIA BARBARA NIERADZIK'
            adres = '43-254 WARSZOWICE, STAWOWA 1'
            nip = '6330006411'
        if najemca == 'HALLERA' or najemca == 'PIELGRZYMOWICE':
            nazwa = 'MARIA-PHARM SP. Z O.O.'
            adres = '43-200 PSZCZYNA, HALLERA 13'
            nip = '5472110371'
        return [nazwa, adres, nip]

    @staticmethod
    def get_last_rachunek_id():
        with open('czynsze.json', encoding='utf-8') as json_file:
            data = json.load(json_file)
        return int(list(data.keys())[-1])

class Przelewy_frame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.configure(bg='#383232')
        self.kolor_razem = '#b58b14'
        self.lista_przelewow_wykaz = []
        self.lista_przelewow = []
        self.lista_pracownikow = []
        self.create_przelewy_LF()
        self.create_przelewy_RF()

    def create_przelewy_LF(self):
        self.przelewy_LF = tk.Frame(self)
        self.przelewy_LF.configure(bg='#383232', relief='groove', bd=1)
        self.przelewy_LF.place(relx=0.01, rely=0.02, relwidth=0.48, relheight=0.96)
        self.create_przlewy_L_1f()
        self.create_odbiorca_treeview()
        self.create_przelewy_L_3f()
        self.create_przelewy_L_4f()
        self.create_eksportuj_przelewy_button()
        self.create_suma_prelewow_info()

    def create_przelewy_RF(self):
        self.przelewy_RF = tk.Frame(self)
        self.przelewy_RF.configure(bg='#383232', relief='groove', bd=1)
        self.przelewy_RF.place(relx=0.51, rely=0.02, relwidth=0.48, relheight=0.96)
        self.get_przelewy_zbiorcze_data()
        self.create_przelewy_R_1f()
        self.create_prelewy_R_2f_treeview()
        self.update_prelewy_R_2f_treeview(self.lista_przelwow_wykaz)

    def create_przelewy_R_1f(self):
        self.przelewy_R_1f = tk.Frame(self.przelewy_RF)
        self.przelewy_R_1f.configure(bg='#383232', relief='groove', bd=1)
        self.przelewy_R_1f.place(relx=0.01, rely=0.01, relwidth=0.98, relheight=0.08)

        szukana_faktura = StringVar()
        szukana_faktura.trace("w", lambda name, index, mode, szukana_faktura=szukana_faktura:
        self.filtruj_faktury(szukana_faktura, 4))
        szukany_kontrahent = StringVar()
        szukany_kontrahent.trace("w", lambda name, index, mode, szukany_kontrahent=szukany_kontrahent:
        self.filtruj_faktury(szukany_kontrahent, 3))

        faktura_label = tk.Label(self.przelewy_R_1f, text='FAKTURA',
                                 foreground='white', background='#383232', anchor='w')
        faktura_label.place(relx=0.01, rely=0.2, relwidth=0.1, relheight=0.25)

        kontrahent_label = tk.Label(self.przelewy_R_1f, text='KONTRAHENT',
                                    foreground='white', background='#383232', anchor='w')
        kontrahent_label.place(relx=0.01, rely=0.6, relwidth=0.1, relheight=0.25)

        self.szukaj_faktura_entry = tk.Entry(self.przelewy_R_1f, justify='center', bg='#6b685f', fg='white',
                                             textvariable=szukana_faktura)
        self.szukaj_faktura_entry.place(relx=0.15, rely=0.2, relwidth=0.8, relheight=0.3)
        self.szukaj_kontrahent_entry = tk.Entry(self.przelewy_R_1f, justify='center', bg='#6b685f', fg='white',
                                                textvariable=szukany_kontrahent)
        self.szukaj_kontrahent_entry.place(relx=0.15, rely=0.6, relwidth=0.8, relheight=0.3)

    def filtruj_faktury(self, fraza, pozycja_lista_wykaz):
        text = fraza.get()
        lista_robocza = []

        if len(text) >= 3:
            for p in self.lista_przelwow_wykaz:
                if text.lower() in p[pozycja_lista_wykaz].lower():
                    lista_robocza.append(p)
            self.update_prelewy_R_2f_treeview(lista_robocza)
        else:
            self.update_prelewy_R_2f_treeview(self.lista_przelwow_wykaz)

    def create_prelewy_R_2f_treeview(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', fieldbackground="#383232", background="#383232", foreground='white')
        style.configure("Treeview.Heading", background="#383232", foreground="white")
        style.map('Treeview.Heading', background=[('disabled', '#383232')])

        def fixed_map(option):  # naprawa buga wersji dla Python 3.7 przy wyświetlaniu koloru linii w treeview
            return [elm for elm in style.map("Treeview", query_opt=option)
                    if elm[:2] != ("!disabled", "!selected")]

        style.map("Treeview", foreground=fixed_map("foreground"),
                  background=fixed_map("background"))

        self.prelewy_R_2f = tk.Frame(self.przelewy_RF)
        self.prelewy_R_2f.configure(bg='#383232', relief='groove', bd=1)
        self.prelewy_R_2f.place(relx=0.01, rely=0.1, relwidth=0.98, relheight=0.88)

        self.prelewy_R_2f_columns = ('KONTRAHENT', 'DATA', 'KWOTA', 'TYTUŁ')
        self.prelewy_R_2f_treeview = ttk.Treeview(self.prelewy_R_2f, columns=self.prelewy_R_2f_columns,
                                                  show='headings',
                                                  style="Treeview", selectmode="browse")

        self.prelewy_R_2f_treeview.heading('KONTRAHENT', text='KONTRAHENT')
        self.prelewy_R_2f_treeview.column('KONTRAHENT', width=250, stretch='no', anchor='center')
        self.prelewy_R_2f_treeview.heading('DATA', text='DATA')
        self.prelewy_R_2f_treeview.column('DATA', width=100, stretch='no', anchor='center')
        self.prelewy_R_2f_treeview.heading('KWOTA', text='KWOTA')
        self.prelewy_R_2f_treeview.column('KWOTA', width=100, stretch='no', anchor='center')
        self.prelewy_R_2f_treeview.heading('TYTUŁ', text='TYTUŁ')
        self.prelewy_R_2f_treeview.column('TYTUŁ', minwidth=300, stretch='yes', anchor='center')

        self.scrolly = ttk.Scrollbar(self.prelewy_R_2f_treeview, orient='vertical',
                                     command=self.prelewy_R_2f_treeview.yview)
        self.prelewy_R_2f_treeview.configure(yscrollcommand=self.scrolly.set)
        map(lambda col: col.configure(yscrollcommand=self.scrolly.set), self.prelewy_R_2f_columns)
        self.scrolly.pack(side=tk.RIGHT, fill=tk.Y)
        map(lambda col: col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True), self.prelewy_R_2f_columns)
        self.prelewy_R_2f_treeview.pack(expand='yes', fill='both')
        self.prelewy_R_2f_treeview.bind('<Double-1>', self.otworz_opcje_rozliczenia)  # lista przelewów

    def create_przlewy_L_1f(self):
        self.przlewy_L_1f = tk.Frame(self.przelewy_LF)
        self.przlewy_L_1f.configure(bg='#383232', relief='groove', bd=1)
        self.przlewy_L_1f.place(relx=0.01, rely=0.01, relwidth=0.98, relheight=0.04)

        kontrahenci_button = tk.Button(self.przlewy_L_1f, text='KONTRAHENCI',
                                       bg='#544949',
                                       fg=f'{self.kolor_razem}', command=self.get_dane_kontrahenci)
        kontrahenci_button.place(relx=0.02, rely=0.17, relwidth=0.9 / 4)
        pracownicy_button = tk.Button(self.przlewy_L_1f, text='PRACOWNICY',
                                      bg='#544949',
                                      fg=f'{self.kolor_razem}', command=self.get_dane_pracownicy)
        pracownicy_button.place(relx=(0.9 / 4) + 0.04, rely=0.17, relwidth=0.9 / 4)
        wyplaty_button = tk.Button(self.przlewy_L_1f, text='WYPŁATY MAIL',
                                   bg='#544949',
                                   fg=f'{self.kolor_razem}', command=self.wyslij_mail_wyplaty)
        wyplaty_button.place(relx=(0.9 / 4) * 2 + 0.06, rely=0.17, relwidth=0.9 / 4)
        zakupy_button = tk.Button(self.przlewy_L_1f, text='ZAKUPY MAIL',
                                  bg='#544949',
                                  fg=f'{self.kolor_razem}', command=self.wyslij_mail_zakupy)
        zakupy_button.place(relx=(0.9 / 4) * 3 + 0.08, rely=0.17, relwidth=0.9 / 4)

    def create_odbiorca_treeview(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', fieldbackground="#383232", background="#383232", foreground='white')
        style.configure("Treeview.Heading", background="#383232", foreground="white")
        style.map('Treeview.Heading', background=[('disabled', '#383232')])

        def fixed_map(option):  # naprawa buga wersji dla Python 3.7 przy wyświetlaniu koloru linii w treeview
            return [elm for elm in style.map("Treeview", query_opt=option)
                    if elm[:2] != ("!disabled", "!selected")]

        style.map("Treeview", foreground=fixed_map("foreground"),
                  background=fixed_map("background"))

        self.przelewy_L_2f = tk.Frame(self.przelewy_LF)
        self.przelewy_L_2f.configure(bg='#383232', relief='groove', bd=1)
        self.przelewy_L_2f.place(relx=0.01, rely=0.06, relwidth=0.98, relheight=0.29)

        self.odbiorcy_columns = ('LP', 'NAZWA', 'KONTO')
        self.odbiorcy_treeview = ttk.Treeview(self.przelewy_L_2f, columns=self.odbiorcy_columns,
                                              show='headings',
                                              style="Treeview", selectmode="browse")

        self.odbiorcy_treeview.heading('LP', text='LP')
        self.odbiorcy_treeview.column('LP', width=30, stretch='no', anchor='center')
        self.odbiorcy_treeview.heading('NAZWA', text='NAZWA')
        self.odbiorcy_treeview.column('NAZWA', minwidth=150, stretch='yes', anchor='w')
        self.odbiorcy_treeview.heading('KONTO', text='KONTO')
        self.odbiorcy_treeview.column('KONTO', minwidth=150, stretch='yes', anchor='center')

        self.scrolly = ttk.Scrollbar(self.odbiorcy_treeview, orient='vertical',
                                     command=self.odbiorcy_treeview.yview)
        self.odbiorcy_treeview.configure(yscrollcommand=self.scrolly.set)
        map(lambda col: col.configure(yscrollcommand=self.scrolly.set), self.odbiorcy_columns)
        self.scrolly.pack(side=tk.RIGHT, fill=tk.Y)
        map(lambda col: col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True), self.odbiorcy_columns)
        self.odbiorcy_treeview.pack(expand='yes', fill='both')
        self.odbiorcy_treeview.bind('<Double-1>', self.update_dane_do_przelwu)

    def create_przelewy_L_3f(self):
        self.przelewy_L_3f = tk.Frame(self.przelewy_LF)
        self.przelewy_L_3f.configure(bg='#383232', relief='groove', bd=1)
        self.przelewy_L_3f.place(relx=0.01, rely=0.36, relwidth=0.98, relheight=0.3)

        kontrahen_label = tk.Label(self.przelewy_L_3f, text=f'KONTRAHENT: ', foreground='white',
                                   background='#383232', anchor='w')
        kontrahen_label.place(relx=0.05, rely=0.1, relwidth=0.12, relheight=0.04)
        nr_kota_label = tk.Label(self.przelewy_L_3f, text=f'NR KONTA: : ', foreground='white',
                                 background='#383232', anchor='w')
        nr_kota_label.place(relx=0.05, rely=0.25, relwidth=0.12, relheight=0.04)
        kwota_label = tk.Label(self.przelewy_L_3f, text=f'KWOTA: ', foreground='white',
                               background='#383232', anchor='w')
        kwota_label.place(relx=0.05, rely=0.4, relwidth=0.12, relheight=0.04)
        data_label = tk.Label(self.przelewy_L_3f, text=f'DATA: ', foreground='white',
                              background='#383232', anchor='w')
        data_label.place(relx=0.05, rely=0.55, relwidth=0.12, relheight=0.04)
        tytul_label = tk.Label(self.przelewy_L_3f, text=f'TYTUŁ: ', foreground='white',
                               background='#383232', anchor='w')
        tytul_label.place(relx=0.05, rely=0.7, relwidth=0.12, relheight=0.04)
        self.kontrahent_entry = tk.Entry(self.przelewy_L_3f, justify='center', bg='#6b685f', fg='white')
        self.kontrahent_entry.place(relx=0.17, rely=0.08, relwidth=0.78, relheight=0.07)
        self.nr_konta_entry = tk.Entry(self.przelewy_L_3f, justify='center', bg='#6b685f', fg='white')
        self.nr_konta_entry.place(relx=0.17, rely=0.23, relwidth=0.78, relheight=0.07)
        self.kwota_entry = tk.Entry(self.przelewy_L_3f, justify='center', bg='#6b685f', fg='white')
        self.kwota_entry.place(relx=0.17, rely=0.38, relwidth=0.78, relheight=0.07)
        self.kwota_entry.bind('<Return>', (lambda event: self.get_dane_do_przelewu()))
        self.data_entry = tk.Entry(self.przelewy_L_3f, justify='center', bg='#6b685f', fg='white')
        self.data_entry.place(relx=0.17, rely=0.53, relwidth=0.78, relheight=0.07)
        self.tytul_entry = tk.Entry(self.przelewy_L_3f, justify='center', bg='#6b685f', fg='white')
        self.tytul_entry.place(relx=0.17, rely=0.68, relwidth=0.78, relheight=0.07)

        dodaj_do_listy_przelewow_button = tk.Button(self.przelewy_L_3f, text='DODAJ DO LISTY',
                                                    bg='#544949',
                                                    fg=f'{self.kolor_razem}', command=self.get_dane_do_przelewu)
        dodaj_do_listy_przelewow_button.place(relx=0.6, rely=0.83, relwidth=0.35)

    def create_przelewy_L_4f(self):  # lista przelewów
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', fieldbackground="#383232", background="#383232", foreground='white')
        style.configure("Treeview.Heading", background="#383232", foreground="white")
        style.map('Treeview.Heading', background=[('disabled', '#383232')])

        def fixed_map(option):  # naprawa buga wersji dla Python 3.7 przy wyświetlaniu koloru linii w treeview
            return [elm for elm in style.map("Treeview", query_opt=option)
                    if elm[:2] != ("!disabled", "!selected")]

        style.map("Treeview", foreground=fixed_map("foreground"),
                  background=fixed_map("background"))

        self.lista_przelewow_treeview_frame = tk.Frame(self.przelewy_LF)
        self.lista_przelewow_treeview_frame.configure(bg='#383232', relief='groove', bd=1)
        self.lista_przelewow_treeview_frame.place(relx=0.01, rely=0.67, relwidth=0.98, relheight=0.28)

        self.lista_przelewow_columns = ('LP', 'NAZWA', 'DATA', 'TYTUŁ', 'KWOTA')
        self.lista_przelewow_treeview = ttk.Treeview(self.lista_przelewow_treeview_frame,
                                                     columns=self.lista_przelewow_columns,
                                                     show='headings',
                                                     style="Treeview", selectmode="browse")

        self.lista_przelewow_treeview.heading('LP', text='LP')
        self.lista_przelewow_treeview.column('LP', width=30, stretch='no', anchor='center')
        self.lista_przelewow_treeview.heading('NAZWA', text='NAZWA')
        self.lista_przelewow_treeview.column('NAZWA', width=150, stretch='no', anchor='w')
        self.lista_przelewow_treeview.heading('DATA', text='DATA')
        self.lista_przelewow_treeview.column('DATA', width=100, stretch='no', anchor='center')
        self.lista_przelewow_treeview.heading('TYTUŁ', text='TYTUŁ')
        self.lista_przelewow_treeview.column('TYTUŁ', minwidth=150, stretch='yes', anchor='center')
        self.lista_przelewow_treeview.heading('KWOTA', text='KWOTA')
        self.lista_przelewow_treeview.column('KWOTA', width=90, stretch='no', anchor='center')

        self.scrolly = ttk.Scrollbar(self.lista_przelewow_treeview, orient='vertical',
                                     command=self.lista_przelewow_treeview.yview)
        self.lista_przelewow_treeview.configure(yscrollcommand=self.scrolly.set)
        map(lambda col: col.configure(yscrollcommand=self.scrolly.set), self.lista_przelewow_columns)
        self.scrolly.pack(side=tk.RIGHT, fill=tk.Y)
        map(lambda col: col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True), self.lista_przelewow_columns)
        self.lista_przelewow_treeview.pack(expand='yes', fill='both')
        self.lista_przelewow_treeview.bind('<Double-1>', self.usun_przelew_z_listy)  # lista przelewów

    def create_eksportuj_przelewy_button(self):
        eksportuj_przelewy_button = tk.Button(self.przelewy_LF, text='EKSPORTUJ',
                                              bg='#544949',
                                              fg=f'{self.kolor_razem}', command=self.eksportuj_przelewy)
        eksportuj_przelewy_button.place(relx=0.60, rely=0.96, relwidth=0.35)

    def create_suma_prelewow_info(self):
        self.suma_przelewow_label = tk.Label(self.przelewy_LF, text=f'SUMA: 0.00 zł', foreground='white',
                                             background='#383232', anchor='w')
        self.suma_przelewow_label.place(relx=0.20, rely=0.96, relwidth=0.3)

    def update_suma_przelewow_info(self):
        suma_przelwow = 0
        for child in self.lista_przelewow_treeview.get_children():
            kwota = self.lista_przelewow_treeview.item(child)["values"][4][0:-3]
            suma_przelwow += float(kwota)
        if suma_przelwow == 0:
            self.suma_przelewow_label.config(text=f'SUMA: 0.00 zł')
        else:
            self.suma_przelewow_label.config(text=f'SUMA: {suma_przelwow:.2f} zł')

    def eksportuj_przelewy(self):
        filename = filedialog.asksaveasfile(initialdir=r"C:\Users\dell\Dysk Google\ZPT_DATA\PRZELEWY\\",
                                            title="ZAPISZ PLIK",
                                            defaultextension='.txt',
                                            initialfile=f'{str(datetime.datetime.now().date()).replace("-", "")}_')

        self.plik_przelewu = str(filename.name)

        with open(self.plik_przelewu, 'w', encoding='utf-8') as f:
            for przelew in self.lista_przelewow:
                f.write(przelew)
        self.lista_przelewow = []
        self.update_lista_przelewow_treeview()
        self.update_prelewy_R_2f_treeview(self.get_przelewy_zbiorcze_data())
        self.suma_przelewow_label.config(text=f'SUMA: 0.00 zł')

    def get_dane_do_przelewu(self):
        kontrahent = f'"{self.kontrahent_entry.get().lstrip()}"'
        nr_konta = f'"{self.nr_konta_entry.get().replace(" ", "")}"'
        kwota = self.kwota_entry.get()
        data = self.data_entry.get()
        tytul = self.tytul_entry.get()
        self.dodaj_do_listy_przelewow(kontrahent, nr_konta, kwota, data, tytul)

    def dodaj_do_listy_przelewow(self, kontrahent, nr_konta, kwota, data, tytul):
        kod_zlecenia = '110'
        data_zlecenia = data.replace('-', '')
        kwota_przelewu = kwota.replace(',', '').replace('.', '')
        nr_rozliczeniowy_banku_zelceniodawcy = '11602202'
        pole_zerowe_pozycja_5 = '0'
        rachunek_zleceniodawcy = '"71116022020000000469095212"'
        rachunek_odbiorcy = nr_konta
        adres_zleceniodawcy = '""'
        nazwa_adres_odbiorcy = kontrahent
        pole_zerowe_pozycja_10 = '0'
        nr_rozliczeniowy_banku_odbiorcy = ''
        pole_puste_pozycja_13 = '""'
        pole_puste_pozycja_14 = '""'
        kod_klasyfikacji = '"51"'
        adnotacje = '""'
        tytul_do_podzialu = tytul

        if self.weryfikacja_pol(kontrahent, nr_konta, kwota, data, tytul) == True:
            linia_przelewu = f'{kod_zlecenia},{data_zlecenia},{kwota_przelewu},{nr_rozliczeniowy_banku_zelceniodawcy},' \
                             f'{pole_zerowe_pozycja_5},{rachunek_zleceniodawcy},{rachunek_odbiorcy},{adres_zleceniodawcy},' \
                             f'{nazwa_adres_odbiorcy},{pole_zerowe_pozycja_10},{nr_rozliczeniowy_banku_odbiorcy},' \
                             f'"{self.podziel_tytul(tytul_do_podzialu)}",{pole_puste_pozycja_13},{pole_puste_pozycja_14},{kod_klasyfikacji},' \
                             f'{adnotacje}\n'

            self.lista_przelewow.append(linia_przelewu)
            print(self.lista_przelewow)
            self.update_lista_przelewow_treeview()
            self.update_suma_przelewow_info()
            self.wyczysc_dane_przelewu()

    @staticmethod
    def messagebox_nipoprawne_pola():
        messagebox.showerror('UWAGA', 'Nie uzupełniono poprawnie wszystkich pól')

    def weryfikacja_pol(self, kontrahent, nr_konta, kwota, data, tytul_do_podzialu):

        if self.sprawdz_pole_kontrahent(kontrahent) == False:
            print('Błąd kontrahent')
            self.messagebox_nipoprawne_pola()
            return False
        if self.sprawdz_pole_koto(nr_konta) == False:
            print('Błąd nr konta')
            self.messagebox_nipoprawne_pola()
            return False
        if self.sprawdz_pole_kwota(kwota) == False:
            print('Błąd kwota')
            self.messagebox_nipoprawne_pola()
            return False
        if self.sprawdz_pole_data(data) == False:
            print('Błąd data')
            self.messagebox_nipoprawne_pola()
            return False
        if self.podziel_tytul(tytul_do_podzialu) == False:
            print('Błąd tytuł')
            return False
        return True

    @staticmethod
    def sprawdz_pole_kontrahent(dane):
        if dane != '':
            return True
        return False

    @staticmethod
    def sprawdz_pole_koto(dane):
        if dane != '':
            return True
        return False

    @staticmethod
    def sprawdz_pole_kwota(dane):
        if dane != '' and (dane[-3] == ',' or dane[-3] == '.'):
            return True
        return False

    @staticmethod
    def sprawdz_pole_data(dane):
        if dane != '':
            return True
        return False

    def podziel_tytul(self, tytul):
        if tytul == '':
            self.messagebox_nipoprawne_pola()
            return False
        if len(tytul) > 140:
            messagebox.showerror('UWAGA', f'Tytuł jest zbyt długi ({len(tytul)})')
            return False
        if len(tytul) > 105:
            tytul_podzielony = f'{tytul[0:35]}|{tytul[35:70]}|{tytul[70:105]}|{tytul[105:]}'
            return tytul_podzielony
        if len(tytul) > 70 and len(tytul) <= 105:
            tytul_podzielony = f'{tytul[0:35]}|{tytul[35:70]}|{tytul[70:]}'
            return tytul_podzielony
        if len(tytul) > 35 and len(tytul) <= 70:
            tytul_podzielony = f'{tytul[0:35]}|{tytul[35:]}'
            return tytul_podzielony
        if len(tytul) <= 35:
            tytul_podzielony = tytul
            return tytul_podzielony

    def wyczysc_dane_przelewu(self):
        self.kontrahent_entry.delete(0, 'end')
        self.nr_konta_entry.delete(0, 'end')
        self.data_entry.delete(0, 'end')
        self.kwota_entry.delete(0, 'end')
        self.tytul_entry.delete(0, 'end')

    def update_lista_przelewow_treeview(self):
        self.lista_przelewow_treeview.delete(*self.lista_przelewow_treeview.get_children())
        i = 0
        for n in self.lista_przelewow:
            i += 1
            dane_przelewu = n.split('"')
            # print(dane_przelewu)
            nazwa = dane_przelewu[7]
            data = f'{dane_przelewu[0][4:8]}-{dane_przelewu[0][8:10]}-{dane_przelewu[0][10:12]}'
            tytul = dane_przelewu[9]
            kwota = f'{dane_przelewu[0].split(",")[2][0:-2]}.{dane_przelewu[0].split(",")[2][-2:]} zł'

            if i % 2 == 0:
                background = 'background_dark'
            else:
                background = 'background_light'

            self.lista_przelewow_treeview.tag_configure('background_dark', background='#383232')
            self.lista_przelewow_treeview.tag_configure('background_light', background='#262424')

            self.lista_przelewow_treeview.insert('', 'end', values=(i, nazwa, data, tytul, kwota), tags=(background))

    def update_dane_do_przelwu(self, event):
        item = self.odbiorcy_treeview.selection()
        nazwa = self.odbiorcy_treeview.item(item, 'values')[1]
        konto = self.odbiorcy_treeview.item(item, 'values')[2]

        if nazwa.strip() in self.lista_pracownikow:
            # data ostatni dzien miesiaca
            offset = pd.tseries.offsets.BMonthEnd()
            data = datetime.datetime.now().date()
            # data = f'{data.year}-{data.month}-{calendar.monthrange(data.year, data.month)[1]}'
            data = offset.rollforward(data).date()

            # tytul
            tytul = f'WYNAGRODZENIE {str(data)[0:7]}'
            if nazwa.strip() == 'KAPPEL-ZIOŁA MARIA' or nazwa.strip() == 'ZIOŁA STEFAN':
                tytul = f'UMOWA ZLECENIE {str(data)[0:7]}'
            kwota = self.ostatnia_wplata_dict[nazwa.strip().upper()]

        else:
            data = datetime.datetime.now().date()
            tytul = ''
            kwota = ''

        self.wyczysc_dane_przelewu()
        self.kontrahent_entry.insert(0, nazwa)
        self.nr_konta_entry.insert(0, konto)
        self.data_entry.insert(0, data)
        self.tytul_entry.insert(0, tytul)
        self.kwota_entry.insert(0, kwota)
        self.kwota_entry.focus()

    def get_dane_pracownicy(self):
        pliki_typ = ("wszystkie pliki", "*.*")
        self.ostatnie_wyplaty = filedialog.askopenfile(initialdir=r'C:\Users\dell\Dysk Google\ZPT_DATA\PRZELEWY',
                                                       title="Wybierz plik",
                                                       filetypes=(pliki_typ, ("wszystkie pliki", "*.*"))).name
        self.create_ostatnia_wyplata_dict()
        with open('slowniki_pracownicy.json', encoding='utf-8') as json_file:
            data = json.load(json_file)
        lista = []
        self.lista_pracownikow = []
        for key in data:
            lista.append([data[key]['pelna_nazwa'], data[key]['konto_bankowe']])
            self.lista_pracownikow.append(data[key]['pelna_nazwa'])
        lista.sort(key=lambda x: x[0])
        self.update_odbiorcy_treeview(lista)

    def create_ostatnia_wyplata_dict(self):
        with open(self.ostatnie_wyplaty, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        self.ostatnia_wplata_dict = {}
        for line in lines:
            linia_split = line.split(',')
            nazwa = linia_split[8]
            kwota = f'{linia_split[2][:-2]},{linia_split[2][-2:]}'
            self.ostatnia_wplata_dict[nazwa.replace('"', '').upper()] = kwota
        print(self.ostatnia_wplata_dict)

    def get_dane_kontrahenci(self):
        filename = r"C:\Users\dell\Dysk Google\ZPT_DATA\PRZELEWY\kontrahenci.xlsx"
        df = pd.read_excel(filename)
        df.sort_values(by='nazwa', inplace=True, ascending=True)
        lista = df.values.tolist()
        self.update_odbiorcy_treeview(lista)

    def update_odbiorcy_treeview(self, dane):
        self.odbiorcy_treeview.delete(*self.odbiorcy_treeview.get_children())
        i = 0
        for n in dane:
            i += 1
            nazwa = n[0]
            konto = n[1]

            if i % 2 == 0:
                background = 'background_dark'
            else:
                background = 'background_light'

            self.odbiorcy_treeview.tag_configure('background_dark', background='#383232')
            self.odbiorcy_treeview.tag_configure('background_light', background='#262424')

            self.odbiorcy_treeview.insert('', 'end', values=(i, f"       {nazwa}", konto), tags=(background))

    def usun_przelew_z_listy(self, event):
        item = self.lista_przelewow_treeview.item(self.lista_przelewow_treeview.selection(), 'values')
        nowa_lista = []
        for p in self.lista_przelewow:
            if self.lista_przelewow.index(p) == int(item[0]) - 1:
                pass
            else:
                nowa_lista.append(p)
        self.lista_przelewow = nowa_lista
        self.update_lista_przelewow_treeview()
        self.update_suma_przelewow_info()

    def wyslij_mail_wyplaty(self):
        subject = 'Poprosze o dane do wypłaty'
        text = f'Urlopy (daty), L4, nadgodziny'
        for key, mail in slowniki.maile_apteki.items():
            self.controller.maile.mail_text(mail, subject, text, keyring.get_password("mejek_mail", "mejek_mail"))

    def wyslij_mail_zakupy(self):
        subject = 'Poprosze o listę zakupów'
        text = f'Pozdrawiam'
        for key, mail in slowniki.maile_apteki.items():
            self.controller.maile.mail_text(mail, subject, text, keyring.get_password("mejek_mail", "mejek_mail"))

    def get_przelewy_zbiorcze_data(self):
        pliki = glob.glob(r'C:\Users\dell\Dysk Google\ZPT_DATA\PRZELEWY\*.txt')
        self.lista_przelwow_wykaz = []

        for path in pliki:
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
                if text != '':
                    for l in text.split('\n')[:-1]:
                        # data - 1
                        # kwota - 2
                        # konto odbiorcy - 6
                        # nazwa odbiorcy - 8
                        # tytuł operacji - 11

                        data = l.split(',')[1][:4] + '-' + l.split(',')[1][4:6] + '-' + l.split(',')[1][6:8]
                        kwota = l.split(',')[2][:-2] + '.' + l.split(',')[2][-2:]
                        konto_odb = l.split(',')[6].replace('"', '')
                        nazwa_odb = l.split(',')[8].replace('"', '')
                        tytul_oper = l.split('"')[9].replace('|', '')

                        # print(f'DATA: {data}')
                        # print(f'KWOTA: {kwota} zł')
                        # print(f'KONTO: {konto_odb}')
                        # print(f'NAZWA: {nazwa_odb}')
                        # print(f'TYTUŁ: {tytul_oper}')
                        # print(f'\n')

                        self.lista_przelwow_wykaz.append([data, kwota, konto_odb, nazwa_odb, tytul_oper])

        self.lista_przelwow_wykaz = sorted(self.lista_przelwow_wykaz, key=lambda x: x[0])
        self.lista_przelwow_wykaz.reverse()
        return self.lista_przelwow_wykaz

    def update_prelewy_R_2f_treeview(self, lista_przelewow):
        self.prelewy_R_2f_treeview.delete(*self.prelewy_R_2f_treeview.get_children())
        i = 0
        for n in lista_przelewow:
            i += 1
            kontrhent = n[3]
            data = n[0]
            kwota = f'{n[1]} zł'
            tytul = n[4]

            if i % 2 == 0:
                background = 'background_dark'
            else:
                background = 'background_light'

            self.prelewy_R_2f_treeview.tag_configure('background_dark', background='#383232')
            self.prelewy_R_2f_treeview.tag_configure('background_light', background='#262424')

            self.prelewy_R_2f_treeview.insert('', 'end', values=(kontrhent, data, kwota, tytul), tags=(background))

    def otworz_opcje_rozliczenia(self, event):
        item = self.prelewy_R_2f_treeview.selection()
        nazwa = self.prelewy_R_2f_treeview.item(item, 'values')[0]
        data = self.prelewy_R_2f_treeview.item(item, 'values')[1]
        kwota = self.prelewy_R_2f_treeview.item(item, 'values')[2]
        tytul = self.prelewy_R_2f_treeview.item(item, 'values')[3]
        faktury_do_rozliczenia = []

        if '(T)' in tytul or '(K)' in tytul:
            faktury_do_rozliczenia = tytul[4:].replace(' ', '').split(',')

        if '(H)' in tytul:
            filename = self.get_filename_zestawienia_przelewow_hurtownie(nazwa)
            dane = self.controller.hurtownie_frame.get_dane_szczegoly_zestawienia_platnosci(data, filename)
            for f in dane:
                faktury_do_rozliczenia.append(str(f[1]))
            print(faktury_do_rozliczenia)

        if self.set_rozlicz_button_state() == True:
            self.rozlicz_przelew(faktury_do_rozliczenia)
        else:
            messagebox.showerror('PROGRAM SYMFONIA MUSI BYĆ URUCHOMIONY')

    def set_rozlicz_button_state(self):
        lista_okien = list(self.controller.ahk.windows())

        for okno in lista_okien:
            if 'Symfonia' in str(okno.title):
                return True
        return False

    def rozlicz_przelew(self, lista_faktur):
        tk_clipboard = self.controller
        faktury_do_rozliczenia = []
        zestawienie_lista = lista_faktur
        zestawienie_test = zestawienie_lista
        test = 1
        sleep_time = 2

        lista_okien = list(self.controller.ahk.windows())

        for okno in lista_okien:
            if 'Symfonia Finanse' in str(okno.title):
                okno.activate()
                sleep(1)
                break

        self.controller.ahk.mouse_move(1036, 124)
        self.controller.ahk.right_click()
        sleep(1)
        self.controller.ahk.mouse_move(1046, 131)
        self.controller.ahk.click()
        sleep(sleep_time)
        data = tk_clipboard.clipboard_get().split('\n')

        for d in data:
            if d != '':
                d_split = d.split('\t')
                faktury_do_rozliczenia.append(d_split[6])
                # print(d_split[6], d_split[2])

        indeks_count = 0
        print(len(faktury_do_rozliczenia))
        print(faktury_do_rozliczenia)
        indeksy = []

        for faktura_zestawienie in faktury_do_rozliczenia:

            if faktura_zestawienie in zestawienie_test:
                zestawienie_test.remove(f'{faktura_zestawienie}')
                indeksy.append(faktury_do_rozliczenia.index(f'{faktura_zestawienie}'))

        print(indeksy)
        print(f'ZOSTAŁO: {zestawienie_lista}')
        print('OK')

        count = 0
        count_pgdn = 0
        number_of_pgdn = int(len(faktury_do_rozliczenia) / 41) + 1

        print(number_of_pgdn)
        for press_pgdn in range(0, number_of_pgdn):
            indeks_start = press_pgdn * 41
            indeks_stop = indeks_start + 41

            while int(indeksy[indeks_count]) >= indeks_start and int(indeksy[indeks_count]) < indeks_stop:
                pozycja_strona_y = ((int(indeksy[indeks_count]) % 41) * 17) + 130
                self.controller.ahk.mouse_move(315, pozycja_strona_y)
                sleep(0.2)
                self.controller.ahk.click(315, pozycja_strona_y)
                sleep(0.3)
                self.controller.ahk.send('!r')
                sleep(0.3)
                print(indeks_count, indeks_start, indeks_stop, faktury_do_rozliczenia[int(indeksy[indeks_count])])
                # alt r
                if indeks_count == len(indeksy) - 1:
                    break
                indeks_count += 1
            self.controller.ahk.key_press('PgDn')

    @staticmethod
    def get_filename_zestawienia_przelewow_hurtownie(hurtownia):
        filename = slowniki.pliki_zestawienia_przelewow[hurtownia]
        return filename

class Dane_archiwalne_frame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.configure(bg='#383232')
        self.kolor_razem = '#b58b14'
        self.kolor_font = 'white'
        self.kolor_font_razem = 'black'
        self.kolor_legenda = '#383232'
        self.zpt_database = ZPT_Database.ZPT_base()
        self.create_dane_archiwalne_dzien_F1()
        self.create_dane_archiwalne_miesiac_F2()
        self.create_dane_archiwalne_apteka_F3()
        self.create_dane_archiwalne_dzien_F1_legenda()
        self.create_dane_archiwalne_miesiac_F2_legenda()
        self.create_dane_archiwalne_apteka_F3_buttons()
        self.create_dane_archiwalne_apteka_F3_treeview()
        self.create_dane_archiwalne_miesiac_wybor_miesiaca_combobox()
        self.create_dane_archiwalne_oborty_dzienne_dane_frame()
        self.get_dane_archiwalne_obroty_dzienne_data()
        self.update_dane_archiwalne_obroty_dzienne(event='')
        self.create_dane_archiwalne_oborty_miesieczne_dane_frame()
        self.get_dane_archiwalne_obroty_miesieczne_data()
        self.update_dane_archiwalne_obroty_miesieczne_dane(event='')

    def create_dane_archiwalne_dzien_F1(self):
        self.dane_archiwalne_dzien_frame = tk.Frame(self)
        self.dane_archiwalne_dzien_frame.configure(bg='#383232', relief='groove', bd=1)
        self.dane_archiwalne_dzien_frame.place(relx=0.01, rely=0.06, relwidth=0.98, relheight=0.22)

    def create_dane_archiwalne_dzien_F1_legenda(self):

        self.dane_archiwalne_dzien_label = tk.Label(self, text=f'WYBIERZ DZIEŃ: ', bg=f'#383232',
                                                    fg=f'{self.kolor_font}')
        self.dane_archiwalne_dzien_label.place(relx=0.01, rely=0.03, relwidth=0.1, relheight=0.03)

        self.dane_archiwalne_dzien_data_picker = DateEntry(self, width=12, background='#383232',
                                                           foreground='white', borderwidth=2, date_pattern='y-mm-dd',
                                                           locale='pl_PL', maxdate=datetime.datetime.now().date())
        self.dane_archiwalne_dzien_data_picker.place(relx=0.11, rely=0.03, relwidth=0.15)

        self.dane_archiwalne_dzien_legenda_apteka = tk.Label(self.dane_archiwalne_dzien_frame, text='APTEKA',
                                                             relief='groove',
                                                             bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.dane_archiwalne_dzien_legenda_apteka.place(relwidth=1 / 6, relheight=1 / 8)
        self.dane_archiwalne_dzien_legenda_pacjenci = tk.Label(self.dane_archiwalne_dzien_frame, text='PACJENCI',
                                                               relief='groove',
                                                               bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.dane_archiwalne_dzien_legenda_pacjenci.place(relx=1 / 6, relwidth=1 / 6, relheight=1 / 8)
        self.dane_archiwalne_dzien_legenda_brutto = tk.Label(self.dane_archiwalne_dzien_frame, text='OBROTY BRUTTO',
                                                             relief='groove',
                                                             bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.dane_archiwalne_dzien_legenda_brutto.place(relx=2 / 6, relwidth=1 / 6, relheight=1 / 8)
        self.dane_archiwalne_dzien_legenda_netto = tk.Label(self.dane_archiwalne_dzien_frame, text='OBROTY NETTO',
                                                            relief='groove',
                                                            bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.dane_archiwalne_dzien_legenda_netto.place(relx=3 / 6, relwidth=1 / 6, relheight=1 / 8)
        self.dane_archiwalne_dzien_legenda_zysk = tk.Label(self.dane_archiwalne_dzien_frame, text='ZYSK NETTO',
                                                           relief='groove',
                                                           bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.dane_archiwalne_dzien_legenda_zysk.place(relx=4 / 6, relwidth=1 / 6, relheight=1 / 8)
        self.dane_archiwalne_dzien_legenda_magazyn = tk.Label(self.dane_archiwalne_dzien_frame, text='MARŻA',
                                                              relief='groove',
                                                              bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.dane_archiwalne_dzien_legenda_magazyn.place(relx=5 / 6, relwidth=1 / 6, relheight=1 / 8)

        self.dane_archiwalne_dzien_legenda_nazwa_02 = tk.Label(self.dane_archiwalne_dzien_frame, text='HIPOKRATES 4',
                                                               relief='groove',
                                                               bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.dane_archiwalne_dzien_legenda_nazwa_02.place(rely=1 / 8, relwidth=1 / 6, relheight=1 / 8)
        self.dane_archiwalne_dzien_legenda_nazwa_04 = tk.Label(self.dane_archiwalne_dzien_frame, text='HALLERA',
                                                               relief='groove',
                                                               bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.dane_archiwalne_dzien_legenda_nazwa_04.place(rely=2 / 8, relwidth=1 / 6, relheight=1 / 8)
        self.dane_archiwalne_dzien_legenda_nazwa_05 = tk.Label(self.dane_archiwalne_dzien_frame, text='PIELGRZYMOWICE',
                                                               relief='groove',
                                                               bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.dane_archiwalne_dzien_legenda_nazwa_05.place(rely=3 / 8, relwidth=1 / 6, relheight=1 / 8)
        self.dane_archiwalne_dzien_legenda_nazwa_06 = tk.Label(self.dane_archiwalne_dzien_frame, text='WISŁA',
                                                               relief='groove',
                                                               bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.dane_archiwalne_dzien_legenda_nazwa_06.place(rely=4 / 8, relwidth=1 / 6, relheight=1 / 8)
        self.dane_archiwalne_dzien_legenda_nazwa_07 = tk.Label(self.dane_archiwalne_dzien_frame, text='BIEDRONKA',
                                                               relief='groove',
                                                               bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.dane_archiwalne_dzien_legenda_nazwa_07.place(rely=5 / 8, relwidth=1 / 6, relheight=1 / 8)
        self.dane_archiwalne_dzien_legenda_nazwa_08 = tk.Label(self.dane_archiwalne_dzien_frame, text='BZIE',
                                                               relief='groove',
                                                               bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.dane_archiwalne_dzien_legenda_nazwa_08.place(rely=6 / 8, relwidth=1 / 6, relheight=1 / 8)
        self.dane_archiwalne_dzien_legenda_razem = tk.Label(self.dane_archiwalne_dzien_frame, text='RAZEM',
                                                            relief='groove',
                                                            bg=f'{self.kolor_razem}', fg=f'{self.kolor_font_razem}')
        self.dane_archiwalne_dzien_legenda_razem.place(rely=7 / 8, relwidth=1 / 6, relheight=1 / 8)
        self.dane_archiwalne_dzien_data_picker.bind("<<DateEntrySelected>>", self.update_dane_archiwalne_obroty_dzienne)

    def create_dane_archiwalne_oborty_dzienne_dane_frame(self):
        self.dane_archiwalne_oborty_dzienne_dane_frame = tk.Frame(self.dane_archiwalne_dzien_frame)
        self.dane_archiwalne_oborty_dzienne_dane_frame.configure(bg='white')
        self.dane_archiwalne_oborty_dzienne_dane_frame.place(relx=1 / 6, rely=1 / 8, relwidth=5 / 6, relheight=7 / 8)

    def create_dane_archiwalne_miesiac_F2(self):
        self.dane_archiwalne_miesiac_frame = tk.Frame(self)
        self.dane_archiwalne_miesiac_frame.configure(bg='#383232', relief='groove', bd=1)
        self.dane_archiwalne_miesiac_frame.place(relx=0.01, rely=0.35, relwidth=0.98, relheight=0.22)

    def create_dane_archiwalne_miesiac_F2_legenda(self):
        self.dane_archiwalne_miesiac_label = tk.Label(self, text=f'WYBIERZ MIESIĄC: ', bg=f'#383232'
                                                      , fg=f'{self.kolor_font}')
        self.dane_archiwalne_miesiac_label.place(relx=0.01, rely=0.32, relwidth=0.1, relheight=0.03)

        self.dane_archiwalne_miesiac_legenda_apteka = tk.Label(self.dane_archiwalne_miesiac_frame, text='APTEKA',
                                                               relief='groove',
                                                               bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.dane_archiwalne_miesiac_legenda_apteka.place(relwidth=1 / 6, relheight=1 / 8)
        self.dane_archiwalne_miesiac_legenda_pacjenci = tk.Label(self.dane_archiwalne_miesiac_frame, text='PACJENCI',
                                                                 relief='groove',
                                                                 bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.dane_archiwalne_miesiac_legenda_pacjenci.place(relx=1 / 6, relwidth=1 / 6, relheight=1 / 8)
        self.dane_archiwalne_miesiac_legenda_brutto = tk.Label(self.dane_archiwalne_miesiac_frame, text='OBROTY BRUTTO',
                                                               relief='groove',
                                                               bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.dane_archiwalne_miesiac_legenda_brutto.place(relx=2 / 6, relwidth=1 / 6, relheight=1 / 8)
        self.dane_archiwalne_miesiac_legenda_netto = tk.Label(self.dane_archiwalne_miesiac_frame, text='OBROTY NETTO',
                                                              relief='groove',
                                                              bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.dane_archiwalne_miesiac_legenda_netto.place(relx=3 / 6, relwidth=1 / 6, relheight=1 / 8)
        self.dane_archiwalne_miesiac_legenda_zysk = tk.Label(self.dane_archiwalne_miesiac_frame, text='ZYSK NETTO',
                                                             relief='groove',
                                                             bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.dane_archiwalne_miesiac_legenda_zysk.place(relx=4 / 6, relwidth=1 / 6, relheight=1 / 8)
        self.dane_archiwalne_miesiac_legenda_magazyn = tk.Label(self.dane_archiwalne_miesiac_frame, text='MARŻA',
                                                                relief='groove',
                                                                bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.dane_archiwalne_miesiac_legenda_magazyn.place(relx=5 / 6, relwidth=1 / 6, relheight=1 / 8)

        self.dane_archiwalne_miesiac_legenda_nazwa_02 = tk.Label(self.dane_archiwalne_miesiac_frame,
                                                                 text='HIPOKRATES 4', relief='groove',
                                                                 bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.dane_archiwalne_miesiac_legenda_nazwa_02.place(rely=1 / 8, relwidth=1 / 6, relheight=1 / 8)
        self.dane_archiwalne_miesiac_legenda_nazwa_04 = tk.Label(self.dane_archiwalne_miesiac_frame, text='HALLERA',
                                                                 relief='groove',
                                                                 bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.dane_archiwalne_miesiac_legenda_nazwa_04.place(rely=2 / 8, relwidth=1 / 6, relheight=1 / 8)
        self.dane_archiwalne_miesiac_legenda_nazwa_05 = tk.Label(self.dane_archiwalne_miesiac_frame,
                                                                 text='PIELGRZYMOWICE', relief='groove',
                                                                 bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.dane_archiwalne_miesiac_legenda_nazwa_05.place(rely=3 / 8, relwidth=1 / 6, relheight=1 / 8)
        self.dane_archiwalne_miesiac_legenda_nazwa_06 = tk.Label(self.dane_archiwalne_miesiac_frame, text='WISŁA',
                                                                 relief='groove',
                                                                 bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.dane_archiwalne_miesiac_legenda_nazwa_06.place(rely=4 / 8, relwidth=1 / 6, relheight=1 / 8)
        self.dane_archiwalne_miesiac_legenda_nazwa_07 = tk.Label(self.dane_archiwalne_miesiac_frame, text='BIEDRONKA',
                                                                 relief='groove',
                                                                 bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.dane_archiwalne_miesiac_legenda_nazwa_07.place(rely=5 / 8, relwidth=1 / 6, relheight=1 / 8)
        self.dane_archiwalne_miesiac_legenda_nazwa_08 = tk.Label(self.dane_archiwalne_miesiac_frame, text='BZIE',
                                                                 relief='groove',
                                                                 bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
        self.dane_archiwalne_miesiac_legenda_nazwa_08.place(rely=6 / 8, relwidth=1 / 6, relheight=1 / 8)

        self.dane_archiwalne_miesiac_legenda_razem = tk.Label(self.dane_archiwalne_miesiac_frame, text='RAZEM',
                                                              relief='groove',
                                                              bg=f'{self.kolor_razem}', fg=f'{self.kolor_font_razem}')
        self.dane_archiwalne_miesiac_legenda_razem.place(rely=7 / 8, relwidth=1 / 6, relheight=1 / 8)

    def create_dane_archiwalne_oborty_miesieczne_dane_frame(self):
        self.dane_archiwalne_oborty_miesieczne_dane_frame = tk.Frame(self.dane_archiwalne_miesiac_frame)
        self.dane_archiwalne_oborty_miesieczne_dane_frame.configure(bg='white')
        self.dane_archiwalne_oborty_miesieczne_dane_frame.place(relx=1 / 6, rely=1 / 8, relwidth=5 / 6, relheight=7 / 8)

    def create_dane_archiwalne_miesiac_wybor_miesiaca_combobox(self):
        self.lista_wyboru = []

        rok_start = 2017
        lista_miesiac = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
        rok = 0
        data = ''

        while True:
            for miesiac in range(12):
                data = f'{rok_start + rok}-{lista_miesiac[miesiac]}'
                self.lista_wyboru.append(data)
                if data == f'{datetime.datetime.now().year}-{datetime.datetime.now().strftime("%m")}':
                    break
            rok += 1
            if data == f'{datetime.datetime.now().year}-{datetime.datetime.now().strftime("%m")}':
                break

        self.lista_wyboru.reverse()

        self.dane_archiwalne_miesiac_combobox = ttk.Combobox(self, values=self.lista_wyboru, state='readonly')
        self.dane_archiwalne_miesiac_combobox.place(relx=0.11, rely=0.32, relwidth=0.15)
        self.dane_archiwalne_miesiac_combobox.current(0)
        self.dane_archiwalne_miesiac_combobox.bind("<<ComboboxSelected>>",
                                                   self.update_dane_archiwalne_obroty_miesieczne_dane)

    def create_dane_archiwalne_apteka_F3(self):
        self.dane_archiwalne_apteka_frame = tk.Frame(self)
        self.dane_archiwalne_apteka_frame.configure(bg='#383232', relief='groove', bd=1)
        self.dane_archiwalne_apteka_frame.place(relx=0.01, rely=0.63, relwidth=0.98, relheight=0.35)

    def create_dane_archiwalne_apteka_F3_buttons(self):
        self.apteka_button_02 = tk.Button(self, text="HIPOKRATES 4", bg='#544949', fg=f'{self.kolor_razem}',
                                          command=lambda: self.set_button_apteka_F3_state(2))
        self.apteka_button_02.place(relx=0.01, rely=0.59, relwidth=0.12, relheight=0.03)
        self.apteka_button_04 = tk.Button(self, text="HALLERA", bg='#544949', fg=f'{self.kolor_razem}',
                                          command=lambda: self.set_button_apteka_F3_state(4))
        self.apteka_button_04.place(relx=0.14, rely=0.59, relwidth=0.12, relheight=0.03)
        self.apteka_button_05 = tk.Button(self, text="PIELGRZYMOWICE", bg='#544949', fg=f'{self.kolor_razem}',
                                          command=lambda: self.set_button_apteka_F3_state(5))
        self.apteka_button_05.place(relx=0.27, rely=0.59, relwidth=0.12, relheight=0.03)
        self.apteka_button_06 = tk.Button(self, text="WISŁA", bg='#544949', fg=f'{self.kolor_razem}',
                                          command=lambda: self.set_button_apteka_F3_state(6))
        self.apteka_button_06.place(relx=0.40, rely=0.59, relwidth=0.12, relheight=0.03)
        self.apteka_button_07 = tk.Button(self, text="BIEDRONKA", bg='#544949', fg=f'{self.kolor_razem}',
                                          command=lambda: self.set_button_apteka_F3_state(7))
        self.apteka_button_07.place(relx=0.53, rely=0.59, relwidth=0.12, relheight=0.03)
        self.apteka_button_08 = tk.Button(self, text="BZIE", bg='#544949', fg=f'{self.kolor_razem}',
                                          command=lambda: self.set_button_apteka_F3_state(8))
        self.apteka_button_08.place(relx=0.66, rely=0.59, relwidth=0.12, relheight=0.03)
        self.apteka_button_razem = tk.Button(self, text="RAZEM", bg='#544949', fg=f'{self.kolor_razem}',
                                             command=lambda: self.set_button_apteka_F3_state(0))
        self.apteka_button_razem.place(relx=0.79, rely=0.59, relwidth=0.12, relheight=0.03)
        self.buttons_lista = [self.apteka_button_razem, 'index_1', self.apteka_button_02, 'index_3',
                              self.apteka_button_04,
                              self.apteka_button_05, self.apteka_button_06, self.apteka_button_07,
                              self.apteka_button_08]

    def create_dane_archiwalne_apteka_F3_treeview(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', fieldbackground="#383232", background="#383232", foreground='white')
        style.configure("Treeview.Heading", background="#383232", foreground="white")
        style.map('Treeview.Heading', background=[('disabled', '#383232')])

        def fixed_map(option):  # naprawa buga wersji dla Python 3.7 przy wyświetlaniu koloru linii w treeview
            return [elm for elm in style.map("Treeview", query_opt=option)
                    if elm[:2] != ("!disabled", "!selected")]

        style.map("Treeview", foreground=fixed_map("foreground"),
                  background=fixed_map("background"))

        self.columns_dane_archiwalne_apteka = ('MIESIĄC', 'PACJENCI', 'OBRÓT BRUTTO', 'OBRÓT NETTO', 'ZYSK NETTO')
        self.treeview_dane_archiwalne_apteka = ttk.Treeview(self.dane_archiwalne_apteka_frame,
                                                            columns=self.columns_dane_archiwalne_apteka,
                                                            show='headings',
                                                            style="Treeview", selectmode="browse")

        self.treeview_dane_archiwalne_apteka.heading('MIESIĄC', text='MIESIĄC')
        self.treeview_dane_archiwalne_apteka.column('MIESIĄC', minwidth=0, width=50, stretch='yes', anchor='center')
        self.treeview_dane_archiwalne_apteka.heading('PACJENCI', text='PACJENCI')
        self.treeview_dane_archiwalne_apteka.column('PACJENCI', minwidth=0, width=150, stretch='yes', anchor='center')
        self.treeview_dane_archiwalne_apteka.heading('OBRÓT BRUTTO', text='OBRÓT BRUTTO')
        self.treeview_dane_archiwalne_apteka.column('OBRÓT BRUTTO', minwidth=0, width=150, stretch='yes',
                                                    anchor='center')
        self.treeview_dane_archiwalne_apteka.heading('OBRÓT NETTO', text='OBRÓT NETTO')
        self.treeview_dane_archiwalne_apteka.column('OBRÓT NETTO', minwidth=0, stretch='yes', anchor='center')
        self.treeview_dane_archiwalne_apteka.heading('ZYSK NETTO', text='ZYSK NETTO')
        self.treeview_dane_archiwalne_apteka.column('ZYSK NETTO', minwidth=0, stretch='yes', anchor='center')

        self.scrolly = ttk.Scrollbar(self.treeview_dane_archiwalne_apteka, orient='vertical',
                                     command=self.treeview_dane_archiwalne_apteka.yview)
        self.treeview_dane_archiwalne_apteka.configure(yscrollcommand=self.scrolly.set)
        map(lambda col: col.configure(yscrollcommand=self.scrolly.set), self.columns_dane_archiwalne_apteka)
        self.scrolly.pack(side=tk.RIGHT, fill=tk.Y)
        map(lambda col: col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True), self.columns_dane_archiwalne_apteka)
        self.treeview_dane_archiwalne_apteka.pack(expand='yes', fill='both')
        # self.treeview_dane_archiwalne_apteka.bind("<Double-1>", self.poprawa_wpisu)

    def set_button_apteka_F3_state(self, id_apteka):
        for n in range(9):
            if n in [1, 3]:
                continue
            if id_apteka == n:
                self.buttons_lista[n].config(bg='#085420')
            else:
                self.buttons_lista[n].config(bg='#544949')
        self.update_dane_archiwalne_apteka_F3_treeview(id_apteka)

    def get_dane_archiwalne_obroty_dzienne_data(self):
        data = self.dane_archiwalne_dzien_data_picker.get_date()
        self.dane_archiwalne_obroty_dzienne_dict = {}
        self.all_pacjenci = 0
        self.all_brutto = 0
        self.all_netto = 0
        self.all_zysk = 0
        self.all_marza = 0

        for n in range(2, 9):
            self.guerry_obroty_dzienne = f'SELECT * FROM obroty_dzienne WHERE data = "{data}" ' \
                                         f'AND apteka = {n}'
            self.obroty_dzienne_dane = self.zpt_database.mysql_querry(self.guerry_obroty_dzienne)

            if self.obroty_dzienne_dane == []:
                self.dane_archiwalne_obroty_dzienne_dict[f'{n}'] = [0, 0, 0, 0, 0]
            else:
                if self.obroty_dzienne_dane[0][4] == 0:
                    self.marza = 0
                else:
                    self.marza = round((self.obroty_dzienne_dane[0][5] * 100) / self.obroty_dzienne_dane[0][4], 2)
                self.dane_archiwalne_obroty_dzienne_dict[f'{n}'] = [self.obroty_dzienne_dane[0][2],
                                                                    self.obroty_dzienne_dane[0][3],
                                                                    self.obroty_dzienne_dane[0][4],
                                                                    self.obroty_dzienne_dane[0][5], self.marza]
                self.all_pacjenci += self.obroty_dzienne_dane[0][2]
                self.all_brutto += self.obroty_dzienne_dane[0][3]
                self.all_netto += self.obroty_dzienne_dane[0][4]
                self.all_zysk += self.obroty_dzienne_dane[0][5]
        if self.all_zysk != 0:
            self.all_marza = (self.all_zysk * 100) / self.all_netto
        else:
            self.all_marza = 0
        self.dane_archiwalne_obroty_dzienne_dict[f'razem'] = [self.all_pacjenci, round(self.all_brutto, 2),
                                                              round(self.all_netto, 2), round(self.all_zysk, 2),
                                                              round(self.all_marza, 2)]
        return self.dane_archiwalne_obroty_dzienne_dict

    def update_dane_archiwalne_obroty_dzienne(self, event):
        self.get_dane_archiwalne_obroty_dzienne_data()
        if self.dane_archiwalne_oborty_dzienne_dane_frame:
            self.dane_archiwalne_oborty_dzienne_dane_frame.destroy()
        self.create_dane_archiwalne_oborty_dzienne_dane_frame()

        self.obroty_dzienne_legenda_razem_pacjeci = tk.Label(self.dane_archiwalne_oborty_dzienne_dane_frame,
                                                             text=f'{self.dane_archiwalne_obroty_dzienne_dict[f"razem"][0]}',
                                                             relief='groove', bg=f'{self.kolor_razem}',
                                                             fg=f'{self.kolor_font_razem}')
        self.obroty_dzienne_legenda_razem_pacjeci.place(rely=6 / 7, relwidth=1 / 5, relheight=1 / 7)
        self.obroty_dzienne_legenda_razem_brutto = tk.Label(self.dane_archiwalne_oborty_dzienne_dane_frame,
                                                            text=f'{self.currency_format(self.dane_archiwalne_obroty_dzienne_dict[f"razem"][1])} zł'
                                                            , relief='groove', bg=f'{self.kolor_razem}',
                                                            fg=f'{self.kolor_font_razem}')
        self.obroty_dzienne_legenda_razem_brutto.place(relx=1 / 5, rely=6 / 7, relwidth=1 / 5, relheight=1 / 7)
        self.obroty_dzienne_legenda_razem_netto = tk.Label(self.dane_archiwalne_oborty_dzienne_dane_frame,
                                                           text=f'{self.currency_format(self.dane_archiwalne_obroty_dzienne_dict[f"razem"][2])} zł'
                                                           , relief='groove', bg=f'{self.kolor_razem}',
                                                           fg=f'{self.kolor_font_razem}')
        self.obroty_dzienne_legenda_razem_netto.place(relx=2 / 5, rely=6 / 7, relwidth=1 / 5, relheight=1 / 7)
        self.obroty_dzienne_legenda_razem_zysk = tk.Label(self.dane_archiwalne_oborty_dzienne_dane_frame,
                                                          text=f'{self.currency_format(self.dane_archiwalne_obroty_dzienne_dict[f"razem"][3])} zł'
                                                          , relief='groove', bg=f'{self.kolor_razem}',
                                                          fg=f'{self.kolor_font_razem}')
        self.obroty_dzienne_legenda_razem_zysk.place(relx=3 / 5, rely=6 / 7, relwidth=1 / 5, relheight=1 / 7)
        self.obroty_dzienne_legenda_razem_marza = tk.Label(self.dane_archiwalne_oborty_dzienne_dane_frame,
                                                           text=f'{self.currency_format(self.dane_archiwalne_obroty_dzienne_dict[f"razem"][4])} %'
                                                           , relief='groove', bg=f'{self.kolor_razem}',
                                                           fg=f'{self.kolor_font_razem}')
        self.obroty_dzienne_legenda_razem_marza.place(relx=4 / 5, rely=6 / 7, relwidth=1 / 5, relheight=1 / 7)

        for n in range(2, 9):
            m = 0
            if n == 3:
                continue

            if n > 3:
                m = n - 1
            else:
                m = n

            self.obroty_dzienne_pacjenci = tk.Label(self.dane_archiwalne_oborty_dzienne_dane_frame,
                                                    text=f'{self.dane_archiwalne_obroty_dzienne_dict[f"{n}"][0]}',
                                                    relief='groove',
                                                    bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
            self.obroty_dzienne_pacjenci.place(rely=(m - 2) / 7, relwidth=1 / 5, relheight=1 / 7)
            self.obroty_dzienne_brutto = tk.Label(self.dane_archiwalne_oborty_dzienne_dane_frame,
                                                  text=f'{self.currency_format(self.dane_archiwalne_obroty_dzienne_dict[f"{n}"][1])} zł',
                                                  relief='groove',
                                                  bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
            self.obroty_dzienne_brutto.place(relx=1 / 5, rely=(m - 2) / 7, relwidth=1 / 5, relheight=1 / 7)
            self.obroty_dzienne_netto = tk.Label(self.dane_archiwalne_oborty_dzienne_dane_frame,
                                                 text=f'{self.currency_format(self.dane_archiwalne_obroty_dzienne_dict[f"{n}"][2])} zł',
                                                 relief='groove',
                                                 bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
            self.obroty_dzienne_netto.place(relx=2 / 5, rely=(m - 2) / 7, relwidth=1 / 5, relheight=1 / 7)
            self.obroty_dzienne_zysk = tk.Label(self.dane_archiwalne_oborty_dzienne_dane_frame,
                                                text=f'{self.currency_format(self.dane_archiwalne_obroty_dzienne_dict[f"{n}"][3])} zł',
                                                relief='groove',
                                                bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
            self.obroty_dzienne_zysk.place(relx=3 / 5, rely=(m - 2) / 7, relwidth=1 / 5, relheight=1 / 7)
            self.obroty_dzienne_marza = tk.Label(self.dane_archiwalne_oborty_dzienne_dane_frame,
                                                 text=f'{self.currency_format(self.dane_archiwalne_obroty_dzienne_dict[f"{n}"][4])} %',
                                                 relief='groove',
                                                 bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
            self.obroty_dzienne_marza.place(relx=4 / 5, rely=(m - 2) / 7, relwidth=1 / 5, relheight=1 / 7)

    @staticmethod
    def currency_format(i):
        currency = str(i)
        if currency == '0':
            return currency

        if currency[-3] == '.':
            pass
        else:
            currency += '0'

        if len(currency) > 6:
            sep_number = int(len(currency) / 3) - 1
            m = 0
            for n in range(sep_number):
                currency = currency[:-(6 + (3 * n) + m)] + ' ' + currency[-(6 + (3 * n) + m):]
                m += 1
        return currency

    def get_dane_archiwalne_obroty_miesieczne_data(self):
        data = self.dane_archiwalne_miesiac_combobox.get()
        self.dane_archiwalne_obroty_miesieczne_dict = {}
        self.all_pacjenci = 0
        self.all_brutto = 0
        self.all_netto = 0
        self.all_zysk = 0

        for n in range(2, 9):
            self.guerry_obroty_miesieczne = f"SELECT SUM(pacjenci), SUM(obrot_brutto), SUM(obrot_netto), SUM(zysk_netto)" \
                                            f" FROM obroty_dzienne WHERE data LIKE '%{data}%' AND apteka = {n}"
            self.obroty_miesieczne_dane = self.zpt_database.mysql_querry(self.guerry_obroty_miesieczne)
            if self.obroty_miesieczne_dane == [(None, None, None, None)]:
                self.dane_archiwalne_obroty_miesieczne_dict[f'{n}'] = [0, 0, 0, 0, 0]

            else:
                if self.obroty_miesieczne_dane[0][2] == 0:
                    self.marza = 0
                else:
                    self.marza = round((self.obroty_miesieczne_dane[0][3] / self.obroty_miesieczne_dane[0][2]) * 100, 2)
                self.dane_archiwalne_obroty_miesieczne_dict[f'{n}'] = [int(self.obroty_miesieczne_dane[0][0]),
                                                                       round(self.obroty_miesieczne_dane[0][1], 2),
                                                                       round(self.obroty_miesieczne_dane[0][2], 2),
                                                                       round(self.obroty_miesieczne_dane[0][3], 2),
                                                                       self.marza]
                self.all_pacjenci += self.obroty_miesieczne_dane[0][0]
                self.all_brutto += self.obroty_miesieczne_dane[0][1]
                self.all_netto += self.obroty_miesieczne_dane[0][2]
                self.all_zysk += self.obroty_miesieczne_dane[0][3]
            if self.all_netto != 0:
                self.marza_all = round((self.all_zysk / self.all_netto) * 100, 2)
            else:
                self.marza_all = 0
            self.dane_archiwalne_obroty_miesieczne_dict[f'razem'] = [int(self.all_pacjenci), round(self.all_brutto, 2),
                                                                     round(self.all_netto, 2), round(self.all_zysk, 2),
                                                                     round(self.marza_all, 2)]
        return self.dane_archiwalne_obroty_miesieczne_dict

    def update_dane_archiwalne_obroty_miesieczne_dane(self, event):
        self.get_dane_archiwalne_obroty_miesieczne_data()
        if self.dane_archiwalne_oborty_miesieczne_dane_frame:
            self.dane_archiwalne_oborty_miesieczne_dane_frame.destroy()
        self.create_dane_archiwalne_oborty_miesieczne_dane_frame()
        self.obroty_miesieczne_legenda_razem_pacjeci = tk.Label(self.dane_archiwalne_oborty_miesieczne_dane_frame,
                                                                text=f'{self.dane_archiwalne_obroty_miesieczne_dict["razem"][0]}',
                                                                relief='groove',
                                                                bg=f'{self.kolor_razem}', fg=f'{self.kolor_font_razem}')
        self.obroty_miesieczne_legenda_razem_pacjeci.place(rely=6 / 7, relwidth=1 / 5, relheight=1 / 7)
        self.obroty_miesieczne_legenda_razem_brutto = tk.Label(self.dane_archiwalne_oborty_miesieczne_dane_frame,
                                                               text=f'{self.currency_format(self.dane_archiwalne_obroty_miesieczne_dict["razem"][1])} zł',
                                                               relief='groove',
                                                               bg=f'{self.kolor_razem}', fg=f'{self.kolor_font_razem}')
        self.obroty_miesieczne_legenda_razem_brutto.place(relx=1 / 5, rely=6 / 7, relwidth=1 / 5, relheight=1 / 7)
        self.obroty_miesieczne_legenda_razem_netto = tk.Label(self.dane_archiwalne_oborty_miesieczne_dane_frame,
                                                              text=f'{self.currency_format(self.dane_archiwalne_obroty_miesieczne_dict["razem"][2])} zł',
                                                              relief='groove',
                                                              bg=f'{self.kolor_razem}', fg=f'{self.kolor_font_razem}')
        self.obroty_miesieczne_legenda_razem_netto.place(relx=2 / 5, rely=6 / 7, relwidth=1 / 5, relheight=1 / 7)
        self.obroty_miesieczne_legenda_razem_zysk = tk.Label(self.dane_archiwalne_oborty_miesieczne_dane_frame,
                                                             text=f'{self.currency_format(self.dane_archiwalne_obroty_miesieczne_dict["razem"][3])} zł',
                                                             relief='groove',
                                                             bg=f'{self.kolor_razem}', fg=f'{self.kolor_font_razem}')
        self.obroty_miesieczne_legenda_razem_zysk.place(relx=3 / 5, rely=6 / 7, relwidth=1 / 5, relheight=1 / 7)
        self.obroty_miesieczne_legenda_razem_marza = tk.Label(self.dane_archiwalne_oborty_miesieczne_dane_frame,
                                                              text=f'{self.dane_archiwalne_obroty_miesieczne_dict["razem"][4]} %',
                                                              relief='groove',
                                                              bg=f'{self.kolor_razem}', fg=f'{self.kolor_font_razem}')
        self.obroty_miesieczne_legenda_razem_marza.place(relx=4 / 5, rely=6 / 7, relwidth=1 / 5, relheight=1 / 7)

        for n in range(2, 9):
            m = 0
            if n == 3:
                continue

            if n > 3:
                m = n - 1
            else:
                m = n
            self.obroty_miesieczne_pacjenci = tk.Label(self.dane_archiwalne_oborty_miesieczne_dane_frame,
                                                       text=f'{self.dane_archiwalne_obroty_miesieczne_dict[f"{n}"][0]}',
                                                       relief='groove',
                                                       bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
            self.obroty_miesieczne_pacjenci.place(rely=(m - 2) / 7, relwidth=1 / 5, relheight=1 / 7)
            self.obroty_miesieczne_brutto = tk.Label(self.dane_archiwalne_oborty_miesieczne_dane_frame,
                                                     text=f'{self.currency_format(self.dane_archiwalne_obroty_miesieczne_dict[f"{n}"][1])} zł',
                                                     relief='groove',
                                                     bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
            self.obroty_miesieczne_brutto.place(relx=1 / 5, rely=(m - 2) / 7, relwidth=1 / 5, relheight=1 / 7)
            self.obroty_miesieczne_netto = tk.Label(self.dane_archiwalne_oborty_miesieczne_dane_frame,
                                                    text=f'{self.currency_format(self.dane_archiwalne_obroty_miesieczne_dict[f"{n}"][2])} zł',
                                                    relief='groove',
                                                    bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
            self.obroty_miesieczne_netto.place(relx=2 / 5, rely=(m - 2) / 7, relwidth=1 / 5, relheight=1 / 7)
            self.obroty_miesieczne_zysk = tk.Label(self.dane_archiwalne_oborty_miesieczne_dane_frame,
                                                   text=f'{self.currency_format(self.dane_archiwalne_obroty_miesieczne_dict[f"{n}"][3])} zł',
                                                   relief='groove',
                                                   bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
            self.obroty_miesieczne_zysk.place(relx=3 / 5, rely=(m - 2) / 7, relwidth=1 / 5, relheight=1 / 7)
            self.obroty_miesieczne_marza = tk.Label(self.dane_archiwalne_oborty_miesieczne_dane_frame,
                                                    text=f'{self.dane_archiwalne_obroty_miesieczne_dict[f"{n}"][4]} %',
                                                    relief='groove',
                                                    bg=f'{self.kolor_legenda}', fg=f'{self.kolor_font}')
            self.obroty_miesieczne_marza.place(relx=4 / 5, rely=(m - 2) / 7, relwidth=1 / 5, relheight=1 / 7)

    def get_dane_archiwalne_apteka(self, id_apteka):
        self.dane_archiwalne_obroty_miesieczne_apteka_list = []
        for m in self.lista_wyboru:
            if id_apteka != 0:
                self.guerry_obroty_miesieczne = f"SELECT SUM(pacjenci), SUM(obrot_brutto), SUM(obrot_netto), SUM(zysk_netto)" \
                                                f" FROM obroty_dzienne WHERE data LIKE '%{m}%' AND apteka = {id_apteka}"
            else:
                self.guerry_obroty_miesieczne = f"SELECT SUM(pacjenci), SUM(obrot_brutto), SUM(obrot_netto), SUM(zysk_netto)" \
                                                f" FROM obroty_dzienne WHERE data LIKE '%{m}%'"
            self.obroty_miesieczne_dane = self.zpt_database.mysql_querry(self.guerry_obroty_miesieczne)
            if self.obroty_miesieczne_dane == [(None, None, None, None)]:
                self.dane_archiwalne_obroty_miesieczne_apteka_list.append([m, 0, 0, 0, 0])
            else:
                self.dane_archiwalne_obroty_miesieczne_apteka_list.append([m, int(self.obroty_miesieczne_dane[0][0]),
                                                                           round(self.obroty_miesieczne_dane[0][1], 2),
                                                                           round(self.obroty_miesieczne_dane[0][2], 2),
                                                                           round(self.obroty_miesieczne_dane[0][3], 2)])
        return self.dane_archiwalne_obroty_miesieczne_apteka_list

    def update_dane_archiwalne_apteka_F3_treeview(self, id_apteki):
        dane = self.get_dane_archiwalne_apteka(id_apteki)
        self.treeview_dane_archiwalne_apteka.delete(*self.treeview_dane_archiwalne_apteka.get_children())
        i = 0
        for n in dane:
            i += 1
            miesiac = n[0]
            pacjenci = n[1]
            obrot_brutto = self.currency_format(n[2])
            obrot_netto = self.currency_format(n[3])
            zysk_netto = self.currency_format(n[4])

            if i % 2 == 0:
                background_gotowki = 'background_dark'
            else:
                background_gotowki = 'background_light'

            self.treeview_dane_archiwalne_apteka.tag_configure('background_dark', background='#383232')
            self.treeview_dane_archiwalne_apteka.tag_configure('background_light', background='#262424')
            self.treeview_dane_archiwalne_apteka.tag_configure('foreground_bank', foreground='red')
            self.treeview_dane_archiwalne_apteka.tag_configure('foreground_plus', foreground='white')

            self.treeview_dane_archiwalne_apteka.insert('', 'end', values=(miesiac, pacjenci, f'{obrot_brutto} zł',
                                                                           f'{obrot_netto} zł', f'{zysk_netto} zł'),
                                                        tags=(background_gotowki))

class Pracownicy_frame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.configure(bg='#383232')
        self.kolor_razem = '#b58b14'
        self.kolor_font = 'white'
        self.kolor_font_razem = 'black'
        self.kolor_legenda = '#383232'
        self.zpt_database = ZPT_Database.ZPT_base()
        self.dane_do_wyplaty = []
        self.create_lista_pracownicy()
        self.create_pracownicy_LF()
        self.create_pracownicy_RF()

    def create_pracownicy_LF(self):
        self.pracownicy_LF = tk.Frame(self)
        self.pracownicy_LF.configure(bg='#383232', relief='groove', bd=1)
        self.pracownicy_LF.place(relx=0.01, rely=0.02, relwidth=0.48, relheight=0.96)
        self.create_dodaj_urlop_field()
        self.create_pracownicy_combobox()
        self.create_urlopy_treeview()
        self.update_urlopy_treeview()
        self.create_nieobecnosci_treeview()
        self.update_nieobecnosci_treeview()

    def create_pracownicy_RF(self):
        self.pracownicy_RF = tk.Frame(self)
        self.pracownicy_RF.configure(bg='#383232', relief='groove', bd=1)
        self.pracownicy_RF.place(relx=0.51, rely=0.02, relwidth=0.48, relheight=0.96)
        self.create_new_edit_button()
        self.create_info_pracownik_labels()
        self.create_wynagrodzenia_field()
        self.create_wynagrodzania_treeview()
        self.set_okres_wynagrodzenia()

    def create_lista_pracownicy(self):
        self.lista_pracownicy = ['']
        with open('slowniki_pracownicy.json', encoding='utf-8') as json_file:
            data = json.load(json_file)
        for key in data:
            self.lista_pracownicy.append(f'{data[key]["nazwisko"]} {data[key]["imie"]}')
        return self.lista_pracownicy.sort()

    def create_pracownicy_combobox(self):
        self.pracownicy_combobox = ttk.Combobox(self.pracownicy_LF, values=self.lista_pracownicy,
                                                height=30, state='readonly')
        self.pracownicy_combobox.place(relx=0.01, rely=0.02, relwidth=0.98)
        self.pracownicy_combobox.bind("<<ComboboxSelected>>", self.wyswietl_dane_pracownika)

    def wyswietl_dane_pracownika(self, event):
        self.update_urlopy_treeview()
        self.update_nieobecnosci_treeview()
        id_pracownika = self.get_pracownik_id()
        self.update_info_pracownik_labels(id_pracownika)

    def create_urlopy_treeview(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', fieldbackground="#383232", background="#383232", foreground='white')
        style.configure("Treeview.Heading", background="#383232", foreground="white")
        style.map('Treeview.Heading', background=[('disabled', '#383232')])

        def fixed_map(option):  # naprawa buga wersji dla Python 3.7 przy wyświetlaniu koloru linii w treeview
            return [elm for elm in style.map("Treeview", query_opt=option)
                    if elm[:2] != ("!disabled", "!selected")]

        style.map("Treeview", foreground=fixed_map("foreground"),
                  background=fixed_map("background"))

        self.pracownicy_treeview_frame = tk.Frame(self.pracownicy_LF)
        self.pracownicy_treeview_frame.configure(bg='#383232', relief='groove', bd=1)
        self.pracownicy_treeview_frame.place(relx=0.01, rely=0.06, relwidth=0.98, relheight=0.59)

        self.pracownicy_columns = self.set_treeview_columns()
        self.pracownicy_treeview = ttk.Treeview(self.pracownicy_treeview_frame, columns=self.pracownicy_columns,
                                                show='headings',
                                                style="Treeview", selectmode="browse")

        self.pracownicy_treeview.heading('DNI', text='DNI')
        self.pracownicy_treeview.column('DNI', width=50, stretch='no', anchor='center')
        self.pracownicy_treeview.heading(f'{self.pracownicy_columns[1]}', text=f'{self.pracownicy_columns[1]}')
        self.pracownicy_treeview.column(f'{self.pracownicy_columns[1]}', minwidth=100, stretch='yes', anchor='center')
        self.pracownicy_treeview.heading(f'{self.pracownicy_columns[2]}', text=f'{self.pracownicy_columns[2]}')
        self.pracownicy_treeview.column(f'{self.pracownicy_columns[2]}', minwidth=100, stretch='yes', anchor='center')
        self.pracownicy_treeview.heading(f'{self.pracownicy_columns[3]}', text=f'{self.pracownicy_columns[3]}')
        self.pracownicy_treeview.column(f'{self.pracownicy_columns[3]}', minwidth=100, stretch='yes', anchor='center')
        self.pracownicy_treeview.heading(f'{self.pracownicy_columns[4]}', text=f'{self.pracownicy_columns[4]}')
        self.pracownicy_treeview.column(f'{self.pracownicy_columns[4]}', minwidth=100, stretch='yes', anchor='center')

        # self.scrolly = ttk.Scrollbar(self.pracownicy_treeview_frame, orient='vertical',
        #                              command=self.pracownicy_treeview.yview)
        # self.pracownicy_treeview.configure(yscrollcommand=self.scrolly.set)
        # map(lambda col: col.configure(yscrollcommand=self.scrolly.set), self.pracownicy_columns)
        # self.scrolly.pack(side=tk.RIGHT, fill=tk.Y)
        # map(lambda col: col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True), self.pracownicy_columns)
        self.pracownicy_treeview.pack(expand='yes', fill='both')
        self.pracownicy_treeview.bind("<Double-1>", self.delete_urlop)

    def update_urlopy_treeview(self):
        daty = self.get_pracownicy_treeview_data()
        # print(daty)
        self.pracownicy_treeview.delete(*self.pracownicy_treeview.get_children())
        if daty != 0:
            for n in range(26):
                if n % 2 == 0:
                    background = 'background_dark'
                else:
                    background = 'background_light'

                self.pracownicy_treeview.tag_configure('background_dark', background='#383232')
                self.pracownicy_treeview.tag_configure('background_light', background='#262424')
                self.pracownicy_treeview.insert('', 'end', values=(n + 1, f'{daty[0][n]}', f'{daty[1][n]}',
                                                                   f'{daty[2][n]}', f'{daty[3][n]}'), tags=(background))

    def delete_urlop(self, event):
        id_pracownika = self.get_pracownik_id()
        curItem = self.pracownicy_treeview.focus()
        daty_urlopy_z_lini = self.pracownicy_treeview.item(curItem)['values']
        data_do_skasowania = ''
        for d in daty_urlopy_z_lini:
            if d != '':
                data_do_skasowania = d
            else:
                break
        querry = f'DELETE FROM urlopy WHERE pracownik={id_pracownika} AND rodzaj=1 AND data="{data_do_skasowania}"'
        self.zpt_database.mysql_no_fetch_querry(querry)
        self.update_urlopy_treeview()

    @staticmethod
    def set_treeview_columns():
        rok = datetime.datetime.now().year
        lista_column = ['DNI']
        for n in range(4):
            lista_column.append(rok - 3 + n)
        return lista_column

    def get_pracownik_id(self):
        pracownik = self.pracownicy_combobox.get()
        if pracownik == '':
            self.dodaj_wolne_button.configure(state='disabled')
            return 0
        else:
            self.dodaj_wolne_button.configure(state='normal')
            with open('slowniki_pracownicy.json', encoding='utf-8') as json_file:
                data = json.load(json_file)
            for key in data:
                if data[key]['pelna_nazwa'] == pracownik:
                    return key

    def get_pracownicy_treeview_data(self):  # 4 listy z datami urlopów dla każdego roku jedna lista
        id_pracownika = self.get_pracownik_id()
        if id_pracownika == 0:
            return 0
        else:
            lista_dat_urlopow = []
            self.ilosc_dni_urlopu_do_konca_roku = 0
            for r in range(4):
                rok = datetime.datetime.now().year - 3 + r
                querry_urlopy_daty = f"SELECT data FROM urlopy WHERE urlop_rok = {rok} AND (rodzaj = 1 OR rodzaj = 6) AND pracownik = {id_pracownika} " \
                                     f"ORDER BY data ASC"
                urlopy_daty = self.zpt_database.mysql_querry(querry_urlopy_daty)
                lista_dat_urlopow.append(self.formatuj_urlopy_lista(urlopy_daty))
            return lista_dat_urlopow

    def formatuj_urlopy_lista(self, lista):
        lista_output = []
        for d in lista:
            lista_output.append(d[0])
        while len(lista_output) < 26:
            lista_output.append('')
            self.ilosc_dni_urlopu_do_konca_roku += 1
        return lista_output

    def create_new_edit_button(self):
        self.new_edit_button = tk.Button(self.pracownicy_RF, text='NOWY \ EDYTUJ', bg='#544949',
                                         fg=f'{self.kolor_razem}', command=self.create_new_edit_toplevel)
        self.new_edit_button.place(relx=0.05, rely=0.04, relwidth=0.2, relheight=0.03)

    def create_info_pracownik_labels(self):
        self.imie_nazwisko_lb = tk.Label(self.pracownicy_RF, text='', bg='#383232', font=("Verdena", "20", "bold")
                                         , fg='#80e89b', anchor='w')
        self.imie_nazwisko_lb.place(relx=0.3, rely=0.03, relwidth=0.65, relheight=0.05)
        self.stanowisko_lb = tk.Label(self.pracownicy_RF, text='', bg='#383232', font=("Verdena", "12", "bold")
                                      , fg='#c2d1c6', anchor='w')
        self.stanowisko_lb.place(relx=0.05, rely=0.09, relwidth=0.9, relheight=0.03)
        self.placowka_lb = tk.Label(self.pracownicy_RF, text='', bg='#383232', font=("Verdena", "12", "bold")
                                    , fg='#c2d1c6', anchor='w')
        self.placowka_lb.place(relx=0.05, rely=0.12, relwidth=0.9, relheight=0.03)
        self.dni_urlopu_do_konca_roku = tk.Label(self.pracownicy_RF, text='', bg='#383232',
                                                 font=("Verdena", "12", "bold")
                                                 , fg='#c2d1c6', anchor='w')
        self.dni_urlopu_do_konca_roku.place(relx=0.05, rely=0.15, relwidth=0.9, relheight=0.03)
        self.pensja_brutto = tk.Label(self.pracownicy_RF, text='', bg='#383232',
                                      font=("Verdena", "12", "bold")
                                      , fg='#c2d1c6', anchor='w')
        self.pensja_brutto.place(relx=0.05, rely=0.18, relwidth=0.9, relheight=0.03)
        self.badania_lekarskie = tk.Label(self.pracownicy_RF, text='', bg='#383232',
                                          font=("Verdena", "12", "bold")
                                          , fg='#c2d1c6', anchor='w')
        self.badania_lekarskie.place(relx=0.05, rely=0.21, relwidth=0.9, relheight=0.03)
        self.data_zakonczenia_umowy = tk.Label(self.pracownicy_RF, text='', bg='#383232',
                                               font=("Verdena", "12", "bold")
                                               , fg='#c2d1c6', anchor='w')
        self.data_zakonczenia_umowy.place(relx=0.05, rely=0.24, relwidth=0.9, relheight=0.03)

        self.data_urodzenia = tk.Label(self.pracownicy_RF, text='', bg='#383232',
                                       font=("Verdena", "12", "bold")
                                       , fg='#c2d1c6', anchor='w')
        self.data_urodzenia.place(relx=0.05, rely=0.27, relwidth=0.9, relheight=0.03)

    def update_info_pracownik_labels(self, id_pracownika):
        if id_pracownika == 0:
            self.imie_nazwisko_lb.config(text='')
            self.stanowisko_lb.config(text='')
            self.placowka_lb.config(text='')
            self.dni_urlopu_do_konca_roku.config(text='')
            self.pensja_brutto.config(text='')
            self.badania_lekarskie.config(text='')
            self.data_zakonczenia_umowy.config(text='')
            self.data_urodzenia.config(text='')

        else:
            with open('slowniki_pracownicy.json', encoding='utf-8') as json_file:
                data = json.load(json_file)
                self.imie_nazwisko_lb.config(text=f'{data[id_pracownika]["pelna_nazwa"].upper()}')
                if data[id_pracownika]['aktywny'] == 'NIE':
                    self.imie_nazwisko_lb.config(fg='#9e9e9e')
                else:
                    self.imie_nazwisko_lb.config(fg='#80e89b')
                self.stanowisko_lb.config(text=f'STANOWISKO:\t{data[id_pracownika]["stanowisko"].upper()}')
                self.placowka_lb.config(text=f'PLACÓWKA:\t{data[id_pracownika]["placowka"].upper()}')
                if data[id_pracownika]['aktywny'] == 'NIE':
                    self.dni_urlopu_do_konca_roku.config(text=f'DNI URLOPU:\t---')
                    self.badania_lekarskie.config(text=f'BADANIA LEK.:\t---')
                else:
                    self.dni_urlopu_do_konca_roku.config(text=f'DNI URLOPU:\t{self.ilosc_dni_urlopu_do_konca_roku} DNI')
                    self.badania_lekarskie.config(text=f'BADANIA LEK.:\t{data[id_pracownika]["badania"]}')
                self.pensja_brutto.config(text=f'PENSJA:\t\t{data[id_pracownika]["pensja"]} ZŁ BRUTTO')
                self.data_zakonczenia_umowy.config(
                    text=f'KONIEC UMOWY:\t{data[id_pracownika]["data_zakonczenia_umowy"]}')
                self.data_urodzenia.config(text=f'DATA UR.:\t{data[id_pracownika]["data_urodzenia"]}')

    def create_new_edit_toplevel(self):
        self.new_edit_toplevel = tk.Toplevel(self.pracownicy_LF, background='#383232',
                                             highlightthickness=2)
        self.new_edit_toplevel.grab_set()
        self.new_edit_toplevel.geometry(f'400x400+600+100')

        # labels + entry
        self.new_edit_imie_lb = tk.Label(self.new_edit_toplevel, text='IMIĘ', bg='#383232', fg='white', anchor='w')
        self.new_edit_imie_lb.place(relx=0.05, rely=0.05, relwidth=0.3, relheight=0.05)
        self.new_edit_imie_entry = tk.Entry(self.new_edit_toplevel, justify='center', bg='#6b685f', fg='white')
        self.new_edit_imie_entry.place(relx=0.35, rely=0.05, relwidth=0.6, relheight=0.05)

        self.new_edit_nazwisko_lb = tk.Label(self.new_edit_toplevel, text='NAZWISKO', bg='#383232', fg='white',
                                             anchor='w')
        self.new_edit_nazwisko_lb.place(relx=0.05, rely=0.11, relwidth=0.3, relheight=0.05)
        self.new_edit_nazwisko_entry = tk.Entry(self.new_edit_toplevel, justify='center', bg='#6b685f', fg='white')
        self.new_edit_nazwisko_entry.place(relx=0.35, rely=0.11, relwidth=0.6, relheight=0.05)

        self.new_edit_stanowisko_lb = tk.Label(self.new_edit_toplevel, text='STANOWISKO', bg='#383232', fg='white',
                                               anchor='w')
        self.new_edit_stanowisko_lb.place(relx=0.05, rely=0.17, relwidth=0.3, relheight=0.05)
        self.new_edit_stanowisko_entry = tk.Entry(self.new_edit_toplevel, justify='center', bg='#6b685f', fg='white')
        self.new_edit_stanowisko_entry.place(relx=0.35, rely=0.17, relwidth=0.6, relheight=0.05)

        self.new_edit_badania_lb = tk.Label(self.new_edit_toplevel, text='BADANIA', bg='#383232', fg='white',
                                            anchor='w')
        self.new_edit_badania_lb.place(relx=0.05, rely=0.23, relwidth=0.3, relheight=0.05)
        self.new_edit_badania_entry = tk.Entry(self.new_edit_toplevel, justify='center', bg='#6b685f', fg='white')
        self.new_edit_badania_entry.place(relx=0.35, rely=0.23, relwidth=0.6, relheight=0.05)

        self.new_edit_koniec_umowy_lb = tk.Label(self.new_edit_toplevel, text='KONIEC UMOWY', bg='#383232', fg='white',
                                                 anchor='w')
        self.new_edit_koniec_umowy_lb.place(relx=0.05, rely=0.29, relwidth=0.3, relheight=0.05)
        self.new_edit_koniec_umowy_entry = tk.Entry(self.new_edit_toplevel, justify='center', bg='#6b685f', fg='white')
        self.new_edit_koniec_umowy_entry.place(relx=0.35, rely=0.29, relwidth=0.6, relheight=0.05)

        self.new_edit_pracownik_aktywny_lb = tk.Label(self.new_edit_toplevel, text='AKTYWNY', bg='#383232', fg='white',
                                                      anchor='w')
        self.new_edit_pracownik_aktywny_lb.place(relx=0.05, rely=0.35, relwidth=0.3, relheight=0.05)
        self.new_edit_pracownik_aktywny_entry = tk.Entry(self.new_edit_toplevel, justify='center', bg='#6b685f',
                                                         fg='white')
        self.new_edit_pracownik_aktywny_entry.place(relx=0.35, rely=0.35, relwidth=0.6, relheight=0.05)

        self.new_edit_placowka_lb = tk.Label(self.new_edit_toplevel, text='PLACOWKA', bg='#383232', fg='white',
                                             anchor='w')
        self.new_edit_placowka_lb.place(relx=0.05, rely=0.41, relwidth=0.3, relheight=0.05)
        self.new_edit_placowka_entry = tk.Entry(self.new_edit_toplevel, justify='center', bg='#6b685f',
                                                fg='white')
        self.new_edit_placowka_entry.place(relx=0.35, rely=0.41, relwidth=0.6, relheight=0.05)

        self.new_edit_konto_bankowe_lb = tk.Label(self.new_edit_toplevel, text='KONTO', bg='#383232', fg='white',
                                                  anchor='w')
        self.new_edit_konto_bankowe_lb.place(relx=0.05, rely=0.47, relwidth=0.3, relheight=0.05)
        self.new_edit_konto_bankowe_entry = tk.Entry(self.new_edit_toplevel, justify='center', bg='#6b685f',
                                                     fg='white')
        self.new_edit_konto_bankowe_entry.place(relx=0.35, rely=0.47, relwidth=0.6, relheight=0.05)

        self.new_edit_pensja_lb = tk.Label(self.new_edit_toplevel, text='PENSJA', bg='#383232', fg='white',
                                           anchor='w')
        self.new_edit_pensja_lb.place(relx=0.05, rely=0.53, relwidth=0.3, relheight=0.05)
        self.new_edit_pensja_entry = tk.Entry(self.new_edit_toplevel, justify='center', bg='#6b685f',
                                              fg='white')
        self.new_edit_pensja_entry.place(relx=0.35, rely=0.53, relwidth=0.6, relheight=0.05)

        self.new_edit_premia_lb = tk.Label(self.new_edit_toplevel, text='PREMIA', bg='#383232', fg='white',
                                           anchor='w')
        self.new_edit_premia_lb.place(relx=0.05, rely=0.59, relwidth=0.3, relheight=0.05)
        self.new_edit_premia_entry = tk.Entry(self.new_edit_toplevel, justify='center', bg='#6b685f',
                                              fg='white')
        self.new_edit_premia_entry.place(relx=0.35, rely=0.59, relwidth=0.6, relheight=0.05)

        self.new_edit_uwagi_lb = tk.Label(self.new_edit_toplevel, text='UWAGI', bg='#383232', fg='white',
                                          anchor='w')
        self.new_edit_uwagi_lb.place(relx=0.05, rely=0.65, relwidth=0.3, relheight=0.05)
        self.new_edit_uwagi_entry = tk.Entry(self.new_edit_toplevel, justify='center', bg='#6b685f',
                                             fg='white')
        self.new_edit_uwagi_entry.place(relx=0.35, rely=0.65, relwidth=0.6, relheight=0.05)

        self.new_edit_data_urodzenia_lb = tk.Label(self.new_edit_toplevel, text='DATA UR.', bg='#383232', fg='white',
                                                   anchor='w')
        self.new_edit_data_urodzenia_lb.place(relx=0.05, rely=0.71, relwidth=0.3, relheight=0.05)
        self.new_edit_data_urodzenia_entry = tk.Entry(self.new_edit_toplevel, justify='center', bg='#6b685f',
                                                      fg='white')
        self.new_edit_data_urodzenia_entry.place(relx=0.35, rely=0.71, relwidth=0.6, relheight=0.05)

        self.new_edit_dodaj_button = tk.Button(self.new_edit_toplevel, text='DODAJ', bg='#544949',
                                               fg=f'{self.kolor_razem}', command=self.dodaj_nowy_pracownik)
        self.new_edit_dodaj_button.place(relx=0.05, rely=0.9, relwidth=0.4, relheight=0.07)

        self.new_edit_popraw_button = tk.Button(self.new_edit_toplevel, text='POPRAW', bg='#544949',
                                                fg=f'{self.kolor_razem}', command=self.popraw_pracownik_dane)
        self.new_edit_popraw_button.place(relx=0.55, rely=0.9, relwidth=0.4, relheight=0.07)

        self.update_new_edit_toplevel_display()  # wypełnienie entry w toplevel

    def dodaj_nowy_pracownik(self):
        self.get_last_pracownik_id()
        with open('slowniki_pracownicy.json', encoding='utf-8') as json_file:
            data = json.load(json_file)
        data[self.get_last_pracownik_id() + 1] = {'imie': self.new_edit_imie_entry.get(),
                                                  'nazwisko': self.new_edit_nazwisko_entry.get(),
                                                  'pensja': self.new_edit_pensja_entry.get(),
                                                  'badania': self.new_edit_badania_entry.get(),
                                                  'data_zakonczenia_umowy': self.new_edit_koniec_umowy_entry.get(),
                                                  'pelna_nazwa': f'{self.new_edit_nazwisko_entry.get()} {self.new_edit_imie_entry.get()}',
                                                  'konto_bankowe': self.new_edit_konto_bankowe_entry.get(),
                                                  'stanowisko': self.new_edit_stanowisko_entry.get(),
                                                  'placowka': self.new_edit_placowka_entry.get(),
                                                  'aktywny': self.new_edit_pracownik_aktywny_entry.get(),
                                                  'pranie': '15.00 zł',
                                                  'premia': self.new_edit_premia_entry.get(),
                                                  'uwagi_wynagrodzenia': self.new_edit_uwagi_entry.get(),
                                                  'data_urodzenia': self.new_edit_data_urodzenia_entry.get()}
        with open('slowniki_pracownicy.json', 'w', encoding='utf-8') as outfile:
            json.dump(data, outfile)
        self.create_lista_pracownicy()
        self.pracownicy_combobox.config(values=self.lista_pracownicy)

    @staticmethod
    def get_last_pracownik_id():
        with open('slowniki_pracownicy.json', encoding='utf-8') as json_file:
            data = json.load(json_file)
        return int(list(data.keys())[-1])  # last id in dictionary

    def update_new_edit_toplevel_display(self):
        id_pracownika = self.get_pracownik_id()
        if id_pracownika == 0:
            self.new_edit_dodaj_button.configure(state='normal')
            self.new_edit_popraw_button.configure(state='disabled')
        else:
            with open('slowniki_pracownicy.json', encoding='utf-8') as json_file:
                data = json.load(json_file)
                self.new_edit_imie_entry.insert(0, f'{data[id_pracownika]["imie"]}')
                self.new_edit_nazwisko_entry.insert(0, f'{data[id_pracownika]["nazwisko"]}')
                self.new_edit_stanowisko_entry.insert(0, f'{data[id_pracownika]["stanowisko"]}')
                self.new_edit_badania_entry.insert(0, f'{data[id_pracownika]["badania"]}')
                self.new_edit_koniec_umowy_entry.insert(0, f'{data[id_pracownika]["data_zakonczenia_umowy"]}')
                self.new_edit_pracownik_aktywny_entry.insert(0, f'{data[id_pracownika]["aktywny"]}')
                self.new_edit_placowka_entry.insert(0, f'{data[id_pracownika]["placowka"]}')
                self.new_edit_konto_bankowe_entry.insert(0, f'{data[id_pracownika]["konto_bankowe"]}')
                self.new_edit_pensja_entry.insert(0, f'{data[id_pracownika]["pensja"]}')
                self.new_edit_premia_entry.insert(0, f'{data[id_pracownika]["premia"]}')
                self.new_edit_uwagi_entry.insert(0, f'{data[id_pracownika]["uwagi_wynagrodzenia"]}')
                self.new_edit_data_urodzenia_entry.insert(0, f'{data[id_pracownika]["data_urodzenia"]}')

                self.new_edit_dodaj_button.configure(state='disabled')
                self.new_edit_popraw_button.configure(state='normal')

    def popraw_pracownik_dane(self):
        with open('slowniki_pracownicy.json', encoding='utf-8') as json_file:
            data = json.load(json_file)
            id_pracownika = self.get_pracownik_id()
            data[id_pracownika]["imie"] = self.new_edit_imie_entry.get()
            data[id_pracownika]["nazwisko"] = self.new_edit_nazwisko_entry.get()
            data[id_pracownika]["stanowisko"] = self.new_edit_stanowisko_entry.get()
            data[id_pracownika]["badania"] = self.new_edit_badania_entry.get()
            data[id_pracownika]["data_zakonczenia_umowy"] = self.new_edit_koniec_umowy_entry.get()
            data[id_pracownika]["aktywny"] = self.new_edit_pracownik_aktywny_entry.get()
            data[id_pracownika]["placowka"] = self.new_edit_placowka_entry.get()
            data[id_pracownika]["konto_bankowe"] = self.new_edit_konto_bankowe_entry.get()
            data[id_pracownika]["pensja"] = self.new_edit_pensja_entry.get()
            data[id_pracownika]["premia"] = self.new_edit_premia_entry.get()
            data[id_pracownika]["uwagi_wynagrodzenia"] = self.new_edit_uwagi_entry.get()
            data[id_pracownika]["data_urodzenia"] = self.new_edit_data_urodzenia_entry.get()

        with open('slowniki_pracownicy.json', 'w') as outfile:
            json.dump(data, outfile)

        self.update_info_pracownik_labels(id_pracownika)
        self.new_edit_toplevel.destroy()

    def create_dodaj_urlop_field(self):
        definicje_nieobecnosci = self.get_definicje_nieobecnosci()
        self.rodzaj_wolnego_combobox = ttk.Combobox(self.pracownicy_LF, values=definicje_nieobecnosci,
                                                    height=30, state='readonly')
        self.rodzaj_wolnego_combobox.current(0)
        self.rodzaj_wolnego_combobox.place(relx=0.01, rely=0.68, relwidth=0.23)

        od_label = tk.Label(self.pracownicy_LF, text='OD', bg='#383232', fg='#80e89b', anchor='w')
        od_label.place(relx=0.25, rely=0.68, relwidth=0.03)

        self.wolne_od_DEntry = DateEntry(self.pracownicy_LF, width=12, background='#383232',
                                         foreground='white', borderwidth=2, date_pattern='y-mm-dd',
                                         locale='pl_PL')
        self.wolne_od_DEntry.place(relx=0.29, rely=0.68, relwidth=0.12)

        do_label = tk.Label(self.pracownicy_LF, text='DO', bg='#383232', fg='#80e89b', anchor='w')
        do_label.place(relx=0.42, rely=0.68, relwidth=0.03)

        self.wolne_do_DEntry = DateEntry(self.pracownicy_LF, width=12, background='#383232',
                                         foreground='white', borderwidth=2, date_pattern='y-mm-dd',
                                         locale='pl_PL')
        self.wolne_do_DEntry.place(relx=0.46, rely=0.68, relwidth=0.12)

        opis_label = tk.Label(self.pracownicy_LF, text='UWAGI', bg='#383232', fg='#80e89b', anchor='w')
        opis_label.place(relx=0.59, rely=0.68, relwidth=0.05)

        self.uwagi_Entry = tk.Entry(self.pracownicy_LF, justify='center', bg='#6b685f', fg='white')
        self.uwagi_Entry.place(relx=0.65, rely=0.68, relwidth=0.2)

        self.dodaj_wolne_button = tk.Button(self.pracownicy_LF, text='DODAJ', bg='#544949',
                                            fg=f'{self.kolor_razem}', command=self.zapisz_wolne_dni_do_bazy)
        self.dodaj_wolne_button.place(relx=0.86, rely=0.68, relwidth=0.13)
        self.dodaj_wolne_button.configure(state='disabled')

    @staticmethod
    def get_definicje_nieobecnosci():
        definicje_nieobecnosci = []
        for key in slowniki.definicje_nieobecnosc:
            definicje_nieobecnosci.append(slowniki.definicje_nieobecnosc[key].upper())
        return definicje_nieobecnosci

    def get_definicje_nieobecnosci_id(self):
        rodzaj = self.rodzaj_wolnego_combobox.get().lower()
        for key in slowniki.definicje_nieobecnosc:
            if slowniki.definicje_nieobecnosc[key] == rodzaj:
                return key
            else:
                pass

    def set_daty_wolne_list(self):
        lista_dat_do_dodania = []
        id_pracownika = self.get_pracownik_id()
        data_od = datetime.datetime.strptime(self.wolne_od_DEntry.get(), '%Y-%m-%d').date()
        data_do = datetime.datetime.strptime(self.wolne_do_DEntry.get(), '%Y-%m-%d').date()
        rodzaj = self.get_definicje_nieobecnosci_id()
        uwagi = self.uwagi_Entry.get()

        if rodzaj == '6':
            return [[id_pracownika, rodzaj, '-', uwagi]]
        data_pomiedzy = data_od
        while True:
            if data_pomiedzy > data_do:
                break
            lista_dat_do_dodania.append([id_pracownika, rodzaj, str(data_pomiedzy), uwagi])
            data_pomiedzy += datetime.timedelta(days=1)
        return lista_dat_do_dodania

    def set_rok_urlopu(self):
        id_pracownika = self.get_pracownik_id()
        for r in range(4):
            rok = datetime.datetime.now().year - r
            querry = f'SELECT * FROM urlopy WHERE urlop_rok={rok} AND pracownik={id_pracownika}'
            daty = self.zpt_database.mysql_querry(querry)
            if len(daty) == 26:
                return rok + 1
            elif len(daty) < 26 and len(daty) != 0:
                return rok

    def zapisz_wolne_dni_do_bazy(self):
        lista_do_dodania = self.set_daty_wolne_list()

        for d in lista_do_dodania:
            if d[1] == '1' or d[1] == '6':
                rok_urlopu = self.set_rok_urlopu()
            else:
                rok_urlopu = ''
            querry = f'INSERT INTO urlopy VALUES(NULL, {d[0]}, {d[1]}, "{d[2]}", "{rok_urlopu}", "{d[3]}")'
            self.zpt_database.mysql_no_fetch_querry(querry)
        self.uwagi_Entry.delete(0, 'end')
        self.wolne_od_DEntry.set_date(f'{datetime.date.today()}')
        self.wolne_do_DEntry.set_date(f'{datetime.date.today()}')
        self.update_urlopy_treeview()
        self.update_nieobecnosci_treeview()
        self.update_info_pracownik_labels(self.get_pracownik_id())

    def create_nieobecnosci_treeview(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', fieldbackground="#383232", background="#383232", foreground='white')
        style.configure("Treeview.Heading", background="#383232", foreground="white")
        style.map('Treeview.Heading', background=[('disabled', '#383232')])

        def fixed_map(option):  # naprawa buga wersji dla Python 3.7 przy wyświetlaniu koloru linii w treeview
            return [elm for elm in style.map("Treeview", query_opt=option)
                    if elm[:2] != ("!disabled", "!selected")]

        style.map("Treeview", foreground=fixed_map("foreground"),
                  background=fixed_map("background"))

        self.nieobecnosci_treeview_frame = tk.Frame(self.pracownicy_LF)
        self.nieobecnosci_treeview_frame.configure(bg='#383232', relief='groove', bd=1)
        self.nieobecnosci_treeview_frame.place(relx=0.01, rely=0.72, relwidth=0.98, relheight=0.26)

        self.nieobecnosci_columns = ['LP', 'RODZAJ', 'DATA', 'UWAGI']
        self.nieobecnosci_treeview = ttk.Treeview(self.nieobecnosci_treeview_frame, columns=self.nieobecnosci_columns,
                                                  show='headings',
                                                  style="Treeview", selectmode="browse")

        self.nieobecnosci_treeview.heading('LP', text='LP')
        self.nieobecnosci_treeview.column('LP', width=50, stretch='no', anchor='center')
        self.nieobecnosci_treeview.heading(f'{self.nieobecnosci_columns[1]}', text=f'{self.nieobecnosci_columns[1]}')
        self.nieobecnosci_treeview.column(f'{self.nieobecnosci_columns[1]}', width=200, stretch='no', anchor='center')
        self.nieobecnosci_treeview.heading(f'{self.nieobecnosci_columns[2]}', text=f'{self.nieobecnosci_columns[2]}')
        self.nieobecnosci_treeview.column(f'{self.nieobecnosci_columns[2]}', width=150, stretch='no', anchor='center')
        self.nieobecnosci_treeview.heading(f'{self.nieobecnosci_columns[3]}', text=f'{self.nieobecnosci_columns[3]}')
        self.nieobecnosci_treeview.column(f'{self.nieobecnosci_columns[3]}', minwidth=250, stretch='yes',
                                          anchor='center')

        self.scrolly = ttk.Scrollbar(self.nieobecnosci_treeview_frame, orient='vertical',
                                     command=self.nieobecnosci_treeview.yview)
        self.nieobecnosci_treeview.configure(yscrollcommand=self.scrolly.set)
        map(lambda col: col.configure(yscrollcommand=self.scrolly.set), self.nieobecnosci_columns)
        self.scrolly.pack(side=tk.RIGHT, fill=tk.Y)
        map(lambda col: col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True), self.nieobecnosci_columns)
        self.nieobecnosci_treeview.pack(expand='yes', fill='both')

    def update_nieobecnosci_treeview(self):
        daty = self.get_nieobecnosci_treeview_data()
        self.nieobecnosci_treeview.delete(*self.nieobecnosci_treeview.get_children())
        if daty != 0:
            n = 1
            for d in daty:
                if n % 2 == 0:
                    background = 'background_dark'
                else:
                    background = 'background_light'

                self.nieobecnosci_treeview.tag_configure('background_dark', background='#383232')
                self.nieobecnosci_treeview.tag_configure('background_light', background='#262424')
                self.nieobecnosci_treeview.insert('', 'end', values=(n, d[0], d[1], d[2]), tags=(background))
                n += 1

    def get_nieobecnosci_treeview_data(self):
        id_pracownika = self.get_pracownik_id()
        if id_pracownika == 0:
            return 0
        else:
            lista_nieobecnosci = []
            querry = f'SELECT * FROM urlopy WHERE pracownik={id_pracownika} AND rodzaj<>1 AND rodzaj<>6 ORDER BY data DESC'
            wynik_querry = self.zpt_database.mysql_querry(querry)
            for n in wynik_querry:
                lista_nieobecnosci.append([slowniki.definicje_nieobecnosc[n[2]].upper(), n[3], n[5]])
            return lista_nieobecnosci

    def create_wynagrodzenia_field(self):
        kreska_lb = tk.Label(self.pracownicy_RF, text='')
        kreska_lb.place(relx=0.01, rely=0.5, relwidth=0.98, relheight=0.003)

        wynagodzenia_lb = tk.Label(self.pracownicy_RF, text='WYNAGRODZENIA', bg='#383232',
                                   font=("Verdena", "15", "bold")
                                   , fg='#80e89b')
        wynagodzenia_lb.place(relx=0.01, rely=0.51, relwidth=0.98)

        self.wynagrodznia_okres_entry = tk.Entry(self.pracownicy_RF, justify='center', bg='#6b685f', fg='white')
        self.wynagrodznia_okres_entry.place(relx=0.01, rely=0.55, relwidth=0.25, relheight=0.03)

        self.generuj_button = tk.Button(self.pracownicy_RF, text='GENERUJ', bg='#544949',
                                        fg=f'{self.kolor_razem}', command=self.get_wynagrodzenia_data)
        self.generuj_button.place(relx=0.27, rely=0.55, relwidth=0.25, relheight=0.03)

        self.generuj_button = tk.Button(self.pracownicy_RF, text='EKSPORTUJ', bg='#544949',
                                        fg=f'{self.kolor_razem}', command=self.eksportuj_wynagrodzenia_do_pdf)
        self.generuj_button.place(relx=0.69, rely=0.96, relwidth=0.3, relheight=0.03)

    def create_wynagrodzania_treeview(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', fieldbackground="#383232", background="#383232", foreground='white')
        style.configure("Treeview.Heading", background="#383232", foreground="white")
        style.map('Treeview.Heading', background=[('disabled', '#383232')])

        def fixed_map(option):  # naprawa buga wersji dla Python 3.7 przy wyświetlaniu koloru linii w treeview
            return [elm for elm in style.map("Treeview", query_opt=option)
                    if elm[:2] != ("!disabled", "!selected")]

        style.map("Treeview", foreground=fixed_map("foreground"),
                  background=fixed_map("background"))

        self.wynagrodzenia_treeview_frame = tk.Frame(self.pracownicy_RF)
        self.wynagrodzenia_treeview_frame.configure(bg='#383232', relief='groove', bd=1)
        self.wynagrodzenia_treeview_frame.place(relx=0.01, rely=0.59, relwidth=0.98, relheight=0.36)

        self.wynagrodzenia_columns = ['LP', 'NAZWA', 'UWAGI', 'URLOPY', 'PREMIA']
        self.wynagrodzenia_treeview = ttk.Treeview(self.wynagrodzenia_treeview_frame,
                                                   columns=self.wynagrodzenia_columns,
                                                   show='headings',
                                                   style="Treeview", selectmode="browse")

        self.wynagrodzenia_treeview.heading('LP', text='LP')
        self.wynagrodzenia_treeview.column('LP', width=50, stretch='no', anchor='center')
        self.wynagrodzenia_treeview.heading(f'{self.wynagrodzenia_columns[1]}', text=f'{self.wynagrodzenia_columns[1]}')
        self.wynagrodzenia_treeview.column(f'{self.wynagrodzenia_columns[1]}', minwidth=200, stretch='yes',
                                           anchor='center')
        self.wynagrodzenia_treeview.heading(f'{self.wynagrodzenia_columns[2]}', text=f'{self.wynagrodzenia_columns[2]}')
        self.wynagrodzenia_treeview.column(f'{self.wynagrodzenia_columns[2]}', minwidth=150, stretch='yes',
                                           anchor='center')
        self.wynagrodzenia_treeview.heading(f'{self.wynagrodzenia_columns[3]}', text=f'{self.wynagrodzenia_columns[3]}')
        self.wynagrodzenia_treeview.column(f'{self.wynagrodzenia_columns[3]}', minwidth=150, stretch='yes',
                                           anchor='center')
        self.wynagrodzenia_treeview.heading(f'{self.wynagrodzenia_columns[4]}', text=f'{self.wynagrodzenia_columns[4]}')
        self.wynagrodzenia_treeview.column(f'{self.wynagrodzenia_columns[4]}', minwidth=150, stretch='yes',
                                           anchor='center')

        self.scrolly = ttk.Scrollbar(self.wynagrodzenia_treeview_frame, orient='vertical',
                                     command=self.wynagrodzenia_treeview.yview)
        self.pracownicy_treeview.configure(yscrollcommand=self.scrolly.set)
        map(lambda col: col.configure(yscrollcommand=self.scrolly.set), self.wynagrodzenia_columns)
        self.scrolly.pack(side=tk.RIGHT, fill=tk.Y)
        map(lambda col: col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True), self.wynagrodzenia_columns)
        self.wynagrodzenia_treeview.pack(expand='yes', fill='both')
        self.wynagrodzenia_treeview.bind("<Double-1>", self.create_wynagrodzenia_toplevel)

    def update_wynagrodzenia_treeview(self):
        n = 1
        self.wynagrodzenia_treeview.delete(*self.wynagrodzenia_treeview.get_children())
        for d in self.dane_do_wyplaty:
            if n % 2 == 0:
                background = 'background_dark'
            else:
                background = 'background_light'

            self.wynagrodzenia_treeview.tag_configure('background_dark', background='#383232')
            self.wynagrodzenia_treeview.tag_configure('background_light', background='#262424')
            self.wynagrodzenia_treeview.insert('', 'end', values=(n, d["nazwa"], d["uwagi"], d["urlopy"], d["premia"]),
                                               tags=(background))
            n += 1

    def get_wynagrodzenia_data(self):
        self.dane_do_wyplaty = []
        okres = self.wynagrodznia_okres_entry.get()
        lista_kluczy = self.set_alfabetyczna_lista_kluczy()
        with open('slowniki_pracownicy.json', encoding='utf-8') as json_file:
            data = json.load(json_file)
        for k in lista_kluczy:
            if k == '23':
                continue
            self.dane_do_wyplaty.append({
                'nazwa': f'{data[k]["pelna_nazwa"]}',
                'pensja': f'{data[k]["pensja"]} zł',
                'uwagi': f'{data[k]["uwagi_wynagrodzenia"]}',
                'urlopy': f'{self.get_ilosc_urlopow_miesiac(k, okres)}',
                'premia': f'{data[k]["premia"]}',
                'pranie': f'{data[k]["pranie"]}',
            })
        self.update_wynagrodzenia_treeview()

    def get_ilosc_urlopow_miesiac(self, id_pracownika, okres):
        querry = f'SELECT * FROM urlopy WHERE pracownik={id_pracownika} AND rodzaj=1 and data LIKE "%{okres}%"'
        wynik = self.zpt_database.mysql_querry(querry)
        return len(wynik)

    @staticmethod
    def set_alfabetyczna_lista_kluczy():
        lista_nazw = []
        lista_kluczy = []
        with open('slowniki_pracownicy.json', encoding='utf-8') as json_file:
            data = json.load(json_file)
            for key in data:
                if data[key]['aktywny'] == 'TAK':
                    lista_nazw.append((data[key]['pelna_nazwa'], key))
            lista_nazw = sorted(lista_nazw, key=lambda x: x[0])

            for n in lista_nazw:
                lista_kluczy.append(n[1])

            return lista_kluczy

    def create_wynagrodzenia_toplevel(self, event):
        curItem = self.wynagrodzenia_treeview.focus()
        index_listy = self.wynagrodzenia_treeview.item(curItem)['values'][0]

        self.wynagrodzenia_toplevel = tk.Toplevel(self.pracownicy_RF, background='#383232',
                                                  highlightthickness=2)
        self.wynagrodzenia_toplevel.grab_set()
        self.wynagrodzenia_toplevel.geometry(f'400x400+600+100')

        self.nazwa_wynagrodzenia_lb = tk.Label(self.wynagrodzenia_toplevel, text='NAZWA', bg='#383232', fg='white',
                                               anchor='w')
        self.nazwa_wynagrodzenia_lb.place(relx=0.05, rely=0.05, relwidth=0.3, relheight=0.05)
        self.nazwa_wynagrodzenia_entry = tk.Entry(self.wynagrodzenia_toplevel, justify='center', bg='#6b685f',
                                                  fg='white')
        self.nazwa_wynagrodzenia_entry.place(relx=0.35, rely=0.05, relwidth=0.6, relheight=0.05)

        self.pensja_wynagrodzenia_lb = tk.Label(self.wynagrodzenia_toplevel, text='PENSJA', bg='#383232', fg='white',
                                                anchor='w')
        self.pensja_wynagrodzenia_lb.place(relx=0.05, rely=0.11, relwidth=0.3, relheight=0.05)
        self.pensja_wynagrodzenia_entry = tk.Entry(self.wynagrodzenia_toplevel, justify='center', bg='#6b685f',
                                                   fg='white')
        self.pensja_wynagrodzenia_entry.place(relx=0.35, rely=0.11, relwidth=0.6, relheight=0.05)

        self.uwagi_wynagrodzenia_lb = tk.Label(self.wynagrodzenia_toplevel, text='UWAGI', bg='#383232', fg='white',
                                               anchor='w')
        self.uwagi_wynagrodzenia_lb.place(relx=0.05, rely=0.17, relwidth=0.3, relheight=0.05)
        self.uwagi_wynagrodzenia_entry = tk.Entry(self.wynagrodzenia_toplevel, justify='center', bg='#6b685f',
                                                  fg='white')
        self.uwagi_wynagrodzenia_entry.place(relx=0.35, rely=0.17, relwidth=0.6, relheight=0.05)

        self.urlopy_wynagrodzenia_lb = tk.Label(self.wynagrodzenia_toplevel, text='URLOPY', bg='#383232', fg='white',
                                                anchor='w')
        self.urlopy_wynagrodzenia_lb.place(relx=0.05, rely=0.23, relwidth=0.3, relheight=0.05)
        self.urlopy_wynagrodzenia_entry = tk.Entry(self.wynagrodzenia_toplevel, justify='center', bg='#6b685f',
                                                   fg='white')
        self.urlopy_wynagrodzenia_entry.place(relx=0.35, rely=0.23, relwidth=0.6, relheight=0.05)

        self.premia_wynagrodzenia_lb = tk.Label(self.wynagrodzenia_toplevel, text='PREMIA', bg='#383232', fg='white',
                                                anchor='w')
        self.premia_wynagrodzenia_lb.place(relx=0.05, rely=0.29, relwidth=0.3, relheight=0.05)
        self.premia_wynagrodzenia_entry = tk.Entry(self.wynagrodzenia_toplevel, justify='center', bg='#6b685f',
                                                   fg='white')
        self.premia_wynagrodzenia_entry.place(relx=0.35, rely=0.29, relwidth=0.6, relheight=0.05)

        self.pranie_wynagrodzenia_lb = tk.Label(self.wynagrodzenia_toplevel, text='PRANIE', bg='#383232', fg='white',
                                                anchor='w')
        self.pranie_wynagrodzenia_lb.place(relx=0.05, rely=0.35, relwidth=0.3, relheight=0.05)
        self.pranie_wynagrodzenia_entry = tk.Entry(self.wynagrodzenia_toplevel, justify='center', bg='#6b685f',
                                                   fg='white')
        self.pranie_wynagrodzenia_entry.place(relx=0.35, rely=0.35, relwidth=0.6, relheight=0.05)

        self.new_edit_popraw_button = tk.Button(self.wynagrodzenia_toplevel, text='POPRAW', bg='#544949',
                                                fg=f'{self.kolor_razem}', command=self.popraw_wynagrodzenia_dane)
        self.new_edit_popraw_button.place(relx=0.55, rely=0.9, relwidth=0.4, relheight=0.07)

        self.nazwa_wynagrodzenia_entry.insert(0, self.dane_do_wyplaty[index_listy - 1]['nazwa'])
        self.pensja_wynagrodzenia_entry.insert(0, self.dane_do_wyplaty[index_listy - 1]['pensja'])
        self.uwagi_wynagrodzenia_entry.insert(0, self.dane_do_wyplaty[index_listy - 1]['uwagi'])
        self.urlopy_wynagrodzenia_entry.insert(0, self.dane_do_wyplaty[index_listy - 1]['urlopy'])
        self.premia_wynagrodzenia_entry.insert(0, self.dane_do_wyplaty[index_listy - 1]['premia'])
        self.pranie_wynagrodzenia_entry.insert(0, self.dane_do_wyplaty[index_listy - 1]['pranie'])

    def popraw_wynagrodzenia_dane(self):
        curItem = self.wynagrodzenia_treeview.focus()
        index_listy = self.wynagrodzenia_treeview.item(curItem)['values'][0]
        self.dane_do_wyplaty[index_listy - 1]['uwagi'] = self.uwagi_wynagrodzenia_entry.get()
        self.dane_do_wyplaty[index_listy - 1]['premia'] = self.premia_wynagrodzenia_entry.get()

        self.update_wynagrodzenia_treeview()
        self.wynagrodzenia_toplevel.destroy()

    def eksportuj_wynagrodzenia_do_pdf(self):
        config = pdfkit.configuration(wkhtmltopdf='c:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')
        file_html = 'wzor_wyplaty.html'
        with open(file_html, "r", encoding='utf-8') as f:
            text = f.read()
        text = text.replace('miesiac_wynagrodzen', self.wynagrodznia_okres_entry.get())
        text = text.replace('pola_z_wynagrodzeniami_pracownicy', self.set_wynagrodzenia_html_text())

        plik_wyjsciowy = rf'C:\Users\dell\Desktop\WYNAGRODZENIA_{self.wynagrodznia_okres_entry.get()}.pdf'
        pdfkit.from_string(text, plik_wyjsciowy, configuration=config)

    def set_wynagrodzenia_html_text(self):
        text_do_dodania = ''
        n = 1
        for d in self.dane_do_wyplaty:
            premia = d["premia"]
            pranie = d["pranie"]
            style_premia = ''
            style_pranie = ''

            if premia != '0,00 zł':
                style_premia = 'style =" background:#cfcdc8"'
            else:
                style_premia = ''

            if pranie != '0,00 zł':
                style_pranie = 'style =" background:#cfcdc8"'
            else:
                style_pranie = ''

            text_do_dodania += f'<tr> ' \
                               f'<td style="width: 5%">{n}</td>' \
                               f'<td >{d["nazwa"]}</td>' \
                               f'<td >{d["pensja"]}</td>' \
                               f'<td >{d["uwagi"]}</td>' \
                               f'<td >{d["urlopy"]}</td>' \
                               f'<td {style_premia}>{d["premia"]}</td>' \
                               f'<td {style_pranie}>{d["pranie"]}</td>' \
                               f'</tr>'
            n += 1

        text_do_dodania += f'<tr><td colspan="7"></td><p></p> </tr>'
        text_do_dodania += f'<tr> ' \
                           f'<td style="widtd: 5%">{n}</td>' \
                           f'<td >STEFAN ZIOŁA</td>' \
                           f'<td colspan="5">PREZES ZARZĄDU - ZLECENIE</td>' \
                           f'</tr>'

        return text_do_dodania

    def set_okres_wynagrodzenia(self):
        okres = str(datetime.datetime.now())[:7]
        self.wynagrodznia_okres_entry.insert(0, okres)

class Todo_manager(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.configure(bg='#383232')
        self.kolor_razem = '#b58b14'
        self.kolor_font = 'white'
        self.kolor_font_razem = 'black'
        self.kolor_legenda = '#383232'
        self.id_event__ = 0
        self.create_todo_LF()
        self.create_todo_RF()

    def create_todo_LF(self):
        self.todo_LF = tk.Frame(self)
        self.todo_LF.configure(bg='#383232', relief='groove', bd=1)
        self.todo_LF.place(relx=0.01, rely=0.02, relwidth=0.48, relheight=0.96)
        self.create_nowy_button()
        self.create_todo_aktywne_treeview()
        self.create_done_treeview()
        self.update_treeviews(wybor=0)

    def create_todo_RF(self):
        self.todo_RF = tk.Frame(self)
        self.todo_RF.configure(bg='#383232', relief='groove', bd=1)
        self.todo_RF.place(relx=0.51, rely=0.02, relwidth=0.48, relheight=0.96)
        self.create_event_remotes()

    def create_nowy_button(self):
        self.todo_nowy_button = tk.Button(self.todo_LF, text='NOWY', bg='#544949',
                                          fg=f'{self.kolor_razem}', command=self.nowy_event)
        self.todo_nowy_button.place(relx=0.01, rely=0.01, relwidth=0.98)

    def create_todo_aktywne_treeview(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', fieldbackground="#383232", background="#383232", foreground='white')
        style.configure("Treeview.Heading", background="#383232", foreground="white")
        style.map('Treeview.Heading', background=[('disabled', '#383232')])

        def fixed_map(option):  # naprawa buga wersji dla Python 3.7 przy wyświetlaniu koloru linii w treeview
            return [elm for elm in style.map("Treeview", query_opt=option)
                    if elm[:2] != ("!disabled", "!selected")]

        style.map("Treeview", foreground=fixed_map("foreground"),
                  background=fixed_map("background"))

        self.todo_treeview_frame = tk.Frame(self.todo_LF)
        self.todo_treeview_frame.configure(bg='#383232', relief='groove', bd=1)
        self.todo_treeview_frame.place(relx=0.01, rely=0.05, relwidth=0.98, relheight=0.45)

        self.todo_columns = ['ID', 'LP', 'TERMIN', 'NAZWA', 'DATA DODANIA']
        self.todo_treeview = ttk.Treeview(self.todo_treeview_frame, columns=self.todo_columns,
                                          show='headings',
                                          style="Treeview", selectmode="browse")

        self.todo_treeview.heading('ID', text='ID')
        self.todo_treeview.column('ID', width=0, stretch='no', anchor='e')
        self.todo_treeview.heading('LP', text='LP')
        self.todo_treeview.column('LP', width=50, stretch='no', anchor='center')
        self.todo_treeview.heading(f'{self.todo_columns[2]}', text=f'{self.todo_columns[2]}')
        self.todo_treeview.column(f'{self.todo_columns[2]}', width=200, stretch='no', anchor='center')
        self.todo_treeview.heading(f'{self.todo_columns[3]}', text=f'{self.todo_columns[3]}')
        self.todo_treeview.column(f'{self.todo_columns[3]}', minwidth=150, stretch='yes', anchor='center')
        self.todo_treeview.heading(f'{self.todo_columns[4]}', text=f'{self.todo_columns[4]}')
        self.todo_treeview.column(f'{self.todo_columns[4]}', width=200, stretch='no',
                                  anchor='center')

        self.scrolly = ttk.Scrollbar(self.todo_treeview_frame, orient='vertical',
                                     command=self.todo_treeview.yview)
        self.todo_treeview.configure(yscrollcommand=self.scrolly.set)
        map(lambda col: col.configure(yscrollcommand=self.scrolly.set), self.todo_columns)
        self.scrolly.pack(side=tk.RIGHT, fill=tk.Y)
        map(lambda col: col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True), self.todo_columns)
        self.todo_treeview.pack(expand='yes', fill='both')
        self.todo_treeview.bind('<<TreeviewSelect>>', self.update_event_remotes_todo)

    def create_done_treeview(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', fieldbackground="#383232", background="#383232", foreground='white')
        style.configure("Treeview.Heading", background="#383232", foreground="white")
        style.map('Treeview.Heading', background=[('disabled', '#383232')])

        def fixed_map(option):  # naprawa buga wersji dla Python 3.7 przy wyświetlaniu koloru linii w treeview
            return [elm for elm in style.map("Treeview", query_opt=option)
                    if elm[:2] != ("!disabled", "!selected")]

        style.map("Treeview", foreground=fixed_map("foreground"),
                  background=fixed_map("background"))

        self.done_treeview_frame = tk.Frame(self.todo_LF)
        self.done_treeview_frame.configure(bg='#383232', relief='groove', bd=1)
        self.done_treeview_frame.place(relx=0.01, rely=0.52, relwidth=0.98, relheight=0.45)

        self.done_columns = ['ID', 'LP', 'TERMIN', 'NAZWA', 'DATA ZAMKNIĘCIA']
        self.done_treeview = ttk.Treeview(self.done_treeview_frame, columns=self.done_columns,
                                          show='headings',
                                          style="Treeview", selectmode="browse")

        self.done_treeview.heading('ID', text='ID')
        self.done_treeview.column('ID', width=0, stretch='no', anchor='e')
        self.done_treeview.heading('LP', text='LP')
        self.done_treeview.column('LP', width=50, stretch='no', anchor='center')
        self.done_treeview.heading(f'{self.done_columns[2]}', text=f'{self.done_columns[2]}')
        self.done_treeview.column(f'{self.done_columns[2]}', width=200, stretch='no', anchor='center')
        self.done_treeview.heading(f'{self.done_columns[3]}', text=f'{self.done_columns[3]}')
        self.done_treeview.column(f'{self.done_columns[3]}', minwidth=150, stretch='yes', anchor='center')
        self.done_treeview.heading(f'{self.done_columns[4]}', text=f'{self.done_columns[4]}')
        self.done_treeview.column(f'{self.done_columns[4]}', width=200, stretch='no',
                                  anchor='center')

        self.scrolly = ttk.Scrollbar(self.done_treeview_frame, orient='vertical',
                                     command=self.done_treeview.yview)
        self.done_treeview.configure(yscrollcommand=self.scrolly.set)
        map(lambda col: col.configure(yscrollcommand=self.scrolly.set), self.done_columns)
        self.scrolly.pack(side=tk.RIGHT, fill=tk.Y)
        map(lambda col: col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True), self.done_columns)
        self.done_treeview.pack(expand='yes', fill='both')
        self.done_treeview.bind('<<TreeviewSelect>>', self.update_event_remotes_done)

    @staticmethod
    def set_treeviews_data():
        with open('todo.json', encoding='utf-8') as json_file:
            data = json.load(json_file)
        todo_list = []
        done_list = []

        for key in data:
            if data[key]['status'] == '0':
                todo_list.append([key, data[key]['nazwa'], data[key]['opis'], data[key]['termin'],
                                  data[key]['data_dodania'], data[key]['data_zamkniecia']])
            else:
                done_list.append([key, data[key]['nazwa'], data[key]['opis'], data[key]['termin'],
                                  data[key]['data_dodania'], data[key]['data_zamkniecia']])

        todo_list.sort(key=lambda x: x[3], reverse=False)
        done_list.sort(key=lambda x: x[5], reverse=True)
        return (todo_list, done_list)

    def update_treeviews(self, wybor):
        dane = self.set_treeviews_data()
        dane_todo = dane[0]
        dane_done = dane[1]

        if wybor == 0 or wybor == 1:
            n = 1
            self.todo_treeview.delete(*self.todo_treeview.get_children())
            for d in dane_todo:
                if n % 2 == 0:
                    background = 'background_dark'
                else:
                    background = 'background_light'

                self.todo_treeview.tag_configure('background_dark', background='#383232')
                self.todo_treeview.tag_configure('background_light', background='#262424')
                self.todo_treeview.insert('', 'end', values=(d[0], n, d[3], d[1], d[4]), tags=(background))
                n += 1

        if wybor == 0 or wybor == 2:
            n = 1
            self.done_treeview.delete(*self.done_treeview.get_children())
            for d in dane_done:
                if n % 2 == 0:
                    background = 'background_dark'
                else:
                    background = 'background_light'

                self.done_treeview.tag_configure('background_dark', background='#383232')
                self.done_treeview.tag_configure('background_light', background='#262424')
                self.done_treeview.insert('', 'end', values=(d[0], n, d[3], d[1], d[5]), tags=(background))
                n += 1

    def create_event_remotes(self):
        self.event_id = tk.Label(self.todo_RF, text='ID: ', bg='#383232', fg='white', anchor='w')
        self.event_id.place(relx=0.05, rely=0.03, relwidth=0.1, relheight=0.03)
        event_nazwa_lb = tk.Label(self.todo_RF, text='NAZWA:', bg='#383232', fg='white', anchor='w')
        event_nazwa_lb.place(relx=0.05, rely=0.07, relwidth=0.08, relheight=0.03)
        self.event_nazwa_entry = tk.Entry(self.todo_RF, justify='center', bg='#6b685f', fg='white')
        self.event_nazwa_entry.place(relx=0.13, rely=0.07, relwidth=0.82, relheight=0.03)
        data_dodania_lb = tk.Label(self.todo_RF, text='DODANE:', bg='#383232', fg='white', anchor='w')
        data_dodania_lb.place(relx=0.05, rely=0.11, relwidth=0.08, relheight=0.03)
        self.data_dodania = DateEntry(self.todo_RF, width=12, background='#383232',
                                      foreground='white', borderwidth=2, date_pattern='y-mm-dd',
                                      locale='pl_PL')
        self.data_dodania.place(relx=0.13, rely=0.11, relwidth=0.34, relheight=0.03)
        data_zamkniecia_lb = tk.Label(self.todo_RF, text='ZAKOŃCZONO:', bg='#383232', fg='white', anchor='w')
        data_zamkniecia_lb.place(relx=0.5, rely=0.11, relwidth=0.11, relheight=0.03)
        self.data_zamkniecia = DateEntry(self.todo_RF, width=12, background='#383232',
                                         foreground='white', borderwidth=2, date_pattern='y-mm-dd',
                                         locale='pl_PL')
        self.data_zamkniecia.place(relx=0.61, rely=0.11, relwidth=0.34, relheight=0.03)
        data_termin_lb = tk.Label(self.todo_RF, text='TERMIN:', bg='#383232', fg='white', anchor='w')
        data_termin_lb.place(relx=0.05, rely=0.15, relwidth=0.08, relheight=0.03)
        self.data_termin = DateEntry(self.todo_RF, width=12, background='#383232',
                                     foreground='white', borderwidth=2, date_pattern='y-mm-dd',
                                     locale='pl_PL')
        self.data_termin.place(relx=0.13, rely=0.15, relwidth=0.34, relheight=0.03)
        status_lb = tk.Label(self.todo_RF, text='STATUS:', bg='#383232', fg='white', anchor='w')
        status_lb.place(relx=0.5, rely=0.15, relwidth=0.11, relheight=0.03)
        self.status_combobox = ttk.Combobox(self.todo_RF, values=["", "TO DO", "DONE"],
                                            height=30, state='readonly')
        self.status_combobox.current(0)
        self.status_combobox.place(relx=0.61, rely=0.15, relwidth=0.34, relheight=0.03)

        self.scrolled_text = scrolledtext.ScrolledText(self.todo_RF, state='normal', height=12, foreground='white',
                                                       wrap='word')
        self.scrolled_text.place(relx=0.05, rely=0.19, relwidth=0.9, relheight=0.76)
        self.scrolled_text.configure(font='TkFixedFont', bg='#383232', foreground='#17bd43')
        self.scrolled_text.bind('<Control-Key-s>', self.zapisz_zmiany)

        self.zapisz_zmiany_button = tk.Button(self.todo_RF, text='ZAPISZ ZMIANY', bg='#544949',
                                              fg=f'{self.kolor_razem}', command=lambda: self.zapisz_zmiany(''))
        self.zapisz_zmiany_button.place(relx=0.05, rely=0.96, relwidth=0.9, relheight=0.03)
        self.data_zamkniecia.delete(0, "end")

    def update_event_remotes_todo(self, event):

        curItem = self.todo_treeview.focus()
        if curItem != '':
            dane_todo = self.todo_treeview.item(curItem)
            id_event = dane_todo['values'][0]
            self.id_event__ = id_event
            self.update_event_remotes_common(id_event)
        self.update_treeviews(2)

    def update_event_remotes_done(self, event):

        curItem = self.done_treeview.focus()
        if curItem != '':
            dane_done = self.done_treeview.item(curItem)
            id_event = dane_done['values'][0]
            self.id_event__ = id_event
            self.update_event_remotes_common(id_event)
        self.update_treeviews(1)

    def update_event_remotes_common(self, id_event):
        with open('todo.json', encoding='utf-8') as json_file:
            data = json.load(json_file)

        self.event_id.config(text=f'ID: {id_event}')
        self.event_nazwa_entry.delete(0, 'end')
        self.event_nazwa_entry.insert(0, f'{data[f"{id_event}"]["nazwa"]}')
        self.scrolled_text.delete('1.0', tk.END)
        self.scrolled_text.insert(tk.END, f'{data[f"{id_event}"]["opis"]}' + '\n')
        if data[f"{id_event}"]["data_dodania"] != '':
            self.data_dodania.set_date(data[f"{id_event}"]["data_dodania"])
        else:
            self.data_dodania.delete(0, "end")

        if data[f"{id_event}"]["termin"] != '':
            self.data_termin.set_date(data[f"{id_event}"]["termin"])
        else:
            self.data_termin.delete(0, "end")

        if data[f"{id_event}"]["data_zamkniecia"] != '':
            self.data_zamkniecia.set_date(data[f"{id_event}"]["data_zamkniecia"])
        else:
            self.data_zamkniecia.delete(0, "end")

        self.status_combobox.current(int(data[f"{id_event}"]["status"]) + 1)

    def zapisz_zmiany(self, event):
        with open('todo.json', encoding='utf-8') as json_file:
            data = json.load(json_file)
        id_ = str(self.id_event__)
        if id_ not in data:
            data[id_] = {}

        data[id_]['nazwa'] = self.event_nazwa_entry.get()
        data[id_]['opis'] = self.scrolled_text.get("1.0", tk.END)
        data[id_]['data_dodania'] = self.data_dodania.get()
        data[id_]['termin'] = self.data_termin.get()
        data[id_]['data_zamkniecia'] = self.data_zamkniecia.get()
        if self.status_combobox.get() == 'DONE':
            data[id_]['status'] = '1'
        else:
            data[id_]['status'] = '0'

        with open('todo.json', 'w', encoding='utf-8') as outfile:
            json.dump(data, outfile)
        self.update_treeviews(0)

    def nowy_event(self):
        self.id_event__ = self.get_last_id()
        self.event_id.config(text=f'ID: {self.id_event__}')
        self.event_nazwa_entry.delete(0, 'end')
        self.event_nazwa_entry.focus()
        self.scrolled_text.delete('1.0', tk.END)
        self.data_dodania.set_date(datetime.date.today())
        self.data_termin.delete(0, "end")
        self.data_zamkniecia.delete(0, "end")
        self.status_combobox.current(1)
        self.update_treeviews(0)

    @staticmethod
    def get_last_id():
        with open('todo.json', encoding='utf-8') as json_file:
            data = json.load(json_file)
        return int(list(data.keys())[-1]) + 1

class Wyciagi_frame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.configure(bg='#383232')
        self.kolor_razem = '#b58b14'
        self.kolor_font = 'white'
        self.kolor_font_razem = 'black'
        self.kolor_legenda = '#383232'
        self.id_event__ = 0
        self.create_wyciagi_LF()
        self.create_wyciagi_RF()
        self.dane_wyciagi_json = self.get_dane_wyciagi_json()

    def create_wyciagi_LF(self):
        self.wyciagi_LF = tk.Frame(self)
        self.wyciagi_LF.configure(bg='#383232', relief='groove', bd=1)
        self.wyciagi_LF.place(relx=0.01, rely=0.02, relwidth=0.48, relheight=0.96)
        self.create_wyciagi_buttons()
        self.create_wyciagi_combobox_frame()
        self.create_wyciagi_treeview()

    def create_wyciagi_RF(self):
        self.wyciagi_RF = tk.Frame(self)
        self.wyciagi_RF.configure(bg='#383232', relief='groove', bd=1)
        self.wyciagi_RF.place(relx=0.51, rely=0.02, relwidth=0.48, relheight=0.96)

        self.create_wyszukaj_przelew_remotes()
        self.create_wyszukaj_przelew_treeview()

    def create_wyciagi_buttons(self):
        self.dodaj_button = tk.Button(self.wyciagi_LF, text='DODAJ NOWY WYCIĄG',
                                      bg='#544949', command=self.wybierz_plik_wyciagu,
                                      fg=f'{self.kolor_razem}')
        self.dodaj_button.place(relx=0.34, rely=0.96, relwidth=0.65, relheight=0.03)

        self.usun_button = tk.Button(self.wyciagi_LF, text='USUŃ WYCIĄG',
                                     bg='#544949', command=self.usun_wyciag,
                                     fg=f'{self.kolor_razem}')
        self.usun_button.place(relx=0.67, rely=0.92, relwidth=0.32, relheight=0.03)

        self.eksportuj_button = tk.Button(self.wyciagi_LF, text='EKSPORTUJ WYCIĄG',
                                          bg='#544949', command=self.eksportuj_wyciag_do_sage,
                                          fg=f'{self.kolor_razem}')
        self.eksportuj_button.place(relx=0.34, rely=0.92, relwidth=0.32, relheight=0.03)

        self.konta_specjalne_button = tk.Button(self.wyciagi_LF, text='KONTA SPECJALNE',
                                                bg='#544949', command=self.create_konta_specjalne_toplevel,
                                                fg=f'{self.kolor_razem}')
        self.konta_specjalne_button.place(relx=0.01, rely=0.92, relwidth=0.32, relheight=0.03)

        self.kontrahenci_button = tk.Button(self.wyciagi_LF, text='KONTRAHENCI',
                                            bg='#544949', command=self.create_kontrahenci_toplevel,
                                            fg=f'{self.kolor_razem}')
        self.kontrahenci_button.place(relx=0.01, rely=0.96, relwidth=0.32, relheight=0.03)

    def create_wyciagi_combobox_frame(self):
        self.wyciagi_combobox_frame = tk.Frame(self.wyciagi_LF)
        self.wyciagi_combobox_frame.configure(bg='#383232', relief='groove', bd=1)
        self.wyciagi_combobox_frame.place(relx=0.01, rely=0.01, relwidth=0.98, relheight=0.04)

        mil_label = tk.Label(self.wyciagi_combobox_frame, text='MIL: ', bg='#383232', fg='#80e89b', anchor='w')
        mil_label.place(relx=0.03, rely=0.2, relwidth=0.04, relheight=0.6)
        pko_label = tk.Label(self.wyciagi_combobox_frame, text='PKO: ', bg='#383232', fg='#80e89b', anchor='w')
        pko_label.place(relx=0.53, rely=0.2, relwidth=0.04, relheight=0.6)

        wyciagi = self.set_wyciagi_combobox_lists()

        self.mil_combobox = ttk.Combobox(self.wyciagi_combobox_frame, values=wyciagi[0],
                                         height=30, state='readonly')
        self.mil_combobox.place(relx=0.08, rely=0.2, relwidth=0.38, relheight=0.6)
        self.mil_combobox.bind("<<ComboboxSelected>>", lambda event: self.update_wyciagi_treeview(bank='MIL'))

        self.pko_combobox = ttk.Combobox(self.wyciagi_combobox_frame, values=wyciagi[1],
                                         height=30, state='readonly')
        self.pko_combobox.place(relx=0.58, rely=0.2, relwidth=0.38, relheight=0.6)
        self.pko_combobox.bind("<<ComboboxSelected>>", lambda event: self.update_wyciagi_treeview(bank='PKO'))

    def create_wyciagi_treeview(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', fieldbackground="#383232", background="#383232", foreground='white')
        style.configure("Treeview.Heading", background="#383232", foreground="white")
        style.map('Treeview.Heading', background=[('disabled', '#383232')])

        def fixed_map(option):  # naprawa buga wersji dla Python 3.7 przy wyświetlaniu koloru linii w treeview
            return [elm for elm in style.map("Treeview", query_opt=option)
                    if elm[:2] != ("!disabled", "!selected")]

        style.map("Treeview", foreground=fixed_map("foreground"),
                  background=fixed_map("background"))

        self.wyciagi_treeview_frame = tk.Frame(self.wyciagi_LF)
        self.wyciagi_treeview_frame.configure(bg='#383232', relief='groove', bd=1)
        self.wyciagi_treeview_frame.place(relx=0.01, rely=0.07, relwidth=0.98, relheight=0.84)

        self.wyciagi_columns = ['LP', 'DATA', 'TYTUŁ', 'KWOTA', 'KONTO_WN', 'KONTO_MA']
        self.wyciagi_treeview = ttk.Treeview(self.wyciagi_treeview_frame, columns=self.wyciagi_columns,
                                             show='headings',
                                             style="Treeview", selectmode="browse")

        self.wyciagi_treeview.heading('LP', text='LP')
        self.wyciagi_treeview.column('LP', width=40, stretch='no', anchor='center')
        self.wyciagi_treeview.heading(f'{self.wyciagi_columns[1]}', text=f'{self.wyciagi_columns[1]}')
        self.wyciagi_treeview.column(f'{self.wyciagi_columns[1]}', width=100, stretch='no', anchor='center')
        self.wyciagi_treeview.heading(f'{self.wyciagi_columns[2]}', text=f'{self.wyciagi_columns[2]}')
        self.wyciagi_treeview.column(f'{self.wyciagi_columns[2]}', minwidth=250, stretch='yes', anchor='center')
        self.wyciagi_treeview.heading(f'{self.wyciagi_columns[3]}', text=f'{self.wyciagi_columns[3]}')
        self.wyciagi_treeview.column(f'{self.wyciagi_columns[3]}', width=100, stretch='no', anchor='center')
        self.wyciagi_treeview.heading(f'{self.wyciagi_columns[4]}', text=f'{self.wyciagi_columns[4]}')
        self.wyciagi_treeview.column(f'{self.wyciagi_columns[4]}', width=100, stretch='no', anchor='center')
        self.wyciagi_treeview.heading(f'{self.wyciagi_columns[5]}', text=f'{self.wyciagi_columns[5]}')
        self.wyciagi_treeview.column(f'{self.wyciagi_columns[5]}', width=100, stretch='no', anchor='center')

        self.scrolly = ttk.Scrollbar(self.wyciagi_treeview_frame, orient='vertical',
                                     command=self.wyciagi_treeview.yview)
        self.wyciagi_treeview.configure(yscrollcommand=self.scrolly.set)
        map(lambda col: col.configure(yscrollcommand=self.scrolly.set), self.wyciagi_columns)
        self.scrolly.pack(side=tk.RIGHT, fill=tk.Y)
        map(lambda col: col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True), self.wyciagi_columns)
        self.wyciagi_treeview.pack(expand='yes', fill='both')
        self.wyciagi_treeview.bind('<Double-1>', self.create_edit_toplevel)

    def update_wyciagi_treeview(self, bank):
        self.wyciagi_treeview.delete(*self.wyciagi_treeview.get_children())
        id_wyciag = ''
        if bank == 'MIL':
            id_wyciag = self.mil_combobox.get()
            self.pko_combobox.current(0)
        if bank == 'PKO':
            id_wyciag = self.pko_combobox.get()
            self.mil_combobox.current(0)

        if id_wyciag == '':
            return False

        with open('sage_wyciagi.json', encoding='utf-8') as json_file:
            data = json.load(json_file)

        self.wybrany_wyciag = data[id_wyciag]

        for n in range(len(self.wybrany_wyciag)):
            lp = n + 1
            data = self.wybrany_wyciag[f'{lp}']['data']
            tytul = self.wybrany_wyciag[f'{lp}']['tytul']
            kwota = self.wybrany_wyciag[f'{lp}']['kwota']
            konto_wn = self.wybrany_wyciag[f'{lp}']['konto_wn']
            konto_ma = self.wybrany_wyciag[f'{lp}']['konto_ma']
            foreground = 'white'

            # tagi kolorujace treeview
            if n % 2 == 0:
                background = 'background_dark'
            else:
                background = 'background_light'

            if tytul == 'ZAPŁATA KARTĄ' or tytul == 'PROWIZJA/OPŁATA' or konto_wn == '404-3':
                foreground = 'foreground_karty'
            elif tytul == 'PŁATNOŚĆ KARTĄ - ZAKUP' and konto_wn.endswith('-'):
                foreground = 'foreground_karty_zakupy_nieuzgodnione'
            elif tytul == 'PŁATNOŚĆ KARTĄ - ZAKUP' and konto_wn[-1] != '-':
                foreground = 'foreground_karty_zakupy_uzgodnione'
            elif tytul == 'WPŁATA GOTÓWKOWA':
                foreground = 'foreground_wplata_gotwki'
            elif konto_wn == '' or konto_ma == '':
                foreground = 'foreground_brak'
            elif '(H)' in tytul:
                foreground = 'foreground_hurtownie'
            elif '(K)' in tytul:
                foreground = 'foreground_koszty'
            elif '(T)' in tytul:
                foreground = 'foreground_towar'
            elif '200' in konto_ma or konto_ma == '149' or konto_ma == '145':
                foreground = 'foreground_przychod'
            elif konto_wn == '230':
                foreground = 'foreground_wynagrodzenie'
            elif 'PODATEK' in tytul or 'ZUS' in tytul or '221' in konto_wn:
                foreground = 'foreground_podatki_zus'
            elif 'PRZELEW ŚRODKÓW WŁASNYCH' in tytul:
                foreground = 'foreground_przelew_srdokow_wychodzacy'
            elif konto_wn == '134' or konto_ma == '134' or konto_wn == '137' or konto_ma == '137':
                foreground = 'foreground_split'

            self.wyciagi_treeview.tag_configure('background_dark', background='#383232')
            self.wyciagi_treeview.tag_configure('background_light', background='#262424')
            self.wyciagi_treeview.tag_configure('foreground_karty', foreground='#8c8787')
            self.wyciagi_treeview.tag_configure('foreground_karty_zakupy_nieuzgodnione', foreground='#3068d1')
            self.wyciagi_treeview.tag_configure('foreground_karty_zakupy_uzgodnione', foreground='#eb5a00')
            self.wyciagi_treeview.tag_configure('foreground_wplata_gotwki', foreground='#3ea800')
            self.wyciagi_treeview.tag_configure('foreground_brak', foreground='#c2041a')
            self.wyciagi_treeview.tag_configure('foreground_hurtownie', foreground='#eba800')
            self.wyciagi_treeview.tag_configure('foreground_koszty', foreground='#eb5a00')
            self.wyciagi_treeview.tag_configure('foreground_przelew_srdokow_wychodzacy', foreground='#eb5a00')
            self.wyciagi_treeview.tag_configure('foreground_towar', foreground='#fa7b2d')
            self.wyciagi_treeview.tag_configure('foreground_przychod', foreground='#3ea800')
            self.wyciagi_treeview.tag_configure('foreground_wynagrodzenie', foreground='#aaf2d3')
            self.wyciagi_treeview.tag_configure('foreground_podatki_zus', foreground='#d95b63')
            self.wyciagi_treeview.tag_configure('foreground_split', foreground='#d95b63')

            # ['LP', 'DATA', 'TYTUŁ', 'KWOTA', 'KONTO_WN', 'KONTO_MA']
            self.wyciagi_treeview.insert('', 'end', values=(lp, data, tytul, kwota, konto_wn, konto_ma),
                                         tags=(background, foreground))

    def create_edit_toplevel(self, event):
        self.edit_toplevel = tk.Toplevel(self, background='#383232',
                                         highlightthickness=2)
        self.edit_toplevel.grab_set()
        self.edit_toplevel.geometry(f'500x700+800+100')

        # labels
        # 0 - nr transakcji, 1 - data, 2 - tytuł, 3 - kontrahent, 4 - kwota, 5 - nip
        # 6 -konto_wn, 7 - konto_ma, 8 - id_sage, 9 - rachunek, 10 - konto specjalne, 11 - opis
        nr_transakcji_lb = tk.Label(self.edit_toplevel, text='Nr trans.', bg='#383232', fg='#80e89b', anchor='w')
        nr_transakcji_lb.place(relx=0.02, rely=0.03, relwidth=0.2, relheight=0.04)
        data_lb = tk.Label(self.edit_toplevel, text='Data', bg='#383232', fg='#80e89b', anchor='w')
        data_lb.place(relx=0.02, rely=0.08, relwidth=0.2, relheight=0.04)
        tytul_lb = tk.Label(self.edit_toplevel, text='Tytuł', bg='#383232', fg='#80e89b', anchor='w')
        tytul_lb.place(relx=0.02, rely=0.13, relwidth=0.2, relheight=0.04)
        kontrahent_lb = tk.Label(self.edit_toplevel, text='Kontrahent', bg='#383232', fg='#80e89b', anchor='w')
        kontrahent_lb.place(relx=0.02, rely=0.29, relwidth=0.2, relheight=0.04)
        kwota_lb = tk.Label(self.edit_toplevel, text='Kwota', bg='#383232', fg='#80e89b', anchor='w')
        kwota_lb.place(relx=0.02, rely=0.45, relwidth=0.2, relheight=0.04)
        nip_lb = tk.Label(self.edit_toplevel, text='NIP', bg='#383232', fg='#80e89b', anchor='w')
        nip_lb.place(relx=0.02, rely=0.50, relwidth=0.2, relheight=0.04)
        konto_wn_lb = tk.Label(self.edit_toplevel, text='KONTO WN', bg='#383232', fg='#80e89b', anchor='w')
        konto_wn_lb.place(relx=0.02, rely=0.55, relwidth=0.2, relheight=0.04)
        konto_ma_lb = tk.Label(self.edit_toplevel, text='KONTO MA', bg='#383232', fg='#80e89b', anchor='w')
        konto_ma_lb.place(relx=0.02, rely=0.60, relwidth=0.2, relheight=0.04)
        id_sage_lb = tk.Label(self.edit_toplevel, text='ID SAGE', bg='#383232', fg='#80e89b', anchor='w')
        id_sage_lb.place(relx=0.02, rely=0.65, relwidth=0.2, relheight=0.04)
        rachunek_lb = tk.Label(self.edit_toplevel, text='Rachunek', bg='#383232', fg='#80e89b', anchor='w')
        rachunek_lb.place(relx=0.02, rely=0.70, relwidth=0.2, relheight=0.04)
        konto_spec_lb = tk.Label(self.edit_toplevel, text='Konto spec.', bg='#383232', fg='#80e89b', anchor='w')
        konto_spec_lb.place(relx=0.02, rely=0.75, relwidth=0.2, relheight=0.04)
        # button zapisz zmiany
        self.nr_transakcji_entry = tk.Entry(self.edit_toplevel, justify='center', bg='#6b685f', fg='white')
        self.nr_transakcji_entry.place(relx=0.21, rely=0.03, relwidth=0.77, relheight=0.04)
        self.data_entry = tk.Entry(self.edit_toplevel, justify='center', bg='#6b685f', fg='white')
        self.data_entry.place(relx=0.21, rely=0.08, relwidth=0.77, relheight=0.04)
        self.tytul_text = tk.Text(self.edit_toplevel, bg='#6b685f', fg='white', wrap='word')
        self.tytul_text.place(relx=0.21, rely=0.13, relwidth=0.77, relheight=0.15)
        self.kontrahent_text = tk.Text(self.edit_toplevel, bg='#6b685f', fg='white', wrap='word')
        self.kontrahent_text.place(relx=0.21, rely=0.29, relwidth=0.77, relheight=0.15)
        self.kwota_entry = tk.Entry(self.edit_toplevel, justify='center', bg='#6b685f', fg='white')
        self.kwota_entry.place(relx=0.21, rely=0.45, relwidth=0.77, relheight=0.04)
        self.nip_entry = tk.Entry(self.edit_toplevel, justify='center', bg='#6b685f', fg='white')
        self.nip_entry.place(relx=0.21, rely=0.50, relwidth=0.77, relheight=0.04)
        self.konto_wn_entry = tk.Entry(self.edit_toplevel, justify='center', bg='#6b685f', fg='white')
        self.konto_wn_entry.place(relx=0.21, rely=0.55, relwidth=0.77, relheight=0.04)
        self.konto_ma_entry = tk.Entry(self.edit_toplevel, justify='center', bg='#6b685f', fg='white')
        self.konto_ma_entry.place(relx=0.21, rely=0.60, relwidth=0.77, relheight=0.04)
        self.id_sage_entry = tk.Entry(self.edit_toplevel, justify='center', bg='#6b685f', fg='white')
        self.id_sage_entry.place(relx=0.21, rely=0.65, relwidth=0.77, relheight=0.04)
        self.rachunek_entry = tk.Entry(self.edit_toplevel, justify='center', bg='#6b685f', fg='white')
        self.rachunek_entry.place(relx=0.21, rely=0.70, relwidth=0.77, relheight=0.04)
        self.konto_spec_entry = tk.Entry(self.edit_toplevel, justify='center', bg='#6b685f', fg='white')
        self.konto_spec_entry.place(relx=0.21, rely=0.75, relwidth=0.77, relheight=0.04)

        item = self.wyciagi_treeview.selection()
        id_transakcji = self.wyciagi_treeview.item(item, 'values')[0]
        id_wyciag = self.mil_combobox.get()
        if id_wyciag == '':
            id_wyciag = self.pko_combobox.get()

        with open('sage_wyciagi.json', encoding='utf-8') as json_file:
            data = json.load(json_file)

        wyciag = data[id_wyciag]
        self.nr_transakcji_entry.insert(0, id_transakcji)
        self.data_entry.insert(0, wyciag[id_transakcji]['data'])
        self.tytul_text.insert('1.0', wyciag[id_transakcji]['tytul'])
        self.kontrahent_text.insert('1.0', wyciag[id_transakcji]['kontrahent'])
        self.kwota_entry.insert(0, wyciag[id_transakcji]['kwota'])
        self.nip_entry.insert(0, wyciag[id_transakcji]['nip'])
        self.konto_wn_entry.insert(0, wyciag[id_transakcji]['konto_wn'])
        self.konto_ma_entry.insert(0, wyciag[id_transakcji]['konto_ma'])
        self.id_sage_entry.insert(0, wyciag[id_transakcji]['id_sage'])
        self.rachunek_entry.insert(0, wyciag[id_transakcji]['rachunek'])
        self.konto_spec_entry.insert(0, wyciag[id_transakcji]['konto_spec'])

        zamknij_button = tk.Button(self.edit_toplevel, text='ZAMKNIJ',
                                   bg='#544949', command=self.zamknij_edit_toplevel,
                                   fg=f'{self.kolor_razem}')
        zamknij_button.place(relx=0.21, rely=0.95, relwidth=0.77, relheight=0.04)

        zapisz_zmiany_button = tk.Button(self.edit_toplevel, text='ZAPISZ ZMIANY',
                                         bg='#544949', command=self.zapisz_zmiany_edit_toplevel,
                                         fg=f'{self.kolor_razem}')
        zapisz_zmiany_button.place(relx=0.21, rely=0.9, relwidth=0.77, relheight=0.04)

    def zamknij_edit_toplevel(self):
        self.edit_toplevel.destroy()

    def zapisz_zmiany_edit_toplevel(self):
        id_wyciag = self.mil_combobox.get()
        bank = 'MIL'
        if id_wyciag == '':
            id_wyciag = self.pko_combobox.get()
            bank = 'PKO'

        id_transakcji = self.nr_transakcji_entry.get()
        data_transakcji = self.data_entry.get()
        tytul = self.tytul_text.get('1.0', 'end').replace('\n', '')
        kontrahent = self.kontrahent_text.get('1.0', 'end').replace('\n', '')
        kwota = self.kwota_entry.get()
        nip = self.nip_entry.get()
        konto_wn = self.konto_wn_entry.get()
        konto_ma = self.konto_ma_entry.get()
        id_sage = self.id_sage_entry.get()
        rachnek = self.rachunek_entry.get()
        konto_spec = self.konto_spec_entry.get()

        with open('sage_wyciagi.json', encoding='utf-8') as json_file:
            data = json.load(json_file)

        data[id_wyciag][id_transakcji]['data'] = data_transakcji
        data[id_wyciag][id_transakcji]['tytul'] = tytul
        data[id_wyciag][id_transakcji]['kontrahent'] = kontrahent
        data[id_wyciag][id_transakcji]['kwota'] = kwota
        data[id_wyciag][id_transakcji]['nip'] = nip
        data[id_wyciag][id_transakcji]['konto_wn'] = konto_wn
        data[id_wyciag][id_transakcji]['konto_ma'] = konto_ma
        data[id_wyciag][id_transakcji]['id_sage'] = id_sage
        data[id_wyciag][id_transakcji]['rachunek'] = rachnek
        data[id_wyciag][id_transakcji]['konto_spec'] = konto_spec

        with open('sage_wyciagi.json', 'w', encoding='utf-8') as outfile:
            json.dump(data, outfile)

        self.zamknij_edit_toplevel()
        self.update_wyciagi_treeview(bank=bank)

    @staticmethod
    def set_wyciagi_combobox_lists():
        with open('sage_wyciagi.json', encoding='utf-8') as json_file:
            data = json.load(json_file)
        mil_list = []
        pko_list = []
        for k in data.keys():
            if 'MIL' in k:
                mil_list.append(k)
            if 'PKO' in k:
                pko_list.append(k)

        mil_list.reverse()
        pko_list.reverse()
        mil_list.insert(0, '')
        pko_list.insert(0, '')
        return [mil_list, pko_list]

    def wybierz_plik_wyciagu(self):
        pliki_typ = ("wszystkie pliki", "*.*")

        self.wyciag_filename = tk.filedialog.askopenfilename(initialdir=r'C:\Users\dell\Dysk Google\IMPORTY\WYCIĄGI',
                                                             title="Wybierz plik",
                                                             filetypes=(pliki_typ, ("wszystkie pliki", "*.*")))
        if 'MIL' in self.wyciag_filename and 'sta' in self.wyciag_filename:
            self.dodaj_wyciag(bank='mil')
        if 'PKO' in self.wyciag_filename and 'xml' in self.wyciag_filename:
            self.dodaj_wyciag(bank='pko')

    def dodaj_wyciag(self, bank):
        dane_do_wyciagu = ''
        if bank == 'mil':
            dane_do_wyciagu = self.mt940_parser()
        if bank == 'pko':
            dane_do_wyciagu = self.pko_parser()

        id_wyciag = self.wyciag_filename.split('/')[-1][:-4]

        with open('sage_wyciagi.json', encoding='utf-8') as json_file:
            data = json.load(json_file)

        if id_wyciag not in data:
            data[id_wyciag] = {}

        for dane in dane_do_wyciagu:
            if dane[0] not in data[id_wyciag]:
                data[id_wyciag][f"{dane[0]}"] = {}

            dane_transakcji = {'data': str(dane[1]), 'tytul': dane[2], 'kontrahent': dane[3],
                               'kwota': dane[4], 'nip': dane[5], 'konto_wn': dane[6], 'konto_ma': dane[7],
                               'id_sage': dane[8], 'rachunek': dane[9], 'konto_spec': dane[10], 'rodzaj': dane[11]}
            data[id_wyciag][f"{dane[0]}"] = dane_transakcji
            print(dane_transakcji)

        with open('sage_wyciagi.json', 'w', encoding='utf-8') as outfile:
            json.dump(data, outfile)

        lista_wyciagow = self.set_wyciagi_combobox_lists()
        self.mil_combobox.configure(values=lista_wyciagow[0])
        self.pko_combobox.configure(values=lista_wyciagow[1])
        messagebox.showinfo('ok', f'DODANO WYCIĄG {id_wyciag}')
        self.get_dane_wyciagi_json()

    @staticmethod
    def sprawdz_konto_spec(nr_rachunku):
        with open('sage_konta_specjalne.json', encoding='utf-8') as json_file:
            data = json.load(json_file)
        if nr_rachunku in data:
            return [data[nr_rachunku]['tytul'], data[nr_rachunku]['konto_wn'], data[nr_rachunku]['konto_ma']]
        return False

    @staticmethod
    def sprawdz_biala_lista(konto, data_param):
        dane = requests.get(f'https://wl-api.mf.gov.pl/api/search/bank-account/{konto}?date={data_param}')
        dane = dane.json()
        print(dane)
        if dane['result']['subjects'] == []:
            print('BRAK DANYCH W BIAŁEJ LIŚCIE')
            return False

        elif 'result' in dane and dane['result']['subjects'] != []:
            nip = dane['result']['subjects'][0]['nip']
            return nip

    def usun_wyciag(self):
        id_wyciag = self.mil_combobox.get()
        if id_wyciag == '':
            id_wyciag = self.pko_combobox.get()

        if id_wyciag == '':
            messagebox.showinfo('INFO', 'WYBIERZ WYCIĄG DO EKSPORTU')
            return 0

        with open('sage_wyciagi.json', encoding='utf-8') as json_file:
            data = json.load(json_file)

        data.pop(f'{id_wyciag}', None)

        with open('sage_wyciagi.json', 'w', encoding='utf-8') as outfile:
            json.dump(data, outfile)

        lista_wyciagow = self.set_wyciagi_combobox_lists()
        self.mil_combobox.configure(values=lista_wyciagow[0])
        self.mil_combobox.current(0)
        self.pko_combobox.configure(values=lista_wyciagow[1])
        self.pko_combobox.current(0)
        self.wyciagi_treeview.delete(*self.wyciagi_treeview.get_children())

    def mt940_parser(self):
        transactions = mt940.parse(self.wyciag_filename)
        data_biala_lista = datetime.date.today()
        lista_zwrotna = []  # 0 - nr transakcji, 1 - data, 2 - tytuł, 3 - kontrahent, 4 - kwota, 5 - nip
        # 6 -konto_wn, 7 - konto_ma, 8 - id_sage, 9 - rachunek, 10 - konto specjalne, 11 - opis

        with open('sage_kontrahenci.json', encoding='utf-8') as json_file:
            kontrahenci_stali = json.load(json_file)

            nr_transakcji = 1
            for t in transactions:
                szczeguly = t.data['transaction_details'].split('\n')
                opis = szczeguly[0][6:]
                data_transakcji = t.data['date']
                tytul = ''
                nr_rachunku = ''
                kontrahent = szczeguly[14][3:]
                nip = ''
                id_sage = ''
                konto_wn = ''
                konto_ma = ''
                konto_specjalne = 'NIE'

                kwota = str(t.data['amount'])
                if '-' in kwota:
                    kwota = kwota.replace('-', '')[:-4]
                else:
                    kwota = kwota[:-4]

                if opis != 'PROWIZJA/OPŁATA' and opis != 'WPŁATA' and opis != 'PŁATNOŚĆ KARTĄ':
                    index_dwukropwek = szczeguly[3].index(':') + 1
                    nr_rachunku = szczeguly[3][index_dwukropwek:]
                    tytul = szczeguly[4][3:] + szczeguly[5][3:] + szczeguly[6][3:] + szczeguly[7][3:]

                # rodzaj transakcji C - uznanie, D - obciążenie
                if t.data['status'] == 'D':
                    rodzaj = 'MINUS'

                    if opis == 'PROWIZJA/OPŁATA':
                        tytul = 'PROWIZJA/OPŁATA'
                        konto_wn = '404-3'
                        konto_ma = '136'

                    if opis == 'PŁATNOŚĆ KARTĄ':
                        tytul = 'PŁATNOŚĆ KARTĄ - ZAKUP'
                        konto_wn = '202-'
                        konto_ma = '136'

                    if opis == 'PRZELEW DO US':
                        if 'VAT-7' in tytul:
                            tytul = f'PODATEK - VAT-7 {tytul.split()[3]}/{tytul.split()[7][-2:]}'
                            konto_wn = '221-5'
                            konto_ma = '136'
                        elif 'PIT-4' in tytul:
                            tytul = f'PODATEK - PIT-4 {tytul.split()[3]}/{tytul.split()[7][-2:]}'
                            konto_wn = '220-1'
                            konto_ma = '136'
                        elif 'CIT' in tytul:
                            tytul = f'PODATEK - CIT {tytul.split()[3]}/{tytul.split()[7][-2:]}'
                            konto_wn = '220-4'
                            konto_ma = '136'

                    if opis == 'PRZELEW DO ZUS':
                        tytul = f'PRZELEW DO ZUS'
                        konto_wn = '220-2'
                        konto_ma = '136'

                    if 'PRZEKSIĘGOWANIE VAT' in opis:
                        tytul = 'PRZEKIĘGOWANIE VAT'
                        konto_wn = '137'
                        konto_ma = '136'

                    if opis == 'PRZELEW WYCHODZĄCY':
                        wynik_konto_spec = self.sprawdz_konto_spec(nr_rachunku)
                        if wynik_konto_spec != False:
                            konto_specjalne = 'TAK'
                            if nr_rachunku == '70116022020000000201154264' and float(kwota) > 6900:
                                tytul = f'NAJEM - MARIA KAPPEL-ZIOŁA {tytul}'
                                konto_wn = '202-135'
                                konto_ma = '136'
                            else:
                                tytul = wynik_konto_spec[0]
                                konto_wn = wynik_konto_spec[1]
                                konto_ma = str(wynik_konto_spec[2])

                        else:
                            nip_biala_lista = self.sprawdz_biala_lista(nr_rachunku, data_biala_lista)
                            if nip_biala_lista != False:
                                nip = nip_biala_lista
                                if nip_biala_lista in kontrahenci_stali:
                                    id_sage = kontrahenci_stali[f"{nip_biala_lista}"]["id_kontrahenta"]
                                    if '(H)' in tytul:
                                        tytul = f'(H-{id_sage}): {tytul}'
                                    else:
                                        tytul = f'{tytul}'
                                        kontrahent = kontrahenci_stali[f"{nip_biala_lista}"]["nazwa"]
                                    konto_wn = f'202-{kontrahenci_stali[f"{nip_biala_lista}"]["id_kontrahenta"]}'
                                    konto_ma = '136'
                                else:
                                    print(f'Brak danych o kontach. Nazwa: {kontrahent}')
                                    kontrahent = ''
                                    konto_wn = '202-'
                                    konto_ma = '136'
                            else:
                                if nr_rachunku == '51103015080000000819321000':
                                    tytul = f'PPK PKO - {tytul}'
                                    konto_wn = '233'
                                    konto_ma = '136'

                if t.data['status'] == 'C':
                    rodzaj = 'PLUS'

                    if opis == 'WPŁATA':
                        tytul = 'WPŁATA GOTÓWKOWA'
                        konto_wn = '136'
                        konto_ma = '149'

                    elif 'SOA/' in tytul or 'Z TYT. TRANSAKCJI KARTAMI' in tytul:
                        tytul = 'ZAPŁATA KARTĄ'
                        konto_wn = '136'
                        konto_ma = '145'

                    elif 'PRZEKSIĘGOWANIE VAT' in opis:
                        tytul = 'PRZEKIĘGOWANIE VAT'
                        konto_wn = '136'
                        konto_ma = '137'

                    elif 'PRZELEW PRZYCHODZĄCY' in opis:

                        nip_biala_lista = self.sprawdz_biala_lista(nr_rachunku, data_biala_lista)
                        if nip_biala_lista != False:
                            nip = nip_biala_lista
                            if nip_biala_lista in kontrahenci_stali:
                                if nip_biala_lista == '5472110371':
                                    konto_wn = '136'
                                    konto_ma = '149'
                                else:
                                    id_sage = kontrahenci_stali[f"{nip_biala_lista}"]["id_kontrahenta"]
                                    kontrahent = kontrahenci_stali[f"{nip_biala_lista}"]["nazwa"]
                                    konto_wn = '136'
                                    konto_ma = f'200-{kontrahenci_stali[f"{nip_biala_lista}"]["id_kontrahenta"]}'

                            else:
                                print(f'Brak kontrahenta w bazie')
                                kontrahent = ''
                                konto_wn = '136'
                                konto_ma = f'200-'
                        else:
                            print(f'Brak danych o kontach. Nazwa: {kontrahent}')
                            konto_wn = '136'
                            konto_ma = f''

                lista_zwrotna.append([nr_transakcji, data_transakcji, tytul, kontrahent, kwota,
                                      nip, konto_wn, konto_ma, id_sage, nr_rachunku, konto_specjalne, rodzaj])
                nr_transakcji += 1

        return lista_zwrotna

    def pko_parser(self):
        data_biala_lista = datetime.date.today()
        lista_zwrotna = []
        tree = ET.parse(self.wyciag_filename)
        root = tree.getroot()

        with open('sage_kontrahenci.json', encoding='utf-8') as json_file:
            kontrahenci_stali = json.load(json_file)

            for elem in root.iter('operation'):

                # 0 - nr transakcji, 1 - data, 2 - tytuł, 3 - kontrahent, 4 - kwota, 5 - nip
                # 6 -konto_wn, 7 - konto_ma, 8 - id_sage, 9 - rachunek, 10 - konto specjalne, 11 - opis

                data_operacji = elem.find('exec-date').text
                kontrahent = ''
                kwota = (elem.find('amount').text).strip('-').strip('+')
                nip = ''
                konto_wn = ''
                konto_ma = ''
                id_sage = ''
                rachunek = ''
                konto_specjalne = 'NIE'
                opis_pm = ''

                rodzaj = elem.find('type').text

                if rodzaj == 'Opłata':
                    tytul = 'OPŁATA'
                    konto_ma = '130'
                    konto_wn = '404-3'
                    opis_pm = 'MINUS'

                if rodzaj == 'Przelew na rachunek' or rodzaj == 'Przelew zagraniczny':
                    opis = elem.find('description').text
                    opis_new = opis.split('\n')
                    opis_pm = 'PLUS'
                    for n_opis in opis_new:
                        nn = n_opis.split(': ')
                        if nn[0] == 'Rachunek nadawcy':
                            rachunek = nn[1].replace(' ', '')
                        if nn[0] == 'Nazwa nadawcy':
                            kontrahent = nn[1]
                        if nn[0] == 'Tytuł':
                            tytul = nn[1]

                    if 'ŚLĄSKI ODDZIAŁ WOJEWÓDZKI' in kontrahent:
                        tytul = f'NFZ: {tytul}'
                        kontrahent = 'NFZ'
                        konto_wn = '130'
                        konto_ma = '200-11'

                    elif rachunek == '73102013900000610205981081':
                        tytul = f'ZWROT Z KONTA VAT'
                        konto_wn = '130'
                        konto_ma = '134'

                    else:
                        nip_biala_lista = self.sprawdz_biala_lista(rachunek, data_biala_lista)
                        nip = nip_biala_lista
                        if nip_biala_lista in kontrahenci_stali:
                            id_sage = kontrahenci_stali[f"{nip_biala_lista}"]["id_kontrahenta"]
                            kontrahent = kontrahenci_stali[f"{nip_biala_lista}"]["nazwa"]
                            konto_wn = '130'
                            konto_ma = f'200-{kontrahenci_stali[f"{nip_biala_lista}"]["id_kontrahenta"]}'
                            tytul = f'{kontrahent} - {tytul}'

                        else:
                            print(f'Brak kontrahenta w bazie')
                            kontrahent = ''
                            konto_wn = '136'
                            konto_ma = f'200-'

                if rodzaj == 'Przelew z rachunku' or rodzaj == 'Przelew podatkowy':
                    opis = elem.find('description').text
                    opis_new = opis.split('\n')
                    opis_pm = 'MINUS'
                    for n_opis in opis_new:
                        nn = n_opis.split(': ')
                        if nn[0] == 'Rachunek odbiorcy':
                            rachunek = nn[1].replace(' ', '')
                        if nn[0] == 'Nazwa odbiorcy':
                            kontrahent = nn[1]
                        if nn[0] == 'Tytuł':
                            tytul = nn[1]
                        if nn[0] == 'Symbol formularza':
                            symbol_form = nn[1]
                        if nn[0] == 'Okres płatności':
                            okres_form = nn[1]
                        if nn[0] == 'Numer faktury VAT lub okres płatności zbiorczej':
                            opis_vat_split = nn[1]

                    if rodzaj == 'Przelew podatkowy':
                        tytul = f'PODATEK - {symbol_form} {okres_form} {kontrahent}'
                        if 'VAT' in symbol_form:
                            konto_wn = '221-5'
                        else:
                            konto_wn = ''
                        konto_ma = '130'

                    elif rachunek == "73102013900000610205981081":
                        tytul = f'PRZELEW VAT SPLIT PAYMENT'
                        konto_wn = '134'
                        konto_ma = '130'

                    elif rachunek == "71116022020000000469095212":
                        tytul = f'PRZELEW ŚRODKÓW WŁASNYCH'
                        konto_ma = '130'
                        konto_wn = '149'

                lista_zwrotna.append([data_operacji, tytul, kontrahent, kwota, nip,
                                      konto_wn, konto_ma, id_sage, rachunek, konto_specjalne, opis_pm])

        lista_zwrotna.reverse()
        n = 1
        for l in lista_zwrotna:
            l.insert(0, n)
            n += 1

        return lista_zwrotna

    def eksportuj_wyciag_do_sage(self):
        id_wyciag = self.mil_combobox.get()
        if id_wyciag == '':
            id_wyciag = self.pko_combobox.get()

        if id_wyciag == '':
            messagebox.showinfo('INFO', 'WYBIERZ WYCIĄG DO EKSPORTU')
            return 0

        wyciag_lista = self.get_dane_wyciag_eksport(id_wyciag)

        ahk = AHK(executable_path=r"C:\Program Files\AutoHotkey\AutoHotkey.exe")
        lista_okien = list(ahk.windows())
        for okno in lista_okien:
            if 'Symfonia Finanse' in str(okno.title):
                okno.activate()
                sleep(1)
                break
        sleep(1)
        ahk.click(208, 210)

        for n in wyciag_lista:
            sleep(0.3)
            ahk.type(n[0])
            ahk.key_press('ENTER')
            ahk.key_press('ENTER')
            os.system(f"echo {n[1].strip('&')} | clip")
            ahk.send_input('^v')
            ahk.key_press('ENTER')
            ahk.key_press('ENTER')
            ahk.type(f'{n[2]}')
            ahk.key_press('ENTER')
            if n[3] != '':
                ahk.type(f'{n[3]}')
            ahk.key_press('ENTER')
            ahk.key_press('ENTER')
            ahk.type(f'{n[4]}')
            ahk.key_press('ENTER')

    @staticmethod
    def get_dane_wyciag_eksport(id_wyciag):
        wyciag_lista = []
        with open('sage_wyciagi.json', encoding='utf-8') as json_file:
            data = json.load(json_file)

        wyciag = data[id_wyciag]
        for k in wyciag:
            wyciag_lista.append([wyciag[k]['data'], wyciag[k]['tytul'], wyciag[k]['kwota'],
                                 wyciag[k]['konto_wn'], wyciag[k]['konto_ma']])
        return wyciag_lista

    def create_konta_specjalne_toplevel(self):
        self.konta_specjalne_tpl = tk.Toplevel(self.wyciagi_LF, background='#383232',
                                               highlightthickness=2)
        self.konta_specjalne_tpl.grab_set()
        self.konta_specjalne_tpl.title('KONATA SPECJALNE')
        self.konta_specjalne_tpl.geometry(f'1200x600+200+100')

        self.create_konta_specjalne_treeview()
        self.update_konta_specjalne_treeview()
        self.create_konta_specjalne_remotes()

        dodaj_popraw_button = tk.Button(self.konta_specjalne_tpl, text='DODAJ / POPRAW',
                                        bg='#544949', command=self.dodaj_popraw_zapis_konto_spec,
                                        fg=f'{self.kolor_razem}')
        dodaj_popraw_button.place(relx=0.72, rely=0.95, relwidth=0.27, relheight=0.04)

        usun_button = tk.Button(self.konta_specjalne_tpl, text='USUŃ',
                                bg='#544949', command=self.usun_zapis_konto_spec,
                                fg=f'{self.kolor_razem}')
        usun_button.place(relx=0.72, rely=0.9, relwidth=0.27, relheight=0.04)

    def create_konta_specjalne_treeview(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', fieldbackground="#383232", background="#383232", foreground='white')
        style.configure("Treeview.Heading", background="#383232", foreground="white")
        style.map('Treeview.Heading', background=[('disabled', '#383232')])

        def fixed_map(option):  # naprawa buga wersji dla Python 3.7 przy wyświetlaniu koloru linii w treeview
            return [elm for elm in style.map("Treeview", query_opt=option)
                    if elm[:2] != ("!disabled", "!selected")]

        style.map("Treeview", foreground=fixed_map("foreground"),
                  background=fixed_map("background"))

        self.konta_specjalne_treeview_frame = tk.Frame(self.konta_specjalne_tpl)
        self.konta_specjalne_treeview_frame.configure(bg='#383232', relief='groove', bd=1)
        self.konta_specjalne_treeview_frame.place(relx=0.01, rely=0.01, relwidth=0.7, relheight=0.98)

        self.konta_specjalne_columns = ['LP', 'TYTUŁ', 'NR KONTA', 'KONTO_WN', 'KONTO_MA']
        self.konta_specjalne_treeview = ttk.Treeview(self.konta_specjalne_treeview_frame,
                                                     columns=self.konta_specjalne_columns,
                                                     show='headings',
                                                     style="Treeview", selectmode="browse")

        self.konta_specjalne_treeview.heading('LP', text='LP')
        self.konta_specjalne_treeview.column('LP', width=40, stretch='no', anchor='center')
        self.konta_specjalne_treeview.heading(f'{self.konta_specjalne_columns[1]}',
                                              text=f'{self.konta_specjalne_columns[1]}')
        self.konta_specjalne_treeview.column(f'{self.konta_specjalne_columns[1]}', minwidth=250, stretch='yes',
                                             anchor='center')
        self.konta_specjalne_treeview.heading(f'{self.konta_specjalne_columns[2]}',
                                              text=f'{self.konta_specjalne_columns[2]}')
        self.konta_specjalne_treeview.column(f'{self.konta_specjalne_columns[2]}', width=200, stretch='no',
                                             anchor='center')
        self.konta_specjalne_treeview.heading(f'{self.konta_specjalne_columns[3]}',
                                              text=f'{self.konta_specjalne_columns[3]}')
        self.konta_specjalne_treeview.column(f'{self.konta_specjalne_columns[3]}', width=100, stretch='no',
                                             anchor='center')
        self.konta_specjalne_treeview.heading(f'{self.konta_specjalne_columns[4]}',
                                              text=f'{self.konta_specjalne_columns[4]}')
        self.konta_specjalne_treeview.column(f'{self.konta_specjalne_columns[4]}', width=100, stretch='no',
                                             anchor='center')

        self.scrolly = ttk.Scrollbar(self.konta_specjalne_treeview_frame, orient='vertical',
                                     command=self.konta_specjalne_treeview.yview)
        self.konta_specjalne_treeview.configure(yscrollcommand=self.scrolly.set)
        map(lambda col: col.configure(yscrollcommand=self.scrolly.set), self.konta_specjalne_columns)
        self.scrolly.pack(side=tk.RIGHT, fill=tk.Y)
        map(lambda col: col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True), self.konta_specjalne_columns)
        self.konta_specjalne_treeview.pack(expand='yes', fill='both')
        self.konta_specjalne_treeview.bind('<Double-1>', self.get_dane_to_update_konta_spec)

    def update_konta_specjalne_treeview(self):
        self.konta_specjalne_treeview.delete(*self.konta_specjalne_treeview.get_children())
        with open('sage_konta_specjalne.json', encoding='utf-8') as json_file:
            data = json.load(json_file)

        n = 0
        for k in data:
            lp = n + 1
            konto = k
            tytul = data[k]['tytul']
            konto_wn = data[k]['konto_wn']
            konto_ma = data[k]['konto_ma']
            foreground = 'white'

            # tagi kolorujace treeview
            if n % 2 == 0:
                background = 'background_dark'
            else:
                background = 'background_light'

            self.konta_specjalne_treeview.tag_configure('background_dark', background='#383232')
            self.konta_specjalne_treeview.tag_configure('background_light', background='#262424')
            self.konta_specjalne_treeview.insert('', 'end', values=(lp, tytul, konto, konto_wn, konto_ma),
                                                 tags=(background))
            n += 1

    def create_konta_specjalne_remotes(self):
        konto_lb = tk.Label(self.konta_specjalne_tpl, text='KONTO', bg='#383232', fg='#80e89b', anchor='w')
        konto_lb.place(relx=0.72, rely=0.01, relwidth=0.27, relheight=0.04)
        tytul_lb = tk.Label(self.konta_specjalne_tpl, text='TYTUŁ', bg='#383232', fg='#80e89b', anchor='w')
        tytul_lb.place(relx=0.72, rely=0.11, relwidth=0.27, relheight=0.04)
        konto_wn = tk.Label(self.konta_specjalne_tpl, text='KONTO_WN', bg='#383232', fg='#80e89b', anchor='w')
        konto_wn.place(relx=0.72, rely=0.32, relwidth=0.27, relheight=0.04)
        konto_ma = tk.Label(self.konta_specjalne_tpl, text='KONTO_MA', bg='#383232', fg='#80e89b', anchor='w')
        konto_ma.place(relx=0.72, rely=0.42, relwidth=0.27, relheight=0.04)
        self.konto_spec_entry = tk.Entry(self.konta_specjalne_tpl, justify='center', bg='#6b685f', fg='white')
        self.konto_spec_entry.place(relx=0.72, rely=0.06, relwidth=0.27, relheight=0.04)
        self.tytul_konto_spec_text = tk.Text(self.konta_specjalne_tpl, bg='#6b685f', fg='white', wrap='word')
        self.tytul_konto_spec_text.place(relx=0.72, rely=0.16, relwidth=0.27, relheight=0.15)
        self.konto_spec_wn_entry = tk.Entry(self.konta_specjalne_tpl, justify='center', bg='#6b685f', fg='white')
        self.konto_spec_wn_entry.place(relx=0.72, rely=0.37, relwidth=0.27, relheight=0.04)
        self.konto_spec_ma_entry = tk.Entry(self.konta_specjalne_tpl, justify='center', bg='#6b685f', fg='white')
        self.konto_spec_ma_entry.place(relx=0.72, rely=0.47, relwidth=0.27, relheight=0.04)

    def wyczysc_konta_tpl_remotes(self):
        self.konto_spec_entry.delete(0, 'end')
        self.tytul_konto_spec_text.delete('1.0', tk.END)
        self.konto_spec_wn_entry.delete(0, 'end')
        self.konto_spec_ma_entry.delete(0, 'end')

    def get_dane_to_update_konta_spec(self, event):
        item = self.konta_specjalne_treeview.selection()
        konto = self.konta_specjalne_treeview.item(item, 'values')[2]
        tytul = self.konta_specjalne_treeview.item(item, 'values')[1]
        konto_wn = self.konta_specjalne_treeview.item(item, 'values')[3]
        konto_ma = self.konta_specjalne_treeview.item(item, 'values')[4]

        self.wyczysc_konta_tpl_remotes()

        self.konto_spec_entry.insert(0, konto)
        self.tytul_konto_spec_text.insert('1.0', tytul)
        self.konto_spec_wn_entry.insert(0, konto_wn)
        self.konto_spec_ma_entry.insert(0, konto_ma)

    def dodaj_popraw_zapis_konto_spec(self):
        konto_spec = self.konto_spec_entry.get()
        tytul_spec = self.tytul_konto_spec_text.get("1.0", tk.END)
        konto_spec_wn = self.konto_spec_wn_entry.get()
        konto_spec_ma = self.konto_spec_ma_entry.get()

        if konto_spec != '':

            with open('sage_konta_specjalne.json', encoding='utf-8') as json_file:
                data = json.load(json_file)

            if konto_spec not in data:
                data[konto_spec] = {}

            data[konto_spec]['tytul'] = tytul_spec.strip('\n')
            data[konto_spec]['konto_wn'] = konto_spec_wn
            data[konto_spec]['konto_ma'] = konto_spec_ma

            with open('sage_konta_specjalne.json', 'w', encoding='utf-8') as outfile:
                json.dump(data, outfile)

            self.wyczysc_konta_tpl_remotes()
            self.update_konta_specjalne_treeview()

    def usun_zapis_konto_spec(self):
        konto_spec = self.konto_spec_entry.get()
        with open('sage_konta_specjalne.json', encoding='utf-8') as json_file:
            data = json.load(json_file)

        data.pop(f'{konto_spec}', None)

        with open('sage_konta_specjalne.json', 'w', encoding='utf-8') as outfile:
            json.dump(data, outfile)

        self.wyczysc_konta_tpl_remotes()
        self.update_konta_specjalne_treeview()

    def create_kontrahenci_toplevel(self):
        self.kontrahenci_tpl = tk.Toplevel(self.wyciagi_LF, background='#383232',
                                           highlightthickness=2)
        self.kontrahenci_tpl.grab_set()
        self.kontrahenci_tpl.title('KONTRAHENCI')
        self.kontrahenci_tpl.geometry(f'1200x600+200+100')

        self.szukany_nip_ = StringVar()
        self.szukany_nip_.trace('w', lambda name, index, mode: self.update_kontrahenci_treeview())
        self.wyszukaj_nip_entry = tk.Entry(self.kontrahenci_tpl, justify='center', bg='#6b685f', fg='white',
                                           textvariable=self.szukany_nip_)
        self.wyszukaj_nip_entry.place(relx=0.01, rely=0.01, relwidth=0.7, relheight=0.04)

        self.create_kontrahenci_treeview()
        self.update_kontrahenci_treeview()
        self.create_kontrahenci_remotes()

        dodaj_popraw_button = tk.Button(self.kontrahenci_tpl, text='DODAJ / POPRAW',
                                        bg='#544949', command=self.dodaj_popraw_zapis_kontrahenci,
                                        fg=f'{self.kolor_razem}')
        dodaj_popraw_button.place(relx=0.72, rely=0.95, relwidth=0.27, relheight=0.04)

        usun_button = tk.Button(self.kontrahenci_tpl, text='USUŃ',
                                bg='#544949', command=self.usun_zapis_kontrahenci,
                                fg=f'{self.kolor_razem}')
        usun_button.place(relx=0.72, rely=0.9, relwidth=0.27, relheight=0.04)

        import_button = tk.Button(self.kontrahenci_tpl, text='IMPORT',
                                  bg='#544949', command=self.importuj_nowych_kontrahentow,
                                  fg=f'{self.kolor_razem}')
        import_button.place(relx=0.72, rely=0.85, relwidth=0.27, relheight=0.04)

    def create_kontrahenci_treeview(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', fieldbackground="#383232", background="#383232", foreground='white')
        style.configure("Treeview.Heading", background="#383232", foreground="white")
        style.map('Treeview.Heading', background=[('disabled', '#383232')])

        def fixed_map(option):  # naprawa buga wersji dla Python 3.7 przy wyświetlaniu koloru linii w treeview
            return [elm for elm in style.map("Treeview", query_opt=option)
                    if elm[:2] != ("!disabled", "!selected")]

        style.map("Treeview", foreground=fixed_map("foreground"),
                  background=fixed_map("background"))

        self.kontrahenci_treeview_frame = tk.Frame(self.kontrahenci_tpl)
        self.kontrahenci_treeview_frame.configure(bg='#383232', relief='groove', bd=1)
        self.kontrahenci_treeview_frame.place(relx=0.01, rely=0.06, relwidth=0.7, relheight=0.93)

        self.kontrahenci_columns = ['LP', 'NAZWA', 'NIP', 'ID_SAGE']
        self.kontrahenci_treeview = ttk.Treeview(self.kontrahenci_treeview_frame,
                                                 columns=self.kontrahenci_columns,
                                                 show='headings',
                                                 style="Treeview", selectmode="browse")

        self.kontrahenci_treeview.heading('LP', text='LP')
        self.kontrahenci_treeview.column('LP', width=40, stretch='no', anchor='center')
        self.kontrahenci_treeview.heading(f'{self.kontrahenci_columns[1]}',
                                          text=f'{self.kontrahenci_columns[1]}')
        self.kontrahenci_treeview.column(f'{self.kontrahenci_columns[1]}', minwidth=250, stretch='yes',
                                         anchor='center')
        self.kontrahenci_treeview.heading(f'{self.kontrahenci_columns[2]}',
                                          text=f'{self.kontrahenci_columns[2]}')
        self.kontrahenci_treeview.column(f'{self.kontrahenci_columns[2]}', width=200, stretch='no',
                                         anchor='center')
        self.kontrahenci_treeview.heading(f'{self.kontrahenci_columns[3]}',
                                          text=f'{self.kontrahenci_columns[3]}')
        self.kontrahenci_treeview.column(f'{self.kontrahenci_columns[3]}', width=100, stretch='no',
                                         anchor='center')

        self.scrolly = ttk.Scrollbar(self.kontrahenci_treeview_frame, orient='vertical',
                                     command=self.kontrahenci_treeview.yview)
        self.kontrahenci_treeview.configure(yscrollcommand=self.scrolly.set)
        map(lambda col: col.configure(yscrollcommand=self.scrolly.set), self.kontrahenci_columns)
        self.scrolly.pack(side=tk.RIGHT, fill=tk.Y)
        map(lambda col: col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True), self.kontrahenci_columns)
        self.kontrahenci_treeview.pack(expand='yes', fill='both')
        self.kontrahenci_treeview.bind('<Double-1>', self.get_dane_to_update_kontrahenci)

    def get_dane_to_update_kontrahenci(self, event):
        item = self.kontrahenci_treeview.selection()
        nip = self.kontrahenci_treeview.item(item, 'values')[2]
        nazwa = self.kontrahenci_treeview.item(item, 'values')[1]
        id_sage = self.kontrahenci_treeview.item(item, 'values')[3]

        self.wyczysc_kontrahenci_tpl_remotes()

        self.nip_kontrahenci_entry.insert(0, nip)
        self.nazwa_kontrahenci_text.insert('1.0', nazwa)
        self.id_sage_kontrahenci_entry.insert(0, id_sage)

    def dodaj_popraw_zapis_kontrahenci(self):
        nip = self.nip_kontrahenci_entry.get()
        nazwa = self.nazwa_kontrahenci_text.get("1.0", tk.END)
        id_sage = self.id_sage_kontrahenci_entry.get()

        if nip != '':

            with open('sage_kontrahenci.json', encoding='utf-8') as json_file:
                data = json.load(json_file)

            if nip not in data:
                data[nip] = {}

            data[nip]['nazwa'] = nazwa.strip('\n')
            data[nip]['id_kontrahenta'] = id_sage

            with open('sage_kontrahenci.json', 'w', encoding='utf-8') as outfile:
                json.dump(data, outfile)

            self.wyczysc_kontrahenci_tpl_remotes()
            self.update_kontrahenci_treeview()

    def usun_zapis_kontrahenci(self):
        nip = self.nip_kontrahenci_entry.get()
        with open('sage_kontrahenci.json', encoding='utf-8') as json_file:
            data = json.load(json_file)

        data.pop(f'{nip}', None)

        with open('sage_kontrahenci.json', 'w', encoding='utf-8') as outfile:
            json.dump(data, outfile)

        self.wyczysc_kontrahenci_tpl_remotes()
        self.update_kontrahenci_treeview()

    def update_kontrahenci_treeview(self):
        self.kontrahenci_treeview.delete(*self.kontrahenci_treeview.get_children())
        with open('sage_kontrahenci.json', encoding='utf-8') as json_file:
            data = json.load(json_file)

        n = 0
        for k in data:
            if len(self.szukany_nip_.get()) >= 3 and self.szukany_nip_.get().lower() not in data[k]['nazwa'].lower() \
                    and self.szukany_nip_.get() not in k:
                continue

            lp = n + 1
            nip = k
            nazwa = data[k]['nazwa']
            id_sage = data[k]['id_kontrahenta']

            # tagi kolorujace treeview
            if n % 2 == 0:
                background = 'background_dark'
            else:
                background = 'background_light'

            self.kontrahenci_treeview.tag_configure('background_dark', background='#383232')
            self.kontrahenci_treeview.tag_configure('background_light', background='#262424')
            self.kontrahenci_treeview.insert('', 'end', values=(lp, nazwa, nip, id_sage), tags=(background))
            n += 1

    def importuj_nowych_kontrahentow(self):
        tk_clipboard = self.controller
        data_sage = tk_clipboard.clipboard_get().split('\n')
        with open('sage_kontrahenci.json', encoding='utf-8') as json_file:
            data = json.load(json_file)

            for d in data_sage:
                if d != '':
                    id_sage = d.split('\t')[1]
                    nazwa = d.split('\t')[3]
                    nip = d.split('\t')[4]
                    if nip != '':
                        if nip not in data:
                            data[nip] = {}

                        data[nip]['nazwa'] = nazwa.strip('\n')
                        data[nip]['id_kontrahenta'] = id_sage

        with open('sage_kontrahenci.json', 'w', encoding='utf-8') as outfile:
            json.dump(data, outfile)

        self.wyczysc_kontrahenci_tpl_remotes()
        self.update_kontrahenci_treeview()

    def create_kontrahenci_remotes(self):
        nip_lb = tk.Label(self.kontrahenci_tpl, text='NIP', bg='#383232', fg='#80e89b', anchor='w')
        nip_lb.place(relx=0.72, rely=0.01, relwidth=0.27, relheight=0.04)
        nazwa_lb = tk.Label(self.kontrahenci_tpl, text='NAZWA', bg='#383232', fg='#80e89b', anchor='w')
        nazwa_lb.place(relx=0.72, rely=0.11, relwidth=0.27, relheight=0.04)
        id_sage_lb = tk.Label(self.kontrahenci_tpl, text='ID SAGE', bg='#383232', fg='#80e89b', anchor='w')
        id_sage_lb.place(relx=0.72, rely=0.32, relwidth=0.27, relheight=0.04)
        self.nip_kontrahenci_entry = tk.Entry(self.kontrahenci_tpl, justify='center', bg='#6b685f', fg='white')
        self.nip_kontrahenci_entry.place(relx=0.72, rely=0.06, relwidth=0.27, relheight=0.04)
        self.nazwa_kontrahenci_text = tk.Text(self.kontrahenci_tpl, bg='#6b685f', fg='white', wrap='word')
        self.nazwa_kontrahenci_text.place(relx=0.72, rely=0.16, relwidth=0.27, relheight=0.15)
        self.id_sage_kontrahenci_entry = tk.Entry(self.kontrahenci_tpl, justify='center', bg='#6b685f', fg='white')
        self.id_sage_kontrahenci_entry.place(relx=0.72, rely=0.37, relwidth=0.27, relheight=0.04)

    def wyczysc_kontrahenci_tpl_remotes(self):
        self.nip_kontrahenci_entry.delete(0, 'end')
        self.nazwa_kontrahenci_text.delete('1.0', tk.END)
        self.id_sage_kontrahenci_entry.delete(0, 'end')

    def create_wyszukaj_przelew_remotes(self):
        self.szukany_tytul_ = StringVar()
        self.szukany_tytul_.trace('w',
                                  lambda name, index, mode: self.update_wyszukaj_przelew_treeview('tytul'))
        tytul_wyszukaj_lb = tk.Label(self.wyciagi_RF, text='TYTUŁ: ', bg='#383232', fg='#80e89b', anchor='w')
        tytul_wyszukaj_lb.place(relx=0.02, rely=0.02, relwidth=0.1, relheight=0.03)
        self.tytul_wyszukaj_entry = tk.Entry(self.wyciagi_RF, justify='center', bg='#6b685f', fg='white',
                                             textvariable=self.szukany_tytul_)
        self.tytul_wyszukaj_entry.place(relx=0.13, rely=0.02, relwidth=0.85, relheight=0.03)

        self.szukany_kontrahent_ = StringVar()
        self.szukany_kontrahent_.trace('w',
                                       lambda name, index, mode: self.update_wyszukaj_przelew_treeview('kontrahent'))
        kontrahent_wyszukaj_lb = tk.Label(self.wyciagi_RF, text='KONTRAHENT: ', bg='#383232', fg='#80e89b', anchor='w')
        kontrahent_wyszukaj_lb.place(relx=0.02, rely=0.06, relwidth=0.1, relheight=0.03)
        self.kontrahent_wyszukaj_entry = tk.Entry(self.wyciagi_RF, justify='center', bg='#6b685f', fg='white',
                                                  textvariable=self.szukany_kontrahent_)
        self.kontrahent_wyszukaj_entry.place(relx=0.13, rely=0.06, relwidth=0.85, relheight=0.03)

    def create_wyszukaj_przelew_treeview(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', fieldbackground="#383232", background="#383232", foreground='white')
        style.configure("Treeview.Heading", background="#383232", foreground="white")
        style.map('Treeview.Heading', background=[('disabled', '#383232')])

        def fixed_map(option):  # naprawa buga wersji dla Python 3.7 przy wyświetlaniu koloru linii w treeview
            return [elm for elm in style.map("Treeview", query_opt=option)
                    if elm[:2] != ("!disabled", "!selected")]

        style.map("Treeview", foreground=fixed_map("foreground"),
                  background=fixed_map("background"))

        self.wyszukaj_przelew_treeview_frame = tk.Frame(self.wyciagi_RF)
        self.wyszukaj_przelew_treeview_frame.configure(bg='#383232', relief='groove', bd=1)
        self.wyszukaj_przelew_treeview_frame.place(relx=0.01, rely=0.1, relwidth=0.98, relheight=0.5)

        self.wyszukaj_przelew_columns = ['WYCIĄG', 'DATA', 'KONTRAHENT', 'TYTUŁ', 'KWOTA']
        self.wyszukaj_przelew_treeview = ttk.Treeview(self.wyszukaj_przelew_treeview_frame,
                                                      columns=self.wyszukaj_przelew_columns,
                                                      show='headings',
                                                      style="Treeview", selectmode="browse")

        self.wyszukaj_przelew_treeview.heading(f'{self.wyszukaj_przelew_columns[0]}',
                                               text=f'{self.wyszukaj_przelew_columns[0]}')
        self.wyszukaj_przelew_treeview.column(f'{self.wyszukaj_przelew_columns[0]}', width=120, stretch='no',
                                              anchor='center')
        self.wyszukaj_przelew_treeview.heading(f'{self.wyszukaj_przelew_columns[1]}',
                                               text=f'{self.wyszukaj_przelew_columns[1]}')
        self.wyszukaj_przelew_treeview.column(f'{self.wyszukaj_przelew_columns[1]}', width=120, stretch='no',
                                              anchor='center')
        self.wyszukaj_przelew_treeview.heading(f'{self.wyszukaj_przelew_columns[2]}',
                                               text=f'{self.wyszukaj_przelew_columns[2]}')
        self.wyszukaj_przelew_treeview.column(f'{self.wyszukaj_przelew_columns[2]}', width=250, stretch='no',
                                              anchor='center')
        self.wyszukaj_przelew_treeview.heading(f'{self.wyszukaj_przelew_columns[3]}',
                                               text=f'{self.wyszukaj_przelew_columns[3]}')
        self.wyszukaj_przelew_treeview.column(f'{self.wyszukaj_przelew_columns[3]}', minwidth=200, stretch='yes',
                                              anchor='center')
        self.wyszukaj_przelew_treeview.heading(f'{self.wyszukaj_przelew_columns[4]}',
                                               text=f'{self.wyszukaj_przelew_columns[4]}')
        self.wyszukaj_przelew_treeview.column(f'{self.wyszukaj_przelew_columns[4]}', width=120, stretch='no',
                                              anchor='center')

        self.scrolly = ttk.Scrollbar(self.wyszukaj_przelew_treeview_frame, orient='vertical',
                                     command=self.wyszukaj_przelew_treeview.yview)
        self.wyszukaj_przelew_treeview.configure(yscrollcommand=self.scrolly.set)
        map(lambda col: col.configure(yscrollcommand=self.scrolly.set), self.wyszukaj_przelew_columns)
        self.scrolly.pack(side=tk.RIGHT, fill=tk.Y)
        map(lambda col: col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True), self.wyszukaj_przelew_columns)
        self.wyszukaj_przelew_treeview.pack(expand='yes', fill='both')

    @staticmethod
    def get_dane_wyciagi_json():
        with open('sage_wyciagi.json', encoding='utf-8') as json_file:
            data = json.load(json_file)
        return data

    def update_wyszukaj_przelew_treeview(self, rodzaj):
        self.wyszukaj_przelew_treeview.delete(*self.wyszukaj_przelew_treeview.get_children())
        if len(self.szukany_tytul_.get()) < 3 and len(self.szukany_kontrahent_.get()) < 3:
            return None

        dane_treeview = []
        for wyciag_key in self.dane_wyciagi_json:
            for trans_key in self.dane_wyciagi_json[wyciag_key]:
                if rodzaj == 'tytul':
                    if self.szukany_tytul_.get().upper() in self.dane_wyciagi_json[wyciag_key][trans_key][
                        'tytul'].upper():
                        dane_treeview.append([f'{wyciag_key}/{trans_key}',
                                              datetime.datetime.strptime(
                                                  self.dane_wyciagi_json[wyciag_key][trans_key]['data'],
                                                  "%Y-%m-%d").date(),
                                              self.dane_wyciagi_json[wyciag_key][trans_key]['kontrahent'],
                                              self.dane_wyciagi_json[wyciag_key][trans_key]['tytul'],
                                              self.dane_wyciagi_json[wyciag_key][trans_key]['kwota']])
                        dane_treeview.sort(key=lambda x: x[1], reverse=True)

                if rodzaj == 'kontrahent':
                    if self.szukany_kontrahent_.get().upper() in self.dane_wyciagi_json[wyciag_key][trans_key][
                        'kontrahent'].upper():
                        dane_treeview.append([f'{wyciag_key}/{trans_key}',
                                              datetime.datetime.strptime(
                                                  self.dane_wyciagi_json[wyciag_key][trans_key]['data'],
                                                  "%Y-%m-%d").date(),
                                              self.dane_wyciagi_json[wyciag_key][trans_key]['kontrahent'],
                                              self.dane_wyciagi_json[wyciag_key][trans_key]['tytul'],
                                              self.dane_wyciagi_json[wyciag_key][trans_key]['kwota']])
                        dane_treeview.sort(key=lambda x: x[1], reverse=True)

        # update treeview
        n = 1
        for k in dane_treeview:
            wyciag = k[0]
            data_trans = k[1]
            kontrahent_trans = k[2]
            tytul_trans = k[3]
            kwota_trans = k[4]

            # tagi kolorujace treeview
            if n % 2 == 0:
                background = 'background_dark'
            else:
                background = 'background_light'

            self.wyszukaj_przelew_treeview.tag_configure('background_dark', background='#383232')
            self.wyszukaj_przelew_treeview.tag_configure('background_light', background='#262424')
            self.wyszukaj_przelew_treeview.insert('', 'end', values=(wyciag, data_trans, kontrahent_trans,
                                                                     tytul_trans, kwota_trans), tags=(background))
            n += 1

class Rozne_frame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.configure(bg='#383232')
        self.zpt_database = ZPT_Database.ZPT_base()
        self.kamsoft_database = Kamsoft_Database.DataBaseKamsoft()
        self.kolor_razem = '#b58b14'
        self.kolor_font = 'white'
        self.kolor_font_razem = 'black'
        self.kolor_legenda = '#383232'
        self.create_rozne_RF()
        self.create_wyszukiwanie_fv_frame()
        self.create_aplikacje_serwera_frame()
        self.create_archiwum_frame()
        self.create_archiwum_sage_frame()
        self.create_katry_platnicze_frame()
        self.create_rekalmowki_frame()
        self.create_dyzury_frame()
        self.create_faktury_fvs_frame()
        self.create_kamsoft_to_sage_frame()

    def create_rozne_RF(self):
        self.rozne_RF = tk.Frame(self)
        self.rozne_RF.configure(bg='#383232', relief='groove', bd=1)
        self.rozne_RF.place(relx=0.51, rely=0.02, relwidth=0.48, relheight=0.96)
        self.create_info_textbox()

    def create_info_textbox(self):
        self.info_textbox = scrolledtext.ScrolledText(self.rozne_RF, state='normal', height=12, foreground='white',
                                                      wrap='word')
        self.info_textbox.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.info_textbox.configure(font='TkFixedFont', bg='#383232', foreground='#17bd43')

    @staticmethod
    def start_new_thread(target):
        threading.Thread(target=target).start()

    # wyszukiwanie faktur
    def create_wyszukiwanie_fv_frame(self):
        self.wyszukiwanie_fv_frame = tk.LabelFrame(self)
        self.wyszukiwanie_fv_frame.configure(bg='#383232', relief='groove', bd=1,
                                             text='   FAKTURY - APTEKI   ', fg='#3b8eed')
        self.wyszukiwanie_fv_frame.place(relx=0.01, rely=0.02, relwidth=0.48, relheight=0.07)
        self.wyszukiwanie_fv_lb = tk.Label(self.wyszukiwanie_fv_frame, text='WYSZUKAJ FV: ',
                                           bg='#383232', fg='#80e89b', anchor='w')
        self.wyszukiwanie_fv_lb.place(relx=0.02, rely=0.2, relwidth=0.15, relheight=0.6)
        self.wyszukiwanie_fv_Entry = tk.Entry(self.wyszukiwanie_fv_frame, justify='center', bg='#6b685f', fg='white')
        self.wyszukiwanie_fv_Entry.place(relx=0.17, rely=0.2, relwidth=0.5, relheight=0.6)
        self.wyszukiwanie_fv_button = tk.Button(self.wyszukiwanie_fv_frame, text='ZNAJDŹ', command=
        lambda: self.start_new_thread(self.wyszukaj_fv), bg='#544949', fg=f'{self.kolor_razem}')
        self.wyszukiwanie_fv_button.place(relx=0.7, rely=0.2, relwidth=0.28, relheight=0.6)
        self.wyszukiwanie_fv_Entry.bind('<Return>', lambda event: self.start_new_thread(self.wyszukaj_fv))

    def wyszukaj_fv(self):
        self.info_textbox.delete('1.0', 'end')
        szukana_fv = self.wyszukiwanie_fv_Entry.get()
        znaleziono = 0

        if len(szukana_fv) < 6:
            messagebox.showerror('BŁĄD', 'Szukana fraza musi mieć co najmniej 6 znaków')
            return 0
        else:
            self.info_textbox.insert(tk.END, f'Szukana fv: {szukana_fv}\n\n')
            for n in range(2, 9):
                query = f'SELECT dat_zak_fv, dostawca, nrfv FROM zakupy_0{n} WHERE nrfv LIKE "{szukana_fv}%"'
                wynik = self.zpt_database.mysql_querry(query)
                if wynik != []:
                    znaleziono = 1
                    for faktura in wynik:
                        nazwa_apteki = slowniki.apteki_id_nazwa[f'{n}']
                        self.info_textbox.insert(tk.END, f'{nazwa_apteki} - {n}\n')
                        id_dostawcy = faktura[1]
                        data_przyjecia = faktura[0]
                        nr_faktury = faktura[2]
                        query_nazwa_dostwcy = f'SELECT nazwa FROM dostawcy WHERE id_0{n} = {id_dostawcy}'
                        nazwa_dostwcy = self.zpt_database.mysql_querry(query_nazwa_dostwcy)[0][0]
                        self.info_textbox.insert(tk.END, f'Faktura numer: {nr_faktury}\n')
                        self.info_textbox.insert(tk.END, f'Dostawca: {nazwa_dostwcy}\n')
                        self.info_textbox.insert(tk.END, f'Data przyjęcia: {data_przyjecia[:10]}\n\n\n')
                        self.info_textbox.yview(tk.END)
                else:
                    continue

        if znaleziono == 0:
            self.info_textbox.insert(tk.END, f'Nie znaleziono faktury: {szukana_fv}\n')
        else:
            return 0

    # progremy z serwera aptecznego na Hallera
    def create_aplikacje_serwera_frame(self):
        self.aplikacje_serwera_frame = tk.LabelFrame(self)
        self.aplikacje_serwera_frame.configure(bg='#383232', relief='groove', bd=1,
                                               text='   APLIKACJE SERWERA APTECZNEGO - ZPT   ', fg='#3b8eed')
        self.aplikacje_serwera_frame.place(relx=0.01, rely=0.1, relwidth=0.48, relheight=0.07)

        self.grupy_zakupowe_button = tk.Button(self.aplikacje_serwera_frame, text='GRUPY ZAKUPOWE', command=
        lambda: self.start_new_thread(self.grupy_zakupowe), bg='#544949', fg=f'{self.kolor_razem}')
        self.grupy_zakupowe_button.place(relx=0.01, rely=0.2, relwidth=(0.96 / 3), relheight=0.6)

        self.grupy_zakupowe_sprzedaz_fwd_button = tk.Button(self.aplikacje_serwera_frame,
                                                            text='GRUPY ZAKUPOWE SPRZ. FWD', command=
                                                            lambda: self.start_new_thread(self.grupy_zakupowe_sprz_fwd),
                                                            bg='#544949', fg=f'{self.kolor_razem}')
        self.grupy_zakupowe_sprzedaz_fwd_button.place(relx=0.02 + (0.96 / 3), rely=0.2, relwidth=(0.96 / 3),
                                                      relheight=0.6)

        self.krotkie_daty_button = tk.Button(self.aplikacje_serwera_frame, text='KRÓTKIE DATY', command=
        lambda: self.start_new_thread(self.krotkie_daty), bg='#544949', fg=f'{self.kolor_razem}')
        self.krotkie_daty_button.place(relx=0.03 + (0.96 / 3) * 2, rely=0.2, relwidth=(0.96 / 3), relheight=0.6)

    def grupy_zakupowe(self):
        self.info_textbox.delete('1.0', 'end')

        grupy_zakupowe_id_querry = "SELECT id_grupy FROM grupy_zakupowe_id"
        grupy_zakupowe_id = self.zpt_database.mysql_querry(grupy_zakupowe_id_querry)
        self.info_textbox.insert(tk.END, f'Pobrano dane id grup z tablicy grupy_zakupowe_id\n')

        self.zpt_database.mysql_no_fetch_querry("DROP TABLE IF EXISTS grupy_towarowe")
        self.info_textbox.insert(tk.END, f'Usunięto starą tablicę grupy_towarowe\n')
        self.zpt_database.mysql_no_fetch_querry(f"CREATE TABLE `grupy_towarowe` (`ID_grupy` INT,"
                                                f"`nazwa_grupy` TEXT, "
                                                f"`bloz` TEXT, "
                                                f"`nazwa` TEXT "
                                                f") ENGINE = MyISAM CHARSET= utf8 COLLATE utf8_polish_ci;")
        self.info_textbox.insert(tk.END, f'Stworzono czystą tablicę grupy_towarowe\n')

        for row_grupy in grupy_zakupowe_id:
            id_grupy = row_grupy[0]
            dane_querry = f"SELECT r.id, r.nazwa, t.bloz07, t.nazwa from grpn r, grpp n, towr t " \
                          f"WHERE t.bloz07<>'0000000' AND n.idtowr=t.id AND n.idtowr<>0 AND r.id=n.idgrpn " \
                          f"AND n.idfirm=r.idfirm AND r.id={id_grupy}"
            dane = self.kamsoft_database.mysql_querry(dane_querry)
            if dane == []:
                continue
            else:
                self.zpt_database.mysql_executemany_querry("INSERT INTO grupy_towarowe VALUES(%s, %s, %s, %s)", dane)

            self.info_textbox.insert(tk.END, f'Zaktualizowano grupę: {dane[0][1]}\n')
            self.info_textbox.yview(tk.END)

        self.zpt_database.mysql_no_fetch_querry(f"UPDATE `aktualizacja` SET `apteka`='99',"
                                                f"`data`='{datetime.datetime.now()}' WHERE apteka = 99 ")
        self.info_textbox.insert(tk.END, f'Zapisano datę/godzinę aktualizacji grup zakupowych\nKONIEC :)')
        self.info_textbox.yview(tk.END)

    def grupy_zakupowe_sprz_fwd(self):
        self.info_textbox.delete('1.0', 'end')

        bloz_lista_query = f'SELECT DISTINCT bloz FROM grupy_towarowe'
        bloz_lista = self.zpt_database.mysql_querry(bloz_lista_query)
        self.info_textbox.insert(tk.END, f'Pobrano listę bloz do aktualizacji\n')

        lista_bloz_sprzedaz = []
        for b in bloz_lista:
            lista_bloz_sprzedaz.append((b[0], 0))

        dict_bloz_sprzedaz = dict(lista_bloz_sprzedaz)

        for n in range(2, 9):
            if n == 3:
                continue
            suma_sprzedazy_3_mce_query = f'SELECT DISTINCT bloz, SUM(ilosp) FROM sprzedaz_0{n} WHERE datsp BETWEEN ' \
                                         f'DATE_SUB(NOW(),INTERVAL 1 YEAR)' \
                                         f' AND DATE_SUB(NOW(),INTERVAL 9 MONTH) ' \
                                         f'AND bloz <> " " AND bloz <> "0000000" ' \
                                         f' GROUP BY bloz'
            suma_sprzedazy_3_mce = self.zpt_database.mysql_querry(suma_sprzedazy_3_mce_query)

            for d in suma_sprzedazy_3_mce:

                if d[0] in dict_bloz_sprzedaz.keys():
                    dict_bloz_sprzedaz[d[0]] += round(d[1], 2)

            self.info_textbox.insert(tk.END, f'Zaktualizowano dane dla {slowniki.apteki_id_nazwa[f"{n}"]}\n')

        lista_bloz_sprzedaz_upload = list(dict_bloz_sprzedaz.items())

        self.zpt_database.mysql_no_fetch_querry("DROP TABLE IF EXISTS grupy_towarowe_sprzedaz_fwd")
        self.info_textbox.insert(tk.END, f'Usunięto starą tablicę danych\n')
        self.zpt_database.mysql_no_fetch_querry(f"CREATE TABLE `grupy_towarowe_sprzedaz_fwd`"
                                                f"(`BLOZ` TEXT, `sprzedaz` FLOAT "
                                                f") ENGINE = MyISAM CHARSET= utf8 COLLATE utf8_polish_ci;")
        self.info_textbox.insert(tk.END, f'Stworzono nową tablicę danych\n')

        upload_query = f"INSERT INTO grupy_towarowe_sprzedaz_fwd VALUES(%s, %s)"
        self.zpt_database.mysql_executemany_querry(upload_query, lista_bloz_sprzedaz_upload)
        self.info_textbox.insert(tk.END, f'Dane zostały zapisane w bazie\n')
        self.info_textbox.insert(tk.END, f'KONIEC :)\n')

    def set_dates_for_krotkie_daty(self):
        # 3 miesiace wstecz
        now = datetime.datetime.now()
        if now.day > 28:
            self.czas_sprzedaz = now.replace(day=28)
        else:
            self.czas_sprzedaz = now

        miesiac_sprzedaz = now.month - 3

        if miesiac_sprzedaz <= 0:
            miesiac_sprzedaz += 12
            rok_sprzedaz = self.czas_sprzedaz.year - 1
        else:
            rok_sprzedaz = now.year

        self.czas_sprzedaz = now.replace(month=miesiac_sprzedaz)
        self.czas_sprzedaz = self.czas_sprzedaz.replace(year=rok_sprzedaz).date()
        self.czas_sprzedaz = str(self.czas_sprzedaz) + ' 00:00:00'

        # czas daty waznosci
        self.czas_mysql = now.replace(day=1)
        miesiac = self.czas_mysql.month + 6
        if miesiac > 12:
            miesiac -= 12
            self.czas_mysql = self.czas_mysql.replace(self.czas_mysql.year + 1)

        self.czas_mysql = self.czas_mysql.replace(month=miesiac).date()

    def krotkie_daty(self):
        self.info_textbox.delete('1.0', 'end')
        self.set_dates_for_krotkie_daty()

        lista_bloz = []
        for n in range(2, 9):
            bloz_query = f"SELECT bloz, dataw FROM rem_0{n} WHERE bloz <> '0000000' AND bloz <> 'None' " \
                         f"AND dataw BETWEEN '{datetime.datetime.now().date().replace(day=1)}' AND  " \
                         f"'{self.czas_mysql}' ORDER BY dataw"
            bloz = self.zpt_database.mysql_querry(bloz_query)

            self.info_textbox.insert(tk.END, f'Pobrano listę bloz dla: {slowniki.apteki_id_nazwa[f"{n}"]}\n')
            for b in bloz:
                if b[0] not in lista_bloz:
                    lista_bloz.append(b[0])

        dict_bloz_sprzedaz_stan = {}

        for b in lista_bloz:
            dict_bloz_sprzedaz_stan[b] = [[], []]

        for apteka in range(2, 9):
            # sprzedaz
            sprzedaz_query = f'SELECT DISTINCT bloz, sum(ilosp) FROM sprzedaz_0{apteka} WHERE ' \
                             f'datsp > "{self.czas_sprzedaz}" AND bloz <> "0000000" AND bloz <> " " GROUP BY bloz'
            sprzedaz = self.zpt_database.mysql_querry(sprzedaz_query)
            sprzedaz_dict = dict(sprzedaz)
            self.info_textbox.insert(tk.END, f'Pobrano listę sprzedaży dla: {slowniki.apteki_id_nazwa[f"{apteka}"]}\n')

            # stan
            stan_query = f'SELECT DISTINCT bloz, SUM(ilakt) FROM rem_0{apteka} ' \
                         f'WHERE bloz <> "0000000" AND BLOZ <> " " GROUP BY bloz'
            stan = self.zpt_database.mysql_querry(stan_query)
            stan_dict = dict(stan)
            self.info_textbox.insert(tk.END, f'Pobrano listę stanów dla: {slowniki.apteki_id_nazwa[f"{apteka}"]}\n')
            self.info_textbox.yview(tk.END)

            for key in dict_bloz_sprzedaz_stan:
                if key in sprzedaz_dict.keys():
                    dict_bloz_sprzedaz_stan[key][0].append(round(sprzedaz_dict[key], 2))
                else:
                    dict_bloz_sprzedaz_stan[key][0].append(0)

                if key in stan_dict.keys():
                    dict_bloz_sprzedaz_stan[key][1].append(round(stan_dict[key], 2))
                else:
                    dict_bloz_sprzedaz_stan[key][1].append(0)

        dane_upload = []

        for key in dict_bloz_sprzedaz_stan:
            lista_robocza = []
            lista_robocza.append(key)
            for n in dict_bloz_sprzedaz_stan[key][0]:
                lista_robocza.append(n)
            for n in dict_bloz_sprzedaz_stan[key][1]:
                lista_robocza.append(n)
            dane_upload.append(tuple(lista_robocza))
        self.info_textbox.insert(tk.END, f'Stworzono listę danych do eksportu.\n')
        self.destry_create_krotkie_daty_table()
        self.info_textbox.insert(tk.END, f'Usunięto starą tablicę danych\n')
        self.info_textbox.insert(tk.END, f'Stworzono nową tablicę danych\n')

        upload_query = f'INSERT INTO krotkie_daty_sprzedaz VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, ' \
                       f'%s, %s, %s, %s, %s)'
        self.zpt_database.mysql_executemany_querry(upload_query, dane_upload)
        self.info_textbox.insert(tk.END, f'Zapisano dane do bazy\n')

        # zapis do tabeli aktualizacja
        self.zpt_database.mysql_no_fetch_querry(
            f"UPDATE `aktualizacja` SET `data`='{datetime.datetime.now()}' WHERE apteka = 98 ")
        self.info_textbox.insert(tk.END, f'Zapisano czas aktualizacji bazy\n')
        self.info_textbox.insert(tk.END, f'KONIEC :)\n')
        self.info_textbox.yview(tk.END)

    def destry_create_krotkie_daty_table(self):
        self.zpt_database.mysql_no_fetch_querry("DROP TABLE IF EXISTS krotkie_daty_sprzedaz")
        self.zpt_database.mysql_no_fetch_querry(f"CREATE TABLE `krotkie_daty_sprzedaz` (`BLOZ` INT,`s02` TEXT,"
                                                f"`s03` TEXT,`s04` TEXT,`s05` TEXT,`s06` TEXT,`s07` TEXT,`s08` TEXT,"
                                                f"`st02` TEXT,`st03` TEXT,`st04` TEXT,`st05` TEXT,`st06` TEXT,"
                                                f"`st07` TEXT,`st08` TEXT,PRIMARY KEY (`BLOZ`)) "
                                                f"ENGINE = MyISAM CHARSET= utf8 COLLATE utf8_polish_ci;")

    # archiwum baz danych + archiwizacja programów python (tylko pliki *.py)
    def create_archiwum_frame(self):
        self.archiwum_frame = tk.LabelFrame(self)
        self.archiwum_frame.configure(bg='#383232', relief='groove', bd=1,
                                      text='   ARCHIWA BAZY DANYCH / PYTHON   ', fg='#3b8eed')
        self.archiwum_frame.place(relx=0.01, rely=0.18, relwidth=0.48, relheight=0.07)

        self.archiwum_bazy_danych_button = tk.Button(self.archiwum_frame, text='SPRAWDŹ ARCHIWA', command=
        lambda: self.start_new_thread(self.sprawdz_archiwum_bazy_danych), bg='#544949', fg=f'{self.kolor_razem}')
        self.archiwum_bazy_danych_button.place(relx=0.01, rely=0.2, relwidth=(0.95 / 4), relheight=0.6)

        self.foldery_button = tk.Button(self.archiwum_frame, text='FOLDERY', command=
        lambda: self.start_new_thread(self.create_foldery_toplevel),
                                        bg='#544949', fg=f'{self.kolor_razem}')
        self.foldery_button.place(relx=0.02 + (0.95 / 4), rely=0.2, relwidth=(0.95 / 4), relheight=0.6)

        self.lista_plikow_button = tk.Button(self.archiwum_frame, text='POKAŻ PLIKI', command=
        lambda: self.start_new_thread(self.pokaz_pliki_py), bg='#544949', fg=f'{self.kolor_razem}')
        self.lista_plikow_button.place(relx=0.03 + (0.95 / 4) * 2, rely=0.2, relwidth=(0.95 / 4), relheight=0.6)

        self.archiwizuj_button = tk.Button(self.archiwum_frame, text='ARCHIWIZUJ', command=
        lambda: self.start_new_thread(self.spakuj_pliki), bg='#544949', fg=f'{self.kolor_razem}')
        self.archiwizuj_button.place(relx=0.04 + (0.95 / 4) * 3, rely=0.2, relwidth=(0.95 / 4), relheight=0.6)

    def sprawdz_archiwum_bazy_danych(self):
        self.info_textbox.delete('1.0', 'end')
        ftp = ftplib.FTP_TLS('ftp.maria-pharm.pl', self.zpt_database.parametry_zpt['ftp_username'],
                             self.zpt_database.parametry_zpt['ftp_password'])  # połaczenie z serwerm
        self.info_textbox.insert(tk.END, f'Połączono z serwerem FTP.\n\n')
        foldery = ['02', '04', '05', '06', '07', '08', 'SAGE', 'PYTHON']
        for n in foldery:
            files_list = []
            if n == '02':
                ftp.cwd(f'{n}')
            else:
                ftp.cwd('..')
                ftp.cwd(f'{n}')

            files = ftp.mlsd()
            for f in files:
                if f[0] != '.' and f[0] != '..':
                    files_list.append((f[0], f[1]['modify'], f[1]['size']))

            files_list.sort(key=lambda tup: tup[1])
            if n.startswith('0'):
                self.info_textbox.insert(tk.END, f'{slowniki.apteki_id_nazwa[f"{n[-1]}"]}: \n'
                                                 f'\tPLIK: {files_list[-1][0]} - {self.set_date_format_for_ftp_file(files_list[-1][1])}\n'
                                                 f'\tPLIK: {files_list[-2][0]} - {self.set_date_format_for_ftp_file(files_list[-2][1])}\n\n')
                self.info_textbox.yview(tk.END)

            else:
                self.info_textbox.insert(tk.END, f'{n}: \n'
                                                 f'\tPLIK: {files_list[-1][0]} - '
                                                 f'{self.set_date_format_for_ftp_file(files_list[-1][1])} - {files_list[-1][2]}\n\n')
                self.info_textbox.yview(tk.END)

    @staticmethod
    def set_date_format_for_ftp_file(date):
        formated_date = f'{date[:4]}-{date[4:6]}-{date[6:8]}'
        return formated_date

    def create_foldery_toplevel(self):
        self.rozne_foldery_archiwizacja_toplevel = tk.Toplevel(self, background='#383232', highlightthickness=2)
        self.rozne_foldery_archiwizacja_toplevel.geometry(f'700x500+200+100')

        self.create_dodaj_folder_treeview()
        self.dodaj_folder_button = tk.Button(self.rozne_foldery_archiwizacja_toplevel, text='DODAJ FOLDER',
                                             command=self.dodaj_folder_do_danych, bg='#544949',
                                             fg=f'{self.kolor_razem}')
        self.dodaj_folder_button.place(relx=0.01, rely=0.94, relwidth=0.98, relheight=0.05)

        self.update_folder_treeview()

    def create_dodaj_folder_treeview(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', fieldbackground="#383232", background="#383232", foreground='white')
        style.configure("Treeview.Heading", background="#383232", foreground="white")
        style.map('Treeview.Heading', background=[('disabled', '#383232')])

        def fixed_map(option):  # naprawa buga wersji dla Python 3.7 przy wyświetlaniu koloru linii w treeview
            return [elm for elm in style.map("Treeview", query_opt=option)
                    if elm[:2] != ("!disabled", "!selected")]

        style.map("Treeview", foreground=fixed_map("foreground"),
                  background=fixed_map("background"))

        self.rozne_foldery_arch_treeview_frame = tk.Frame(self.rozne_foldery_archiwizacja_toplevel)
        self.rozne_foldery_arch_treeview_frame.configure(bg='#383232', relief='groove', bd=1)
        self.rozne_foldery_arch_treeview_frame.place(relx=0.01, rely=0.01, relwidth=0.98, relheight=0.92)

        self.columns_foldery_arch = ('LP', 'FOLDER')
        self.treeview_foldery_arch = ttk.Treeview(self.rozne_foldery_arch_treeview_frame,
                                                  columns=self.columns_foldery_arch, show='headings',
                                                  style="Treeview", selectmode="browse")

        self.treeview_foldery_arch.heading('LP', text='LP')
        self.treeview_foldery_arch.column('LP', minwidth=0, width=50, stretch='no', anchor='center')
        self.treeview_foldery_arch.heading('FOLDER', text='FOLDER')
        self.treeview_foldery_arch.column('FOLDER', minwidth=0, width=150, stretch='yes', anchor='center')

        self.scrolly = ttk.Scrollbar(self.treeview_foldery_arch, orient='vertical',
                                     command=self.treeview_foldery_arch.yview)
        self.treeview_foldery_arch.configure(yscrollcommand=self.scrolly.set)
        map(lambda col: col.configure(yscrollcommand=self.scrolly.set), self.columns_foldery_arch)
        self.scrolly.pack(side=tk.RIGHT, fill=tk.Y)
        map(lambda col: col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True), self.columns_foldery_arch)
        self.treeview_foldery_arch.pack(expand='yes', fill='both')

    def update_folder_treeview(self):

        with open('rozne.json', encoding='utf-8') as json_file:
            data = json.load(json_file)
        lista_folderow = data['foldery_arch']

        n = 1
        self.treeview_foldery_arch.delete(*self.treeview_foldery_arch.get_children())
        for d in lista_folderow:
            if n % 2 == 0:
                background = 'background_dark'
            else:
                background = 'background_light'

            self.treeview_foldery_arch.tag_configure('background_dark', background='#383232')
            self.treeview_foldery_arch.tag_configure('background_light', background='#262424')
            self.treeview_foldery_arch.insert('', 'end', values=(n, d), tags=background)
            n += 1

    def dodaj_folder_do_danych(self):
        folder = filedialog.askdirectory()
        with open('rozne.json', encoding='utf-8') as json_file:
            data = json.load(json_file)
        lista_folderow = data['foldery_arch']

        if folder not in lista_folderow:
            lista_folderow.append(folder)
        else:
            pass

        self.update_folder_treeview()
        data['foldery_arch'] = lista_folderow
        with open('rozne.json', 'w', encoding='utf-8') as outfile:
            json.dump(data, outfile)
        self.rozne_foldery_archiwizacja_toplevel.lift()

    def pokaz_pliki_py(self):
        self.info_textbox.delete('1.0', 'end')
        with open('rozne.json', encoding='utf-8') as json_file:
            data = json.load(json_file)
        lista_folderow = data['foldery_arch']

        for folder in lista_folderow:
            self.info_textbox.insert(tk.END, f'{folder}\n')
            for file in os.listdir(f'{folder}'):
                if file.endswith(".py") or file.endswith('.json') or file.endswith('.html'):
                    self.info_textbox.insert(tk.END, f'\t{file}\n')
            self.info_textbox.insert(tk.END, f'\n')
            self.info_textbox.yview(tk.END)

    def spakuj_pliki(self):
        zipfile_to_upload = zipfile.ZipFile(f'Python_arch_{str(datetime.datetime.today().date()).replace("-", "")}.zip',
                                            'w')
        self.info_textbox.delete('1.0', 'end')
        with open('rozne.json', encoding='utf-8') as json_file:
            data = json.load(json_file)
        lista_folderow = data['foldery_arch']

        for folder in lista_folderow:
            for file in os.listdir(f'{folder}'):
                if file.endswith(".py") or file.endswith('.json') or file.endswith('.html'):
                    zipfile_to_upload.write(os.path.join(folder, file))
                    self.info_textbox.insert(tk.END, f'SPAKOWANO PLIK: {os.path.join(folder, file)}\n')
                    self.info_textbox.yview(tk.END)

        zipfile_to_upload.close()
        ftp = ftplib.FTP_TLS('ftp.maria-pharm.pl', self.zpt_database.parametry_zpt['ftp_username'],
                             self.zpt_database.parametry_zpt['ftp_password'])
        self.info_textbox.insert(tk.END, f'Połączono z serwerem FTP.\n')
        self.info_textbox.yview(tk.END)
        ftp.cwd(f'PYTHON')

        with open(f'Python_arch_{str(datetime.datetime.today().date()).replace("-", "")}.zip', 'rb') as file_to_send:
            ftp.storbinary('STOR ' + f'Python_arch_{str(datetime.datetime.today().date()).replace("-", "")}.zip',
                           file_to_send)
        self.info_textbox.insert(tk.END, f'Pliki zarchiwizowane.\n')
        self.info_textbox.insert(tk.END, f'KONIEC :)')
        self.info_textbox.yview(tk.END)

        os.unlink(f'Python_arch_{str(datetime.datetime.today().date()).replace("-", "")}.zip')

    # archiwum SAGE
    def create_archiwum_sage_frame(self):
        self.archiwum_sage_frame = tk.LabelFrame(self)
        self.archiwum_sage_frame.configure(bg='#383232', relief='groove', bd=1,
                                           text='   ARCHIWUM SAGE   ', fg='#3b8eed')
        self.archiwum_sage_frame.place(relx=0.01, rely=0.26, relwidth=0.48, relheight=0.07)

        self.archiwum_sage_button = tk.Button(self.archiwum_sage_frame, text='ARCHIWIZACJA SAGE', command=
        lambda: self.start_new_thread(self.archiwizuj_sage), bg='#544949', fg=f'{self.kolor_razem}')
        self.archiwum_sage_button.place(relx=0.01, rely=0.2, relwidth=0.98, relheight=0.6)

    def archiwizuj_sage(self):
        self.info_textbox.delete('1.0', 'end')

        path = r'\\SERWERWIN\Importy\BACKUP'
        file_list = os.listdir(path)
        bufferSize = 64 * 1024
        ilosc_plikow_do_zachowania = 2
        ftp_username = self.zpt_database.parametry_zpt['ftp_username']
        ftp_password = self.zpt_database.parametry_zpt['ftp_password']

        file_check = 0
        for f in file_list:
            if f.endswith('.bak'):
                file_check = 1

        # #Archiwizacja
        if file_check == 1:
            for f in file_list:
                if f.endswith('.bak'):
                    self.info_textbox.insert(tk.END, f'Pakowanie pliku: {f}...\n')
                    with zipfile.ZipFile(fr'\\SERWERWIN\Importy\BACKUP\{f}.zip', 'w',
                                         zipfile.ZIP_DEFLATED) as zipfile_arch:
                        zipped_file = fr'\\SERWERWIN\Importy\BACKUP\{f}.zip'
                        zipped_file_name = f'{f}.zip'
                        zipfile_arch.write(os.path.join(path, f))
            self.info_textbox.insert(tk.END, f'Plik spakowany.\n')
        else:
            self.info_textbox.insert(tk.END, f'Brak plików do archiwizacji.\n')

        # wysyłanie na FTP
        self.info_textbox.insert(tk.END, f'Łączenie z serwerem FTP.\n')
        ftp = ftplib.FTP_TLS('ftp.maria-pharm.pl', ftp_username, ftp_password)  # połaczenie z serwerm
        ftp.cwd('SAGE')  # zmiana folderu na odpowiedni

        with open(zipped_file, 'rb') as file_to_send:
            self.info_textbox.insert(tk.END, f'Przesyłanie pliku na serwer...\n')
            file = ftp.storbinary('STOR ' + zipped_file_name, file_to_send)
            self.info_textbox.insert(tk.END, f'Wysyłka OK.\n')

        # kasowanie pliku z importy
        for f in file_list:
            os.remove(os.path.join(path, f))
        self.info_textbox.insert(tk.END, f'Skasoano archiwum z komputera.\n')
        # kasowanie starych plików na ftp
        files = ftp.mlsd()
        files_list = []
        for f in files:  # tworzenie listy plikow
            if f[0] != '.' and f[0] != '..':
                files_list.append((f[0], f[1]['modify']))

        files_list.sort(key=lambda tup: tup[1])  # sortowanie wg daty
        if len(files_list) > ilosc_plikow_do_zachowania:  # przygotownie listy plików do usunięcia
            files_list = files_list[0:-ilosc_plikow_do_zachowania]
        else:
            files_list = []
        self.info_textbox.insert(tk.END, f'Usuwanie starych plików z serwera FTP.\n')
        for f in files_list:  # usuwanie starych plików
            ftp.delete(f[0])
            self.info_textbox.insert(tk.END, f'Skasowano plik: {f[0]}.\n')

        ftp.quit()
        self.info_textbox.insert(tk.END, f'Koniec połączenia z serwerem FTP.\n')

    # karty_płaatnicze_hallera
    def create_katry_platnicze_frame(self):
        self.karty_platnicze_frame = tk.LabelFrame(self)
        self.karty_platnicze_frame.configure(bg='#383232', relief='groove', bd=1,
                                             text='   KARTY PŁATNICZE - HALLERA   ', fg='#3b8eed')
        self.karty_platnicze_frame.place(relx=0.01, rely=0.34, relwidth=0.48, relheight=0.10)

        self.dodaj_dane_button = tk.Button(self.karty_platnicze_frame, text='DODAJ DANE Z BANKU', command=
        lambda: self.start_new_thread(self.dodaj_dane_karty_platnicze), bg='#544949', fg=f'{self.kolor_razem}')
        self.dodaj_dane_button.place(relx=0.01, rely=0.1, relwidth=(0.95 / 4), relheight=0.35)

        self.data_kamsoft_od = DateEntry(self.karty_platnicze_frame, width=12, background='#383232',
                                         foreground='white', borderwidth=2, date_pattern='y-mm-dd',
                                         locale='pl_PL')
        self.data_kamsoft_od.place(relx=0.02 + (0.95 / 4), rely=0.1, relwidth=(0.95 / 4), relheight=0.35)
        self.data_kamsoft_do = DateEntry(self.karty_platnicze_frame, width=12, background='#383232',
                                         foreground='white', borderwidth=2, date_pattern='y-mm-dd',
                                         locale='pl_PL')
        self.data_kamsoft_do.place(relx=0.03 + (0.95 / 4) * 2, rely=0.1, relwidth=(0.95 / 4), relheight=0.35)

        self.sprawdz_dane_kamsoft_button = tk.Button(self.karty_platnicze_frame, text='PORÓWNAJ DANE Z KAMSOFT',
                                                     command=
                                                     lambda: self.start_new_thread(self.sprawdz_dane_z_kamsoft),
                                                     bg='#544949', fg=f'{self.kolor_razem}')
        self.sprawdz_dane_kamsoft_button.place(relx=0.04 + (0.95 / 4) * 3, rely=0.1, relwidth=(0.95 / 4),
                                               relheight=0.35)

        self.data_edycja_entry = tk.Entry(self.karty_platnicze_frame, justify='center', bg='#6b685f', fg='white')
        self.data_edycja_entry.place(relx=0.01, rely=0.55, relwidth=(0.95 / 4), relheight=0.35)

        self.data_do_edycji_dodania = DateEntry(self.karty_platnicze_frame, width=12, background='#383232',
                                                foreground='white', borderwidth=2, date_pattern='y-mm-dd',
                                                locale='pl_PL')
        self.data_do_edycji_dodania.place(relx=0.02 + (0.95 / 4), rely=0.55, relwidth=(0.95 / 4), relheight=0.35)

        self.dodaj_popraw_button = tk.Button(self.karty_platnicze_frame, text='DODAJ / POPRAW DANE', command=
        lambda: self.start_new_thread(self.dodaj_popraw_karty_platnicze), bg='#544949', fg=f'{self.kolor_razem}')
        self.dodaj_popraw_button.place(relx=0.03 + (0.95 / 4) * 2, rely=0.55, relwidth=(0.95 / 2) + 0.01,
                                       relheight=0.35)

    def dodaj_dane_karty_platnicze(self):
        self.info_textbox.delete('1.0', 'end')
        with open('rozne.json', encoding='utf-8') as json_file:
            data_json = json.load(json_file)

        dane_bank = self.controller.clipboard_get().split('\n')
        dane_bank.reverse()

        for t in dane_bank:
            if t.startswith('SOA/'):
                linia = t.split(' ')
                data = f'20{linia[2][-2:]}-{linia[2][3:5]}-{linia[2][:2]}'
                kwota = linia[3][1:]
                self.info_textbox.insert(tk.END, f'Dodano: {data}: {kwota}\n')
                if data not in data_json['karty_platnicze'].keys():
                    data_json['karty_platnicze'][data] = kwota
            else:
                continue

        with open('rozne.json', 'w', encoding='utf-8') as outfile:
            json.dump(data_json, outfile)

    def sprawdz_dane_z_kamsoft(self):
        self.info_textbox.delete('1.0', 'end')
        with open('rozne.json', encoding='utf-8') as json_file:
            data_json = json.load(json_file)
        dane_terminal = data_json['karty_platnicze']
        lista_dat_do_sprawdzenia = self.get_lista_dat_do_sprzedzenia()
        for data_s in lista_dat_do_sprawdzenia:
            if f'{data_s}' in dane_terminal.keys():
                query = f"SELECT SUM(kwota) FROM dokp WHERE (iddedp = 2 OR iddedp = 17 ) " \
                        f"AND id_osu = 0 AND datsp='{data_s}'"
                wynik = self.kamsoft_database.mysql_querry(query)
                if wynik[0][0] != None:
                    kwota_karty_kamsoft = round(float(wynik[0][0]), 2) * (-1)
                else:
                    kwota_karty_kamsoft = 0
                self.info_textbox.insert(tk.END, f'{data_s}: TERMINAL: {dane_terminal[f"{data_s}"]},'
                                                 f' KAMSOFT: {kwota_karty_kamsoft}\n')
                roznica = round(float(dane_terminal[f"{data_s}"]) - kwota_karty_kamsoft, 2)
                self.info_textbox.insert(tk.END, f'\tRÓŻNICA:'
                                                 f' {roznica}\n')
                self.info_textbox.yview(tk.END)
            else:
                continue

            if roznica > 0:
                query_sumy_pacjenci = f"SELECT  nrkln, ROUND(SUM(zplcl),2) from sprz  where id>0 and" \
                                      f" nrpar>0 and bufor=0 and wskus=0 and zplcl > 0 and datsp = '{data_s}'" \
                                      f" AND iddokf = 0 GROUP BY nrkln ORDER BY SUM(zplcl) DESC "
                wynik_sumy = self.kamsoft_database.mysql_querry(query_sumy_pacjenci)

                query_klienci_karta = f"SELECT nrkln FROM dokp WHERE (iddedp = 2 OR iddedp = 17 )" \
                                      f" AND id_osu = 0 AND datsp='{data_s}'"
                wynik_pacjenci_karta = self.kamsoft_database.mysql_querry(query_klienci_karta)
                lista_pacjenci_karta = []
                for w in wynik_pacjenci_karta:
                    lista_pacjenci_karta.append(w[0])

                suma_dzien = 0
                for n in wynik_sumy:
                    if n[0] not in lista_pacjenci_karta:
                        suma_dzien += n[1]
                        if suma_dzien >= roznica:
                            ostatnia_faktura_kwota = round(n[1] - (suma_dzien - roznica), 2)
                            self.info_textbox.insert(tk.END,
                                                     f'\t\t\tKLIENT: {n[0]} - {n[1]} ({ostatnia_faktura_kwota})\n')
                            self.info_textbox.insert(tk.END, f'\n')
                            break
                        else:
                            self.info_textbox.insert(tk.END, f'\t\t\tKLIENT: {n[0]} - {n[1]}\n')
            else:
                self.info_textbox.insert(tk.END, f'\n')
            self.info_textbox.yview(tk.END)

    def get_lista_dat_do_sprzedzenia(self):
        data_start = datetime.datetime.strptime(self.data_kamsoft_od.get(), '%Y-%m-%d')
        data_end = datetime.datetime.strptime(self.data_kamsoft_do.get(), '%Y-%m-%d')
        date_modified = data_start
        lista_dat = [data_start.date()]

        while date_modified < data_end:
            date_modified += datetime.timedelta(days=1)
            lista_dat.append(date_modified.date())
        return lista_dat

    def dodaj_popraw_karty_platnicze(self):
        data_edycji = self.data_do_edycji_dodania.get()
        kwota_edycji = self.data_edycja_entry.get().replace(',', '.')
        self.info_textbox.delete('1.0', 'end')
        with open('rozne.json', encoding='utf-8') as json_file:
            data_json = json.load(json_file)

        dane_terminal = data_json['karty_platnicze']
        dane_terminal[f'{data_edycji}'] = kwota_edycji

        data_json['karty_platnicze'] = dane_terminal
        with open('rozne.json', 'w', encoding='utf-8') as outfile:
            json.dump(data_json, outfile)
        self.info_textbox.insert(tk.END, f'Dodano / Poprawiono: {data_edycji}: {kwota_edycji}\n')

    # reklamówki
    def create_rekalmowki_frame(self):
        self.reklamowki_frame = tk.LabelFrame(self)
        self.reklamowki_frame.configure(bg='#383232', relief='groove', bd=1,
                                        text='   RAPORT REKLAMÓWKI - RECYCLING   ', fg='#3b8eed')
        self.reklamowki_frame.place(relx=0.01, rely=0.45, relwidth=0.48, relheight=0.07)

        self.reklamowki_button = tk.Button(self.reklamowki_frame, text='GENERUJ RAPORT', command=
        lambda: self.start_new_thread(self.pokaz_raport_reklamowki), bg='#544949', fg=f'{self.kolor_razem}')
        self.reklamowki_button.place(relx=0.54, rely=0.2, relwidth=0.45, relheight=0.6)

        rok_label = tk.Label(self.reklamowki_frame, text='OD: ', bg='#383232', fg='#80e89b', anchor='w')
        rok_label.place(relx=0.01, rely=0.2, relwidth=0.03, relheight=0.6)

        self.czas_start_entry = DateEntry(self.reklamowki_frame, width=12, background='#383232',
                                          foreground='white', borderwidth=2, date_pattern='y-mm-dd',
                                          locale='pl_PL')
        self.czas_start_entry.place(relx=0.06, rely=0.2, relwidth=0.2, relheight=0.6)

        kwartal_label = tk.Label(self.reklamowki_frame, text='DO: ', bg='#383232', fg='#80e89b', anchor='w')
        kwartal_label.place(relx=0.28, rely=0.2, relwidth=0.03, relheight=0.6)

        self.czas_stop_entry = DateEntry(self.reklamowki_frame, width=12, background='#383232',
                                         foreground='white', borderwidth=2, date_pattern='y-mm-dd',
                                         locale='pl_PL')
        self.czas_stop_entry.place(relx=0.33, rely=0.2, relwidth=0.2, relheight=0.6)

    def pokaz_raport_reklamowki(self):
        self.info_textbox.delete('1.0', 'end')
        self.info_textbox.insert(tk.END, f'OPŁATA RECYCLINGOWA - RAPORT\n')

        czas_start = self.czas_start_entry.get()
        czas_stop = self.czas_stop_entry.get()
        self.info_textbox.insert(tk.END, f'ZAKRES DAT {czas_start} - {czas_stop}\n\n')

        with open('rozne.json', encoding='utf-8') as json_file:
            data_json = json.load(json_file)
        reklamowki_dict = data_json['reklamowki']

        for n in range(2, 9):
            if n == 3:
                continue
            query_reklamowki = f'SELECT SUM(ilosp) FROM sprzedaz_0{n} WHERE idtowr = {reklamowki_dict[f"{n}"]} ' \
                               f'AND datsp BETWEEN "{czas_start}" AND "{czas_stop}"'
            wynik_reklamowki = self.zpt_database.mysql_querry(query_reklamowki)
            self.info_textbox.insert(tk.END, f'{slowniki.apteki_id_nazwa[f"{n}"]}: {wynik_reklamowki[0][0]}\n\n')

    # dyzury
    def create_dyzury_frame(self):
        self.dyzury_frame = tk.LabelFrame(self)
        self.dyzury_frame.configure(bg='#383232', relief='groove', bd=1,
                                    text='   DYŻURY APTECZNE   ', fg='#3b8eed')
        self.dyzury_frame.place(relx=0.01, rely=0.53, relwidth=0.48, relheight=0.07)

        self.dyzury_czas_start_entry = DateEntry(self.dyzury_frame, width=12, background='#383232',
                                                 foreground='white', borderwidth=2, date_pattern='y-mm-dd',
                                                 locale='pl_PL')
        self.dyzury_czas_start_entry.place(relx=0.01, rely=0.2, relwidth=0.25, relheight=0.6)

        self.dyzury_czas_stop_entry = DateEntry(self.dyzury_frame, width=12, background='#383232',
                                                foreground='white', borderwidth=2, date_pattern='y-mm-dd',
                                                locale='pl_PL')
        self.dyzury_czas_stop_entry.place(relx=0.28, rely=0.2, relwidth=0.25, relheight=0.6)

        self.reklamowki_button = tk.Button(self.dyzury_frame, text='GENERUJ / WYŚLIJ DYŻURY', command=
        lambda: self.start_new_thread(self.pokaz_wyslij_dyzury), bg='#544949', fg=f'{self.kolor_razem}')
        self.reklamowki_button.place(relx=0.54, rely=0.2, relwidth=0.45, relheight=0.6)

    def pokaz_wyslij_dyzury(self):

        config = pdfkit.configuration(wkhtmltopdf='c:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')
        with open('dyzury.json', encoding='utf-8') as json_file:
            data_json = json.load(json_file)
        text_do_dodania = ''

        self.info_textbox.delete('1.0', 'end')
        daty = self.get_lista_dat_dyzury()

        for d in daty:
            apteka = data_json[f'{d}']['apteka']
            adres_1 = data_json[f'{d}']['adres_1']
            adres_2 = data_json[f'{d}']['adres_2']
            telefon = data_json[f'{d}']['telefon']

            self.info_textbox.insert(tk.END, f'{d} - {apteka} - {adres_1} {adres_2} - {telefon}\n')
            text_do_dodania += f'<tr>' \
                               f'<td style = "width: 15%"><b>{d}</b></td>' \
                               f'<td style = "width: 30%"><b>{apteka}</b></td>' \
                               f'<td style = "width: 35%"><b>{adres_1} {adres_2}</b></td>' \
                               f'<td style = "width: 20%"><b>{telefon}</b></td>' \
                               f'</tr>'

        with open('wzor_dyzury.html', "r", encoding='utf-8') as f:
            text = f.read()
        text = text.replace('wiersze_do_dodania', text_do_dodania)

        pdfkit.from_string(text, fr'C:\Users\dell\Desktop\DYZURY.pdf', configuration=config)

        pytanie_mail = messagebox.askyesno('email?', 'Czy wysłać zestawienei mailem?')
        lista_maile_dyzury = ['tomasz.zembok@gmail.com', 'aptekanahallera@hotmail.com',
                              'apteka.mariapharm@gmail.com', 'wisla.fv@gmail.com']
        if pytanie_mail == False:
            pass
        else:
            pliki_typ = ("wszystkie pliki", "*.*")
            plik_dyzury = tk.filedialog.askopenfilename(initialdir=r'C:\Users\dell\Desktop', title="Wybierz plik",
                                                        filetypes=(pliki_typ, ("wszystkie pliki", "*.*")))
            print(plik_dyzury)
            for mail in lista_maile_dyzury:
                # zapytaj o hasło
                password = keyring.get_password("mejek_mail", "mejek_mail")
                tutul_wiadomosci = f'DYŻURY {daty[0]} - {daty[-1]}'
                text_wiadomosci = 'Pozdrawiam'

                while os.path.isfile(plik_dyzury) == False:
                    sleep(1)

                self.controller.maile.mail_text_attachmen(mail, tutul_wiadomosci, text_wiadomosci,
                                                          plik_dyzury, password)

    def get_lista_dat_dyzury(self):
        data_start = datetime.datetime.strptime(self.dyzury_czas_start_entry.get(), '%Y-%m-%d')
        data_end = datetime.datetime.strptime(self.dyzury_czas_stop_entry.get(), '%Y-%m-%d')
        date_modified = data_start
        lista_dat = [data_start.date()]

        while date_modified < data_end:
            date_modified += datetime.timedelta(days=1)
            lista_dat.append(date_modified.date())
        return lista_dat

    # wyciągi faktury FVS - płatności
    def create_faktury_fvs_frame(self):
        self.faktury_fvs_frame = tk.LabelFrame(self)
        self.faktury_fvs_frame.configure(bg='#383232', relief='groove', bd=1,
                                         text='   WYCIĄGI - FAKTURY FVS - ZAPŁATA   ', fg='#3b8eed')
        self.faktury_fvs_frame.place(relx=0.01, rely=0.61, relwidth=0.48, relheight=0.07)

        self.rok_entry = tk.Entry(self.faktury_fvs_frame, justify='center', bg='#6b685f', fg='white')
        self.rok_entry.place(relx=0.01, rely=0.2, relwidth=0.25, relheight=0.6)

        rok = datetime.datetime.today().year
        if datetime.datetime.today().month >= 3:
            miesiac = datetime.datetime.today().month - 2
        else:
            miesiac = datetime.datetime.today().month - 2 + 12
        self.rok_entry.insert(0, rok)

        miesiac_list = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
        self.miesiac_combobox = ttk.Combobox(self.faktury_fvs_frame, values=miesiac_list, state='readonly')
        self.miesiac_combobox.place(relx=0.28, rely=0.2, relwidth=0.25, relheight=0.6)
        self.miesiac_combobox.current(miesiac)

        self.reklamowki_button = tk.Button(self.faktury_fvs_frame, text='SZUKAJ WPŁAT', command=
        lambda: self.start_new_thread(self.szukaj_wplat), bg='#544949', fg=f'{self.kolor_razem}')
        self.reklamowki_button.place(relx=0.54, rely=0.2, relwidth=0.45, relheight=0.6)

    def szukaj_wplat(self):
        self.info_textbox.delete('1.0', 'end')
        rok = self.rok_entry.get()
        miesiac = self.miesiac_combobox.get()
        self.info_textbox.insert(tk.END, f'ROK: {rok}\nMIESIĄC: {miesiac}\n\n')

        plik = fr'C:\Users\dell\Dysk Google\IMPORTY\WYCIĄGI\MIL_{rok}{miesiac}.sta'

        if os.path.isfile(plik):
            transactions = mt940.parse(plik)
            for t in transactions:
                szczeguly = t.data['transaction_details'].split('\n')
                if szczeguly[2] == '<20PRZELEW PRZYCHODZĄCY':
                    if 'SOA/' in szczeguly[4] or '<22PRZELEW ŚRODKÓW WŁASNYCH' in szczeguly[4]:
                        pass
                    else:
                        tytul = f'{szczeguly[4][3:]} {szczeguly[5][3:]} {szczeguly[6][3:]} {szczeguly[7][3:]}'
                        self.info_textbox.insert(tk.END, f'Kontrahent: {szczeguly[9][3:]}\n')
                        self.info_textbox.insert(tk.END, f'Tytuł: {tytul}\n')
                        self.info_textbox.insert(tk.END, f'Tytuł: {t.data["amount"]}\n\n')
                        self.info_textbox.yview(tk.END)
        else:
            self.info_textbox.insert(tk.END, f'PLIK: {plik} nie isrnieje\n')

    # eksport RF z kamsoft do SAGE - odpowiednie z Stefano_Italiano.py
    def create_kamsoft_to_sage_frame(self):
        self.kamsoft_to_sage_frame = tk.LabelFrame(self)
        self.kamsoft_to_sage_frame.configure(bg='#383232', relief='groove', bd=1,
                                             text='   KAMSOFT RF ----> SAGE IMPORT   ', fg='#3b8eed')
        self.kamsoft_to_sage_frame.place(relx=0.01, rely=0.69, relwidth=0.48, relheight=0.07)

        apteka_list = ['']
        for key in slowniki.apteki_nazwa_id:
            apteka_list.append(key)
        self.wybor_apteki_combobox = ttk.Combobox(self.kamsoft_to_sage_frame, values=apteka_list, state='readonly')
        self.wybor_apteki_combobox.place(relx=0.01, rely=0.2, relwidth=0.25, relheight=0.6)
        self.wybor_apteki_combobox.current(0)

        self.kamsoft_to_sage_rok_entry = tk.Entry(self.kamsoft_to_sage_frame, justify='center', bg='#6b685f',
                                                  fg='white')
        self.kamsoft_to_sage_rok_entry.place(relx=0.28, rely=0.2, relwidth=0.25, relheight=0.6)
        rok = datetime.datetime.today().year
        miesiac = datetime.datetime.today().month - 1
        if miesiac == 0:
            miesiac = 12
            rok = rok - 1
        elif miesiac < 10:
            miesiac = f'0{miesiac}'
        else:
            pass
        self.kamsoft_to_sage_rok_entry.insert(0, f'{rok}-{miesiac}')

        self.eksportuj_rf_to_sage_button = tk.Button(self.kamsoft_to_sage_frame, text='GENERUJ PLIKI', command=
        lambda: self.start_new_thread(self.eksportuj_rf_to_sage), bg='#544949', fg=f'{self.kolor_razem}')
        self.eksportuj_rf_to_sage_button.place(relx=0.54, rely=0.2, relwidth=0.45, relheight=0.6)

    def eksportuj_rf_to_sage(self):
        self.info_textbox.delete('1.0', 'end')
        nazwa_apteki = self.wybor_apteki_combobox.get()

        text_start = '''INFO{
        	Nazwa programu =Mejek_konwerter
        	Wersja szablonu =4
        	dane_z_oddzialu =1
        	Kontrahent{
        	}
        }
        '''

        if nazwa_apteki != '':
            id_apteki = slowniki.apteki_nazwa_id[f'{nazwa_apteki}']
            self.info_textbox.insert(tk.END, f'APTEKA: {nazwa_apteki}\n\n')

            pulpit = r'C:\Users\dell\Desktop'
            if len(glob.glob(f'{pulpit}\*.dbf')) != 0:
                plik = glob.glob(f'{pulpit}\*.dbf')[0]
                # GENERACJA PLIKU FBP (faktury bez paragonu - dla firm)
                self.info_textbox.insert(tk.END, f'GENEROWANIE PLIKU FBP\n')
                txt_FBP = fr'C:\Users\dell\Desktop\0{id_apteki}_FBP_20{plik[-10:-4]}.txt'
                opis_FBP = 'sprzedaż leków FV'
                konto_WN_FBP = 145

                dbf = Dbf5(plik, codec='mazovia')
                db = dbf.to_dataframe()

                db_list = db.values.tolist()
                with open(txt_FBP, 'w') as file:
                    file.write(text_start)
                    for p in db_list:
                        if p[2] == 'FSV' and str(p[60]) == 'nan':
                            file.write(self.set_text_dokument_FBP(p, opis_FBP, konto_WN_FBP, id_apteki))
                            self.info_textbox.insert(tk.END, f'\t\tFBP: {p[8]}\n')
                            self.info_textbox.yview(tk.END)
                shutil.move(txt_FBP,
                            fr'C:\Users\dell\Dysk Google\IMPORTY\00_FBP\0{id_apteki}_FBP_20{plik[-10:-4]}.txt')

                # GENERACJA PLIKU FPAR (faktury z paragonem)
                self.info_textbox.insert(tk.END, f'\nGENEROWANIE PLIKU FPAR\n')
                txt_FPAR = fr'C:\Users\dell\Desktop\0{id_apteki}_FPAR_20{plik[-10:-4]}.txt'
                opis_FPAR = 'sprzedaż lekarstw'
                konto_WN_FPAR = 145
                with open(txt_FPAR, 'w') as file:
                    file.write(text_start)
                    for p in db_list:
                        if p[2] == 'FSV' and str(p[60]) != 'nan':
                            file.write(self.set_text_dokument_FPAR(p, opis_FPAR, konto_WN_FPAR, id_apteki))
                            self.info_textbox.insert(tk.END, f'\t\tFPAR: {p[8]}\t{p[55]}\n')
                            self.info_textbox.yview(tk.END)

                shutil.move(txt_FPAR,
                            fr'C:\Users\dell\Dysk Google\IMPORTY\00_FPAR\0{id_apteki}_FBP_20{plik[-10:-4]}.txt')

                # GENERACJA PLIKU TOW (zakupy i korekty) - razem ze sprawdzeniem)
                self.info_textbox.insert(tk.END, f'\nGENEROWANIE PLIKU TOW\n')
                txt_TOW = fr'C:\Users\dell\Desktop\0{id_apteki}_TOW_20{plik[-10:-4]}.txt'
                czas_query = self.kamsoft_to_sage_rok_entry.get()
                querry = f'SELECT dane FROM fv_sage WHERE apteka = {id_apteki} AND data_akt = "{czas_query}"'
                wynik_querry = self.zpt_database.mysql_querry(querry)[0][0]
                dane = json.loads(wynik_querry, encoding='utf-8')

                zpt_zakupy = []
                zpt_korekty = []

                i = 0
                for n in dane['Z']:
                    zpt_zakupy.append(dane['Z'][f'{n}']['nr_faktury'])
                for n in dane['K']:
                    zpt_korekty.append(dane['K'][f'{n}']['nr_faktury'])

                # get lista fakrut z kamsoft fp
                kamsoft_zakupy = []
                kamsoft_korekty = []

                for p in db_list:
                    if p[2] == 'FZV' and float(p[23]) != 0:
                        kamsoft_zakupy.append(p[8])
                    if p[2] == 'KZV' and float(p[23]) != 0:
                        kamsoft_korekty.append(p[8])

                # porownanie ilości elementów
                if len(kamsoft_zakupy) == len(zpt_zakupy):
                    self.info_textbox.insert(tk.END, f'\tLiczba elementów obu tablic ZAKUPÓW: {len(kamsoft_zakupy)}\n')
                else:
                    self.info_textbox.insert(tk.END, f'\tBŁĄD. Tablica kamsoft zakupy:'
                                                     f' {len(kamsoft_zakupy)}, tablica zpt zakupy:'
                                                     f' {len(zpt_zakupy)}\n')
                    return 0

                if len(kamsoft_korekty) == len(zpt_korekty):
                    self.info_textbox.insert(tk.END, f'\tLiczba elementów obu tablic KOREKT: {len(kamsoft_korekty)}\n')
                else:
                    self.info_textbox.insert(tk.END, f'\tBŁĄD. Tablica kamsoft korekty:'
                                                     f' {len(kamsoft_korekty)}, tablica zpt korekty:'
                                                     f' {len(zpt_korekty)}\n')
                    return 0

                # sprawdzenie elementow
                zakupy_braki = []
                korekty_braki = []

                for f in kamsoft_zakupy:
                    if f not in zpt_zakupy:
                        zakupy_braki.append(f)
                for f in kamsoft_korekty:
                    if f not in zpt_korekty:
                        korekty_braki.append(f)

                if zakupy_braki != []:
                    self.info_textbox.insert(tk.END, f'\tBŁĄD. Brak faktur {zakupy_braki}\n')
                    return 0
                else:
                    self.info_textbox.insert(tk.END, f'\tWszystkie faktury zakupu są zapisane w ZPT\n')

                if korekty_braki != []:
                    self.info_textbox.insert(tk.END, f'\tBŁĄD. Brak faktur {korekty_braki}\n')
                    return 0
                else:
                    self.info_textbox.insert(tk.END, f'\tWszystkie faktury korekty są zapisane w ZPT\n')

                with open(txt_TOW, 'w') as file:
                    file.write(text_start)
                    n = 1
                    for fv in zpt_zakupy:
                        for p in db_list:
                            if p[8] == fv:
                                if p[2] == 'FZV' or p[2] == 'KZV' and self.set_text_dokument_TOW(p, id_apteki, 'zakup') != False:
                                    file.write(self.set_text_dokument_TOW(p, id_apteki, 'zakup'))
                                    self.info_textbox.insert(tk.END, f'\t\tTOW_ZAKUPY_{n}: {p[8]}\n')
                                    self.info_textbox.yview(tk.END)
                                    n += 1
                                    break

                    n = 1
                    for fv in zpt_korekty:
                        for p in db_list:
                            if p[8] == fv:
                                if p[2] == 'FZV' or p[2] == 'KZV' and self.set_text_dokument_TOW(p, id_apteki, 'korekta') != False:
                                    file.write(self.set_text_dokument_TOW(p, id_apteki, 'korekta'))
                                    self.info_textbox.insert(tk.END, f'\t\tTOW_KOREKTY_{n}: {p[8]}\n')
                                    self.info_textbox.yview(tk.END)
                                    n += 1
                                    break

                shutil.move(txt_TOW,
                            fr'{slowniki.apteki_id_rf_to_sage[f"{id_apteki}"]["folder"]}\0{id_apteki}_TOW_20{plik[-10:-4]}.txt')

            else:
                self.info_textbox.insert(tk.END, f'\n\n\t\t\t\tBRAK PLIKU Z DANYMI\n\n')
        else:
            self.info_textbox.insert(tk.END, f'\n\n\t\t\t\tProszę wybrać aptekę\n\n')

    @staticmethod
    def set_text_dokument_FBP(row, opis, konto_WN, apteka_id):
        if str(row[58]) == 'nan': nip = ''
        konto_MA = slowniki.apteki_id_rf_to_sage[f'{apteka_id}']['konto_MA']

        text_dokument = f'''Kontrahent{{
    	id ={row[58]}
    	info =N
    	kod ={row[55]}
    	nazwa ={row[55]}
    	miejscowosc ={row[56].split(' ')[-1]}
    	ulica ={row[56].split(' ')[0] + ' ' + row[56].split(' ')[1]}
        nip ={row[58]}
    	VIES =0
    	krajKod =PL
    	osfiz =0
    	kraj{{
    		symbol =PL
    	}}
    }}
    Dokument{{
        rodzaj_dok =sprzedaży
        dozaplaty ={row[23]:.2f}
        wdozaplaty ={row[23]:.2f}
        FK nazwa ={row[8]}
        opis FK ={opis} 
        mppFlags =0
        kwota ={row[23]:.2f}
        obsluguj jak =FVS
        symbol FK =FVS
        dataWystawienia ={str(row[4])}
        datawpl ={row[4]}
        dataSprzedazy ={row[4]}
        kod ={row[8]}
        plattermin ={row[6]}
        rejestr_platnosci =BANK
        forma_platnosci =przelew
        Dane Nabywcy{{
            khid ={row[58]}
            khnazwa ={row[55]}
            khulica ={row[56].split(' ')[0] + ' ' + row[56].split(' ')[1]}
            khmiasto ={row[56].split(' ')[-1]}
            khnip ={row[58]}
        }}
        Zapis{{
            strona =WN
            kwota ={row[23]:.2f}
            konto ={konto_WN}
            IdDlaRozliczen =1
            pozycja =0
            ZapisRownolegly =0
            NumerDok ={row[8]}
            opis ={opis}
        }}
        Zapis{{
            strona =MA
            pozycja =0
            ZapisRownolegly =0
            IdDlaRozliczen =2
            kwota ={row[24]:.2f}
            konto ={konto_MA}
            NumerDok ={row[8]}
        }}
        Zapis{{
            strona =MA
            pozycja =0
            ZapisRownolegly =0
            IdDlaRozliczen =3
            kwota ={row[25]:.2f}
            konto =221-2
            opis ={opis}
            NumerDok ={row[8]}
        }}
        '''

        text_dokument += f'''Rejestr{{
            Skrot =rSPV
            Nazwa =Sprzedaż VAT
            ABC =1
            okres ={str(row[4])[:7] + '-01'}
            stawka =23.00
            brutto ={(float(row[65]) + float(row[73])):.2f}
            netto ={row[65]:.2f}
            VAT ={row[73]:.2f}
        }}
        '''

        text_dokument += f'''Rejestr{{
            Skrot =rSPV
            Nazwa =Sprzedaż VAT
            ABC =1
            okres ={str(row[4])[:7] + '-01'}
            stawka =8.00
            brutto ={(float(row[66]) + float(row[74])):.2f}
            netto ={row[66]:.2f}
            VAT ={row[74]:.2f}
        }}
        '''

        text_dokument += f'''Rejestr{{
            Skrot =rSPV
            Nazwa =Sprzedaż VAT
            ABC =1
            okres ={str(row[4])[:7] + '-01'}
            stawka =5.00
            brutto ={(float(row[67]) + float(row[75])):.2f}
            netto ={row[67]:.2f}
            VAT ={row[75]:.2f}
        }}
        '''

        text_dokument += f'''Transakcja{{
            IdDlaRozliczen =1
            kwota ={row[23]:.2f}
            termin ={row[6]}
        }}
    }}
    '''
        return text_dokument

    @staticmethod
    def set_text_dokument_FPAR(row, opis, konto_WN, apteka_id):
        if str(row[58]) != 'nan':
            nip = f'nip ={row[58]}\n'
            khnip = f'nip ={row[58]}\n'
        else:
            nip = ''
            khnip = ''

        nazwa_zastepcza = ''
        if row[55] == 'B╒HM KLAUDIA':
            nazwa_zastepcza = 'BOHM KLAUDIA'
        else:
            nazwa_zastepcza = row[55]

        konto_MA = slowniki.apteki_id_rf_to_sage[f'{apteka_id}']['konto_MA']
        print(nazwa_zastepcza)
        text_dokument = f'''Kontrahent{{
    	id ={nazwa_zastepcza}
    	info =N
    	kod ={nazwa_zastepcza}
    	nazwa ={nazwa_zastepcza}
    	miejscowosc ={row[56].split(' ')[-1]}
    	ulica ={row[56].split(' ')[0] + ' ' + row[56].split(' ')[1]}
        {nip}
    	VIES =0
    	krajKod =PL
    	osfiz =0
    	kraj{{
    		symbol =PL
    	}}
    }}
    Dokument{{
        rodzaj_dok =sprzedaży
        dozaplaty ={row[23]:.2f}
        wdozaplaty ={row[23]:.2f}
        FK nazwa ={row[8]}
        opis FK ={opis} 
        mppFlags =0
        kwota ={row[23]:.2f}
        obsluguj jak =FVS
        symbol FK =FVS
        dataWystawienia ={row[4]}
        datawpl ={row[4]}
        dataSprzedazy ={row[4]}
        kod ={row[8]}
        plattermin ={row[6]}
        rejestr_platnosci =BANK
        forma_platnosci =przelew
        Dane Nabywcy{{
            khid ={nazwa_zastepcza.replace(' ', '')}
            khnazwa ={nazwa_zastepcza}
            khulica ={row[56].split(' ')[0] + ' ' + row[56].split(' ')[1]}
            khmiasto ={row[56].split(' ')[-1]}
            {khnip}
        }}
        Zapis{{
            strona =WN
            kwota ={row[23]:.2f}
            konto ={konto_WN}
            IdDlaRozliczen =1
            pozycja =0
            ZapisRownolegly =0
            NumerDok ={row[8]}
            opis ={opis}
        }}
        Zapis{{
            strona =MA
            pozycja =0
            ZapisRownolegly =0
            IdDlaRozliczen =2
            kwota ={row[24]:.2f}
            konto ={konto_MA}
            NumerDok ={row[8]}
        }}
        Zapis{{
            strona =MA
            pozycja =0
            ZapisRownolegly =0
            IdDlaRozliczen =3
            kwota ={row[25]:.2f}
            konto =221-2
            opis ={opis}
            NumerDok ={row[8]}
        }}
        '''

        text_dokument += f'''Rejestr{{
            Skrot =rSPV
            Nazwa =Sprzedaż VAT
            ABC =1
            okres ={str(row[4])[:7] + '-01'}
            stawka =23.00
            brutto ={(float(row[65]) + float(row[73])):.2f}
            netto ={row[65]:.2f}
            VAT ={row[73]:.2f}
        }}
        '''

        text_dokument += f'''Rejestr{{
            Skrot =rSPV
            Nazwa =Sprzedaż VAT
            ABC =1
            okres ={str(row[4])[:7] + '-01'}
            stawka =8.00
            brutto ={(float(row[66]) + float(row[74])):.2f}
            netto ={row[66]:.2f}
            VAT ={row[74]:.2f}
        }}
        '''

        text_dokument += f'''Rejestr{{
            Skrot =rSPV
            Nazwa =Sprzedaż VAT
            ABC =1
            okres ={str(row[4])[:7] + '-01'}
            stawka =5.00
            brutto ={(float(row[67]) + float(row[75])):.2f}
            netto ={row[67]:.2f}
            VAT ={row[75]:.2f}
        }}
        '''

        text_dokument += f'''Transakcja{{
            IdDlaRozliczen =1
            kwota ={row[23]:.2f}
            termin ={row[6]}
        }}
    }}
    '''
        return text_dokument

    @staticmethod
    def set_text_dokument_TOW(row, apteka_id, rodzaj):
        symbol_FK = ''
        opis = ''
        nazwa_kor = ''
        data_kor = ''
        miejscowosc = ''
        opis_ZAKUP = 'Zakup towaru'
        opis_ZWROT = 'zwrot towaru'

        if float(row[23]) == 0:
            return False
        if rodzaj == 'zakup':
            symbol_FK = 'FVZ'
            opis = opis_ZAKUP
            nazwa_kor = ''
            data_kor = ''
        if rodzaj == 'korekta':
            opis = opis_ZWROT
            symbol_FK = 'FKZ'
            nazwa_kor = f'\nNazwaKor ={row[9]}\n'
            data_kor = f'DataKor ={row[6]}\n'

        if len(row[56].split(' ')) == 4:
            miejscowosc = f'{row[56].split(" ")[-2]} {row[56].split(" ")[-1]}, {row[56].split(" ")[0] + " " + row[56].split(" ")[1]}'
        elif row[56].split(' ')[0] == 'Kolista':
            miejscowosc = f'{row[56].split(" ")[-2]} {row[56].split(" ")[-1]}, {row[56].split(" ")[0] + " " + row[56].split(" ")[2]}'
        elif row[56].split(' ')[0] == 'DUBLIN':
            miejscowosc = f'{row[56].split(" ")[0]}'
        else:
            miejscowosc = ''

        text_dokument = f'''Kontrahent{{
    	id ={row[58].replace(' ', '').replace('-', '')}
    	info =N
    	kod ={row[55]}
            nazwa ={row[55]}
            miejscowosc ={miejscowosc}
            nip ={row[58].replace(' ', '').replace('-', '')}
    	VIES =0
    	krajKod =PL
    	osfiz =0
    	kraj{{
    		symbol =PL
    	}}
    }}
    Dokument{{
        rodzaj_dok =zakupu
        dozaplaty ={row[23]:.2f}
        wdozaplaty ={row[23]:.2f}
        FK nazwa ={row[8]}
        opis FK ={opis} 
        mppFlags =0
        kwota ={row[23]:.2f}
        obsluguj jak =FVZ
        symbol FK ={symbol_FK}
        dataWystawieniaObca ={row[4]}
        datawpl ={row[5]}
        dataZakupu ={row[5]}
        kod ={row[8]}
        plattermin ={row[4]}
        rejestr_platnosci =BANK
        forma_platnosci =przelew{nazwa_kor}{data_kor}
        Dane Nabywcy{{
            khid ={row[58].replace(' ', '').replace('-', '')}
            khnazwa ={row[55]}
            khmiasto ={miejscowosc}
            khnip ={row[58].replace(' ', '').replace('-', '')}
        }}
        Zapis{{
            strona =WN
            pozycja =0
            ZapisRownolegly =0
            IdDlaRozliczen =2
            kwota ={row[24]:.2f}
            konto =330-{apteka_id}    
            NumerDok ={row[8]}
        }}
        Zapis{{
            strona =MA
            kwota ={row[23]:.2f}
            konto =202-K{row[58].replace(' ', '').replace('-', '')}
            IdDlaRozliczen =1
            pozycja =0
            ZapisRownolegly =0
            NumerDok ={row[8]}
            opis ={opis}
        }}
        Zapis{{
            strona =WN
            pozycja =0
            ZapisRownolegly =0
            IdDlaRozliczen =3
            kwota ={row[25]:.2f}
            konto =221-1
            opis ={opis}
            NumerDok ={row[8]}
        }}
        '''

        text_dokument += f'''Rejestr{{
            Skrot =rZPV
    		Nazwa =Zakup VAT
    		ABC =1
    		okres ={str(row[5])[:7] + '-01'}
    		stawka =23.00
    		brutto ={(float(row[65]) + float(row[73])):.2f}
    		netto ={row[65]:.2f}
    		VAT ={row[73]:.2f}
        }}
        '''

        text_dokument += f'''Rejestr{{
            Skrot =rZPV
    		Nazwa =Zakup VAT
    		ABC =1
    		okres ={str(row[5])[:7] + '-01'}
    		stawka =8.00
    		brutto ={(float(row[66]) + float(row[74])):.2f}
            netto ={row[66]:.2f}
            VAT ={row[74]:.2f}
        }}
        '''

        text_dokument += f'''Rejestr{{
            Skrot =rZPV
    		Nazwa =Zakup VAT
    		ABC =1
    		okres ={str(row[5])[:7] + '-01'}
            stawka =5.00
            brutto ={(float(row[67]) + float(row[75])):.2f}
            netto ={row[67]:.2f}
            VAT ={row[75]:.2f}
        }}
        '''

        text_dokument += f'''Transakcja{{
            IdDlaRozliczen =1
            kwota ={row[23]:.2f}
            termin ={row[6]}
        }}
    }}
    '''
        return str(text_dokument)

class Maile(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.configure(bg='#383232')

    def mail_text(self, to, subject, text_html, password):  # wysylanie maila
        # self.maile_toplevel()
        # self.after(2000, lambda: self.text_box.insert(tk.END, 'Pobieranie danych\n'))
        gmail_user = "tomasz.zembok@gmail.com"
        gmail_pwd = password
        msg = MIMEMultipart()

        msg['From'] = gmail_user
        msg['To'] = to
        msg['Subject'] = subject

        msg.attach(MIMEText(text_html, 'html'))

        mailServer = smtplib.SMTP("smtp.gmail.com", 587)
        mailServer.ehlo()
        mailServer.starttls()
        mailServer.ehlo()
        mailServer.login(gmail_user, gmail_pwd)
        # self.after(2000, lambda: self.text_box.insert(tk.END, 'Połączenie do serwera ... OK\n'))
        mailServer.sendmail(gmail_user, to, msg.as_string())
        # self.after(2000, lambda: self.text_box.insert(tk.END, 'Wysyłanie maila...\n'))
        # Should be mailServer.quit(), but that crashes...
        mailServer.close()
        # print(f"wyslano do: {to}")
        # self.after(3000, lambda: self.text_box.insert(tk.END, f"wyslano do: {to}"))
        # self.after(5000, lambda: self.mail_toplevel.destroy())
        # self.after(6000, lambda: sleep(1))
        self.message = messagebox.showinfo('WYSŁANO MAILA', f"wyslano do: {to}")

    def mail_text_attachmen(self, to, subject, text_html, attachment, password):  # wysylanie maila
        # self.maile_toplevel()
        # self.after(2000, lambda: self.text_box.insert(tk.END, 'Pobieranie danych\n'))
        gmail_user = "tomasz.zembok@gmail.com"
        gmail_pwd = password
        msg = MIMEMultipart()

        msg['From'] = gmail_user
        msg['To'] = to
        msg['Subject'] = subject

        msg.attach(MIMEText(text_html, 'html'))

        part = MIMEBase('application', 'octet-stream')
        part.set_payload(open(attachment, 'rb').read())
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        'attachment; filename="%s"' % os.path.basename(attachment))
        msg.attach(part)

        mailServer = smtplib.SMTP("smtp.gmail.com", 587)
        mailServer.ehlo()
        mailServer.starttls()
        mailServer.ehlo()
        mailServer.login(gmail_user, gmail_pwd)
        # self.after(2000, lambda: self.text_box.insert(tk.END, 'Połączenie do serwera ... OK\n'))
        mailServer.sendmail(gmail_user, to, msg.as_string())
        # self.after(2000, lambda: self.text_box.insert(tk.END, 'Wysyłanie maila...\n'))
        # Should be mailServer.quit(), but that crashes...
        mailServer.close()
        # print(f"wyslano do: {to}")
        # self.after(3000, lambda: self.text_box.insert(tk.END, f"wyslano do: {to}"))
        # self.after(5000, lambda: self.mail_toplevel.destroy())
        self.message = messagebox.showinfo('WYSŁANO MAILA', f"wyslano do: {to}")

    def maile_toplevel(self):
        self.mail_toplevel = tk.Toplevel(self, background='#383232',
                                         highlightthickness=2)
        self.mail_toplevel.grab_set()
        self.mail_toplevel.geometry(f'400x200+200+100')
        self.text_box = tk.Text(self.mail_toplevel, bg='#6b685f', fg='white', wrap='word')
        self.text_box.place(relx=0.01, rely=0.01, relwidth=0.98, relheight=0.98)

# todo zakładka info z testami
# odswież liste faktur kosztowych button + poprawa wpisu double click na fakturze zapłaconej już
# opcja wysłanie zestawienia z urlopami do pracownika
# dodaj plik z parametrami dla label i entry - kolory itp. globalna zmienna (kiedyś może)