#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Size Position JoinInfo
"""
from optparse import OptionParser
import os.path

import Image
import ImageDraw


class Size(object):
    """It keeps size(width, height).
    """
    def __init__(self, width, height):
        """
        Arguments:
            width -- image width
            height -- image height
        """
        self.width = int(width)
        self.height = int(height)


class Position(object):
    """It keeps position(x, y).
    """
    def __init__(self, x, y):
        """
        Arguments:
            x -- image coordinate
            y -- image coordinate
        """
        self.x = int(x)
        self.y = int(y)


class JoinInfo(object):
    """It keeps join infomation.
    """
    def __init__(self, destination, filename, origin, size):
        """
        Arguments:
            destination -- paste coodinate
            filename -- paste image file
            origin -- source image coodinate
            size -- source image size
        """
        self.destination = destination
        self.filename = filename
        self.origin = origin
        self.size = size

    def destination_box(self):
        """
        Returns:
            destination box giving 4-tuple the left, upper, right, lower.
        """
        return (
            self.destination.x,
            self.destination.y,
            self.destination.x + self.size.width,
            self.destination.y + self.size.height,
            )

    def origin_box(self):
        """
        Returns:
            origin box giving 4-tuple the left, upper, right, lower.
        """
        return (
            self.origin.x,
            self.origin.y,
            self.origin.x + self.size.width,
            self.origin.y + self.size.height,
            )


def read_joininfo(filename, enc='utf-8'):
    u"""read joininfo

    Arguments:
        filename -- join info file name
        enc -- file encoding
    """
    joininfos = []
    f = file(filename)
    for line in f:
        line = line.decode(enc)
        line = line.replace(u'\r', u'').replace(u'\n', u'')
        if not line:
            continue
        if line[0] == u'#':
            continue
        datas = line.split(u',')
        if len(datas) >= 7:
            joininfo = JoinInfo(
                Position(datas[0], datas[1]),
                datas[2].strip(),
                Position(datas[3], datas[4]),
                Size(datas[5], datas[6]),
                )
            joininfos.append(joininfo)
    f.close()

    return joininfos


def get_outputsize(joininfos):
    """calc output size from joininfos

    Arguments:
        joininfos -- JoinInfo list
    """
    min_x = 0
    min_y = 0
    max_x = 0
    max_y = 0
    for joininfo in joininfos:
        (x0, y0, x1, y1) = joininfo.destination_box()
        if x0 < min_x:
            min_x = x0
        if x1 > max_x:
            max_x = x1
        if y0 < min_y:
            min_y = y0
        if y1 > max_y:
            max_y = y1

    return Size(max_x - min_x + 1, max_y - min_y + 1)


def render_image(joininfos, image_path=''):
    """render image by joininfos

    Arguments:
        joininfos -- Joininfo list
        image_path -- image file path
    """
    size = get_outputsize(joininfos)
    im = Image.new('RGBA',
                   (size.width, size.height),
                   (0, 0, 0, 0))

    for joininfo in joininfos:
        fn = os.path.join(image_path, joininfo.filename)
        # cripping
        crip_box = joininfo.origin_box()
        im_src = Image.open(fn).crop(crip_box)
        # copy
        box = joininfo.destination_box()
        im.paste(im_src, box)

    return im


def main():
    """
    """
    usage = "usage: %prog [options] infofile"
    version = "%prog 0.6"
    parser = OptionParser(usage=usage, version=version)
    parser.add_option("-p", "--path", dest="imagepath", default='',
                      help="image file path", metavar="IMAGE_PATH")
    parser.add_option("-o", "--output", dest="output",
                      help="output image file", metavar="OUTPUT_FILE")
    (option, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("infofile is required")

    image_path = option.imagepath
    output = option.output
    infofile = args[0]

    joininfos = read_joininfo(infofile)
    image = render_image(joininfos, image_path)

    if output:
        image.save(output)
    else:
        image.show()


if __name__ == u'__main__':
    main()
