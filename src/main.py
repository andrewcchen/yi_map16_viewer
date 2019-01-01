#!/usr/bin/env python3

import sys

from PySide2.QtWidgets import QApplication, QMainWindow, QListWidgetItem
from PySide2.QtGui import QImage, QPixmap, QPainter, QColor, QIcon
from PySide2.QtCore import QRect, QPoint

from ui.mainwindow import Ui_MainWindow
from yi import YiRom

tileset_names = [
"0 : Cave 0",
"1 : Forest 1",
"2 : Pond",
"3 : 3D stone",
"4 : Snow",
"5 : Jungle",
"6 : Brick Castle",
"7 : Grass 1",
"8 : Cave 2",
"9 : Forest 2",
"A : Wooden Castle",
"B : Sewer",
"C : Flower Garden",
"D : Sky",
"E : Stone Castle",
"F : Grass 2"
]

def pixels_to_qimage(pixels, s):
    im = QImage(s, s, QImage.Format_RGB32)
    buf = im.bits().cast('I')
    for i in range(0, s):
        for j in range(0, s):
            buf[i*s+j] = pixels[i][j]
    return im

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        for i in tileset_names:
            self.tilesetSelect.addItem(i)
        for i in range(0x20):
            self.paletteSelect.addItem('{:02X}'.format(i))

        slot = lambda _: self.change_tiles()
        self.pageSelect.valueChanged.connect(slot)
        self.tilesetSelect.currentIndexChanged.connect(slot)
        self.paletteSelect.currentIndexChanged.connect(slot)
        self.scaleSelect.valueChanged.connect(slot)

        self.tileDisplay.selectionChanged.connect(lambda tile_num:
                self.tileText.setText("0x{:02X}".format(tile_num)))

        self.yi = YiRom()
        self.change_tiles()

    def change_tiles(self):
        self.tileDisplay.set_scale(self.scaleSelect.value())
        self.yi.set_bg1_tileset(self.tilesetSelect.currentIndex())
        self.yi.set_bg1_palette(self.paletteSelect.currentIndex())

        #tiles = []
        #for i in range(1024):
        #    pixels = self.yi.snes.get_4bpp_tile_rgb(0x7000, i)
        #    im = pixels_to_qimage(pixels, 8)
        #    tiles.append(im)
        #self.tileDisplay.set_tiles(tiles)
        #return

        page = self.pageSelect.value()
        ntiles = len(self.yi.map16[page])
        tiles = []
        for i in range(ntiles):
            pixels = self.yi.get_bg1_tile(page, i)
            im = pixels_to_qimage(pixels, 16)
            tiles.append(im)
        self.tileDisplay.set_tiles(tiles)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())
