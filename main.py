
# TODO:
#  - Implement tilesets from OsmAnd map?
#  - Move the 'help_file' key from individual localized to config.ini
#  - Implement scale bar in coord_picker_v2a
#  - BUG - Changing the UI language doesn't work
#  - BUG - Help window is modal, make it Nonmodal so that the user can follow
#    the instructions and operate with the other windows.
#  --------------------------------------------------------------------------------------------------------------------
# DONE:
#  - Remove all the trailing dots, semicolons, etc. from the ui_xxx.ini files
#  - coord_picker_v2a.load_ui_strings() -- Automatically detect the keys present in the specified section of the ini file
#  - Set the main window to show at the center of the display on launch.
#  - Set the tile preview box so that when the zoom is changed the tile zoom value in main window is updated accordingly.
#  - Fix the estimated tile number in the coord_picker_v2a form.
#  - Add tile count and program icon to the download monitor.
#  - Force the DL Monitor to be foreground
#  - Do not show multiple instances of confirmation prompt
#  - Adjust the size of the download monitor.
#  - Change the download text in the monitor, when paused it will be "Paused", otherwise it will show the progress
#  - In the Download Monitor, intercept window closure ( [x] ) so that the window is closed gracefully instead of
#    throwing exceptions.

from pathlib import Path

import coord_picker_v2a
import globals
import lat_lon_tileid
import inifile_access
import fileaccess
import png_from_osm_v2


# -------------------------------------------------------------------------------------------------------------------
appinfo = f'{globals.APPNAME} v.{globals.APPVERSION} - {globals.APPINFO}'

print(f'{appinfo}')

output_picture = 'PngMap.png'
#  Restore configuration
ini = inifile_access.IniManager('config.ini')

# Launch the Coordinate picker to get the bbox of the wanted area
user_selection = coord_picker_v2a.select_bbox()
    # Output from user_selection:
    #   [0]             ->  (lat, lon) of top-left bbox corner (tuple)
    #   [1]             ->  (lat, lon) of bottom-right bbox corner (tuple)
    #   [2]             ->  requested map style >(i.e. 'mapnik')
    #   [3]             ->  requested map zoom
    #   [4], [5] etc.   ->  other information not used for download

xx = ini.getkeys('general')

if user_selection:
    # Ask for the output file name, through a selection window
    language = ini.getvalue('general', 'language')
    ui_ini = inifile_access.IniManager(Path('lang') / f'ui_{language}.ini')
    savedir = ini.getvalue('tile_download', 'savedir')
    prompt = ui_ini.getvalue('save_file', 'prompt')
    allfiles = ui_ini.getvalue('save_file', 'all_files')
    pngfiles = ui_ini.getvalue('save_file', 'png_files')
    filetypes = [(allfiles, '*.*'), (pngfiles, '*.png')]

    filename = fileaccess.select_output_file(
        initial_dir=savedir,
        default_extension='.png',
        filetypes=filetypes, prompt=prompt,
    )

    # Download the required tiles
    if filename:
        ini.setvalue('tile_download', 'savedir', Path(filename).parent)
        min_xy = lat_lon_tileid.latlon_to_tile(user_selection[0][0], user_selection[0][1], user_selection[3])
        max_xy = lat_lon_tileid.latlon_to_tile(user_selection[1][0], user_selection[1][1], user_selection[3])
        tilezoom = user_selection[3]
        mapstyle = user_selection[2]
        # Start downloading
        n_tiles = png_from_osm_v2.get_tiles(
            min_xy[0],
            max_xy[0],
            min_xy[1],
            max_xy[1],
            tilezoom,mapstyle,
            filename
        )
        print(f"\n {n_tiles} tiles merged into single picture '{filename}'.")

pass