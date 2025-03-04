import math

"""
This module gathers fragmented OCR words into sentences and groups the sentences into paragraphs.
Close words are combined to form sentences, 
and adjacent sentences are clustered into paragraphs based on the position of their starting words.
"""


def calculate_distance(x1: int, y1: int, x2: int, y2: int) -> float:
    """
    Calculate the Euclidean distance between two points.

    Args:
        x1 (int): X-coordinate of the first point.
        y1 (int): Y-coordinate of the first point.
        x2 (int): X-coordinate of the second point.
        y2 (int): Y-coordinate of the second point.

    Returns:
        float: The Euclidean distance.
    """
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def find_sentence(ocr_data: dict, threshold:int = 50) -> dict:
    """
    Group OCR words into sentences based on Tesseract output.

    For each word in the OCR result (with keys such as 'text', 'level', 'left', 'top', 'width', 'height', 'conf'),
    this function concatenates words that are close together (level 5) 
    and flushes the current sentence when a new line (level 4)
    is encountered or when a gap between words is detected.

    Args:
        ocr_data (dict): Dictionary containing Tesseract OCR results.
        threshold (int, optional): Confidence threshold for including words. Defaults to 50.

    Returns:
        dict: A dictionary containing the grouped sentence data with keys 'text', 'left', 'top', 'width', 'height', and 'fsize'.
    """
    result = {
        'text': [],
        'left': [],
        'top': [],
        'width': [],
        'height': [],
        'fsize': []
    }

    sentence_string = ''
    sentence_left = -1
    sentence_top = -1
    sentence_width = -1
    sentence_height = -1
    sentence_font_size = []

    def flush_sentence():
        nonlocal sentence_string, sentence_left, sentence_top, sentence_width, sentence_height, sentence_font_size

        if len(sentence_string.strip()) > 1:
            result['text'].append(sentence_string.strip())
            result['left'].append(sentence_left)
            result['top'].append(sentence_top)
            result['width'].append(sentence_width)
            result['height'].append(sentence_height)
            result['fsize'].append(int(sum(list(map(lambda x : x*len(sentence_font_size), sentence_font_size))) / len(sentence_font_size)**2))

            sentence_string = ''
            sentence_left = -1
            sentence_top = -1
            sentence_width = -1
            sentence_height = -1
            sentence_font_size = []

    num_words = len(ocr_data.get('text', []))
    for i in range(num_words):
        lv = ocr_data['level'][i]
        x = ocr_data['left'][i]
        y = ocr_data['top'][i]
        w = ocr_data['width'][i]
        h = ocr_data['height'][i]
        conf = int(ocr_data['conf'][i])
        word = ocr_data['text'][i].strip()

        # Initialize when OCR result level drops to 4
        if lv == 4:
            flush_sentence()

        # Save if the word's location is close to the previous word
        elif lv == 5 and conf > threshold and word:
            if sentence_left != -1 and sentence_left+sentence_width+w < x:
                flush_sentence()

            sentence_string += ' ' + word
            sentence_left = x if sentence_left==-1 else min(sentence_left, x)
            sentence_top = y if sentence_top==-1 else min(sentence_top, y)
            sentence_width = w if sentence_width==-1 else max(sentence_left+sentence_width, x+w)-sentence_left
            sentence_height = h if sentence_height==-1 else max(sentence_height, h)
            sentence_font_size.append(h)

    # Finally save the remaining value
    flush_sentence()

    return result


def make_sentence_block(sentence_data: dict, threshold: float = 1.5) -> dict:
    """
    Cluster adjacent sentences into paragraph blocks.

    This function groups sentences based on the distance between the starting positions of consecutive sentences.
    If the vertical distance between the blocks exceeds a threshold (based on the height of the current block)
    or if the height condition is met, the current paragraph block is flushed and a new block begins.

    Args:
        sentence_data (dict): Dictionary containing sentence data with keys 'text', 'left', 'top', 'width', 'height', and 'fsize'.
        threshold (float, optional): Threshold factor for grouping sentences. Defaults to 1.5.

    Returns:
        dict: A dictionary with paragraph data containing keys 'text', 'left', 'top', 'width', 'height', 'line', 'lpos', and 'fsize'.
    """
    result = {
        'text': [],
        'left': [],
        'top': [],
        'width': [],
        'height': [],
        'line': [],
        'lpos': [],
        'fsize': []
    }

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

    def flush_block():
        nonlocal block_string, block_left, block_top, block_width, block_height, line, line_pos, line_height
        result['text'].append(block_string)
        result['left'].append(block_left)
        result['top'].append(block_top)
        result['width'].append(block_width)
        result['height'].append(block_height)
        result['line'].append(line)
        result['lpos'].append(line_pos)
        result['fsize'].append(line_height)


    for i in range(1, len(sentence_data['text'])):
        text = sentence_data['text'][i]
        x = sentence_data['left'][i]
        y = sentence_data['top'][i]
        w = sentence_data['width'][i]
        h = sentence_data['height'][i]
        font_size = sentence_data['fsize'][i]

        distance = calculate_distance(block_left, block_top+block_height, x,y)

        # Construct a paragraph based on the distance between the positions of the starting words of the two sentences
        if h*threshold < base_height or distance > base_height*threshold:
            flush_block()

            block_string = text
            block_left = x
            block_top = y
            block_width = w
            block_height = h
            line = 1
            line_pos = [(block_left, block_top, block_width, block_height)]
            line_height = [font_size]
            base_height = h

        else:
            block_string += ' ' + text
            block_left = min(block_left, x)
            block_width = max(block_left+block_width, x+w)-block_left
            block_height = max(block_top+block_height, y+h)-block_top
            line += 1
            line_pos.append((x, y, w, h))
            line_height.append(font_size)

    # Finally save the remaining value
    flush_block()
    
    return result


def distribute_text(text: str, line_num: int, line_width: list) -> list:
    """
    Distribute a text string into multiple lines according to specified line widths.

    The text is split into words, and the number of words allocated to each line is determined
    by the proportional width of that line. The final line receives any remaining words.

    Args:
        text (str): The text to distribute.
        line_num (int): The number of lines to divide the text into.
        line_width (list): A list of integers representing the widths for each line.

    Returns:
        list: A list of strings, each representing a line of text.
    """
    tokens = text.split()
    total_tokens_length = len(tokens)
    total_width = sum(line_width)

    # Calculate the proportion of tokens for each line.
    line_ratios = [round(w / total_width, 2) for w in line_width]

    distributed_lines = []

    # Divide one sentence into multiple lines to match the line width ratio
    for i in range(line_num):
        if i == line_num - 1:
            line_tokens = tokens
            tokens = []
        else:
            num_tokens = int(total_tokens_length * line_ratios[i])
            line_tokens = tokens[:num_tokens]
            tokens = tokens[num_tokens:]

        distributed_lines.append(" ".join(line_tokens))
    
    return distributed_lines