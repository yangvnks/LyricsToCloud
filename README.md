# LyricsToCloud
LyricsToCloud is a tool that generates a word cloud using lyrics from Billboard Top 100 End of The Year songs.<br>
* Supported years 1960 to 2017
* User specified


## Configuration
* Use the Config.ini file to update the fields you want. 
* 'Font_path' MUST be updated as the default only works on Linux machines.
* 'Font_colors' are matplotlib colormaps whose values can be found online ( see link in Config.ini )
* 'Background' takes a default color value ( see link in Config.ini)

## Usage
* Using Billboard Top 100 End of the Year songs:

```
python LyricsToCloud.py bb 2010 2017 yearly
```
Generates an image for each specified year using the lyrics of Top100 songs.
```
python LyricsToCloud.py bb 2010 2017 timespan
```
Generates a single image by combining all lyrics of the Top100 songs of the specified time span.

* [Work in progress] Lyrics by band:
```
python LyricsToCloud.py band Gorillaz
```

## Example
![lyricloud](https://github.com/yangvnks/LyricsToCloud/blob/master/plot_2000s.png)

## Requirements
```
pip install -r requirements.txt
```
Check out [WordCloud](https://github.com/amueller/word_cloud) - An amazing tool to generate easy word clouds

## Python Version
Works only with Python 2.7
