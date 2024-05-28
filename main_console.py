import gc
import time
import glob

import cv2
import numpy as np



print("                        IMAGE TRANSLATOR                       ")


import sys
sys.path.append(".\\source")

print("MODULE LOADING ...")

from source import image_processing
print("IP MODULE LOADING COMPLETE")

from source import text_to_speech
print("TTS MODULE LOADING COMPLETE")



print()
print("DATA INITIALIZING ... ", end='')

SRC_LANG = "en"
DEST_LANG = "ko"
IMAGE_PATH = None
SAVE_PATH = ".\\result"
FONT_TYPE = "fonts\\gulim.ttc"

TESTDATA = glob.glob('.\\testdata\\*.jpg')
DATA_SIZE = len(TESTDATA)

IP = None
TTS = None
def flush():
    global IP, TTS
    try:
        del(IP)
        del(TTS)
        gc.collect()
    except:
        pass
    IP = None
    TTS = None
    return

print("COMPLETE")
print()



while True:
    check_ip = "Undefined" if IP is None else "Defined"
    check_tts = "Undefined" if TTS is None else "Defined"
    print()
    print(f"PROCESSING BLOCK : {check_ip} , TTS BLOCK : {check_tts}")
    print(f"SELECTED IMAGE PATH = {IMAGE_PATH}")
    print(f"SOURCE LANGUAGE = {SRC_LANG} , TARGET LANGUAGE = {DEST_LANG}")
    print(f"check commands by 'help'")


    # input command
    while True:
        print(f">>> ",end='')
        COMMAND = list(map(lambda x : x.lower(), input().split()))
        if len(COMMAND) != 0:
            break
    

    # help command section
    if COMMAND[0] == "help":
        print("exit\t\tterminate program")
        print("flush\t\tflush all buffer space")
        print("run [image path]\t\tPerform image translation with [image path] or existing path")
        print("tts [play|stop]\t\tPlay or stop tts voice")
        print("set [path|source|target] [value]\t\tSet the [path|source|target] to [value]")
        # end of help command


    # run command section
    if COMMAND[0] == "run":
        try:
            if len(COMMAND) == 1 and IMAGE_PATH is None:
                print("HELP COMMAND : run [image path]")

            if len(COMMAND) > 1:
                if IMAGE_PATH is not None:
                    flush()
                IMAGE_PATH = COMMAND[1]
            
            if IMAGE_PATH is None:
                print(f"! SELECT IMAGE PATH !")
                continue

            try:
                if IP is None:
                    start_time = time.time()
                    print(f"::LOG:: start image translate")
                    IP = image_processing.ProcessingBlock(image_path = IMAGE_PATH, \
                                                            save_path = SAVE_PATH, \
                                                            dest_lang = DEST_LANG, \
                                                            src_lang = SRC_LANG, \
                                                            font_type = FONT_TYPE)
                    
                    print(f"::LOG:: OCR processing ... ",end='')
                    IP.ocr_process()
                    print(f"done.")

                    print(f"::LOG:: reassembly processing ... ",end='')
                    IP.recollection_text()
                    IP.build_blocks()
                    print(f"done.")

                    print(f"::LOG:: translate and overwrite processing ... ",end='')
                    IP.processing_run()
                    IP.draw_process()
                    print(f"done.")
                    end_time = time.time()

                    print(f"::LOG:: COMPLETE ALL PROCESS, TOTAL RUN TIME = {end_time-start_time:.2f} sec")
                    IP.show_all()
                else:
                    print(f"::LOG:: find previous data, show Image")
                    IP.show_all()

            except Exception as e:
                print(f"ERROR SYSTEM INTERRUPT")
                print(f"ERROR MESSAGE = {e}")

                flush()
                IMAGE_PATH = None

                continue
        except Exception as e:
            print(f"ERROR SYSTEM INTERRUPT")
            print(f"ERROR MESSAGE = {e}")

            flush()
            IMAGE_PATH = None

            continue
        # end of run command


    # set command section
    if COMMAND[0] == "set":
        try:
            if len(COMMAND) < 3:
                print("HELP COMMAND : set [path|source|target] [value]")
                continue

            if COMMAND[1] == "path":
                IMAGE_PATH = COMMAND[2]

            elif COMMAND[1] == "source":
                SRC_LANG = COMMAND[2]

            elif COMMAND[1] == "target":
                DEST_LANG = COMMAND[2]

            else:
                print("! unknown command !")
                print("HELP COMMAND : set [path|source|target] [value]")
        except Exception as e:
            print(f"ERROR SYSTEM INTERRUPT")
            print(f"ERROR MESSAGE = {e}")
            continue
        # end of set command

    
    # tts command section
    if COMMAND[0] == "tts":
        try:
            if len(COMMAND) < 2:
                print("HELP COMMAND : tts [play|stop]")
                continue

            if IP is None:
                print("! Image translation must be performed first !")
                continue

            if COMMAND[1] == "stop":
                if TTS is None:
                    print("can not stop, tts block is not defined")
                    continue
                else:
                    TTS.tts_stop()
            elif COMMAND[1] == "play":
                if TTS is None:
                    start_time = time.time()
                    print(f"::LOG:: TTS build start")
                    TTS = text_to_speech.TTSBlock(dict_data=IP.block_data_, \
                                                src_lang=SRC_LANG, \
                                                dest_lang=DEST_LANG)
                    
                    print(f"::LOG:: build and translate script ... ",end='')
                    TTS.translate_script()
                    print(f"done.")

                    print(f"::LOG:: build tts file ... ",end='')
                    TTS.run_tts()
                    print(f"done.")

                    end_time = time.time()
                    print(f"::LOG:: COMPLETE ALL PROCESS, TOTAL RUN TIME = {end_time-start_time:.2f} sec")
                else:
                    print(f"::LOG:: find previous data, show Image")
                    TTS.tts_play()
        except Exception as e:
            print(f"ERROR SYSTEM INTERRUPT")
            print(f"ERROR MESSAGE = {e}")
            TTS = None
            continue
        # end of tts command


    # flush command section
    if COMMAND[0] == "flush":
        try:
            flush()
            SRC_LANG = "en"
            DEST_LANG = "ko"
            IMAGE_PATH = None
            print("flush all buffer")
        except Exception as e:
            print(f"ERROR SYSTEM INTERRUPT")
            print(f"ERROR MESSAGE = {e}")
            continue
        # end of flush command

    
    if COMMAND[0] == "exit":
        print("system terminate")
        break


    