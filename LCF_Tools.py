from PIL import Image, ImageDraw
structured_text = ''
with open(r'E:\Рабочий стол\res\test_image.tstimg', 'rb') as f:
    structured_text = f.read()

@staticmethod
def get_rgba(color_byte):
    r = color_byte >> 24
    g = color_byte >> 16 & 0xff
    b = color_byte >> 8& 0xff

    return r, g, b, 255


test = 0
for width in range(10, 200,1):
    heidth = 100
    image = Image.new('RGBA', (width, heidth))
    img = ImageDraw.Draw(image)

    for y in range(0, heidth):
        for x in range(0, width):
            pos = x*4 + (y*width*4)
            color = get_rgba(int.from_bytes(structured_text[pos:pos + 4], 'big'))
            img.point((x, y), color)

    image.save(f'E:\\Рабочий стол\\res\\test_img\\image_{test}.png')
    test+=1
    print('', test-1)