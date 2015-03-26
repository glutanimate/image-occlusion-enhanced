import os
import base64
import urllib


from Imaging.PIL import Image  # PIL.Image will only be used in 3 lines of code
import etree.ElementTree as etree

image_layer_index = 0
shapes_layer_index = 1

blank_svg_path = os.path.join(os.path.dirname(__file__),
                             "blank-svg.svg")


def strip_attributes(root, attrs):
    for elt in root.iter():
        for attr in attrs:
            elt.attrib.pop(attr, None)


def image2svg(im_path, embed_image=True):
    ### Only part of the code that uses PIL ######
    im = Image.open(im_path)
    width, height = im.size
    fmt = im.format.lower()
    ### End of PIL ###############################

    if embed_image:
        f = open(im_path, 'rb')
        im_contents = f.read()
        f.close()
        b64 = base64.b64encode(im_contents)
        #im_href = "data:image/" + fmt + ";base64," + base64.b64encode(im_contents)
        im_href = "data:image/{0};base64,{1}".format(fmt, b64)
    else:
        im_href = "file:" + urllib.pathname2url(im_path)

    ### SVG ###
    doc = etree.parse(blank_svg_path)
    svg = doc.getroot()
    svg.set('width', str(width))
    svg.set('height', str(height))
    svg.set('xmlns:xlink', "http://www.w3.org/1999/xlink")
    ### Use descriptive variables for the layers
    image_layer = svg[image_layer_index]
    shapes_layer = svg[shapes_layer_index]
    ### Create the 'image' element
    image = etree.SubElement(image_layer, 'image')
    image.set('x', '0')
    image.set('y', '0')
    image.set('height', str(height))
    image.set('width', str(width))
    image.set('xlink:href', im_href)  # encode base64
    ###
    svg_content = etree.tostring(svg)  # remove
    #### Very Ugly Hack Ahead !!!
    hack_head, hack_body = svg_content.split('\n', 1)
    hack_head = hack_head[:-1]
    hack_head = ''.join([hack_head, ' xmlns="http://www.w3.org/2000/svg">'])
    svg_content = '\n'.join([hack_head, hack_body])
    #### END HACK

    svg_b64 = "data:image/svg+xml;base64," + base64.b64encode(svg_content)

    return {'svg': svg_content,
            'svg_b64': svg_b64,
            'height': height,
            'width': width}


# Copied from 'simplestyle.py', from the Inkscape project
def parseStyle(s):
    """Create a dictionary from the value of an inline style attribute"""
    if s is None:
        return {}
    else:
        return dict([i.split(":") for i in s.split(";") if len(i)])


# Copied from 'simplestyle.py', from the Inkscape project
def formatStyle(a):
    """Format an inline style attribute from a dictionary"""
    return ";".join([att + ":" + str(val) for att, val in a.iteritems()])


def nr_of_shapes(svg):
    return len(svg[shapes_layer_index]) - 1  # subtract one because of <title>


def set_color(elt, color):
    elt.attrib["fill"] = "#" + color


#  Applies the change of color to the children of the
# children and so on. Useful when we want to color shapes
# that are part of a group.
def set_color_recursive(elt, color):
    for e in elt.iter():
        set_color(e, color)


##### Functions to generate filenames: ###################################
### ext is the file extension (e.g. 'svg', 'png')
def gen_fnames(q_or_a, dir, nr_of_cards, ext):

    def basename(i):
        return "{q_or_a} {i}.{ext}".format(q_or_a=q_or_a,
                                           i=str(i),
                                           ext=ext)

    return [os.path.join(dir, basename(i)) for i in xrange(nr_of_cards)]


# Question side of the cards:
def gen_fnames_q(dir, nr_of_cards, ext):
    return gen_fnames('Q', dir, nr_of_cards, ext)


# Answer side of the cards:
def gen_fnames_a(dir, nr_of_cards, ext):
    return gen_fnames('A', dir, nr_of_cards, ext)
###########################################################################