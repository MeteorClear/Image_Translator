import urllib.request
import math

'''
source code of miscellaneous functions
'''

def check_online(url:str="https://www.google.com", detail:bool=False) -> bool:
    '''
    Check Internet connection, 
    Using web page responses
    '''
    is_online = False

    try:
        response = urllib.request.urlopen(url)
        status = response.status

        if 100 <= status <= 199:
            is_online = True
            if detail:
                print(f"HTTP status : {status} - Information responses")
                print("web request confirm, internet is connected")
        elif 200 <= status <= 299:
            is_online = True
            if detail:
                print(f"HTTP status : {status} - Successful responses")
                print("web request confirm, internet is connected")
        elif 300 <= status <= 399:
            is_online = True
            if detail:
                print(f"HTTP status : {status} - Redirection messages")
                print("web request confirm, internet is connected")
        elif 400 <= status <= 499:
            if detail:
                print(f"HTTP status : {status} - Client error responses")
                print("web request fail, change offline mode")
        elif 500 <= status <= 599:
            if detail:
                print(f"HTTP status : {status} - Server error responses")
                print("web request fail, change offline mode")
        else:
            if detail:
                print("Unkown status, requst fail, change offline mode")

    except:
        if detail:
            print("web request fail, change offline mode")

    return is_online


def calculate_distance(x1: int, y1: int, x2: int, y2: int) -> float:
    '''
    Find Euclidean distance, 
    Using 2 coordinates
    '''
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def print_dict_data(dict_data: dict) -> None:
    '''
    Just console print dictionary
    '''
    for i in dict_data:
        print(i, dict_data[i])
    return