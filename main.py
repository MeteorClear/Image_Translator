import argparse
import time
import sys

sys.path.append(".\\source")
from source import image_processing

def run(args):
    image_translator = image_processing.ProcessingBlock(
        image_path = args.file,
        save_path = args.save,
        src_lang = args.src,
        dest_lang = args.dest,
        font_type = args.font,
        translator_mode = args.translator
    )
    image_translator.ocr_process()
    image_translator.recollection_text()
    image_translator.build_blocks()
    image_translator.processing_run()
    image_translator.draw_process()

    if args.result == 0:
        image_translator.show_result()

    elif args.result == 1:
        image_translator.save_result()

    elif args.result == 2:
        image_translator.save_result()
        image_translator.show_result()

    elif args.result == 3:
        image_translator.save_result()
        image_translator.show_all()

    return

def main():
    parser = argparse.ArgumentParser(description="This program translates the image")

    parser.add_argument("file", type=str, help="Path to the file")
    parser.add_argument("--save", type=str, default=".\\result", help="Path to save")
    parser.add_argument("--src", type=str, default="en", help="The source language")
    parser.add_argument("--dest", type=str, default="ko", help="The target language")
    parser.add_argument("--font", type=str, default="fonts\\gulim.ttc", help="Path to font")
    parser.add_argument("--translator", type=str, default="argos", help="Translator name to use")
    parser.add_argument("--result", type=int, default="0", help="Result options, 0: only show result, 1: save only, 2: save and show, 3: save all process")

    args = parser.parse_args()

    run(args)

    return

if __name__ == "__main__":
    main()
