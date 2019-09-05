
'''
0.1 : First attempt.
0.2 : Fixed rebuilding with animations.
0.3 : Sprite edge duplication.
0.3.1 : Sprite edge duplication fixes, still WiP.

'''

from PIL import Image, ImageOps
from xml.etree.ElementTree import parse, Element, SubElement, Comment, tostring
from xml.etree import ElementTree
from xml.dom import minidom
from PyTexturePacker import Packer
import os
import plistlib
import argparse
import time


version = "0.3.1"

def generate_spritesheet( src_dir, sheet_name ):

    print("# Generating sprite sheet from sprites found in \"" + src_dir + "\"...")
    print("# \tPacking sprites (this may take a minute for larger sheets)...")

    texture_border_padding = 2

    # create a MaxRectsBinPacker
    # See here for argument details: https://github.com/wo1fsea/PyTexturePacker/blob/master/README.rst
    packer = Packer.create( texture_format=".png",
                            max_width=4096, 
                            max_height=4096, 
                            bg_color=(255,255,255,0),
                            enable_rotated=False,
                            # force_square=False,
                            border_padding=texture_border_padding,
                            shape_padding=2,
                            inner_padding=1,
                            trim_mode=1,
                            reduce_border_artifacts=True )

    # pack texture images under directory <src_dir> and name the output image[s] as <sheet_name>.
    packer.pack( src_dir, sheet_name )

    print("# \tCropping sheet...")

    # Read image and get info
    new_img_path = sheet_name + ".png"
    img = Image.open( new_img_path )
    img_info = img.info

    tweaked_bbox = img.getbbox()
    cropped_bbox = img.convert("RGBa").getbbox()

    if ( cropped_bbox == None ):
        bands = ""
        for band in img.getbands():
            bands += band + ","
        print( "!# \tFailed to convert image to pre-multiplied alpha, skipping cropping step, image bands: " + bands )
    else:
        # we know the 0/0 top left point is fine, but add border padding to the cropped w/h
        tweaked_bbox = (0, 0, cropped_bbox[2] + texture_border_padding, cropped_bbox[3] + texture_border_padding)

        # crop
        img = img.crop( tweaked_bbox )

    print("# \tSaving sheet...")

    # Re-save texture
    img.save( new_img_path, **img_info )

    return tweaked_bbox
    

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="\t")

def get_immediate_subdirectories(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]

# Convert PyTexturePacker's auto-generated plist into NK XML format
def convert_plist( plist_name, bbox, src_dir ):

    print("# Generating xml...")

    print("# \tSearching for animations for special formatting...")

    # keep track of deepest image we've found
    deepest_depth = 0
    # keep track of image and parent directory
    map_image_parent_dir = {}

    # walk the directory tree
    for (dirpath, dirnames, filenames) in os.walk(src_dir):
        # for every file
        for filename in filenames:
            # get depth in tree
            sep_count = dirpath.count('/') + dirpath.count('\\')

            # if depth is greater than greatest depth we've seen so far
            if ( sep_count > deepest_depth ):
                # store new deepes depth
                deepest_depth = sep_count
                # nuke the dict, we only want the deepest images
                map_image_parent_dir = {}

            # add new image/dir pair
            map_image_parent_dir[filename] = os.path.basename(dirpath)

            # print( "Depth: " + str(dirpath.count(os.sep)) + " or " + str(sep_count) + ", " + dirpath )

    # Build plist file path
    plist_path = plist_name + '.plist'


    print("# \tLoading plist...")

    # Read plist file and load data
    f_plist = open(plist_path,"rb")
    plist_contents = plistlib.load( f_plist )
    f_plist.close()

    # Get root dict
    frames = plist_contents['frames']

    metadata = plist_contents['metadata']
    # print( metadata['realTextureFileName'] )

    texture_name_type = metadata['realTextureFileName'].split('.')
    texture_wh = metadata['size'][1:-1].split(',')


    print("# \tConverting to xml...")

    xml_root = Element('SpriteInformation')
    xml_frame_info = SubElement(xml_root, 'FrameInformation')
    xml_frame_info.set('name', texture_name_type[0])
    xml_frame_info.set('texw', str(bbox[2]) ) # texture_wh[0]
    xml_frame_info.set('texh', str(bbox[3]) )  # texture_wh[1]
    xml_frame_info.set('type', texture_name_type[1])

    current_anim = ""

    anim = None

    map_sprites = {}

    # For each frame in dict
    for frame_key in frames:
        frame = frames[frame_key]

        sprite_name = os.path.splitext(frame_key)[0]
        xywh = frame['frame']
        xywh = xywh.replace('{', '')
        xywh = xywh.replace('}', '')
        xywh = xywh.split(',')
        offset = frame['offset']
        rotated = frame['rotated']
        sourceColorRect = frame['sourceColorRect']
        sourceColorRect = sourceColorRect.replace('{', '')
        sourceColorRect = sourceColorRect.replace('}', '')
        sourceColorRect = sourceColorRect.split(',')
        sourceSize = frame['sourceSize']
        sourceSize = sourceSize.replace('{', '')
        sourceSize = sourceSize.replace('}', '')
        sourceSize = sourceSize.split(',')
        # print ( frame['frame'] )

        map_sprites[sprite_name] = {'x': xywh[0],'y': xywh[1],'w': xywh[2],'h': xywh[3],'ax': sourceColorRect[0],'ay': sourceColorRect[1],'aw': sourceSize[0],'ah': sourceSize[1]}

        cell = None

        if frame_key in map_image_parent_dir:
            new_anim = map_image_parent_dir[frame_key]
            if new_anim != current_anim:
                current_anim = new_anim
                anim = SubElement(xml_frame_info, 'Animation')
                anim.set('name', current_anim)
            
            cell = SubElement(anim, 'Cell')
        else:

            cell = SubElement(xml_frame_info, 'Cell')
        
        cell.set('name', sprite_name)
        cell.set('x', xywh[0])
        cell.set('y', xywh[1])
        cell.set('w', xywh[2])
        cell.set('h', xywh[3])
        cell.set('ax', sourceColorRect[0])
        cell.set('ay', sourceColorRect[1])
        cell.set('aw', sourceSize[0])
        cell.set('ah', sourceSize[1])

    print("# \tFormatting and writing xml...")

    # Write back to file
    xmlstr = prettify(xml_root)
    with open(texture_name_type[0] + '.xml', "w") as f_xml:
        f_xml.write(xmlstr)
        f_xml.close()

    os.remove( plist_path )

    return map_sprites

def pad_sprites( map_sprites, sheet_name ):
    print("# \tDuplicating sprite egdes...")

    # Read image and get info
    new_img_path = sheet_name + ".png"
    img = Image.open( new_img_path )

    pixels = img.load() # create the pixel map

    for k, v in map_sprites.items():

        # left edge
        x = int(v['x'])
        y = int(v['y'])
        w = int(v['w'])
        h = int(v['h'])
        
        ax = int(v['ax'])
        ay = int(v['ay'])
        aw = int(v['aw'])
        ah = int(v['ah'])
        
        # Left
        if ax == 0:
            # print("Duplicated left edge for sprite " + k)
            _x = x
            for _y in range(y, y+h):
                if _y % 2 == 0 or True:
                    pixels[_x-1, _y] = pixels[_x, _y]
                else:
                    pixels[_x-1, _y] = (255,0,0,255)

        # Right
        if aw-ax == w:
            # print("Duplicated right edge for sprite " + k)
            _x = x + w - 1
            for _y in range(y, y+h):
                if _y % 2 == 0 or True:
                    pixels[_x+1, _y] = pixels[_x, _y]
                else:
                    pixels[_x+1, _y] = (255,0,0,255)

        # Top
        if ay == 0:
            # print("Duplicated top edge for sprite " + k)
            _y = y
            for _x in range(x, x+w):
                if _x % 2 == 0 or True:
                    pixels[_x, _y-1] = pixels[_x, _y]
                else:
                    pixels[_x, _y-1] = (255,0,0,255)
            
        # Bottom
        if ah-ay == h:
            # print("Duplicated bottom edge for sprite " + k)
            _y = y + h - 1
            for _x in range(x, x+w):
                if _x % 2 == 0 or True:
                    pixels[_x, _y+1] = pixels[_x, _y]
                else:
                    pixels[_x, _y+1] = (255,0,0,255)
        
    img.save( new_img_path )


# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("dir", nargs=1)
parser.add_argument("-o", "-output_name")
results = parser.parse_args()

output_texture_name = results.o

start = time.time()

print("### SpriteSheetRebuilder v" + version + ", By Argh ###")

bbox = generate_spritesheet( results.dir[0], output_texture_name )


map_sprites = convert_plist( output_texture_name, bbox, results.dir[0] )

pad_sprites( map_sprites, output_texture_name )

end = time.time()
time_elapsed = end - start
print("# Finished in " + str(time_elapsed))
