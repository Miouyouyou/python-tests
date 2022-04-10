import logging
import os

from argparse import ArgumentParser, RawDescriptionHelpFormatter
from gooey import GooeyParser

logging.basicConfig(level=logging.DEBUG)

def list_dirs(from_dir=".", containing_files=[]) -> list:
    entries = os.scandir(from_dir)
    dirs = []
    for entry in entries:
        if entry.is_dir():
            directory = entry.name
            all_files_present = True
            for file_to_search in containing_files:
                checked_file_path = os.path.join(os.path.join(from_dir,directory), file_to_search)
                file_exist = os.path.exists(checked_file_path)
                print(f'Does {checked_file_path} exist ? {file_exist}')
                all_files_present &= file_exist
            
            if all_files_present:
                dirs.append(directory)
    return dirs

def main():
    available_dockers = list_dirs('softwares', ['docker-compose.yml'])
    images_list = "\n\t" + "\n\t".join(available_dockers)
    parser = ArgumentParser(description='Armbian docker installation module', formatter_class=RawDescriptionHelpFormatter, epilog='IMAGES :' + images_list)
    parser.add_argument('--install', nargs='+', metavar='IMAGE', choices=available_dockers, help='Add docker installations')
    args = parser.parse_args()
    if args.install == None or len(args.install) == 0:
        args = GooeyParser(add_help=False, parents=[parser]).parse_args()
        print(args)

main()
