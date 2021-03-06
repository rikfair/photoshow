# photoshow

Another photo slideshow module. This one was originally designed to run on a spare Raspberry Pi, with a copy of our photo library on a mounted USB stick, plugged into the back of our main family TV. It plays continuously, so during the ads or while waiting for a programme to start, we can flick the TV source and get a few random photos to reminisce for a moment or two. That's how this slideshow module came about, but it can show any photos, just point it at a folder and it can slideshow all the photos under it.

The slideshow uses the tkinter fullscreen option. To fill the display space nicely, as images have differing ratios, a white saturated abstract image is first created from the photo. This fills the background, with the main photo placed front and centre. An optional caption can be added based on the Exif data, filename, or folder name to complete each slide.

# How to Use

The module can be run directly from the command line. For example for a slideshow of all the photos in the `c:\temp` directory would be: 

```
python -m photoshow c:/temp
```

There are further configurable options, for these you can specifiy a parameter json file, see blow for parameter details.

```
python -m photoshow c:/temp/parameters.json
```

Or imported from another module. Call the present function to run the slides.

```
import photoshow
photoshow.present('c:/temp', caption='detail', delay_time=5)
```

The parameters file can still be used if enbedding in another module.

```
import photoshow
photoshow.present('c:/temp/parameters.json')
```

Parameters can be overridden, preference order is explictly provided, parameter file, default value.

The path parameter normally contains either the photos path or the path for the parameters file.
To override the path in the parameters file, pass the overriding path using the `override_path` parameter.

```
import photoshow
photoshow.present('c:/temp/parameters.json', override_path='c:/myphotos')
```

# Controls

During the slideshow, use the spacebar or mouse button to move on to skip on to the next image, and press escape or mouse double-click to end the show.

# Parameters

Further configuarble parameters, incude whether captions are required and what font should they be in, the time each photo is displayed for, whether the photos should be randomised or played in order, should the slideshow repeat when it reaches the end, plus some others.

- *path*: String, the path to the photo library or the parameter file. This is the only mandatory parameter.
- *caption*: String or boolean, whether a caption should be added to the slide and if so which, options are: `directory`, `detail`, `filename`. Detail will try and use Exif data from the `DateTimeOriginal` and `ImageDescription` elements, falling back to the folder name if data is not found. Use False for no caption. 
- *delay_time*: Int, the time each photo is displayed for, default 15
- *delay_unit*: String, either `M` minutes or `S` seconds, default 'S'
- *font_path*: String, the true type font file, including path. I recommend `Kalam-Bold.ttf` which can be downloaded from [Google Fonts](https://fonts.google.com/specimen/Kalam),
- *max_photos*: Int, the photo limit for the slideshow, enter `0` for unlimited.
- *override_path*: String, use only when the photo path should override the path in the parameters file.
- *random*: Boolean, `true` if photos should be randomised, `false` will play the slides in order
- *repeat*: Boolean, `true` starts over when all photos have been displayed, `false` will end the slideshow after one run through.
- *ignore*: List, of directories and/or files that should not be shown in the slideshow. Only include the path from the `photo_path` location.

The parameters should be kept in a json file, such as:

```
{
  "captions": "detail",
  "delay_time": 2,
  "delay_unit": "S",
  "font_path": "C:/Temp/Kalam-Bold.ttf",
  "max_photos": 0,
  "path": "C:/Temp",
  "random": true,
  "repeat": true,
  "ignore": [
    "C:/Temp/ignoreme",
    "C:/Temp/ignoreonephoto/tipsy.jpg"
  ]
}
```

# Raspberry Pi Dedicated Slideshow Project

Although the photoshow is not solely for the Raspberry Pi, I've used a Pi as an "always on" slideshow. To enable this I've created an extra script and added details to the cron.

First, create a new python file called `wait_and_run.py` and enter the following code. Adjust the paths obviously.

```
import photoshow
import time

wait = 5

for i in range(1, 6):
    print(f'Sleeping...{i * wait}')
    time.sleep(wait)

print('Presenting photoshow')    
photoshow.present('/home/pi/usb1/python/slideshowbob/parameters.json')
print("That's all folks")
```

An issue with the cron is that when it runs the reboot elements, the display is not enabled. To resolve that the above code waits 25 seconds before starting the slides.

Here it uses a json parameter file but any of the options descibed above can be used.

Secondly, add the following reboot line to the cron. (The shutdown line is optional, I reboot the Pi every night due to having flakey wi-fi that sometimes drops after a few days)

```
@reboot DISPLAY=:0 python3 /home/pi/usb1/python/slideshowbob/wait_and_run.py > /home/pi/usb1/python/slideshowbob/cron_reboot.log 2>&1
8 3 * * *  sudo shutdown -r 0
```

Due to the shutdown, I add the following to the end of the `/boot/config.txt` file, to stop the TV turning itself on in the middle of the night.

```
hdmi_ignore_cec_init=1
```

The slideshow should now always be playing when you switch over the TV input.

# Environment

Tested on Python 3.7 and 3.10, on Windows 10 and Raspberry Pi OS.

# Licence

This software is released under the MIT license, see LICENSE.
