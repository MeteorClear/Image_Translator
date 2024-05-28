import numpy as np

import erase_text
import make_sentence_block

import argos_translate
import google_translate_lib

'''
Class for paragraph and internal sentence control
Controls the sentences inside the paragraph and performs color extraction and translation
'''

class ParagraphBlock:
    '''
    Class on paragraph blocks,
    Receive information of block, 
    translate text and save,
    Color extraction included
    '''
    x_ = -1
    y_ = -1
    w_ = -1
    h_ = -1
    text_ = ''
    line_ = -1
    lpos_ = []
    fsize_ = []
    color_weight_ = 0
    translator_mode_ = None

    background_color_ = None
    font_color_ = None
    trans_text_ = None
    src_lang_ = None
    dest_lang_ = None


    def __init__(self, \
                 x: int, y: int, w: int, h: int, \
                 text: str, line: int, \
                 lpos: list, fsize: list, \
                 color_weight:int=30, \
                 translator_mode:str='argos') -> None:
        '''
        Receive information of block
        Color weight is the value added to the font color
        '''
        self.x_ = x
        self.y_ = y
        self.w_ = w
        self.h_ = h
        self.text_ = text
        self.line_ = line
        self.lpos_ = lpos
        self.fsize_ = fsize
        self.color_weight_ = color_weight
        self.translator_mode_ = translator_mode

        return
    
    def color_find(self, image: np.ndarray) -> None:
        '''
        Extracts background color and character color of block from a given image
        Works differently depending on the number of lines in the block
        '''
        # Works differently depending on the number of sentences in the paragraph
        if self.line_ > 1:
            self.multi_line_init(image)
        else:
            self.single_line_init(image)

        return
    

    def single_line_init(self, image: np.ndarray) -> None:
        '''
        Used when there is only one line in a paragraph
        '''
        roi = erase_text.find_roi(image, self.x_, self.y_, self.w_, self.h_)
        cluster = erase_text.make_cluster(roi)

        self.background_color_ = [erase_text.find_dominant_color(cluster, cluster.cluster_centers_, order=0)]

        font_color = erase_text.find_dominant_color(cluster, cluster.cluster_centers_, order=1)
        font_color = tuple(font_color)
        self.font_color_ = [erase_text.correction_color(font_color, self.color_weight_)]

        return
    

    def multi_line_init(self, image: np.ndarray) -> None:
        '''
        Used when a paragraph has two or more lines
        '''
        bg_colors = []
        ft_colors = []
        for n_lines in range(self.line_):
            line_x, line_y, line_w, line_h = self.lpos_[n_lines]

            roi = erase_text.find_roi(image, line_x, line_y, line_w, line_h)
            cluster = erase_text.make_cluster(roi)

            bg_colors.append(erase_text.find_dominant_color(cluster, cluster.cluster_centers_, order=0))

            font_color = erase_text.find_dominant_color(cluster, cluster.cluster_centers_, order=1)
            font_color = tuple(font_color)
            ft_colors.append(erase_text.correction_color(font_color, self.color_weight_))

        self.background_color_ = bg_colors.copy()
        self.font_color_ = ft_colors.copy()

        return
    

    def text_translate(self, src_lang:str='en', dest_lang:str='ko', translator_mode:str=None) -> None:
        '''
        Translates text in paragraphs into target language
        '''
        self.src_lang_ = src_lang
        self.dest_lang_ = dest_lang
        if translator_mode is not None:
            self.translator_mode_ = translator_mode
        
        # Translating sentences inside paragraphs into target languages
        if self.translator_mode_ == "google_lib":
            translated_text = google_translate_lib.text_translate(text=self.text_, src=self.src_lang_, dest=self.dest_lang_)
        else:
            translated_text = argos_translate.text_translate(text=self.text_, src=self.src_lang_, dest=self.dest_lang_)

        # Separate translated sentences to fit the lines in the paragraph
        if self.line_ > 1:
            line_width = []

            for line_pos in self.lpos_:
                line_width.append(line_pos[2])
            split_text = make_sentence_block.distribute_text(translated_text, self.line_, line_width)

            self.trans_text_ = split_text
        else:
            self.trans_text_ = [translated_text]

        return


    def get_position(self) -> tuple:
        '''
        Returns the coordinate of the paragraph block,
        (x, y, w, h)
        '''
        position = (self.x_, self.y_, self.w_, self.h_)
        
        return position
    

    def get_translated_text(self) -> tuple:
        '''
        Returns Number of lines in paragraph, the coordinates of each line, and translated text
        '''
        result = (self.line_, self.lpos_, self.trans_text_)

        return result
    

    def get_color(self) -> tuple:
        '''
        Returns the extracted background color and text color
        '''
        result = (self.background_color_, self.font_color_)

        return result