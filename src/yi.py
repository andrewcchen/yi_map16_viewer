from snes import Snes

def addr_to_offset(addr):
    bank = addr // 0x10000
    x = (addr % 0x10000) - 0x8000
    if x < 0:
        raise ValueError('Not a rom address: {0:#x}'.format(addr))
    return bank*0x8000 + x

class YiRom:
    def __init__(self):
        with open('../data/yi.sfc', 'rb') as f:
            self.rom = f.read()

        self.snes = Snes()

        self.lz2_files = []
        self.lz16_files = []

        self.bg1_files = [self.rom_bytes(0x00AF39 + 3*i, 3) for i in range(0, 32)]

        self.load_gfx_files()
        self.load_map16()

    def rom_byte(self, addr):
        return self.rom[addr_to_offset(addr)]

    def rom_bytes(self, addr, count):
        o = addr_to_offset(addr)
        return [self.rom[o+i] for i in range(0, count)]

    def rom_word(self, addr):
        o = addr_to_offset(addr)
        return self.rom[o] | (self.rom[o+1] << 8)

    def rom_words(self, addr, count):
        o = addr_to_offset(addr)
        return [self.rom[o+2*i] | (self.rom[o+2*i+1] << 8) for i in range(0, count)]

    def load_gfx_files(self):
        for i in range(21, 21+265):
            filename = '../data/GFX{0:03X}.bin'.format(i)
            with open(filename, 'rb') as f:
                self.lz2_files.append(f.read())

        for i in range(21+265, 21+265+187):
            filename = '../data/GFX{0:03X}.bin'.format(i)
            with open(filename, 'rb') as f:
                self.lz16_files.append(f.read())

    def load_map16(self):
        base = 0x18B3F2
        n_pages = 167
        offsets = self.rom_words(0x18B2A4, n_pages)
        offsets.append(0xA228) # end $19D61A

        self.map16 = [ [] for _ in range(n_pages) ]
        for i in range(0, n_pages):
            n_tiles = (offsets[i+1] - offsets[i]) // 8   # 16x16 tiles
            for j in range(0, n_tiles):
                addr = (base + offsets[i] + j*8) | 0x8000
                self.map16[i].append(self.rom_words(addr, 4))

    def set_bg1_tileset(self, bg1_set):
        def load(f, a):
            if a & 0x8000: self.snes.vram_load(a, self.lz16_files[f])
            else:          self.snes.vram_load(a, self.lz2_files[f])
        bg1 = self.bg1_files[bg1_set]

        load(0x19, 0xF800)
        load(0x12, 0x9200)
        load(0x76, 0x9500)
        load(0x72, 0xC000)
        load(0x4f, 0x6000)
        load(bg1[0], 0x0000)
        load(bg1[1], 0x0800)
        load(bg1[2], 0x7000)

    def set_bg1_palette(self, bg1_pal):
        def src(x): return addr_to_offset(0x3FA000+x)
        bg1 = self.rom_word(0x00B874 + 2*bg1_pal)

        self.snes.cgram_load(0x11, 3, 11, src(0x027C), self.rom)
        self.snes.cgram_load(0x41, 2, 15, src(bg1), self.rom)
        self.snes.cgram_load(0x1c, 3, 4, src(bg1)+0x3C, self.rom)

    def get_bg1_tile(self, page, index):
        tilemaps = self.map16[page][index]
        tiles = [self.snes.get_4bpp_tile_rgb(0x7000, t) for t in tilemaps]
        left_tiles = tiles[0] + tiles[2]
        right_tiles = tiles[1] + tiles[3]
        res = [ [] for i in range(16) ]
        for i in range(0, 16):
            res[i] = left_tiles[i] + right_tiles[i]
        return res
