
import sys
import numpy as np
import exifread

import rawpy
import pyvips

from imutils import writeimage, np_dtype_to_vips_format


def rawimsize(param):
    rawfilename=param[0]
    raw = rawpy.imread(rawfilename)
    print(raw.sizes.width, raw.sizes.height)


# print basic info about raw image
def rawinfo(param):
    checkonly=False
    for i in range(2):
        if (not param or not isinstance(param[0], str)): break
        if(param[0]=='-c'):
            checkonly=True
            del param[0]
    rawfilename=param[0]

    try:
        tags = exifread.process_file(open(rawfilename, 'rb'))
        raw = rawpy.imread(rawfilename)
    except:
        print("ERROR: unable to read file by using rawpy", file=sys.stderr)
        exit(-1)
    if checkonly: exit(0)

    for key, value in tags.items():
        if (key != 'JPEGThumbnail'):
            if (key.startswith('Image')):
                print(f'{key}: {value}')

    print("raw type:   ", raw.raw_type)
    print("color desc: ", raw.color_desc)
    print("raw pattern:", raw.raw_pattern.tolist())
    print("black:      ", raw.black_level_per_channel)
    print("white:      ", raw.white_level)
    print("16bit-mult: ", int(2**16 / raw.white_level))
    print("image size: ", raw.sizes.width, raw.sizes.height)
    #print("sizes:      ", raw.sizes)



# linear CFA gray image
# note: implicite scaling to full 16bit range
def rawtogray(param):
    outfmt='pgm'
    rawfilename=param[0]
    outfilename=param[1]

    raw = rawpy.imread(rawfilename)

    cfa = raw.raw_image_visible.copy()

    # convert to vips image   
    height, width = cfa.shape
    bands=1
    nparr = cfa.reshape(width * height)
    outimg = pyvips.Image.new_from_memory(nparr.data, width, height, bands,
        np_dtype_to_vips_format[str(cfa.dtype)])
    #print("data range:", outimg.min(), outimg.max())
    
    # stretch to 16bit
    mult=int(2**16 / raw.white_level)
    if (mult>1):
        outimg = outimg.linear(mult, 0)
    
    # writing output image
    writeimage(["-fmt", outfmt, outimg, outfilename])


# linear 16bit RGB
# note: implicite scaling to full 16bit range
def rawtorgb(param):
    outfmt='ppm'
    develop=False
    for i in range(2):
        if (not param or not isinstance(param[0], str)): break
        if(param[0]=='-d'):
            develop=True
            del param[0]

    rawfilename=param[0]
    outfilename=param[1]
    algorithm=1     # 0-bilinear, 1-VNG, 2-PPG, 3-AHD
    colorspace=0    # 0-raw 1-sRGB 2-Adobe

    raw = rawpy.imread(rawfilename)

    if (develop):
        rgb = raw.postprocess()
    else:
        rgb = raw.postprocess(
            user_flip=0,
            user_wb=(1,1,1,1),
            user_black=0,
            demosaic_algorithm=rawpy.DemosaicAlgorithm(algorithm),
            output_color=rawpy.ColorSpace(colorspace),
            gamma=(1,1),
            no_auto_bright=True,
            output_bps=16)

    # convert to vips image   
    height, width, bands = rgb.shape
    nparr = rgb.reshape(width * height * bands)
    outimg = pyvips.Image.new_from_memory(nparr.data, width, height, bands,
        np_dtype_to_vips_format[str(rgb.dtype)])

    # stretch to 16bit
    mult=int(2**16 / raw.white_level)
    if (mult>1):
        outimg = outimg.linear(mult, 0)

    # writing output image
    writeimage(["-fmt", outfmt, outimg, outfilename])

