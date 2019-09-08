OVERVIEW:

sprite_sheet_rebuilder.exe Can be invoked via the commandline to either break a sprite sheet into it's component sprites, or to do the reverse and build a sprite sheet from a given folder of sprites and also generate a matching xml.


HOW TO USE:

Open Command Prompt, can be found by typing "cmd" into windows search bar, hit enter.
Navigate to the directory you have downloaded the exe into, you can do this by typing "cd " then dragging the folder from explorer onto the Command Prompt window.

EXPLODE:

To explode a sprite sheet:
> sprite_sheet_rebuilder explode my_spritesheets/cool_spritesheet.png"
This will create a folder next to the executable named 'exploded' with a subfolder for your exploded texture.
The explode command can accept multiple inputs, and these inputs do not have to be single images, it will also accept folders which will be recursively searched and every sprite sheet found within will be exploded.

REBUILD:

To build a new sprite sheet:
> sprite_sheet_rebuilder build my_folder_of_sprites my_new_sprite_sheet
This will search for sprites recursively in the given folder and use them to generate a sprite sheet and matching xml file ready for use in game.
