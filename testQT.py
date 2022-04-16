import logging
import os
import sys

from argparse import ArgumentParser, RawDescriptionHelpFormatter
from gooey import Gooey
from renderers.qt.widgets import SelectionMenu, provide_user_choice

logging.basicConfig(level=logging.DEBUG)

def list_dirs(from_dir=".", containing_files=[]) -> list:
    entries = None
    try:
        entries = os.scandir(from_dir)
    except:
        return []
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

if __name__ == '__main__':
    # TODO : Parse from configuration file
    default_templates_dir = './softwares'
    default_install_dir = '/opt/armbian/installed/docker'
    available_dockers = list_dirs(default_templates_dir, ['docker-compose.yml'])
    installed_dockers = list_dirs(default_install_dir, ['docker-compose.yml'])
    installed_dockers.append('haproxy')
    images_list = '\n\t' + '\n\t'.join(available_dockers)
    parser = ArgumentParser(description='Armbian docker installation module', formatter_class=RawDescriptionHelpFormatter, epilog='IMAGES :' + images_list)
    parser.add_argument('--install', nargs='+', metavar='IMAGE', choices=available_dockers, help='Add docker installations')
    parser.add_argument('--templates-dir', nargs='?', default=default_templates_dir, help='Directory path to list templates from')
    parser.add_argument('--install-dir', nargs='?', default=default_install_dir, help='Directory path where docker images are installed')
    args = parser.parse_args()
    print(args)
    
    install_dir = args.install_dir
    templates_dir = args.templates_dir
    
    print(install_dir)
    print(templates_dir)
    
    if args.install == None or len(args.install) == 0:
        try:
            installed_set = set(installed_dockers)
            selected, unselected = provide_user_choice(available_dockers, installed_set)
            available_set = set(available_dockers)
            
            
            print(f'selected: {selected} - unselected: {unselected}')
            to_install = (selected - installed_set)
            to_remove = (installed_set & unselected)
            print(f'Install : {to_install}, Remove: {to_remove}')
        except Exception as e:
            print("An exception occured")
            print(e)
        #    print(args.install)
            parser.print_help()


