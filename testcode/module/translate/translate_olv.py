#!pip install googletrans==4.0.0-rc1
#!pip install argostranslate

import urllib.request
import googletrans
from googletrans import Translator
import argostranslate
import argostranslate.package
import argostranslate.translate


def check_online(url="https://www.google.com", detail=0):
    # 인터넷 연결 확인 함수
    # 파라미터
    #       url         : <str> : 연결할 사이트 문자열, 생략가능
    #       detail      : <int> : 출력표시, 생략가능
    # 리턴 : <bool>     : 온라인이면 True, 아니면 False
    is_online = False
    try:
        _response = urllib.request.urlopen(url)
        _r_s = _response.status

        if 100 <= _r_s <= 199:
            is_online = True
            if detail >= 1:
                print(f"HTTP status : {_r_s} - Information responses")
                print("web request confirm, internet is connected")
        elif 200 <= _r_s <= 299:
            is_online = True
            if detail >= 1:
                print(f"HTTP status : {_r_s} - Successful responses")
                print("web request confirm, internet is connected")
        elif 300 <= _r_s <= 399:
            is_online = True
            if detail >= 1:
                print(f"HTTP status : {_r_s} - Redirection messages")
                print("web request confirm, internet is connected")
        elif 400 <= _r_s <= 499:
            is_online = False
            if detail >= 1:
                print(f"HTTP status : {_r_s} - Client error responses")
                print("web request fail, change offline mode")
        elif 500 <= _r_s <= 599:
            is_online = False
            if detail >= 1:
                print(f"HTTP status : {_r_s} - Server error responses")
                print("web request fail, change offline mode")
        else:
            is_online = False
            if detail >= 1:
                print("Unkown status, requst fail, change offline mode")

    except:
        is_online = False
        if detail >= 1:
            print("web request fail, change offline mode")

    return is_online



def vaild_argostranslate_check(package_num=None, all=False):
    argostranslate.package.update_package_index()
    available_packages = argostranslate.package.get_available_packages()
    
    if all:
        argostranslate.argospm.install_all_packages()

    elif package_num != None:
        argostranslate.package.install_from_path(available_packages[package_num].download())

    else:
        installed_languages = argostranslate.translate.get_installed_languages()
        install_lang = list(map(str, installed_languages))

        if not('English' in install_lang and 'Korean' in install_lang):
            argostranslate.package.install_from_path(available_packages[26].download())
            argostranslate.package.install_from_path(available_packages[48].download())



def text_translate_offline(text, dest, src, detail=0):
    vaild_argostranslate_check()
    
    trans_text = argostranslate.translate.translate(text, src, dest)
    
    if detail > 1:
        return (trans_text, text, dest, src, None, None)
    elif detail == 1:
        return (trans_text, text, dest, src)
    else:
        return trans_text



def text_translate(text, dest, src=None, online=True, detail=0):
    # 문장 번역 함수
    # 파라미터
    #       text        : <str> : 번역할 문장
    #       dest        : <str> : 번역 목표 언어
    #       src         : <str> : 입력 문장의 언어
    #       online      : <bool>: 인터넷 연결 여부
    #       detail      : <int> : 출력값의 상세 여부
    # 리턴  
    #       detail=0    : <str>     : 번역된 문장
    #       detail=1    : <tuple>   : (번역된문장, 원본문장, 번역언어, 원본언어)
    #       detail=2    : <tuple>   : (번역된문장, 원본문장, 번역언어, 원본언어, 번역발음, 원본발음)
    
    if online:
        translator = Translator()
    else:
        if src==None:
            raise Exception("offline mode does not support language detection")
        return text_translate_offline(text, dest, src, detail)

    if src == None:
        translated = translator.detect(text)
        src = translated.lang
    
    translated = translator.translate(text=text, dest=dest, src=src)

    result = translated._response
    if str(result)[11:14] == '200':
        trans_text = translated.text
        trans_pri = translated.pronunciation
        origin_pri = translated.extra_data['origin_pronunciation']
    else:
        raise Exception("HTTP response fail")

    if detail > 1:
        return (trans_text, text, dest, src, trans_pri, origin_pri)
    elif detail == 1:
        return (trans_text, text, dest, src)
    else:
        return trans_text
    

'''
# 사용법 가이드 (예외처리 권장)
import translate_olv

print(translate_olv.check_online())

tk = '안녕하세요? 이 문장은 임시 예제 문장입니다! 번역기의 성능을 시험하려는 문장으로, 번역 확인을 위해 사용됩니다.'
k = translate_olv.text_translate(tt, 'en')
print(k)

te = 'hello?This sentence is a temporary example sentence!It is a sentence to test the performance of the translator and is used to check the translation.'
k = translate_olv.text_translate(tt, 'ko')
print(k)

#출력 :
#True
#hello?This sentence is a temporary example sentence!It is a sentence to test the performance of the translator and is used to check the translation.
#안녕하세요? 이 문장은 임시 예제 문장입니다! 번역기의 성능을 시험하려는 문장으로, 번역 확인을 위해 사용됩니다.
'''