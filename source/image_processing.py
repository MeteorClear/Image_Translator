import cv2
import numpy as np
import pytesseract
from PIL import ImageFont, ImageDraw, Image

import make_sentence_block
import paragraph_block

'''
Class for performing OCR and other functions on images
Perform OCR, sentence and paragraph re-collect, paragraph object control
It is estimated that the object can be reused, but not tried
Can require a lot of resources
'''

class ProcessingBlock:
    '''
    Image processing by receiving image path and setting value,
    It recognizes through ocr, translates, and puts text in the same position 
    '''
    image_path_ = ".\\test1.jpg"
    save_path_ = ''
    src_lang_ = ''
    dest_lang_ = ''
    font_type_ = ''

    # thresholds and weights used in the operation
    font_weight_ = 1.2
    sentence_threshold_ = 50
    block_threshold_ = 1.5
    translator_mode_ = 'argos'

    # Image read in cv, Original, for visualization, for results
    image_ = None
    sub_image_ = None
    result_image_ = None

    # Dictionaries and list used for paragraph objects
    ocr_data_ = None
    block_data_ = None
    blocks_ = []
    

    def __init__(self, image_path: str, \
                 save_path: str= ".\\result", \
                 src_lang: str= "en", \
                 dest_lang: str= "ko", \
                 font_type: str= "fonts\\gulim.ttc", \
                 font_weight: float= 1.2, \
                 sentence_threshold: int= 50, \
                 block_threshold: float= 1.5, \
                 translator_mode: str= "argos") -> None:
        '''
        Read images using the inputed path
        '''
        self.image_path_ = image_path
        self.save_path_ = save_path
        self.src_lang_ = src_lang
        self.dest_lang_ = dest_lang
        self.font_type_ = font_type

        self.font_weight_ = font_weight
        self.sentence_threshold_ = sentence_threshold
        self.block_threshold_ = block_threshold
        self.translator_mode_ = translator_mode

        # the part read the image in cv
        self.image_ = cv2.imread(self.image_path_)
        self.sub_image_ = self.image_.copy()
        self.result_image_ = self.image_.copy()

        return
    

    def ocr_process(self) -> dict:
        '''
        Use the Tesserect OCR engine to extract text and store it in dictionary form
        '''
        self.ocr_data_ = pytesseract.image_to_data(self.image_, \
                                                   output_type=pytesseract.Output.DICT)

        return self.ocr_data_
    

    def recollection_text(self) -> dict:
        '''
        Recombine data extracted through OCR into sentences and paragraphs
        '''
        if self.ocr_data_ is None:
            self.ocr_process()

        # Estimate sentence structure
        sentence_data = make_sentence_block.find_sentence(self.ocr_data_, self.sentence_threshold_)

        # Estimate paragraph structure 
        self.block_data_ = make_sentence_block.make_sentence_block(sentence_data, threshold=self.block_threshold_)

        return self.block_data_
    

    def build_blocks(self) -> None:
        '''
        Create paragraph objects using recombined data
        '''
        self.blocks_ = []

        if self.block_data_ is None:
            self.recollection_text()

        for i in range(len(self.block_data_['text'])):
            x = self.block_data_['left'][i]
            y = self.block_data_['top'][i]
            w = self.block_data_['width'][i]
            h = self.block_data_['height'][i]

            text = self.block_data_['text'][i]
            line = self.block_data_['line'][i]
            lpos = self.block_data_['lpos'][i]
            fsize = self.block_data_['fsize'][i]

            # Forming a list of paragraph objects
            self.blocks_.append(paragraph_block.ParagraphBlock(x=x, y=y, w=w, h=h, \
                                                               text=text, \
                                                               line=line, \
                                                               lpos=lpos, \
                                                               fsize=fsize, \
                                                               translator_mode=self.translator_mode_))
            
        return
    

    def processing_run(self) -> np.ndarray:
        '''
        Use paragraph objects to insert translated text into an image
        '''
        if self.block_data_ is None:
            self.recollection_text()
            self.build_blocks()
        
        # Works with each paragraph object
        for block in self.blocks_:
            block.color_find(self.image_)
            block.text_translate(src_lang=self.src_lang_, dest_lang=self.dest_lang_)
            block_line, block_lpos, block_text = block.get_translated_text()
            background_color, font_color = block.get_color()
            font_size = block.get_font_size()

            # Works with every sentence contained in a paragraph
            for i in range(block_line):
                box_x, box_y, box_w, box_h = block_lpos[i]
                box_text = block_text[i]
                box_bg = background_color[i]
                box_ft = font_color[i]
                box_fs = font_size[i]

                # Clear existing text by covering the existing text area with background color
                cv2.rectangle(self.result_image_, (box_x, box_y), (box_x+box_w, box_y+box_h), box_bg, -1)

                # Converting image type for Unicode insertion
                pil_image = Image.fromarray(self.result_image_)

                # Insert text into the image using translated text and sentence positions
                # The font size uses the average of the text height contained in the sentence multiplied by the weight
                # Weights typically use 1.2 but tend to be larger than the original in oversized letters
                # If you don't use weights, they usually appear smaller than the original
                draw = ImageDraw.Draw(pil_image)
                font = ImageFont.truetype(self.font_type_, int(box_fs * (self.font_weight_)))
                position = (box_x, box_y)

                draw.text(position, box_text, font=font, fill=box_ft)

                # Reconverting for cv processing
                self.result_image_ = np.array(pil_image)

        return self.result_image_
    

    def draw_process(self) -> None:
        for i in range(len(self.ocr_data_['text'])):
            x = self.ocr_data_['left'][i]
            y = self.ocr_data_['top'][i]
            w = self.ocr_data_['width'][i]
            h = self.ocr_data_['height'][i]
            
            text = self.ocr_data_['text'][i]
            conf = int(self.ocr_data_['conf'][i])

            if conf > self.sentence_threshold_ and len(text)>0:
                cv2.rectangle(self.sub_image_, (x,y), (x+w,y+h), (0,255,0), 1)

        for i in range(len(self.block_data_['text'])):
            x = self.block_data_['left'][i]
            y = self.block_data_['top'][i]
            w = self.block_data_['width'][i]
            h = self.block_data_['height'][i]

            text = self.block_data_['text'][i]
            line = self.block_data_['line'][i]
            lpos = self.block_data_['lpos'][i]
            
            for j in range(line):
                lx, ly, lw, lh = lpos[j]
                cv2.rectangle(self.sub_image_, (lx-1,ly-1), (lx+lw+1,ly+lh+1), (255,0,0), 1)

            cv2.rectangle(self.sub_image_, (x-3,y-3), (x+w+3,y+h+3), (0,0,255), 1)

        return
    

    def show_result(self, wait_time: int= 0) -> None:
        '''
        Show result image
        '''
        cv2.imshow("result", self.result_image_)

        cv2.waitKey(wait_time)
        cv2.destroyAllWindows()

        return
    

    def show_all(self, wait_time: int= 0) -> None:
        '''
        Show saved all image
        '''
        cv2.imshow("origin", self.image_)
        cv2.imshow("process", self.sub_image_)
        cv2.imshow("result", self.result_image_)

        cv2.waitKey(wait_time)
        cv2.destroyAllWindows()

        return
    

    def save_result(self, path:str =None) -> None:
        if path is None:
            file_name = self.save_path_ + self.image_path_[1:]
            cv2.imwrite(file_name, self.result_image_)
        else:
            cv2.imwrite(path, self.result_image_)
        return