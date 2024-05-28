import os
import time
import pygame

from gtts import gTTS

import argos_translate
import google_translate_lib

'''
Class that collects text from paragraphs and converts them into speech
https://pypi.org/project/gTTS/
'''

class TTSBlock:
    '''
    Class that reads text into tts, 
    makes it an audio file and plays it, 
    Using pygame, 
    Internet connection required
    '''
    base_path_ = ''
    base_extension_ = ''
    file_name_adder_ = ''
    tts_file_path_ = ''

    src_lang_ = ''
    dest_lang_ = ''

    script_ = ''
    script_list_ = None
    trans_script_ = ''
    trans_script_list_ = None
    

    def __init__(self, \
                 dict_data: dict, \
                 src_lang: str= "en", \
                 dest_lang: str= "ko", \
                 path: str= ".//temp//tts_data//", \
                 extension: str= ".mp3") -> None:
        self.base_path_ = path
        self.base_extension_ = extension
        self.src_lang_ = src_lang
        self.dest_lang_ = dest_lang

        self.script_ = self.make_script(dict_data)
        self.script_list_ = self.make_script_list(dict_data)

        pygame.mixer.init()

        return
    

    def set_parameter(self, path:str=None, extension:str=None, adder:str=None, file_path:str=None) -> None:
        '''
        Set class variable, 
        Related to save files
        '''
        if path != None:
            self.base_path_ = path

        if extension != None:
            self.base_extension_ = extension

        if adder != None:
            self.file_name_adder_ = adder

        if file_path != None:
            self.tts_file_path_ = file_path

        return
    

    def make_script(self, dict_data: dict) -> str:
        '''
        Collecting strings from a dictionary into a single string
        '''
        full_script = ''

        for i in range(len(dict_data['text'])):
            text = dict_data['text'][i]

            full_script += text + " \n"

        return full_script


    def make_script_list(self, dict_data: dict) -> list:
        '''
        Collecting strings from a dictionary into a string list
        '''
        script_list = list()

        for i in range(len(dict_data['text'])):
            text = dict_data['text'][i]

            script_list.append(text)

        return script_list
    

    def translate_script(self) -> None:
        '''
        Translate saved script
        '''
        trans_list = []
        trans_script = ''

        if len(self.script_list_) > 1:
            for script_text in self.script_list_:
                trans_line = argos_translate.text_translate(script_text, src=self.src_lang_, dest=self.dest_lang_)

                trans_list.append(trans_line)
                trans_script += trans_line + ". \n"

        self.trans_script_ = trans_script
        self.trans_script_list_ = trans_list

        return
    

    def tts_stop(self) -> None:
        '''
        Stop playing audio
        '''
        pygame.mixer.music.stop()
        return
    

    def tts_play(self, path:str=None) -> None:
        '''
        Play audio files on the specified path
        '''
        if path is None:
            path = self.tts_file_path_

        if os.path.isfile(path):
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()

        else:
            raise "does not exist audio file"
        
        return
    

    def run_tts(self, text:str=None, lang:str=None, file_adder:str=None, file_path:str=None) -> None:
        '''
        Use tts to convert the string into audio and play it
        '''
        if text is None:
            text = self.trans_script_
        
        if lang is None:
            lang = self.dest_lang_

        if len(text) < 1:
            raise "no text"

        if file_adder == None:
            self.file_name_adder_ = str(int(time.time()))
        else:
            self.file_name_adder_ = file_adder

        if file_path == None:
            self.tts_file_path_ = self.base_path_ + self.file_name_adder_ + self.base_extension_
        else:
            self.tts_file_path_ = file_path

        try:
            tts = gTTS(text, lang=lang)
        except:
            raise "cannot work gTTS, check internet connection"
        
        try:
            tts.save(self.tts_file_path_)
        except:
            raise "cannot save file, check user permision"
        
        time.sleep(0.5)

        self.tts_play()
        
        return