import argostranslate
import argostranslate.package
import argostranslate.translate

'''
Source file for Argos translation
Used for offline translation
Argos Translate is Open-source offline translation library written in Python
https://github.com/argosopentech/argos-translate
'''

# global flag: check for installed language pack
VALID_CHECK = False


def find_package_index(package_language: str) -> list:
    available_packages = argostranslate.package.get_available_packages()
    package_index = []

    for idx, pack_name in enumerate(available_packages):
        if str(pack_name).find(package_language) != -1:
            package_index.append(idx)

    return package_index


def valid_check(package_language: str= None, \
                install_all: bool= False) -> None:

    global VALID_CHECK

    try:
        argostranslate.package.update_package_index()
        available_packages = argostranslate.package.get_available_packages()
        installed_languages = argostranslate.translate.get_installed_languages()
        installed_languages_list = list(map(str, installed_languages))
        
        # install all package (not recommended)
        if install_all:
            argostranslate.argospm.install_all_packages()

        elif package_language != None:
            package_index = find_package_index(package_language)

            for num in package_index:
                argostranslate.package.install_from_path(available_packages[num].download())

        else:
            package_index = find_package_index("Korean")

            if not('English' in installed_languages_list and 'Korean' in installed_languages_list):
                for num in package_num:
                    argostranslate.package.install_from_path(available_packages[num].download())

        # flag update
        VALID_CHECK = True

    except Exception as e:
        raise Exception(f"Error during valid_check: {e}")
    
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