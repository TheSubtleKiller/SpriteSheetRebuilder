explode.exe: 
    Takes a file or folder as an argument and will output a folder named for that texture under the root 'exploded' and fill it with sprites.

explode my_texture.png
OR
explode my_texture_folder


build.exe: 
    Takes a folder as an argument along with an output name, will generate a texture with the given name using sprites under the given folder.
    Also generates the matching sprite xml.

build my_sprite_folder -o my_new_sprite_sheet