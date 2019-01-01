
def rgb555_to_rgb32(x):
    r = (x & 0x1f) << 3
    g = ((x >> 5) & 0x1f) << 3
    b = ((x >> 10) & 0x1f) << 3
    return 0xff000000 | (r << 16) | (g << 8) | b

class Snes:
    def __init__(self):
        self.vram = [0] * 0x8000 # 0x8000 words
        self.cgram = [0] * 256 # 256 words

    def vram_load(self, addr, data):
        addr %= 0x8000
        for i in range(0, len(data) // 2):
            self.vram[addr+i] = data[i*2] | (data[i*2+1] << 8)

    def cgram_load(self, dest, rows, size, src, rom):
        for i in range(0, rows):
            addr = dest + 16*i
            for j in range(0, size):
                self.cgram[addr+j] = rom[src] | (rom[src+1] << 8)
                src += 2

    def palette_lookup(self, palette, index):
        rgb555 = self.cgram[palette * 16 + index]
        return rgb555_to_rgb32(rgb555)

    # bg1 base = 0x6800
    # assuming 8x8 tiles
    def get_4bpp_tile_rgb(self, base, tile):
        tile_num = tile & 0x3ff
        palette = (tile >> 10) & 0x7
        hflip = bool((tile >> 14) & 0x1)
        vflip = bool((tile >> 15) & 0x1)
        addr = (base + tile_num * 16) & 0x7fff

        pixels = [ [] for i in range(8) ]
        for i in range(0, 8):
            r01 = self.vram[addr + i]
            r23 = self.vram[addr + 8 + i]
            for j in range(0, 8):
                b0 = (r01 >> j) & 1
                b1 = (r01 >> (j+8)) & 1
                b2 = (r23 >> j) & 1
                b3 = (r23 >> (j+8)) & 1
                colour = b0 | (b1 << 1) | (b2 << 2) | (b3 << 3)
                pixels[i].append(self.palette_lookup(palette, colour))
                #x = colour << 4; pixels[i].append(0xff << 24 | x << 16 | x << 8 | x)
            if not hflip:
                pixels[i].reverse()
        if vflip:
            pixels.reverse()

        return pixels

