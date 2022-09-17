#!/usr/bin/python
# -*- coding: utf-8 -*-

from tkinter import messagebox, ttk
import os
from pyAesCrypt import decryptFile
from json import load as json_load
import pymysql as connection
import keyring
import sys

class ZPT_base():
    def __init__(self):
        self.parametry_zpt = self.get_parametry_zpt()

    def get_parametry_zpt(self):
        self.bufferSize = 64 * 1024
        self.password = keyring.get_password("zpt_db", "zpt_db")
        self.decrypted_file = r'C:/MARIA-PHARM/netdatabase.json'
        self.encrypted_file = r'C:/MARIA-PHARM/netdatabase.json.aes'
        decryptFile(self.encrypted_file, self.decrypted_file, self.password, self.bufferSize)

        with open(self.decrypted_file) as json_file_zpt:
            parametry_zpt = json_load(json_file_zpt)
        os.remove(self.decrypted_file)
        return parametry_zpt

    def connect_zpt_database(self):
        self.con_zpt = connection.connect(host=self.parametry_zpt['host'],
                                     port=self.parametry_zpt['port'],
                                     user=self.parametry_zpt['user'],
                                     passwd=self.parametry_zpt['passwd'],
                                     db=self.parametry_zpt['db'],
                                     charset=self.parametry_zpt['charset']
                                     )
        self.con_zpt.text_factory = str
        self.cur_zpt = self.con_zpt.cursor()
        if self.cur_zpt:
            self.cur_zpt.execute("SET NAMES utf8mb4;")  # or utf8 or any other charset you want to handle
            self.cur_zpt.execute("SET CHARACTER SET utf8mb4;")  # same as above
            self.cur_zpt.execute("SET character_set_connection=utf8mb4;")  # same as above
            return self.cur_zpt
        else:
            messagebox.showinfo('BŁĄD', 'BRAK POŁĄCZENIA Z BAZĄ')

    def mysql_querry(self, querry_text):
        cur_zpt = self.connect_zpt_database()
        self.question = cur_zpt.execute(querry_text)
        self.database_answer = cur_zpt.fetchall()
        self.con_zpt.commit()
        cur_zpt.close()
        self.con_zpt.close()
        return self.database_answer

    def mysql_no_fetch_querry(self, querry_text):
        cur_zpt = self.connect_zpt_database()
        self.question = cur_zpt.execute(querry_text)
        self.con_zpt.commit()
        cur_zpt.close()
        self.con_zpt.close()

    def mysql_executemany_querry(self, querry_text, dane):
        cur_zpt = self.connect_zpt_database()
        self.question = cur_zpt.executemany(querry_text, dane)
        self.con_zpt.commit()
        cur_zpt.close()
        self.con_zpt.close()
