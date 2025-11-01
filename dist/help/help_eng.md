# 🗺️ OSM to PNG
This program was born out of a need to combine multiple tiles from the OSM map into a single large image that included the entire extension of a city, with a zoom factor allowing to read street names.

The starting point was the script *png_from_osm.py*, found on the webpage *https://bikingaroundagain.com/make-paper-maps-osm-data*, along with other small utilities.

The original Python v.2 script was adapted to work in Python v. 3.12; I also added a simple GUI allowing to select the bounding box (bbox) directly from the map and set the zoom factor to download.


<br>

## Area selection on the map

On program start-up, an interactive OpenStreetMap map is shown. The view can be moved by dragging with the mouse; change the zoom with the mouse wheel.

Center the window on the desired location and resize it to include the entire desired area; You can also search for the wanted location via the *Nominatim* service, by just typing its name (for example: *Milan*) in the *Location Search* text box and clicking on the *Search* button.

Adjust the map zoom with the [+] and [-] buttons in the upper left corner of the map or with the mouse wheel. 

> **IMPORTANT** - *The bbox is defined by the window borders, so it will enclose the entire displayed area; The current map zoom DOES NOT affect the zoom factor of the downloaded tiles; it must be set manually (see below).*

## Setting tile download
Select the desired map style among those available from the *Map style* dropdown list.

> **ATTENTION** - *The styles other than "Mapnik (OSM)" are provided by the Thunderforest service; to view and download them you need to enter an "API Key", which can be obtained by registering on the site https://www.thunderforest.com; the free plan allows you to download 150,000 tiles every month.*

Use the *Tile zoom* control to set the desired zoom factor for the downloaded tiles (this control DOES NOT change the zoom of the map displayed in the window); on the right, you can read the number of tiles to download to cover the entire area, and an estimate of their overall weight in Megabytes.

Click the *Tile Preview* button to check the actual zoom and level of detail set for download in a pop-up window. 
 


 
## Downloading the tiles
Click on the *Start* button to begin downloading the images of the area corresponding to the desired style and zoom factor. 

Select the directory and the output file name (extension must be *.png*); click on the *Save* button to start the operations.

> **ATTENTION** - *This operation uses online services and may take a long time. The OpenStreetMap and Thunderforest servers are not designed to handle massive operations: the program tries to behave respectfully and sends its requests at a quite slow rate, with frequent pauses.*



## Other program settings
In the area selection screen, click the [⚙️] button, in the top right corner of the window.

The menu allows to set:
**Font size** used in program window
**API Key**, needed to get the style tiles provided by thunderforest.com (Cyclemap, Transport, etc).  
To obtain an API Key, just visit the *https://www.thunderforest.com* web page,  sign up for a new account (a valid email address in required), then log in. 
The Free plan offered by Thunderforest.com allows downloading up to 150,000 tiles per month. The amount should be fine for non-intensive use of the service: for example, to obtain the entire area of Milan (Italy) at zoom 17 (where all the street names are visible) about 11,000 tiles are needed (~7% of the entire quota)

**OpenStreetMap email**: required to obtain the Mapnik tiles, native to the OpenStreetMap project. Any email address can be used, but it's a good idea to sign up to the project at *https://www.openstreetmap.org* with a valid email address and use that in the program.    
OpenstreetMap doesn't set any limit to the number of downloadable tiles, but recommends the users "not to send an excessive number of requests" (also aquite generic concept): for intensive use, using a local tile server is more recommended. 
By design, the program interfaces with the OSM public server, sending its requests at a slow pace, in order not to overload it.

**Interface language**: Select the desired language from those available.

<br>

## Translating the user interface into a different language
The UI language is defined by *.ini* files located in the */lang* directory:

  1: With a File Manager, reach the folder where the main program is located (osm2png)

  2: Access the */lang* directory

  3: Create a copy of one of the files present by replacing the language suffix with the on desired.   
For example, to create a French translation, copy *ui_eng.ini* (English language) to *ui_fra.ini*.

  4: Open the new file and translate all the strings presetne on the right of the "=" characters.
 
	-> Example: *zoom_map_label = Map zoom:* will become *zoom_map_label = Zoom de la carte:*

  5: Save the file and restart the program: the new language should be available in the settings menu.

<br>

## Translating the help file into a different language

To translate the help file, go to the */help* directory and copy one of the existing files by replacing the language suffix, for example *help-eng.md* --> *help-fra.md*; Help files are just text files written in Markdown format: they can be edited with any text editor such as *Notepad* in Windows, however it's recommended to use an editor that also allows preview of the result, such as *Visual Studio Code* (*https://code.visualstudio.com/download*) or *Ghostwriter* (*https://github.com/KDE/ghostwriter*)

A literal translation is not required, however the structure of this document should be kept.


