
'''
    @file sprite_sheet_rebuilder.py
    @date 07/SEP/2019
    @author Stephen
    @brief Tie together the funcionality of the explode and build scripts.
'''

import explode
import build

import os
import time
import argparse

version = "0.4"

print("# SpriteSheetRebuilder v" + version + ", By Argh\n")

# root parser
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest='command')

# explode parser
parser_explode = subparsers.add_parser('explode', help="Explodes a sprite sheet into it's component sprites.")
parser_explode.add_argument('f', nargs='+')

# build parser
parser_build = subparsers.add_parser('build', help="Builds a sprite sheet using given sprites and generates matching xml.")
parser_build.add_argument("sprite_directory", nargs=1)
parser_build.add_argument("output_sheet_name")
parser_build.add_argument("-maxw", type=int, default=4096)
parser_build.add_argument("-maxh", type=int, default=4096)

results = parser.parse_args()


# Explode that sprite sheet
if ( results.command == 'explode' ):

    start = time.time()

    # Attempt to handle each value in file list
    results = parser.parse_args()
    for path in results.f:
        print("# Searching for sprite sheets at: " + path)
        explode.explode_spritesheet( path, "./exploded" )

    end = time.time()
    time_elapsed = end - start
    print("Finished exploding in " + str(time_elapsed))

# Build new sprite sheet
elif ( results.command == 'build' ):

    # Get output file name (ignores extension if given)
    output_texture_name = os.path.splitext( results.output_sheet_name )[0]
    
    start = time.time()

    # build sprite sheet, return size
    texture_wh = build.generate_spritesheet( results.sprite_directory[0], output_texture_name, results.maxw, results.maxh )

    # Convert the auto-generated plist file into the NK xml format, return map of sprites and locations
    map_sprites = build.convert_plist( output_texture_name, texture_wh, results.sprite_directory[0] )

    # Do a final pass on the spritesheet, duplicating edges where appropriate
    build.pad_sprites( map_sprites, output_texture_name )

    end = time.time()
    time_elapsed = end - start
    print("# Finished building in " + str(time_elapsed))

else:
    
    print("You must use either the 'explode' or 'build' commands.")
