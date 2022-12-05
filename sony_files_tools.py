import os
import argparse

import TGP_Tools
import STX_Tools

path_unpacked = 'skin_rom_unpack'

parser = argparse.ArgumentParser(usage='sony_files_tools.py [option]')
parser.add_argument('-u', '--unpack', action='store_true', help='Unpack mode')
parser.add_argument('-p', '--pack', action='store_true', help='Pack mode')
TGP_group = parser.add_argument_group('TGP files options')
TGP_group.add_argument('--tgp-path', help='Select directory with all .tgp or .json files', dest='path_tgp', type=str)
TGP_group.add_argument('--tgp-file', help='Select .tgp file or .json', dest='file_tgp', type=str)
STX_group = parser.add_argument_group('STX files options')
STX_group.add_argument('--stx-path', help='Select directory with all .stx or .json files', dest='path_stx', type=str)
STX_group.add_argument('--stx-file', help='Select .stx file or .json', dest='file_stx', type=str)

options = parser.parse_args()

if options.unpack is False and options.pack is False and options.path_tgp is None and options.file_tgp is None and \
        options.path_stx is None and options.file_stx is None:
    print(parser.print_help())
    exit(0)

if options.unpack is True:
    if options.path_tgp is not None:
        if not os.path.exists(options.path_tgp):
            print('Directory not exists!')
            exit()

        for root, dirs, files in os.walk(options.path_tgp):
            for filename in files:
                if not os.path.exists(os.path.join(options.path_tgp, path_unpacked)):
                    os.mkdir(os.path.join(options.path_tgp, path_unpacked))
                if filename.lower().find('.tgp') != -1:
                    if not os.path.exists(os.path.join(options.path_tgp, path_unpacked, filename.replace('.tgp', ''))):
                        os.mkdir(os.path.join(options.path_tgp, path_unpacked, filename.replace('.tgp', '')))

                    tgp = TGP_Tools.TGP(
                        os.path.join(options.path_tgp, filename),
                        os.path.join(options.path_tgp, path_unpacked)
                    )
                    print(f'Unpacking file: {os.path.join(options.path_tgp, filename)}')
                    for i in range(0, tgp.get_count_images()):
                        tgp.get_image(i, os.path.join(options.path_tgp, path_unpacked,filename.replace('.tgp',''),
                                                           f'{i}_image.png'))
                if files is []:
                    break;
        print('Done!\n'
              f'Output path: {os.path.join(options.path_tgp, path_unpacked)}')
    elif options.file_tgp is not None:
        if not os.path.exists(options.file_tgp):
            print('File not exists!')
            exit()

        path = options.file_tgp[0: options.file_tgp.rfind('/')]
        path1 = options.file_tgp[0: options.file_tgp.rfind('\\')]
        last_index = options.file_tgp.rfind('/') + 1

        if path.find('.tgp'):
            path = path1
            last_index = options.file_tgp.rfind('\\') + 1

        if not os.path.exists(os.path.join(path, path_unpacked)):
            os.mkdir(os.path.join(path, path_unpacked))
        if options.file_tgp.lower().find('.tgp') != -1:
            if not os.path.exists(os.path.join(path, path_unpacked,
                                               options.file_tgp[last_index:].replace('.tgp', ''))):
                os.mkdir(os.path.join(path, path_unpacked, options.file_tgp[last_index:].replace('.tgp', '')))

            tgp = TGP_Tools.TGP(
                os.path.join(path, options.file_tgp),
                os.path.join(path, path_unpacked)
            )
            print(f'Unpacking file: {os.path.join(path, options.file_tgp)}')
            for i in range(0, tgp.get_count_images()):
                tgp.get_image(i, os.path.join(path, path_unpacked, options.file_tgp[last_index:].replace('.tgp', ''),
                                                   f'{i}_image.png'))
        print('Done!\n'
              f'Output path: {os.path.join(path, path_unpacked)}')
    elif options.path_stx is not None:
        if not os.path.exists(options.path_stx):
            print('Directory not exists!')
            exit()

        for root, dirs, files in os.walk(options.path_stx):
            for filename in files:
                if filename.lower().find('.stx') != -1:

                    print(f'Unpacking file: {os.path.join(options.path_stx, filename)}')
                    STX_Tools.STX.unpack_stx(None, os.path.join(root, filename))
                if files is []:
                    break;
        print('Done!\n'
              f'Output path: {os.path.join(options.path_stx, "unpacked_stx")}')
    elif options.file_stx is not None:
        if not os.path.exists(options.file_stx):
            print('File not exists!')
            exit()

        print(f'Unpacking file: {options.file_stx}')
        out_filename = STX_Tools.STX.unpack_stx(None, options.file_stx)
        print('Done!\n'
              f'Output path: {out_filename}')
elif options.pack is True:
    if options.path_tgp is not None:
        if not os.path.exists(options.path_tgp):
            print('Directory not exists!')
            exit()

        if not os.path.exists(os.path.join(os.path.dirname(options.path_tgp), 'packed_tgp')):
            os.mkdir(os.path.join(os.path.dirname(options.path_tgp), 'packed_tgp'))

        for root, dirs, files in os.walk(options.path_tgp):
            for filename in files:
                if filename.find('.json') != -1:
                    print(f'Packing file: {os.path.join(options.path_tgp, filename)}')
                    TGP_Tools.TGP.pack_tgp(None, os.path.join(os.path.join(root), filename),
                                           os.path.join(root),
                                           os.path.join(os.path.dirname(options.path_tgp), 'packed_tgp'))
                            # tgp = TGP_Tools.TGP.pack_tgp(None, )
            if files is []:
                break;
        print('Done!\n'
              f'Packed files: {os.path.join(os.path.dirname(options.path_tgp), "packed_tgp")}')
    elif options.file_tgp is not None:
        if not os.path.exists(options.file_tgp):
            print('File not exists!')
            exit()

        if not os.path.exists(os.path.join(os.path.dirname(options.file_tgp), 'packed_tgp')):
            os.mkdir(os.path.join(os.path.dirname(options.file_tgp), 'packed_tgp'))

        for root, dirs, files in os.walk(os.path.dirname(options.file_tgp)):
            for filename in files:
                if filename.find('.json') != -1 and filename == os.path.basename(options.file_tgp):
                    print(f'Packing file: {filename}')
                    TGP_Tools.TGP.pack_tgp(None, os.path.join(os.path.join(root), filename),
                                           os.path.join(root),
                                           os.path.join(os.path.dirname(options.file_tgp), 'packed_tgp'))
                    # tgp = TGP_Tools.TGP.pack_tgp(None, )
            if files is []:
                break;
        print('Done!\n'
              f'Packed files: {os.path.join(os.path.dirname(options.file_tgp), "packed_tgp")}')
    elif options.path_stx is not None:
        if not os.path.exists(options.path_stx):
            print('Directory not exists!')
            exit()

        for root, dirs, files in os.walk(options.path_stx):
            for filename in files:
                if filename.lower().find('.json') != -1:
                    print(f'Packing file: {os.path.join(root, filename)}')
                    STX_Tools.STX.pack_stx(None, os.path.join(root, filename))
                if files is []:
                    break;
        print('Done!\n'
              f'Output path: {os.path.join(options.path_stx, "packed_stx")}')
    elif options.file_stx is not None:
        if not os.path.exists(options.file_stx):
            print('File not exists!')
            exit()

        print(f'Packing file: {options.file_stx}')
        STX_Tools.STX.pack_stx(None, options.file_stx)
        print('Done!\n'
              f'Output path: {os.path.join(options.path_stx, "packed_stx")}')