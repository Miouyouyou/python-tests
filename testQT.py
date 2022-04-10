import logging
import os
import sys

from argparse import ArgumentParser, RawDescriptionHelpFormatter
from gooey import Gooey
from PyQt5.QtWidgets import QAbstractItemView, QApplication, QWidget, QPushButton, QListWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import pyqtSlot

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


class ListWidget(QListWidget):
    pass

class SelectionMenu(QWidget):
    def __init__(self, title, choices=[]):
        super().__init__()
        self.title = title
        self.left = 10
        self.top = 10
        self.width = 320
        self.height = 200
        self.choices = choices
        self.initUI(choices)
    
    def cb_selection_changed(self):
        items = []
        for item in self.selectionList.selectedItems():
            items.append(item.text())
        self.select_button.setEnabled(len(items) > 0)
        self.items = items
    
    def cb_cancel(self):
        sys.exit(1)
        
    def cb_select(self):
        print(self.items)
        sys.exit(0)
    
    def initUI(self, choices=[]):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        
        layout = QVBoxLayout(self)
        
        selectionList = ListWidget(self)
        for choice in choices:
            selectionList.addItem(choice)
        selectionList.setSelectionMode(QAbstractItemView.MultiSelection)
        self.selectionList = selectionList
        selectionList.itemSelectionChanged.connect(self.cb_selection_changed)
        layout.addWidget(selectionList)
        
        buttonsLayout = QHBoxLayout(self)
        button = QPushButton('Cancel', self)
        button.setToolTip('Cancel the operation')
        button.clicked.connect(self.cb_cancel)
        buttonsLayout.addWidget(button)
        
        button = QPushButton('Select', self)
        button.setToolTip('This is an example button')
        button.clicked.connect(self.cb_select)
        button.setEnabled(False)
        buttonsLayout.addWidget(button)
        self.select_button = button
        
        layout.addLayout(buttonsLayout)
        self.setLayout(layout)
        
        self.show()

    @pyqtSlot()
    def on_click(self):
        print('PyQt5 button click')


def provide_user_choice(choices=[]):
    app = QApplication(sys.argv)
    ex = SelectionMenu(title="Armbian docker installation module", choices=choices)
    app.exec_()
    return ex.items
    

if __name__ == '__main__':
    available_dockers = list_dirs('softwares', ['docker-compose.yml'])
    images_list = "\n\t" + "\n\t".join(available_dockers)
    parser = ArgumentParser(description='Armbian docker installation module', formatter_class=RawDescriptionHelpFormatter, epilog='IMAGES :' + images_list)
    parser.add_argument('--install', nargs='+', metavar='IMAGE', choices=available_dockers, help='Add docker installations')
    args = parser.parse_args()
    print(args)
    if args.install == None or len(args.install) == 0:
        try:
            args.install = provide_user_choice(available_dockers)
        except:
            parser.print_help()
    
    print(args.install)

