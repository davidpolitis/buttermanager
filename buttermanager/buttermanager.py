#!/usr/bin/env python3
#
# -*- coding: utf-8 -*-
#
# Copyright 2018-2019 Eloy García Almadén <eloy.garcia.pca@gmail.com>
#
# This file is part of buttermanager.
#
# This program is free software: you can redistribute it and / or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import filesystem.filesystem
import util.utils
import util.settings
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget, QDialog
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt
from PyQt5 import uic


class PasswordWindow(QMainWindow):
    """Window to let the user type his/her password.

    Class inherited from QMainWindow (Window constructor)
    """
    # Constructor
    def __init__(self, parent):
        QMainWindow.__init__(self, parent)
        self.parent = parent
        # Configuring the application
        self.__buttermanager_configurator = util.utils.ConfigManager()
        self.__buttermanager_configurator.configure()
        # Logger
        self.__logger = util.utils.Logger(self.__class__.__name__).get()
        # Initializing the application
        self.init_ui()

    def init_ui(self):
        """Initializes the Graphic User Interface.

        """
        # Loading User Interface
        uic.loadUi("ui/PasswordWindow.ui", self)

        # Centering the window
        qt_rectangle = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        qt_rectangle.moveCenter(center_point)
        self.move(qt_rectangle.topLeft())

        # Events
        # OK button event
        self.button_ok.clicked.connect(self.load_main_window)

        # Cancel button event
        self.button_cancel.clicked.connect(self.exit)

        # Press enter within QLineEdit
        self.input_password.returnPressed.connect(self.load_main_window)

        # Showing password window
        self.show()

    def load_main_window(self):
        # Storing user's password
        util.settings.user_password = self.input_password.text()

        # Exiting password window
        self.hide()

        # Showing main window
        butter_manager_window = ButtermanagerMainWindow(self)
        butter_manager_window.show()

    def exit(self):
        # Exits the application
        self.hide()
        sys.exit()


class ButtermanagerMainWindow(QMainWindow):
    """Main window.

    Class inherited from QMainWindow (Window constructor)
    """
    # Constructor
    def __init__(self, parent):
        QMainWindow.__init__(self, parent)
        self.parent = parent
        # Logger
        self.__logger = util.utils.Logger(self.__class__.__name__).get()
        # Current filesystem (it will be initialize in initialize method)
        self.__current_filesystem = None
        # Current filesystem uuid (it will be initialize in initialize method)
        self.__current_filesystem_uuid = None
        # Initializing the application
        self.init_ui()

    def init_ui(self):
        """Initializes the Graphic User Interface.

        """
        try:
            # Loading User Interface
            uic.loadUi("ui/MainWindow.ui", self)

            # Setting maximum and minimum  size for the main window
            self.setMinimumHeight(550)
            self.setMinimumWidth(800)
            self.setMaximumHeight(550)
            self.setMaximumWidth(800)

            # Centering the window
            qt_rectangle = self.frameGeometry()
            center_point = QDesktopWidget().availableGeometry().center()
            qt_rectangle.moveCenter(center_point)
            self.move(qt_rectangle.topLeft())

            # Retrieving BTRFS Filesystems uuid
            uuid_filesystems = filesystem.filesystem.get_btrfs_filesystems()
            self.__current_filesystem_uuid = uuid_filesystems[0]
            self.combobox_filesystem.addItems(uuid_filesystems)
            self.__current_filesystem = filesystem.filesystem.Filesystem(self.__current_filesystem_uuid)
            self.__logger.info("BTRFS filesystems found in the system:")
            self.__logger.info(str(self.__current_filesystem))

            # Displaying all the info related to the filesystem selected by default
            self.fill_filesystem_info(self.__current_filesystem)

            # Button event
            self.button_balance.clicked.connect(self.balance_filesystem)

        except util.utils.NoCommandFound:
            self.__logger.info("The application couldn't start normally. There are some programs needed that are not "
                               "installed.")
            self.__logger.info("Please, install these programs and start ButterManager again.")
            # Exits the application
            sys.exit()

    def balance_filesystem(self):
        """Runs the balance method.

        """
        # Displaying info
        info_dialog = InfoWindow(self, "In progress: please wait until filesystem is balanced. "
                                       "It will take a little bit...")
        info_dialog.show()
        filesystem.filesystem.balance_filesystem(
            filesystem.filesystem.BTRFS_BALANCE_DATA_USAGE_FILTER,
            self.__current_filesystem.data_percentage,
            self.__current_filesystem.mounted_points[0])
        filesystem.filesystem.balance_filesystem(
            filesystem.filesystem.BTRFS_BALANCE_METADATA_USAGE_FILTER,
            self.__current_filesystem.metadata_percentage,
            self.__current_filesystem.mounted_points[0])

        # Closing info
        info_dialog.hide()
        info_dialog.close()

        # Calculating new values for the filesystem balanced
        self.__current_filesystem = filesystem.filesystem.Filesystem(self.__current_filesystem_uuid)
        # Displaying all the info related to the filesystem recently balanced
        self.fill_filesystem_info(self.__current_filesystem)

    def fill_filesystem_info(self, filesystem):
        """Fills filesystem information in the GUI.

        Arguments:
            filesystem (obj: Filesystem): Filesystem.
        """
        tooltip = "More info about the filesystem: \n " \
                  "Devices: {devices} \n " \
                  "Mounted points: {mounted_points}".format(devices=filesystem.devices,
                                                            mounted_points=filesystem.mounted_points)
        self.label_filesystem_info_more.setToolTip(tooltip)
        self.label_filesystem_info_more.setCursor(QCursor(Qt.WhatsThisCursor))
        self.label_filesystem_size_value.setText(filesystem.total_size)
        self.label_filesystem_allocated_value.setText(filesystem.total_allocated)
        self.progressbar_data.setValue(filesystem.data_percentage)
        self.progressbar_metadata.setValue(filesystem.metadata_percentage)
        self.progressbar_system.setValue(filesystem.system_percentage)

class InfoWindow(QDialog):
    """Window to display information.

    Class inherited from QDialog (Window constructor)
    """
    # Constructor
    def __init__(self, parent, information):
        QDialog.__init__(self, parent)
        self.parent = parent
        # Initializing the window
        self.init_ui(information)

    def init_ui(self, information):
        """Initializes the Graphic User Interface.

        """
        # Loading User Interface
        uic.loadUi("ui/InfoWindow.ui", self)

        # Centering the window
        qt_rectangle = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        qt_rectangle.moveCenter(center_point)
        self.move(qt_rectangle.topLeft())

        # Setting information
        self.label_info.setText(information)


if __name__ == '__main__':
    # Creating application instance
    application = QApplication(sys.argv)
    # Creating main window instance
    password_window = PasswordWindow(None)
    # Launching the application
    application.exec_()
