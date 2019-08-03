'''
Decompiles either one spritesheet, a list of desired spritesheets, or every spritesheet in a given folder into individual sprites, 
giving each spritesheet its own folder. Remembers every nonzero ah, aw, ax, and ay value and the sprites they belong to 
(maybe append these values to the file name, or list them in a separate file?)

- Scales every sprite to a desired scale, and multiplies all the memorized a values by the same scale. 
  Rounds any decimal a values to the nearest integer.
- Recompiles all the sprite folders into their spritesheets (options are PNG, JPEG, JPNG, or initial, warn about recompression for the latter three). 
  Inserts them as demonstrated in this image.

0.1 : First attempt.
0.2 : Fixed exporting animations.

'''

version = "0.2"

from PIL import Image, ImageOps
from xml.etree.ElementTree import parse, Element, SubElement, Comment, tostring
from xml.etree import ElementTree
from os import walk
import os
import argparse
import time

ignored_exts = [".xml"]
valid_img_exts = [".png", ".jpg", ".jpeg"]


def parse_cell( cell, img, img_info, dir_name, sheet_ext ):

    try:
        sprite_x = int(cell.attrib['x'])
        sprite_y = int(cell.attrib['y'])
        sprite_w = int(cell.attrib['w'])
        sprite_h = int(cell.attrib['h'])

        sprite_ax = int(cell.attrib['ax'])
        sprite_ay = int(cell.attrib['ay'])
        sprite_aw = int(cell.attrib['aw'])
        sprite_ah = int(cell.attrib['ah'])

        # Create new image from spritesheet cropped around the target sprite
        sprite_area = ( sprite_x, sprite_y, sprite_x + sprite_w, sprite_y + sprite_h )

        # print("sprite area: " + str(sprite_area[0]) + ", " + str(sprite_area[1]) + ", " + str(sprite_area[2]) + ", " + str(sprite_area[3]) )

        if sprite_area[0] < 0:
            print("too big")
            
        if sprite_area[1] < 0:
            print("too big")

        if sprite_area[2] >= img.width:
            print("too big")
            
        if sprite_area[3] >= img.height:
            print("too big")

        sprite_img = img.crop( sprite_area )

        # Expand border around to rebuild original alpha padding
        alpha_border = (sprite_ax, sprite_ay, sprite_aw - sprite_ax - sprite_w, sprite_ah - sprite_ay - sprite_h)
        sprite_img = ImageOps.expand( sprite_img, alpha_border, 0)

        # Save out sprite
        sprite_img.save( dir_name + cell.attrib['name'] + sheet_ext, **img_info )

    except:
        print("\033[1;31;40m ! Failed to save sprite '" + "', area: " + str(sprite_area))

def explode_spritesheet( sheet_path ):

    # Check the path is valid
    if os.path.exists(sheet_path) == False:
        print ("Could not find file: " + sheet_path)
        return

    # If the path is a folder...
    if os.path.isdir(sheet_path) == True:
        print ("Path is a dir: " + sheet_path)

        # Walk the directory tree and ind every file in it
        sub_files = []
        for (dirpath, dirnames, filenames) in walk(sheet_path):
            sub_files.extend(os.path.join(dirpath, filename) for filename in filenames)

        # Attempt to explode each file
        for sub_file in sub_files:
            explode_spritesheet(sub_file)

        return

    # We got this far and the thing still isn't a file?
    if os.path.isfile(sheet_path) == False:
        print ("Path is not a file: " + sheet_path)
        return

    # Get directory/file tuple
    split_path = os.path.split(sheet_path)

    # Get some useful chunks of the file's full path
    sheet_dir = split_path[0]
    sheet_name = os.path.splitext( split_path[1] )[0]
    sheet_ext = os.path.splitext( sheet_path )[1]

    print ("dir: " + sheet_dir + ", file: " + sheet_name + ", ext: " + sheet_ext)

    # If file extension is an ignored type, silently bail out
    if sheet_ext in ignored_exts:
        return

    # Make sure file extension is valid image type
    if (sheet_ext in valid_img_exts) == False:
        print("Invalid image extension: " + sheet_ext)
        return

    # Build path to accompanying xml
    xml_path = os.path.join(sheet_dir, sheet_name + '.xml')

    # Make sure the xml exists
    if os.path.exists(xml_path) == False:
        print ("Could not find texture xml: " + xml_path)
        return

    # Read image and get info
    img = Image.open( sheet_path )
    img_info = img.info
    
    # make sure output folder path exists
    dir_name = os.path.join("exploded", os.path.join(sheet_dir, sheet_name + '/'))
    if not os.path.exists( dir_name ):
        os.makedirs( dir_name )

    # Open xml file
    texture_xml = parse( xml_path )

    elem_frame_info = texture_xml.getroot().find('FrameInformation')
    
    # For each animation element
    for anim in elem_frame_info.findall('Animation'):
        anim_name = anim.attrib['name']
        # print("Anim: " + anim_name)

        # Create a folder for the animation frame cells
        anim_dir_name = os.path.join(dir_name, anim_name + '/')
        if not os.path.exists( anim_dir_name ):
            os.makedirs( anim_dir_name )

        # Parse each sprite cell in animation
        for cell in anim.findall('Cell'):
            # print("\tAnim frame: " + cell.attrib['name'])

            parse_cell( cell, img, img_info, anim_dir_name, sheet_ext )

    # Parse each sprite cell in xml
    for cell in elem_frame_info.findall('Cell'):
        # print(cell.attrib['name'])

        parse_cell( cell, img, img_info, dir_name, sheet_ext )

    print ("Finished exploding file: " + sheet_path)

    
# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('f', nargs='+')

print("SpriteSheetRebuilder v" + version + ", By Argh")

start = time.time()

# Attempt to handle each value in file list
results = parser.parse_args()
for path in results.f:
    explode_spritesheet( path )

end = time.time()
time_elapsed = end - start
print("Finished in " + str(time_elapsed))
