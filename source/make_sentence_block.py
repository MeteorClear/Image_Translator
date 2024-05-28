import sub_func

'''
Source code that gathers fragmented words to form sentences and paragraphs
Close words are grouped together to form a sentence
Create a paragraph by grouping the surrounding sentences based on the position of the starting word of the sentence
'''

def find_sentence(ocr_data: dict, threshold:int=50) -> dict:
    '''
    collection of words into sentences, 
    Using Tesserect result
    '''
    result = dict()
    result['text'] = []
    result['left'] = []
    result['top'] = []
    result['width'] = []
    result['height'] = []
    result['fsize'] = []

    sentence_string = ''
    sentence_left = -1
    sentence_top = -1
    sentence_width = -1
    sentence_height = -1
    sentence_fsize = []

    for i in range(len(ocr_data['text'])):
        lv = ocr_data['level'][i]
        x = ocr_data['left'][i]
        y = ocr_data['top'][i]
        w = ocr_data['width'][i]
        h = ocr_data['height'][i]

        conf = int(ocr_data['conf'][i])
        text = ocr_data['text'][i]
        text = text.strip()

        # Initialize when OCR result level drops to 4
        if lv == 4:
            if len(sentence_string.strip()) > 1:
                result['text'].append(sentence_string.strip())
                result['left'].append(sentence_left)
                result['top'].append(sentence_top)
                result['width'].append(sentence_width)
                result['height'].append(sentence_height)
                result['fsize'].append(int(sum(list(map(lambda x : x*len(sentence_fsize), sentence_fsize))) / len(sentence_fsize)**2))

                sentence_string = ''
                sentence_left = -1
                sentence_top = -1
                sentence_width = -1
                sentence_height = -1
                sentence_fsize = []

        # Save if the word's location is close to the previous word
        elif lv == 5:
            if conf > threshold and len(text) > 0:
                if sentence_left != -1 and sentence_left+sentence_width+w < x:
                    result['text'].append(sentence_string.strip())
                    result['left'].append(sentence_left)
                    result['top'].append(sentence_top)
                    result['width'].append(sentence_width)
                    result['height'].append(sentence_height)
                    result['fsize'].append(int(sum(list(map(lambda x : x*len(sentence_fsize), sentence_fsize))) / len(sentence_fsize)**2))

                    sentence_string = ''
                    sentence_left = -1
                    sentence_top = -1
                    sentence_width = -1
                    sentence_height = -1
                    sentence_fsize = []

                    sentence_string += ' ' + text
                    sentence_left = x if sentence_left==-1 else min(sentence_left, x)
                    sentence_top = y if sentence_top==-1 else min(sentence_top, y)
                    sentence_width = w if sentence_width==-1 else max(sentence_left+sentence_width, x+w)-sentence_left
                    sentence_height = h if sentence_height==-1 else max(sentence_height, h)
                    sentence_fsize.append(h)

                # Save words if they are consecutive
                else:
                    sentence_string += ' ' + text
                    sentence_left = x if sentence_left==-1 else min(sentence_left, x)
                    sentence_top = y if sentence_top==-1 else min(sentence_top, y)
                    sentence_width = w if sentence_width==-1 else max(sentence_left+sentence_width, x+w)-sentence_left
                    sentence_height = h if sentence_height==-1 else max(sentence_height, h)
                    sentence_fsize.append(h)

    # Finally save the remaining value
    if len(sentence_string.strip()) > 1:
        result['text'].append(sentence_string.strip())
        result['left'].append(sentence_left)
        result['top'].append(sentence_top)
        result['width'].append(sentence_width)
        result['height'].append(sentence_height)
        result['fsize'].append(int(sum(list(map(lambda x : x*len(sentence_fsize), sentence_fsize))) / len(sentence_fsize)**2))

    return result


def make_sentence_block(sentence_data: dict, threshold:float=1.5) -> dict:
    '''
    Gather adjacent sentences and cluster them into paragraphs
    '''
    result = dict()
    result['text'] = []
    result['left'] = []
    result['top'] = []
    result['width'] = []
    result['height'] = []
    result['line'] = []
    result['lpos'] = []
    result['fsize'] = []

    if len(sentence_data['text']) < 1:
        return result
    
    block_string = sentence_data['text'][0]
    block_left = sentence_data['left'][0]
    block_top = sentence_data['top'][0]
    block_width = sentence_data['width'][0]
    block_height = sentence_data['height'][0]
    line = 1
    line_pos = [(block_left, block_top, block_width, block_height)]
    line_height = [sentence_data['fsize'][0]]
    base_height = block_height

    for i in range(1, len(sentence_data['text'])):
        text = sentence_data['text'][i]
        x = sentence_data['left'][i]
        y = sentence_data['top'][i]
        w = sentence_data['width'][i]
        h = sentence_data['height'][i]
        fsize = sentence_data['fsize'][i]

        distance = sub_func.calculate_distance(block_left, block_top+block_height, x,y)

        # Construct a paragraph based on the distance between the positions of the starting words of the two sentences
        if h*threshold < base_height or distance > base_height*threshold:
            result['text'].append(block_string)
            result['left'].append(block_left)
            result['top'].append(block_top)
            result['width'].append(block_width)
            result['height'].append(block_height)
            result['line'].append(line)
            result['lpos'].append(line_pos)
            result['fsize'].append(line_height)

            block_string = text
            block_left = x
            block_top = y
            block_width = w
            block_height = h
            line = 1
            line_pos = [(block_left, block_top, block_width, block_height)]
            line_height = [fsize]
            base_height = h

        else:
            block_string += ' ' + text
            block_left = min(block_left, x)
            block_width = max(block_left+block_width, x+w)-block_left
            block_height = max(block_top+block_height, y+h)-block_top
            line += 1
            line_pos.append((x, y, w, h))
            line_height.append(fsize)

    # Finally save the remaining value
    result['text'].append(block_string)
    result['left'].append(block_left)
    result['top'].append(block_top)
    result['width'].append(block_width)
    result['height'].append(block_height)
    result['line'].append(line)
    result['lpos'].append(line_pos)
    result['fsize'].append(line_height)
    
    return result


def distribute_text(text: str, line_num: int, line_width: list) -> list:
    '''
    Split one string to number of line and widths of each line
    '''
    token = text.split()
    token_len = len(token)

    # Find proportions proportional to line width
    line_rato = list(map(lambda x : round(x/sum(line_width), 2), line_width))

    div_text = []

    # Divide one sentence into multiple lines to match the line width ratio
    for i in range(line_num):
        sentence_buffer = ''
        max_voca = int(token_len * line_rato[i])

        if i == (line_num-1):
            while len(token) > 0:
                sentence_buffer += token.pop(0) + ' '
        else:
            for i in range(max_voca):
                if len(token) > 0:
                    sentence_buffer += token.pop(0) + ' '

        div_text.append(sentence_buffer)
    
    return div_text