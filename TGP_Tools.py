import os

import jsonpickle
from PIL import Image, ImageDraw


class TGP_Info:
    filename = ''
    unknown1 = 0
    unknown2 = 0
    count_images = 0
    files = None

    class TXD_Info:
        idx = 0
        byte_depth = 0
        size = 0

        def __init__(self, idx: int, byte_depth: int):
            self.idx = idx
            self.byte_depth = byte_depth

    def __init__(self, filename: str, idx_txd: list[int], raw: bytes):
        self.filename = filename.replace('.tgp', '')
        self.count_images = int.from_bytes(raw[12:12 + 4], "big")
        self.unknown1 = int.from_bytes(raw[4:4 + 4], "big")
        self.unknown2 = int.from_bytes(raw[8:8 + 4], "big")
        self.files = []

        for _ in range(0, self.count_images):
            idx = idx_txd[_]
            byte_depth = int.from_bytes(raw[idx + 12: idx + 12 + 4], "big")
            self.files.append(
                self.TXD_Info(_, byte_depth)
            )

    def get_null_image(self, bit_depth) -> bytes:
        header = b'TXD\x00'
        header += (1).to_bytes(4, 'big')
        header += (1).to_bytes(4, 'big')
        header += (bit_depth).to_bytes(4, 'big')
        header += b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        len_block = (1 if bit_depth == 1 else
                     (2 if bit_depth == 2 else
                      (3 if bit_depth == 8 else 4)))
        header += (len_block).to_bytes(4, 'big')
        for i in range(0, 16):
            if i + 1 <= len_block:
                header += b'\xFF'
            else:
                header += b'\x00'
        return header

    def get_tgp_header(self, unknown1: int, unknown2: int, count_images: int, len_block_data: int) -> bytes:
        header = b'TGP\x00'
        header += unknown1.to_bytes(4, 'big')
        header += unknown2.to_bytes(4, 'big')
        header += count_images.to_bytes(4, 'big')
        header += b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        header += len_block_data.to_bytes(4, 'big')
        return header

    def get_txd_header(self, width: int, heigth: int, bit_depth: int, len_block_data: int) -> bytes:
        header = b'TXD\x00'
        header += width.to_bytes(4, 'big')
        header += heigth.to_bytes(4, 'big')
        header += (bit_depth).to_bytes(4, 'big')
        header += b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        header += len_block_data.to_bytes(4, 'big')
        return header


class TGP:
    raw_data = b''
    len_sector = 0
    count_images = 0
    unknown1 = 0
    unknown2 = 0

    _idx_TXD_start = []

    def __init__(self, filename: str, directory: str):
        tgp_data = b''
        with open(filename, 'rb') as f:
            tgp_data = f.read()

        math_header = tgp_data.find(b"TGP\x00\x01\x00\x00\x00")
        if math_header == -1:
            raise Exception('Is not TGP file!')

        self.raw_data = tgp_data
        self.len_sector = int.from_bytes(tgp_data[28:28 + 4], "big")
        self.count_images = int.from_bytes(tgp_data[12:12 + 4], "big")
        self.unknown1 = int.from_bytes(tgp_data[4:4 + 4], "big")
        self.unknown2 = int.from_bytes(tgp_data[8:8 + 4], "big")
        self._idx_TXD_start = []

        for i in range(0, self.count_images):
            idx = tgp_data.find(b"TXD\x00",
                                0 if len(self._idx_TXD_start) == 0 else self._idx_TXD_start[-1] + 1)

            if idx != -1:
                self._idx_TXD_start.append(idx)

        tgp_info = TGP_Info(os.path.basename(filename), self._idx_TXD_start, tgp_data)
        file = os.path.join(directory, os.path.basename(filename).replace('.tgp', ''),
                               os.path.basename(filename).replace('.tgp', '')) + '.json'
        with open(file, 'w') as f:
            f.write(jsonpickle.encode(tgp_info, unpicklable=False))

    def get_count_images(self) -> int:
        return self.count_images

    @staticmethod
    def get_rgba(color_byte):
        r = color_byte >> 24
        g = color_byte >> 16 & 0xff
        b = color_byte >> 8 & 0xff
        a = color_byte & 0xff

        return r, g, b, a

    @staticmethod
    def get_rgb(color_byte):
        r = color_byte >> 16
        g = color_byte >> 8 & 0xff
        b = color_byte & 0xff

        return r, g, b

    @staticmethod
    def get_rgb_2byte(color_byte):
        b = (color_byte >> 8 & 0b11111)
        r = color_byte >> 3 & 0b11111
        g = ((color_byte & 0b111) << 3) + (color_byte >> 13 & 0b111)

        return r * 8, g * 4, b * 8

    def get_image(self, index: int, filename: str) -> None:
        idx = self._idx_TXD_start[index]
        width = int.from_bytes(self.raw_data[idx + 4: idx + 4 + 4], "big")
        height = int.from_bytes(self.raw_data[idx + 8: idx + 8 + 4], "big")
        color_pallete = int.from_bytes(self.raw_data[idx + 12: idx + 12 + 4], "big")
        len_block = int.from_bytes(self.raw_data[idx + 28: idx + 28 + 4], "big")
        if color_pallete == 4:
            raise Exception('4 color_pallete')
            return Image.new('RGB', (1, 1), 'white')

        bytes_color = len_block // (width * height)
        # print(f'idx: {index} pos: {idx:0x} bit_depth: {bytes_color}')

        raw_img = self.raw_data[idx + 32: idx + 32 + len_block + 1]
        raw_pixels = []

        for pixel in range(0, len(raw_img), bytes_color):
            raw_pixels.append(int.from_bytes(raw_img[pixel:pixel + bytes_color], "big"))

        img = None
        if color_pallete == 16:
            img = Image.new('RGBA', (width, height), 'black')
        elif color_pallete == 8:
            img = Image.new('RGB', (width, height), 'black')
        elif color_pallete == 2:
            img = Image.new('RGB', (width, height))
        elif color_pallete < 2:
            img = Image.new('L', (width, height))
        image = ImageDraw.Draw(img)

        for y in range(0, height):
            for x in range(0, width):
                if color_pallete == 16:
                    image.point((x, y), self.get_rgba(raw_pixels[y * width + x]))
                elif color_pallete == 8:
                    image.point((x, y), self.get_rgb(raw_pixels[y * width + x]))
                elif color_pallete == 2:
                    image.point((x, y), self.get_rgb_2byte(raw_pixels[y * width + x]))
                elif color_pallete < 1:
                    image.point((x, y), raw_pixels[y * width + x])
        img.save(filename)

    def pack_tgp(self, filename: str, directory: str, out_directory: str):
        tgp_json: TGP_Info
        with open(filename, 'r') as f:
            tgp_json = jsonpickle.decode(f.readline())

        tgp_file = b''

        for i in range(0, tgp_json['count_images']):
            image_path = os.path.join(directory, f'{i}_image.png')

            if os.path.exists(image_path):
                image = Image.open(image_path)

                raw_data = b''
                if tgp_json['files'][i]['byte_depth'] == 16:
                    for y in range(0, image.height):
                        for x in range(0, image.width):
                            color = image.getpixel((x, y))
                            raw_data += ((color[0] << 24) + (color[1] << 16) + (color[2] << 8) + (color[3])).to_bytes(4,
                                                                                                                      'big')
                elif tgp_json['files'][i]['byte_depth'] == 8:
                    for y in range(0, image.height):
                        for x in range(0, image.width):
                            color = image.getpixel((x, y))
                            raw_data += ((color[0] << 16) + (color[1] << 8) + (color[2])).to_bytes(3, 'big')
                elif tgp_json['files'][i]['byte_depth'] == 2:
                    for y in range(0, image.height):
                        for x in range(0, image.width):
                            color = image.getpixel((x, y))
                            color = (color[0] // 8, color[1] // 4, color[2] // 8)
                            raw_data += (((color[1] & 0b111) << 13) | ((color[2] & 0b11111) << 8) |
                                         ((color[0] & 0b11111) << 3) | ((color[1] & 0b111000) >> 3)).to_bytes(2, 'big')
                elif tgp_json['files'][i]['byte_depth'] == 1:
                    for y in range(0, image.height):
                        for x in range(0, image.width):
                            color = image.getpixel((x, y))
                            raw_data += b'\xff'
                elif tgp_json['files'][i]['byte_depth'] == 0:
                    for y in range(0, image.height):
                        for x in range(0, image.width):
                            color = image.getpixel((x, y))
                            raw_data += b'\xff'

                tgp_file += TGP_Info.get_txd_header(None, image.width, image.height,
                                                    tgp_json['files'][i]['byte_depth'], len(raw_data)) + raw_data

                if len(raw_data) % 16 != 0:
                    for _ in range(0, 16 - (len(raw_data) % 16)):
                        tgp_file += b'\x00'
            else:
                print(f'File is missing: {image_path}')
                return
        tgp_file = TGP_Info.get_tgp_header(
            None, tgp_json['unknown1'], tgp_json['unknown2'], tgp_json['count_images'], len(tgp_file)+32
        ) + tgp_file

        out_path = os.path.join(out_directory, tgp_json['filename'])+'.tgp'
        with open(out_path, 'wb') as f:
            f.write(tgp_file)

    def debug(self):
        print(self.len_sector, self.count_images, self._idx_TXD_start, sep='\n')
