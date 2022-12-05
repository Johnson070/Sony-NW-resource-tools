import os

import jsonpickle


class STX:
    def __init__(self):
        pass

    class STX_Info:
        filename = ''
        count_headers = 0
        texts = {}

        def __init__(self, filename):
            self.count_headers = 0
            self.texts = {}
            self.filename = filename

    def pack_stx(self, filename):
        if not os.path.exists(filename):
            print('File not exists!')

        json = ''
        try:
            with open(filename, 'r', encoding='utf-16') as f:
                json = jsonpickle.decode(f.readline())
        except:
            print('Error parse json!\n'
                  'Check file!')
            return

        filename_out = json['filename']
        count_headers = json['count_headers']
        strings: dict = json['texts']

        len_to_strings = 56 + count_headers * 4
        out_bytes = b''
        out_headers = b''

        for key in range(0, count_headers):
            if strings.get(str(key)) is not None:
                text = strings[str(key)]
                out_string = b''
                for char in text:
                    out_string += ord(char).to_bytes(2, 'big')[::-1]
                out_string += b'\x00\x00'

                out_headers += (len_to_strings + len(out_bytes)).to_bytes(4, 'big')[::-1]
                out_bytes += out_string
            else:
                out_headers += b'\x00\x00\x00\x00'

        stx_file = out_headers
        stx_file += out_bytes

        len_file_stx = len(stx_file).to_bytes(4, 'big')[::-1]

        stx_header = b'\x63\x6F\x6E\x74\x65\x6E\x74\x2D\x74\x79\x70\x65\x3A\x20\x74\x65' \
                     b'\x78\x74\x2F\x73\x74\x78\x0A\x0A\x00\x00\x00\x00\x00\x00\x00\x00' \
                     b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x01\x38\x00\x00\x00'  # Header default
        stx_header += (count_headers).to_bytes(4, 'big')[::-1]  # Count of addrs to strings reversed
        stx_header += (len(stx_file) + 56).to_bytes(4, 'big')[::-1]  # Len all file in bytes

        stx_file = stx_header + stx_file

        if not os.path.exists(os.path.join(os.path.dirname(filename), 'packed_stx')):
            os.mkdir(os.path.join(os.path.dirname(filename), 'packed_stx'))

        with open(os.path.join(os.path.dirname(filename), 'packed_stx', filename_out), 'wb') as f:
            f.write(stx_file)

    def unpack_stx(self, filename):
        if not os.path.exists(filename):
            print('File not exists!')

        raw = ''
        with open(filename, 'rb') as f:
            raw = f.read()

        out_json = STX.STX_Info(os.path.basename(filename))
        headers_addrs = []
        len_headers = int.from_bytes(raw[48:52][::-1], 'big') * 4

        for i in range(56, len_headers + 56, 4):
            byte = raw[i:i + 4][::-1]
            headers_addrs.append(int.from_bytes(byte, 'big'))

        out_json.count_headers = int.from_bytes(raw[48:52][::-1], 'big')
        idx = 0
        for i in headers_addrs:
            if i != 0:
                out_string = ''

                idx_char = 0
                while raw[i + idx_char:i + idx_char + 2] != b'\x00\x00':
                    byte = raw[i + idx_char:i + idx_char + 2]
                    try:
                        if byte[1] == 228:
                            out_string += byte.decode('utf-16')
                        else:
                            out_string += byte.decode('utf-16')
                    except:
                        out_string += byte.decode('utf-16')

                    idx_char += 2

                out_json.texts[idx] = out_string
            idx += 1

        jsonpickle.set_preferred_backend('json')
        jsonpickle.set_encoder_options('json', ensure_ascii=False)

        if not os.path.exists(os.path.join(os.path.dirname(filename), 'unpacked_stx')):
            os.mkdir(os.path.join(os.path.dirname(filename), 'unpacked_stx'))

        new_filename = os.path.join(os.path.dirname(filename), 'unpacked_stx',
                                       os.path.basename(filename).replace('.stx', '.json'))
        with open(new_filename, 'w', encoding='utf-16') as f:
            f.write(jsonpickle.encode(out_json, unpicklable=False))
        return new_filename


if __name__ == '__main__':
    pass
    # STX.unpack_stx(None, r'E:\Рабочий стол\res\stx\ucs2-dev-ru.stx')
    # STX.pack_stx(None, r'E:\Рабочий стол\res\stx\ucs2-dev-ru.stx.json')
