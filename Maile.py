#!/usr/bin/python
# -*- coding: utf-8 -*-

import slowniki
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
import email.encoders as Encoders
import os

class Maile():

    def __init__(self):
        self.email = '######'
        self.password = '######'

    def mail_text(self, to, subject, text_html, password):  # wysylanie maila
        gmail_user = self.email
        gmail_pwd = self.password
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
        mailServer.sendmail(gmail_user, to, msg.as_string())
        # Should be mailServer.quit(), but that crashes...
        mailServer.close()
        print(f"wyslano do: {to}")

    def mail_text_attachmen(self, to, subject, text_html, attachment,  password):  # wysylanie maila
        gmail_user = self.email
        gmail_pwd = self.password
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
        mailServer.sendmail(gmail_user, to, msg.as_string())
        # Should be mailServer.quit(), but that crashes...
        mailServer.close()
        print(f"wyslano do: {to}")
