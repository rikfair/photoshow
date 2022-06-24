#!/usr/bin/python3
# -----------------------------------------------
"""
    DESCRIPTION:
        Slideshow for photos
        The new Pillow constants are causing errors to be flagged in the IDE.
        These have been marked with noqa for now, until it can be addressed.

    ASSUMPTIONS:
        No assumptions to note

    ACCURACY:
        No accuracy issues to note
"""
# -----------------------------------------------

import datetime
import json
import os
import random
import re
import time
import tkinter as tk

import piexif
from PIL import ImageTk, Image, ImageDraw, ImageFont, ImageFilter

# -----------------------------------------------

_CAPTIONS = 'captions'
_DELAY = 'delay'
_DELAY_TIME = 'delay_time'
_DELAY_UNIT = 'delay_unit'
_FONT_BIG = 'font_big'
_FONT_PATH = 'font_path'
_FONT_SMALL = 'font_small'
_MAX_PHOTOS = 'max_photos'
_NEXT_PHOTO = 'next_photo'
_OVERRIDE_PATH = 'override_path'
_PATH = 'path'
_RANDOM = 'random'
_RUN = 'run'
_REPEAT = 'repeat'
_IGNORE = 'ignore'

# ---

_RE_FOLDER_PREFIX = re.compile(r'^[\d\-~]* ')

# -----------------------------------------------


def _create_image(parameters, win, filename):
    """ Create an image based on the photo """

    photo = Image.open(filename)

    # Get EXIF data to rotate image if necessary
    try:
        exif_data = piexif.load(photo.info['exif'])
        orientation = exif_data.get(piexif.ImageIFD.Orientation, 0)
        if orientation == 3:
            photo = photo.transpose(Image.Transpose.ROTATE_180)  # noqa
        elif orientation == 6:
            photo = photo.transpose(Image.Transpose.ROTATE_270)  # noqa
        elif orientation == 8:
            photo = photo.transpose(Image.Transpose.ROTATE_90)   # noqa
    except AttributeError as e:
        print(f'EXIF Attribute Error: {filename} : {e}')
        exif_data = {}

    # Get image size
    photo_width, photo_height = photo.size
    wratio = win.winfo_screenwidth() / photo_width
    hratio = win.winfo_screenheight() / photo_height

    # Resize background, bigger than screen, then crop
    ratio = max(wratio, hratio) * 1.2
    bg_width = int(photo_width * ratio)
    bg_height = int(photo_height * ratio)
    left = int((bg_width - win.winfo_screenwidth()) / 2)
    top = int((bg_height - win.winfo_screenheight()) / 2)
    # Background image: Greyscale, Blur and Brightness
    bg = Image.new('RGBA', (bg_width, bg_height))
    bg.paste(photo.resize((bg_width, bg_height), Image.Resampling.LANCZOS).convert('L'), (0, 0))  # noqa
    bg = bg.crop((left, top, (left + win.winfo_screenwidth()), (top + win.winfo_screenheight())))
    bg = bg.filter(ImageFilter.GaussianBlur(radius=6))

    # Blend white image to fade the background
    wi = Image.new('RGBA', bg.size, color=(255, 255, 255))
    bg = Image.blend(bg, wi, 0.7)

    # Add photo to background
    ratio = min(wratio, hratio) * 0.95
    fg_width = int(photo_width * ratio)
    fg_height = int(photo_height * ratio)
    photo = photo.resize((fg_width, fg_height), Image.Resampling.LANCZOS)  # noqa Anti-Alias
    left = int((win.winfo_screenwidth() - fg_width) / 2)
    top = int((win.winfo_screenheight() - fg_height) / 2)
    bg.paste(photo, (left, top))

    # Add captions to image
    if parameters[_CAPTIONS]:
        caption1, caption2 = _get_captions(parameters, filename, exif_data)
        if caption1:
            bg = bg.transpose(Image.Transpose.ROTATE_270)  # noqa
            d = ImageDraw.Draw(bg)
            d.text((21, 11), caption1, font=parameters[_FONT_BIG], fill='white')
            d.text((20, 10), caption1, font=parameters[_FONT_BIG], fill='darkslateblue')
            d.text((31, 71), caption2, font=parameters[_FONT_SMALL], fill='white')
            d.text((30, 70), caption2, font=parameters[_FONT_SMALL], fill='slateblue')
            bg = bg.transpose(Image.Transpose.ROTATE_90)   # noqa

    return ImageTk.PhotoImage(bg)


# -----------------------------------------------


def _format_path(path):
    """ Formats a path easier comparison """

    return path.upper().replace('/', '?').replace('\\', '?')


# -----------------------------------------------


def _get_captions(parameters, filename, exif_data):
    """ Extracts text from the filename and the path. """

    caption2 = ''

    if parameters[_CAPTIONS] == 'directory':
        caption1 = os.path.basename(os.path.dirname(filename))
    elif parameters[_CAPTIONS] == 'filename':
        caption1 = os.path.basename(filename)
    elif parameters[_CAPTIONS] == 'detail':
        if 'Exif' in exif_data:
            exif_date = exif_data['Exif'][piexif.ExifIFD.DateTimeOriginal].decode()
            caption1 = f'{_get_month(exif_date[5:7])} {exif_date[:4]}'
            caption2 = os.path.basename(filename)
        else:
            caption1 = ''
        # ---
        description = ''
        if '0th' in exif_data and piexif.ImageIFD.ImageDescription in exif_data['0th']:
            description += exif_data['0th'][piexif.ImageIFD.ImageDescription].decode().strip()
        if not description:
            folder = os.path.basename(os.path.dirname(filename))
            folder_prefix = re.match(_RE_FOLDER_PREFIX, folder)
            if folder_prefix and len(folder_prefix.group(0)) > 8:
                description = folder.split(' ', 1)[1]
            else:
                description = folder
        if description:
            caption1 += (': ' if caption1 else '') + description

    else:
        caption1 = ''

    return caption1, caption2


# -----------------------------------------------


def _get_month(m):
    """ Returns the month number as text """

    return datetime.datetime.strptime(m, '%m').strftime('%B')


# -----------------------------------------------


def _get_next_photo(parameters):
    """ Generator to loop through the photos """

    while True:
        photo_list = _get_photo_list(parameters)  # Refresh the list
        for i in photo_list:
            yield i
        if not parameters[_REPEAT]:
            break


# -----------------------------------------------


def _get_parameters(path, **kwargs):
    """ Sets the parameters, adding defaults if not set """

    # Read json file if path contains a json file

    if path.lower().endswith('.json'):
        with open(path, encoding='utf-8') as file:
            parameters = json.load(file)
        for k, v in parameters.items():
            if k not in kwargs:
                kwargs[k] = v
        if _OVERRIDE_PATH in kwargs:
            kwargs[_PATH] = _OVERRIDE_PATH
    else:
        kwargs[_PATH] = path

    # Check path exists

    if _PATH not in kwargs:
        raise Exception('No path provided')
    if not os.path.isdir(kwargs[_PATH]):
        raise Exception(f"Path is not a directory: {kwargs[_PATH]}")

    # Check for font if provided

    font_path = kwargs.get(_FONT_PATH, '')
    font_exists = os.path.isfile(font_path) if font_path else ''
    if not font_exists:
        if font_path:
            raise Exception(f"Font not found: {font_path}")
        else:
            font_path = 'arial.ttf'

    # Return provided parameter or default values

    delay_time = int(kwargs.get(_DELAY_TIME, 15))
    delay_unit = kwargs.get(_DELAY_UNIT, 'S')

    return {
        _CAPTIONS: kwargs.get(_CAPTIONS.lower(), False),
        _DELAY: delay_time * {'M': 60}.get(delay_unit, 1),
        _FONT_BIG: ImageFont.truetype(font_path, 40),
        _FONT_SMALL: ImageFont.truetype(font_path, 16),
        _MAX_PHOTOS: kwargs.get(_MAX_PHOTOS, 0),
        _PATH: kwargs[_PATH],
        _RANDOM: kwargs.get(_RANDOM, True),
        _REPEAT: kwargs.get(_REPEAT, True),
        _IGNORE: [_format_path(os.path.join(path, i)) for i in kwargs.get(_IGNORE, [])],
        _NEXT_PHOTO: False,
        _RUN: True
    }


# -----------------------------------------------


def _get_photo_list(parameters):
    """ Returns a List of photo paths """

    # ---

    def ignore_path(path):
        """ Checks the ignore list """

        fp = _format_path(path)
        for p in parameters[_IGNORE]:
            if fp.startswith(p):
                return True
        return False

    # ---

    photos_list = []
    home = parameters[_PATH]

    for root, _, files in os.walk(home):
        if not ignore_path(root):
            for img in [f for f in files if f.lower().endswith('.jpg') or f.lower().endswith('.jpeg')]:
                img_path = os.path.join(root, img)
                if not ignore_path(img_path):
                    photos_list.append(img_path)

    if parameters[_RANDOM]:
        return _get_photo_list_random(parameters, photos_list)

    return photos_list


# -----------------------------------------------


def _get_photo_list_random(parameters, photo_list):
    """
    Gets a list of photos to display
    :return: List of photo filenames
    """

    max_photos = parameters[_MAX_PHOTOS]
    photo_count = min(max_photos, len(photo_list)) if max_photos else len(photo_list)
    random_list = list()

    if photo_count:
        for i in range(photo_count):
            rn = random.randrange(len(photo_list))
            random_list.append(photo_list[rn])
            photo_list.pop(rn)

    return random_list


# -----------------------------------------------


def _skip_photo(parameters):
    """ Shows the next photo """

    parameters[_NEXT_PHOTO] = True


# -----------------------------------------------


def _stop(win, parameters):
    """ Stop the slideshow """

    win.destroy()
    parameters[_RUN] = False


# -----------------------------------------------


def present(path, **kwargs):
    """
    Run the photo slideshow
    :param path: String, the root path for the photos
    :param kwargs: The parameters, see documentation.
    """

    parameters = _get_parameters(path, **kwargs)
    win = tk.Tk()
    win.overrideredirect(True)
    win.overrideredirect(False)
    win.attributes('-fullscreen', True)
    win.geometry('%dx%d+0+0' % (win.winfo_screenwidth(), win.winfo_screenheight()))
    win.configure(background='black', cursor='none')
    win.bind('<Escape>', lambda _: _stop(win, parameters))
    win.bind('<Double-Button>', lambda _: _stop(win, parameters))
    win.picture_display = tk.Label(win)
    win.picture_display.pack()
    win.focus_set()

    # ---

    for filename in _get_next_photo(parameters):
        win.unbind('<Button>')
        win.unbind('<space>')

        try:
            image = _create_image(parameters, win, filename)
            win.picture_display.config(image=image, borderwidth=0, highlightthickness=0)
        except Exception as e:
            print(f'Error: {filename}, {e}')
            continue

        parameters[_NEXT_PHOTO] = False
        win.update()

        if parameters[_RUN]:
            win.bind('<Button>', lambda _: _skip_photo(parameters))
            win.bind('<space>', lambda _: _skip_photo(parameters))

        for s in range(parameters[_DELAY]):
            if not parameters[_RUN] or parameters[_NEXT_PHOTO]:
                break
            win.update()
            time.sleep(1)  # Repeat the sleep to improve bind reactions

        if not parameters[_RUN]:
            break


# -----------------------------------------------
# End.
