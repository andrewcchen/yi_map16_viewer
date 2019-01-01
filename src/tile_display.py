from math import ceil

from PySide2.QtWidgets import QWidget
from PySide2.QtGui import QImage, QPixmap, QPainter, QColor
from PySide2.QtCore import Qt, Signal, QPoint, QRect

class TileDisplay(QWidget):
    selectionChanged = Signal(int)

    def __init__(self, parent = None):
        super(TileDisplay, self).__init__(parent)

        self.tiles = []
        self.pixmap = None
        self.selection = None

    def invalidate(self):
        self.pixmap = None
        self.update()

    def set_tiles(self, tiles):
        # tiles: [Qimage]
        self.tiles = tiles
        self.invalidate()

    def set_scale(self, scale):
        self.tile_size = 16 * scale
        self.border_size = 1 * scale
        self.invalidate()

    def render_pixmap(self):
        tsize = self.tile_size
        bsize = self.border_size
        csize = tsize + bsize

        tile_count = len(self.tiles)
        ncols = (self.width() - bsize) // csize
        if ncols < 1: ncols = 1
        nrows = ceil(tile_count / ncols)

        width = bsize + ncols * csize
        height = bsize + nrows * csize
        
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)

        for r in range(nrows):
            for c in range(ncols):
                i = r*ncols + c
                if i >= tile_count: break
                x = bsize + c * csize
                y = bsize + r * csize

                painter.fillRect(x-bsize, y-bsize, csize+bsize, csize+bsize, Qt.white)
                im = self.tiles[i].scaled(tsize, tsize)
                painter.drawImage(x, y, im)

        self.setMinimumSize(0, height)
        self.pixmap = pixmap
        self.ncols = ncols

    def paintEvent(self, event):
        if not self.pixmap:
            self.render_pixmap()
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.pixmap)

    def resizeEvent(self, event):
        self.invalidate()

    def mouseMoveEvent(self, event):
        bsize = self.border_size
        tsize = self.tile_size
        csize = bsize + tsize
        pos = event.pos() - QPoint(bsize, bsize)

        c = pos.x() // csize
        r = pos.y() // csize
        tile_rect = QRect(c*csize, r*csize, tsize, tsize)
        tile_num = r * self.ncols + c

        if c < self.ncols and \
           tile_num >= 0 and \
           tile_num < len(self.tiles) and \
           tile_rect.contains(pos) and \
           self.selection != tile_num:

            self.selection = tile_num
            self.selectionChanged.emit(tile_num)
