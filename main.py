from PIL import Image
from sys import argv


def encode(image, message):
    message = ''.join([bin(x)[2:].zfill(8) for x in bytes(message, 'utf-8')])
    pixels = image.load()
    max_avbl_size = image.size[0] * image.size[1] * 3
    if len(message) > max_avbl_size:
        raise(f"Sorry, but only {(max_avbl_size)//8} bytes can be written to this image!")
    pixels = [list(x) for x in image.getdata()]
    channels_len = len(pixels[0])
    for bit_idx in range(len(message)):
        idx_x, idx_y = bit_idx // channels_len, bit_idx % channels_len
        if message[bit_idx] == '0' and pixels[idx_x][idx_y] % 2:
            pixels[idx_x][idx_y] -= 1
        elif message[bit_idx] == '1' and pixels[idx_x][idx_y] % 2 == 0:
            pixels[idx_x][idx_y] += 1
    pixels = [tuple(rgb) for rgb in pixels]
    return pixels


def decode(image, length):
    message = ''
    pixels = [x for x in image.getdata()]
    data = []
    channels_len = len(pixels[0])
    if channels_len == 3:
        for r, g, b in pixels:
            data.append(r)
            data.append(g)
            data.append(b)
    elif channels_len == 4:
        for r, g, b, a in pixels:
            data.append(r)
            data.append(g)
            data.append(b)
            data.append(a)
    for i in range(length):
       message += str(data[i] % 2)
    return int(message, 2).to_bytes((len(message) + 7) // 8, byteorder='big').decode('utf-8')


if len(argv) < 2:
    exit("Lack of arguments")
fname = input("Input image path: ")
image = Image.open(fname)
if argv[1] in ('-e', '--encode'):
    message = input("Input secret message: ")
    print([x for x in image.getdata()][:100])
    image.putdata(encode(image, message))
    print([x for x in image.getdata()][:100])
    fname = input("Input output file name (without extension): ") + '.png'
    image.save(fname, format='PNG')
    with open(fname, 'ab') as f:
        f.write(("\n" + str(len(message) * 8)).encode())
elif argv[1] in ('-d', '--decode'):
    with open(fname, 'rb') as f:
        data = f.read()[::-1]
    message = decode(image, int(data[:data.find(b'\n')][::-1]))
    print(message)
else:
    print("Unknown argument", argv[2])
