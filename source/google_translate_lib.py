import googletrans

'''
Source file for google translation
Not likely to work
https://pypi.org/project/googletrans/
'''

def text_translate(text: str, dest: str, src:str=None, detail:bool=False) -> str:
    '''
    Translate text, 
    Using google translator, 
    Internet connection required, 
    https://pypi.org/project/googletrans/
    '''
    translator = googletrans.Translator()

    # Estimate by language detection if the source language is not entered
    if src == None:
        translated = translator.detect(text)
        src = translated.lang
    
    translated = translator.translate(text=text, dest=dest, src=src)

    result = translated._response

    # Work HTTP response results are 200
    # There may be a better way, but it works
    if str(result)[11:14] == '200':
        trans_text = translated.text
        trans_pronunciation = translated.pronunciation
        origin_pronunciation = translated.extra_data['origin_pronunciation']
        
    else:
        raise Exception("HTTP response fail")

    if detail:
        return (trans_text, text, dest, src, trans_pronunciation, origin_pronunciation)
    
    return trans_text