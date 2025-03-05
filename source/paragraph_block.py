import numpy as np

import erase_text
import make_sentence_block

import argos_translate
import google_translate_lib

"""
Class for paragraph and sentence control.
Manages paragraph blocks by grouping sentences, extracting colors, and performing translations.
"""

class ParagraphBlock:
    def __init__(self, \
                 x: int, y: int, w: int, h: int, \
                 text: str, line: int, \
                 lpos: list, fsize: list, \
                 color_weight:int=30, \
                 translator_mode:str='argos') -> None:
        """
        Initialize a paragraph block with its bounding box, text content, and settings.

        Args:
            x (int): X-coordinate of the block.
            y (int): Y-coordinate of the block.
            w (int): Width of the block.
            h (int): Height of the block.
            text (str): The block's text.
            line (int): Number of lines in the block.
            lpos (list): List of line positions as tuples (x, y, width, height).
            fsize (list): List of font sizes for each line.
            color_weight (int, optional): Value to adjust the font color. Defaults to 30.
            translator_mode (str, optional): Translation mode ('argos' or 'google_lib'). Defaults to 'argos'.
        """
        self.x_ = x
        self.y_ = y
        self.width_ = w
        self.height_ = h
        self.text_ = text
        self.line_ = line
        self.line_positions_ = lpos
        self.font_size_ = fsize
        self.color_weight_ = color_weight
        self.translator_mode_ = translator_mode

        self.background_color_ = None
        self.font_color_ = None
        self.translated_text_ = None
        self.src_lang_ = None
        self.dest_lang_ = None

        return
    
    def color_find(self, image: np.ndarray) -> None:
        """
        Extract background and font colors from the block using the provided image.  

        Uses a different method for single-line and multi-line blocks.  
        You can check the color extracted through `get_color()`

        Args:
            image (np.ndarray): The full image array to find color.
        """
        if self.line_ > 1:
            self.multi_line_init(image)
        else:
            self.single_line_init(image)

        return
    

    def single_line_init(self, image: np.ndarray) -> None:
        """
        Extract colors for a single-line block.
        """
        roi = erase_text.find_roi(image, self.x_, self.y_, self.width_, self.height_)
        cluster = erase_text.make_cluster(roi)

        self.background_color_ = [erase_text.find_dominant_color(cluster, cluster.cluster_centers_, order=0)]

        font_color = erase_text.find_dominant_color(cluster, cluster.cluster_centers_, order=1)
        font_color = tuple(font_color)
        self.font_color_ = [erase_text.correction_color(font_color, self.color_weight_)]

        return
    

    def multi_line_init(self, image: np.ndarray) -> None:
        """
        Extract colors for a multi-line block by processing each line separately.
        """
        bg_colors = []
        ft_colors = []
        for n_lines in range(self.line_):
            line_x, line_y, line_w, line_h = self.line_positions_[n_lines]

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
        """
        Translate the block's text into the target language.

        Uses either the argos_translate or google_translate_lib based on translator_mode.  
        For multi-line blocks, splits the translated text to match line widths.  
        You can check the translated text through `get_translated_text()`

        Args:
            src_lang (str, optional): Source language code. Defaults to 'en'.
            dest_lang (str, optional): Target language code. Defaults to 'ko'.
            translator_mode (str, optional): If provided, overrides the block's translator mode.
        """
        self.src_lang_ = src_lang
        self.dest_lang_ = dest_lang
        if translator_mode is not None:
            self.translator_mode_ = translator_mode
        
        if self.translator_mode_ == "google_lib":
            translated_text = google_translate_lib.text_translate(text=self.text_, src=self.src_lang_, dest=self.dest_lang_)
        else:
            translated_text = argos_translate.text_translate(text=self.text_, src=self.src_lang_, dest=self.dest_lang_)

        if self.line_ > 1:
            line_width = []

            for line_pos in self.line_positions_:
                line_width.append(line_pos[2])
            split_text = make_sentence_block.distribute_text(translated_text, self.line_, line_width)

            self.translated_text_ = split_text
        else:
            self.translated_text_ = [translated_text]

        return


    def get_position(self) -> tuple:
        """
        Return the bounding box of the paragraph block as (x, y, width, height).

        Returns:
            tuple: The paragraph block position as (x, y, width, height)
        """
        position = (self.x_, self.y_, self.width_, self.height_)
        
        return position
    

    def get_translated_text(self) -> tuple:
        """
        Return the number of lines, line positions, and the translated text.

        Returns:
            tuple: The translated sentence information inside block as (number of lines, line positions, translated text)
        """
        result = (self.line_, self.line_positions_, self.translated_text_)

        return result
    

    def get_color(self) -> tuple:
        """
        Return the extracted background and font colors.

        Returns:
            tuple: The extracted colors as (background color, font color)
        """
        result = (self.background_color_, self.font_color_)

        return result