import argostranslate
import argostranslate.package
import argostranslate.translate

"""
Source file for Argos translation.
Used for offline translation.
Argos Translate is Open-source offline translation library written in Python.
https://github.com/argosopentech/argos-translate
"""

# Global flag: check for installed language pack.
VALID_CHECK = False


def find_package_index(package_language: str) -> list:
    """
    Find the indexes of available language packages that match the given language string.

    Args:
        package_language (str): The language string to search for in the available packages.

    Returns:
        list: A list of indexes where the available package's name includes the package_language.
    """
    available_packages = argostranslate.package.get_available_packages()
    package_index = []

    for idx, pack_name in enumerate(available_packages):
        if str(pack_name).find(package_language) != -1:
            package_index.append(idx)

    return package_index


def valid_check(package_language: str= None, install_all: bool= False) -> None:
    """
    Validate and install the required language packages for translation.

    Args:
        package_language (str, optional): The language for which packages should be installed.
        install_all (bool, optional): If True, installs all available language packages.

    Raises:
        Exception: If an error occurs during the package installation process.
    """
    global VALID_CHECK

    try:
        argostranslate.package.update_package_index()
        available_packages = argostranslate.package.get_available_packages()
        installed_languages = list(map(str, argostranslate.translate.get_installed_languages()))
        
        # Install all available packages. (not recommended)
        if install_all:
            argostranslate.argospm.install_all_packages()

        # Install packages for the specified language.
        elif package_language is not None:
            package_index = find_package_index(package_language)

            for num in package_index:
                argostranslate.package.install_from_path(available_packages[num].download())

        # Default behavior: install Korean package.
        else:
            package_index = find_package_index("Korean")

            if not('English' in installed_languages and 'Korean' in installed_languages):
                for num in package_index:
                    argostranslate.package.install_from_path(available_packages[num].download())

        # Update global flag, installation is complete.
        VALID_CHECK = True

    except Exception as e:
        raise Exception(f"Error during valid_check: {e}")
    
    return


def text_translate(text: str, dest: str, src: str, detail: bool= False) -> str:
    """
    Translate a given text from the source language to the destination language.

    Args:
        text (str): The text to be translated.
        dest (str): The destination language code.
        src (str): The source language code.
        detail (bool, optional): If True, returns a tuple with detailed translation information

    Returns:
        str/tuple: The translated text if detail is False, otherwise a tuple with detailed translation info.

    Raises:
        Exception: If an error occurs during the translation process.
    """
    global VALID_CHECK

    if not VALID_CHECK:
        valid_check()
    
    trans_text = argostranslate.translate.translate(text, src, dest)
    
    if detail:
        return (trans_text, text, dest, src, None, None)
    
    return trans_text