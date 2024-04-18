import os
import shutil
import sys
import time

import qdarkstyle
from PySide6.QtCore import QTimer, QSize, Qt
from PySide6.QtGui import QAction
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QMenu,
    QSystemTrayIcon,
    QWidget,
    QGridLayout,
    QTabWidget,
    QLabel,
    QFileDialog,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QVBoxLayout,
    QPushButton,
)
from loguru import logger

logger.add(
    "dankutility.log", rotation="100 MB", compression="zip"
)  # Automatically rotate too big file


class ModsBackupUI(QWidget):
    def __init__(self):
        super().__init__()
        # initialize the mods folder
        self.SIMS4_MOD_FOLDERNAME_DEFAULT = os.path.expanduser(
            os.path.join("~", "Documents", "Electronic Arts", "The Sims 4", "Mods")
        )
        self.SIMS4_BACKUP_FOLDERNAME_DEFAULT = os.path.expanduser(
            os.path.join("~", "Documents", "Electronic Arts", "The Sims 4")
        )
        # mod foldername
        self.sims4_mod_folderName = ""
        # backup foldername
        self.sims4_backup_folderName = ""
        # get all mod related info
        self.checkDefaultFolders = os.path.exists(
            self.SIMS4_MOD_FOLDERNAME_DEFAULT
        ) and os.path.exists(self.SIMS4_BACKUP_FOLDERNAME_DEFAULT)
        # when testing add a "not" to the if condition to test the false condition
        if self.checkDefaultFolders:
            self.sims4_mod_folderName = self.SIMS4_MOD_FOLDERNAME_DEFAULT
            self.sims4_backup_folderName = self.SIMS4_BACKUP_FOLDERNAME_DEFAULT
        else:
            # popup for selection of mode folder locations
            self.sims4_mod_folderName = QFileDialog.getExistingDirectory(
                None,
                "Select Sims 4 Mods Directory",
                r"C:/",
                QFileDialog.ShowDirsOnly,
            )
            # popup for selection of backup folder locations
            self.sims4_backup_folderName = QFileDialog.getExistingDirectory(
                None,
                "Select Sims 4 Mods Directory",
                r"C:/",
                QFileDialog.ShowDirsOnly,
            )
            logger.info(self.sims4_mod_folderName)

        # TODO: Not sure if this is the best way or place for the backup logic
        # backing up mods every 1 minute
        self.timer = QTimer()
        self.timer.timeout.connect(self.backupMods)
        # prod
        # self.timer.start(2.16e7)  # 6 hours, unit is ms
        # dev
        self.timer.start(10000)  # dev only, run every 10 seconds
        # UI
        # Create layout
        main_layout = QVBoxLayout()
        form_layout = QFormLayout()
        buttons_layout = QHBoxLayout()
        layout_sims4_mod_folder_name = QHBoxLayout()
        layout_sims4_backup_folder_name = QHBoxLayout()
        # labels
        self.label = QLabel("Mods Backup Settings")
        # folder icon
        folder_icon = QIcon("icons/folder.png")
        # Create UI
        # text box
        self.textbox_sims4_mod_folderName = QLineEdit(self.sims4_mod_folderName)
        self.textbox_sims4_backup_folderName = QLineEdit(self.sims4_backup_folderName)
        # layout
        form_layout.addRow("Mods Folder", self.textbox_sims4_mod_folderName)
        form_layout.addRow("Backup Folder", self.textbox_sims4_backup_folderName)
        # Add forms layout to main
        main_layout.addLayout(form_layout)
        # Add buttons
        # buttons = QDialogButtonBox()
        save_button = QPushButton("Save")
        save_button.setFixedSize(QSize(50, 25))
        save_button.clicked.connect(self.saveClickHandler)
        buttons_layout.addWidget(save_button, alignment=Qt.AlignRight)
        # Set layout for the window
        main_layout.addLayout(buttons_layout)
        self.setLayout(main_layout)

    # action method
    def cancelClickHandler(self):
        # printing pressed
        logger.info("Cancel!")

    def saveClickHandler(self):
        # printing pressed
        logger.info("Save!")

    def backupMods(self):
        """
        backing up sims4 mods folder
        @return: None
        """
        # change directory to Mods directory
        os.chdir(self.SIMS4_BACKUP_FOLDERNAME_DEFAULT)
        timestr = time.strftime("%Y%m%d")
        zip_filename = f"Mods_{timestr}.zip"
        shutil.make_archive(
            zip_filename,
            "zip",
            self.sims4_mod_folderName,
        )
        logger.info(f"Backed up Sims 4 Mods as {zip_filename}")


class MainUI(QWidget):
    def __init__(self):
        super().__init__()
        # import UI components
        self.modsBackupUI = ModsBackupUI()
        # set window title
        self.setWindowTitle("dankutility")
        # set window icon
        self.setWindowIcon(QIcon("icons/dankutility.png"))
        # Create layout
        layout = QGridLayout()
        tabwidget = QTabWidget()
        # add tabs
        tabwidget.addTab(self.modsBackupUI, "Mods Backup")
        layout.addWidget(tabwidget, 0, 0)
        # Set layout for the window
        self.setLayout(layout)


class DankUtilityApp:
    """
    Class for main utility tool
    """

    def __init__(self):
        self.app = QApplication(sys.argv)
        # setup stylesheet API for various themes
        self.app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api="pyside6"))
        self.app.setQuitOnLastWindowClosed(False)
        # Create a system tray icon
        self.tray_icon = QSystemTrayIcon(QIcon("icons/dankutility.png"), self.app)
        self.tray_icon.setToolTip("dankutility")

        # Create a context menu for the tray icon
        self.tray_menu = QMenu()
        self.open_action = QAction("Open", self.app)
        self.quit_action = QAction("Quit", self.app)
        self.tray_menu.addAction(self.open_action)
        self.tray_menu.addAction(self.quit_action)

        # Connect actions to functions
        self.open_action.triggered.connect(self.show_window)
        self.quit_action.triggered.connect(self.quit_application)

        # Set the context menu for the tray icon
        self.tray_icon.setContextMenu(self.tray_menu)
        # set log levels
        self.loglevel = "INFO"
        # Show the tray icon
        self.tray_icon.show()
        # initialize main UI
        self.window = MainUI()
        self.window.setMinimumSize(500, 150)

    def show_window(self):
        """

        @return: None
        """
        # This function will be called when "Open" is clicked
        # Do stuff here!
        #############################
        logger.info("Main UI opened")
        #############################
        # For demonstration, let's show a message box
        """QMessageBox.information(
            None, "Background App", "Application is running in the background."
        )"""
        self.window.show()

    def quit_application(self):
        """

        @return: None
        """
        # This function will be called when "Quit" is clicked
        print("Quitting application")
        self.app.quit()

    def run(self):
        """

        @return: None
        """
        # Start the application event loop
        sys.exit(self.app.exec())


# run main method
if __name__ == "__main__":
    # create app
    background_app = DankUtilityApp()
    # run in background
    background_app.run()