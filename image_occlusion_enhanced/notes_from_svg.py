# -*- coding: utf-8 -*-
####################################################
##                                                ##
##           Image Occlusion Enhanced             ##
##                                                ##
##        Copyright (c) Glutanimate 2016          ##
##       (https://github.com/Glutanimate)         ##
##                                                ##
##     Original Image Occlusion 2.0 add-on is     ##
##         Copyright (c) 2012-2015 tmbb           ##
##           (https://github.com/tmbb)            ##
##                                                ##
####################################################

import tempfile
import copy
import os

from svgutils import *
import add_notes


# attributes that are useless in the shapes layer
# (stroke and opacity settings)
useless_attribs = ['opacity',
                   'stroke-opacity',
                   'fill-opacity',
                   'stroke-dasharray',
                   'stroke-linecap',
                   'stroke-linejoin',
                   'stroke']

def generate_nonoverlapping(svg, q_color):
    fnames_q_svg = gen_fnames_q(tmp_media_dir, nr_of_cards, 'svg')
    fnames_a_svg = gen_fnames_a(tmp_media_dir, nr_of_cards, 'svg')
    # Generate the question sides of the cards:
    for i in xrange(nr_of_cards):
        svg_i = copy.deepcopy(svg)
        shapes_layer = svg_i[curr_shapes_index]
        set_color_recursive(shapes_layer[i+1], q_color)  # <title>
        set_id(shapes_layer[i+1], 'question-element')
        strip_attributes(svg_i, useless_attribs)
        f = open(fnames_q_svg[i], 'w')
        f.write(etree.tostring(svg_i))
        f.close()

    # Generate the answer sides of the cards:
    for i in xrange(nr_of_cards):
        svg_i = copy.deepcopy(svg)
        shapes_layer = svg_i[curr_shapes_index]
        shapes_layer.remove(shapes_layer[i+1])
        strip_attributes(svg_i, useless_attribs)
        f = open(fnames_a_svg[i], 'w')
        f.write(etree.tostring(svg_i))
        f.close()

def generate_overlapping():
    fnames_q_svg = gen_fnames_q(tmp_media_dir, nr_of_cards, 'svg')
    fname_a_svg = gen_fnames_a(tmp_media_dir, 1, 'svg')[0]
    # Generate the question sides of the cards:
    for i in xrange(nr_of_cards):
        #  We use a deep copy because we will be destructively modifying
        # the variable svg_i
        svg_i = copy.deepcopy(svg)
        shapes_layer = svg_i[curr_shapes_index]
        shapes = [shapes_layer[j+1] for j in xrange(nr_of_cards)] # j+1 stays because
          # we want the modifications to be destructive. Bad style, but whatever...
        j = 0
        for shape in shapes:
            if j == i:
                set_color_recursive(shape, q_color)
                set_id(shape, 'question-element')
            else:
                shapes_layer.remove(shape)
            j = j + 1
        strip_attributes(svg_i, useless_attribs)

        f = open(fnames_q_svg[i], 'w')
        f.write(etree.tostring(svg_i))
        f.close()

    svg_a = copy.deepcopy(svg)
    svg_a[curr_shapes_index].clear()
    svg_a.remove(svg_a[0])
    # Generate the answer side of the cards:
    f = open(fname_a_svg, 'w')
    f.write(etree.tostring(svg_a)) # Write dummy file
    f.close()

def add_notes_now(choice, svg, did, onote):
    # onote fields  tags, fname_original, header, footer, remarks, sources, 
    # extra1, extra2, 
    q_color = ""
    svg = copy.deepcopy(svg)
    print etree.tostring(svg)
    curr_shapes_index = get_shapes_layer_idx(svg)
    nr_of_cards = nr_of_shapes(svg, curr_shapes_index)
    tmp_media_dir = tempfile.mkdtemp(prefix="media-for-anki")

    strip_attributes(svg, useless_attribs)
    svg_fname = os.path.join(tmp_media_dir, "fmask.svg")
    f = open(svg_fname, 'w')
    f.write(etree.tostring(svg))
    f.close()

    if choice == "nonoverlapping":
        generate_nonoverlapping()
    elif choice == "overlapping":
        generate_overlapping()


    add_notes.gui_add_QA_notes(fnames_q_svg, fnames_a_svg,
                               tmp_media_dir, tags, svg_fname, fname_original,
                               header, footer, remarks, sources, 
                               extra1, extra2, did)

    return tmp_media_dir

def add_notes_non_overlapping(svg, q_color, tags, fname_original,
                              header, footer, remarks, sources, 
                              extra1, extra2, did):
    svg = copy.deepcopy(svg)

    print etree.tostring(svg)

    # The index of the shapes layer
    curr_shapes_index = get_shapes_layer_idx(svg)

    # The number of cards that will be generated.
    nr_of_cards = nr_of_shapes(svg, curr_shapes_index)

    # Get a temporary directory to store the images
    tmp_media_dir = tempfile.mkdtemp(prefix="media-for-anki")


    strip_attributes(svg, useless_attribs)
    svg_fname = os.path.join(tmp_media_dir, "fmask.svg")
    f = open(svg_fname, 'w')
    f.write(etree.tostring(svg))
    f.close()

    fnames_q_svg = gen_fnames_q(tmp_media_dir, nr_of_cards, 'svg')
    fnames_a_svg = gen_fnames_a(tmp_media_dir, nr_of_cards, 'svg')

    # Generate the question sides of the cards:
    for i in xrange(nr_of_cards):
        svg_i = copy.deepcopy(svg)
        shapes_layer = svg_i[curr_shapes_index]
        set_color_recursive(shapes_layer[i+1], q_color)  # <title>
        set_id(shapes_layer[i+1], 'question-element')
        strip_attributes(svg_i, useless_attribs)
        f = open(fnames_q_svg[i], 'w')
        f.write(etree.tostring(svg_i))
        f.close()

    # Generate the answer sides of the cards:
    for i in xrange(nr_of_cards):
        svg_i = copy.deepcopy(svg)
        shapes_layer = svg_i[curr_shapes_index]
        shapes_layer.remove(shapes_layer[i+1])
        strip_attributes(svg_i, useless_attribs)
        f = open(fnames_a_svg[i], 'w')
        f.write(etree.tostring(svg_i))
        f.close()

    add_notes.gui_add_QA_notes(fnames_q_svg, fnames_a_svg,
                               tmp_media_dir, tags, svg_fname, fname_original,
                               header, footer, remarks, sources, 
                               extra1, extra2, did)

    return tmp_media_dir


def add_notes_overlapping(svg, q_color, tags, fname_original,
                          header, footer, remarks, sources, 
                          extra1, extra2, did):
    
    svg = copy.deepcopy(svg)

    # The index of the shapes layer
    curr_shapes_index = get_shapes_layer_idx(svg)

    # The number of cards that will be generated.
    nr_of_cards = nr_of_shapes(svg, curr_shapes_index)

    # Get a temporary directory to store the images
    tmp_media_dir = tempfile.mkdtemp(prefix="media-for-anki")

    strip_attributes(svg, useless_attribs)
    svg_fname = os.path.join(tmp_media_dir, "source_svg.svg")
    f = open(svg_fname, 'w')
    f.write(etree.tostring(svg))
    f.close()

    fnames_q_svg = gen_fnames_q(tmp_media_dir, nr_of_cards, 'svg')
    fname_a_svg = gen_fnames_a(tmp_media_dir, 1, 'svg')[0]

    # Generate the question sides of the cards:
    for i in xrange(nr_of_cards):
        #  We use a deep copy because we will be destructively modifying
        # the variable svg_i
        svg_i = copy.deepcopy(svg)
        shapes_layer = svg_i[curr_shapes_index]
        shapes = [shapes_layer[j+1] for j in xrange(nr_of_cards)] # j+1 stays because
          # we want the modifications to be destructive. Bad style, but whatever...
        j = 0
        for shape in shapes:
            if j == i:
                set_color_recursive(shape, q_color)
                set_id(shape, 'question-element')
            else:
                shapes_layer.remove(shape)
            j = j + 1
        strip_attributes(svg_i, useless_attribs)

        f = open(fnames_q_svg[i], 'w')
        f.write(etree.tostring(svg_i))
        f.close()

    svg_a = copy.deepcopy(svg)
    svg_a[curr_shapes_index].clear()
    svg_a.remove(svg_a[0])
    # Generate the answer side of the cards:
    f = open(fname_a_svg, 'w')
    f.write(etree.tostring(svg_a)) # Write dummy file
    f.close()

    # add notes, updating the GUI:
    add_notes.gui_add_QA_notes(fnames_q_svg, [fname_a_svg]*nr_of_cards,
                               tmp_media_dir, tags, svg_fname, fname_original,
                               header, footer, remarks, sources, 
                               extra1, extra2, did)

    return tmp_media_dir
