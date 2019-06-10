'''
Decompiles either one spritesheet, a list of desired spritesheets, or every spritesheet in a given folder into individual sprites, 
giving each spritesheet its own folder. Remembers every nonzero ah, aw, ax, and ay value and the sprites they belong to 
(maybe append these values to the file name, or list them in a separate file?)

- Scales every sprite to a desired scale, and multiplies all the memorized a values by the same scale. 
  Rounds any decimal a values to the nearest integer.
- Recompiles all the sprite folders into their spritesheets (options are PNG, JPEG, JPNG, or initial, warn about recompression for the latter three). 
  Inserts them as demonstrated in this image.
  
'''

from PIL import Image, ImageOps
from xml.etree.ElementTree import parse, Element, SubElement, Comment, tostring
from xml.etree import ElementTree
from xml.dom import minidom
import os
import plistlib

from PyTexturePacker import Packer

def explode_spritesheet( sheet_name ):
    img_path = sheet_name + '.png'
    xml_path = sheet_name + '.xml'

    img = Image.open( img_path )
    img_info = img.info
    
    # make sure output folder exists
    dir_name = sheet_name + '/'
    if not os.path.exists( dir_name ):
        os.mkdir( dir_name )

    # Open xml file
    texture_xml = parse( xml_path )

    for cell in texture_xml.getroot().iter('Cell'):
        print(cell.attrib['name'])

        sprite_x = int(cell.attrib['x'])
        sprite_y = int(cell.attrib['y'])
        sprite_w = int(cell.attrib['w'])
        sprite_h = int(cell.attrib['h'])

        sprite_ax = int(cell.attrib['ax'])
        sprite_ay = int(cell.attrib['ay'])
        sprite_aw = int(cell.attrib['aw'])
        sprite_ah = int(cell.attrib['ah'])

        sprite_area = ( sprite_x, sprite_y, sprite_x + sprite_w, sprite_y + sprite_h )
        cropped = img.crop( sprite_area )

        alpha_border = (sprite_ax, sprite_ay, sprite_aw - sprite_ax - sprite_w, sprite_ah - sprite_ay - sprite_h)
        cropped = ImageOps.expand( cropped, alpha_border, 0)

        cropped.save( dir_name + cell.attrib['name'] + '.png', **img_info )


def generate_spritesheet( src_dir, sheet_name ):
    # create a MaxRectsBinPacker
    # See here for argument details: https://github.com/wo1fsea/PyTexturePacker/blob/master/README.rst
    packer = Packer.create( texture_format=".png",
                            max_width=4096, 
                            max_height=4096, 
                            bg_color=(255,255,255,0),
                            enable_rotated=False,
                            force_square=False,
                            border_padding=2,
                            shape_padding=2,
                            inner_padding=False,
                            trim_mode=1,
                            reduce_border_artifacts=False )

    # pack texture images under directory <src_dir> and name the output image[s] as <sheet_name>.
    packer.pack( src_dir, sheet_name )

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="\t")

# Convert PyTexturePacker's auto-generated plist into NK XML format
def convert_plist( plist_name ):
    # Build plist file path
    plist_path = plist_name + '.plist'

    # Read plist file and load data
    f = open(plist_path,"rb")
    plist_contents = plistlib.load( f )

    # Get root dict
    frames = plist_contents['frames']

    metadata = plist_contents['metadata']
    print( metadata['realTextureFileName'] )

    texture_name_type = metadata['realTextureFileName'].split('.')
    texture_wh = metadata['size'][1:-1].split(',')


    xml_root = Element('SpriteInformation')
    xml_frame_info = SubElement(xml_root, 'FrameInformation')
    xml_frame_info.set('name', texture_name_type[0])
    xml_frame_info.set('texw', texture_wh[0])
    xml_frame_info.set('texh', texture_wh[1])
    xml_frame_info.set('type', texture_name_type[1])

    # For each frame in dict
    for frame_key in frames:
        frame = frames[frame_key]

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

        cell = SubElement(xml_frame_info, 'Cell')
        cell.set('name', frame_key)
        cell.set('x', xywh[0])
        cell.set('y', xywh[1])
        cell.set('w', xywh[2])
        cell.set('h', xywh[3])
        cell.set('ax', sourceColorRect[0])
        cell.set('ay', sourceColorRect[1])
        cell.set('aw', sourceSize[0])
        cell.set('ah', sourceSize[1])

    # Write back to file
    xmlstr = prettify(xml_root)
    with open(texture_name_type[0] + '_CONVERT.xml', "w") as f:
        f.write(xmlstr)
        f.close()




src_texture_name = 'boss_death'

explode_spritesheet( src_texture_name )

output_texture_name = 'boss_death_repacked'

generate_spritesheet( src_texture_name, output_texture_name )

convert_plist( output_texture_name )
