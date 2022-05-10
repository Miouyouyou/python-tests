import logging
import os
from pathlib import Path
import shutil
import subprocess
import sys

from argparse import ArgumentParser, RawDescriptionHelpFormatter
from renderers.qt.widgets import SelectionMenu, provide_user_choice

logging.basicConfig(level=logging.DEBUG)

config = {
    'templates_dir': '/usr/share/armbian/configurator/modules/softwares',
    'install_dir': '/opt/armbian/docker',
    'install': [],
    'remove': []
}

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

class Module:
    def __init__(self, configuration):
        self.configuration = configuration
        configuration["install_dir"] = Path(configuration("install_dir"))
        configuration["templates_dir"] = Path(configuration["templates_dir"))

    def installed_path(self, service_name:str):
        service_path = (configuration["install_dir"] / service_name)


    def docker_install(self, configuration=None):
        configuration = self.configuration if configuration == None else configuration
        if len(configuration["install"]) == 0:
            print('No docker to install')
            return
        install_path = configuration["install_dir"]
        templates_path = configuration["templates_dir"]
        try:
            install_path.mkdir( mode=0o755, parents=True, exist_ok=True )
        except Exception as e:
            print(f'mkdir -p {install_path} failed: ')
            print(e)
            sys.exit(1)

        print(configuration)
        for selected_dir in configuration["install"]:
            shutil.copytree((templates_path / selected_dir), (install_path / selected_dir))

    def docker_remove(self, configuration=None):
        configuration = self.configuration if configuration == None else configuration
        if len(configuration["remove"]) is 0:
            print('No docker to remove')
            return

        for docker_compose_service in configuration["remove"]:
            remove_path = self.installed_path(docker_compose_service)
            if remove_path.exists():
                try:
                    shutil.rmtree(remove_path)
                except Exception as e:
                    print(f'Could not delete {remove_path}')
                    continue
            else:
                print(f'{remove_path} does not exist. Skipping {docker_compose_servivce}')
                continue

    def start_script(self, script="", args=[]):
        return subprocess.Popen([script] + args)

    def start_service(self, docker_service_name):
        service_path = self.installed_path(docker_service_name)
        if service_path.exists():
            self.start_script('./scripts/start_service.sh', [service_path])

    def stop_service(self, docker_service_name):
        service_path = self.installed_path(docker_service_name)
        if service_path.exists():
            self.start_script('./scripts/stop_service.sh', [service_path])

    def run(self):

        self.docker_remove()
        self.docker_install()

def module_payload(configuration):
    docker_install(configuration["install"])


if __name__ == '__main__':
    # TODO : Parse from configuration file
    available_dockers = list_dirs(config["templates_dir"], ['docker-compose.yml'])
    installed_dockers = list_dirs(config["install_dir"], ['docker-compose.yml'])
    images_list = '\n\t' + '\n\t'.join(available_dockers)
    parser = ArgumentParser(description='Armbian docker installation module', formatter_class=RawDescriptionHelpFormatter, epilog='IMAGES :' + images_list)
    parser.add_argument('--install', nargs='+', metavar='IMAGE', choices=available_dockers, help='Add docker installations')
    parser.add_argument('--start', nargs='+', metavar='IMAGE', choices=installed_dockers, help='Start selected installed docker-compose images')
    parser.add_argument('--stop', nargs='+', metavar='IMAGE', choices=installed_dockers, help='Stop selected installed docker-compose images')
    parser;add_argument('--edit', nargs=1, metavar='IMAGE', choices=installed_dockers, help='Edit an installed docker-compose image YAML file')
    parser.add_argument('--templates-dir', nargs='?', default=config['templates_dir'], help='Directory path to list templates from')
    parser.add_argument('--install-dir', nargs='?', default=config['install_dir'], help='Directory path where docker images are installed')
    args = parser.parse_args()
    
    install_dir = args.install_dir
    templates_dir = args.templates_dir
    
    if args.install == None or len(args.install) == 0:
        try:
            installed_set = set(installed_dockers)
            selected, unselected = provide_user_choice(available_dockers, installed_set)
            available_set = set(available_dockers)
            
            print(f'selected: {selected} - unselected: {unselected}')
            to_install = (selected - installed_set)
            to_remove = (installed_set & unselected)
            print(f'Install : {to_install}, Remove: {to_remove}')
            config["install"] = to_install
            config["remove"] = to_remove
            Module(config).run()

        except Exception as e:
            parser.print_help()
            print(f'A problem araised {e}')

