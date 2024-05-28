import os
import time

import pygame
from gtts import gTTS


'''
tts_init(path=".//tts_data//", extension=".mp3")

make_tts_script(dict_data)

run_tts(text, lang, file_adder=None, file_path=None)
'''


base_path = ''
base_extension = ''


def tts_init(path=".//tts_data//", extension=".mp3"):
    global base_path, base_extension

    base_path = path
    base_extension = extension

    pygame.mixer.init()

    return


def make_tts_script(dict_data):
    full_script = ''

    for i in range(len(dict_data['text'])):
        text = dict_data['text'][i]

        full_script += text + " \n"

    return full_script


def make_tts_script_list(dict_data):
    script_list = ''

    for i in range(len(dict_data['text'])):
        text = dict_data['text'][i]

        script_list.append(text)

    return script_list


def run_tts(text, lang, file_adder=None, file_path=None):
    global base_path, base_extension

    if file_adder == None:
        file_name_adder = str(int(time.time()))
    else:
        file_name_adder = file_adder

    if file_path == None:
        tts_file_path = base_path + file_name_adder + base_extension
    else:
        tts_file_path = file_path

    target_text = text
    target_lang = lang

    try:
        tts = gTTS(target_text, lang=target_lang)
    except:
        raise "cannot work gTTS, check internet connection"
    
    try:
        tts.save(tts_file_path)
    except:
        raise "cannot save file, check user permision"
    
    time.sleep(0.5)

    if os.path.isfile(tts_file_path):
        pygame.mixer.music.load(tts_file_path)
        pygame.mixer.music.play()
    else:
        raise "does not exist audio file"
    
    return


def tts_stop():
    pygame.mixer.music.stop()
    return