import argostranslate
import argostranslate.package
import argostranslate.translate

'''
Source file for Argos translation
Used for offline translation
Argos Translate is Open-source offline translation library written in Python
https://github.com/argosopentech/argos-translate
'''

VALID_CHECK = False

def valid_check(package_num: str= None, \
                all: bool= False) -> None:

    global VALID_CHECK

    # load and check language pack
    argostranslate.package.update_package_index()
    available_packages = argostranslate.package.get_available_packages()
    
    # install all package (not recommended)
    if all:
        argostranslate.argospm.install_all_packages()

    elif package_num != None:
        argostranslate.package.install_from_path(available_packages[package_num].download())

    else:
        installed_languages = argostranslate.translate.get_installed_languages()
        install_lang = list(map(str, installed_languages))

        package_num = []
        for idx, pack_name in enumerate(available_packages):
            if str(pack_name).find("Korean") != -1:
                package_num.append(idx)

        if not('English' in install_lang and 'Korean' in install_lang):
            for num in package_num:
                argostranslate.package.install_from_path(available_packages[num].download())

    VALID_CHECK = True
    return


def text_translate(text: str, \
                   dest: str, \
                   src: str, \
                   detail: bool= False) -> str:

    global VALID_CHECK

    if not VALID_CHECK:
        valid_check()
    
    trans_text = argostranslate.translate.translate(text, src, dest)
    
    if detail:
        return (trans_text, text, dest, src, None, None)
    
    return trans_text