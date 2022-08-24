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


def _add_captions(parameters, filename, exif_data, bgi):
    """ Extracts text from the filename and the path, then adds the captions to the image """

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

    # ---

    if caption1:
        bgi = bgi.transpose(Image.Transpose.ROTATE_270)  # noqa
        bgd = ImageDraw.Draw(bgi)
        bgd.text((21, 11), caption1, font=parameters[_FONT_BIG], fill='white')
        bgd.text((20, 10), caption1, font=parameters[_FONT_BIG], fill='darkslateblue')
        bgd.text((31, 71), caption2, font=parameters[_FONT_SMALL], fill='white')
        bgd.text((30, 70), caption2, font=parameters[_FONT_SMALL], fill='slateblue')
        bgi = bgi.transpose(Image.Transpose.ROTATE_90)  # noqa

    return bgi


# -----------------------------------------------


def _create_image(parameters, win, filename):
    """ Create an image based on the photo """

    photo = Image.open(filename)

    # Get EXIF data and rotate image if necessary
    try:
        exif_data = piexif.load(photo.info['exif'])
        orientation = exif_data.get('0th', {}).get(piexif.ImageIFD.Orientation, 0)
        if orientation == 3:
            photo = photo.transpose(Image.Transpose.ROTATE_180)  # noqa
        elif orientation == 6:
            photo = photo.transpose(Image.Transpose.ROTATE_270)  # noqa
        elif orientation == 8:
            photo = photo.transpose(Image.Transpose.ROTATE_90)   # noqa
    except AttributeError as err:
        print(f'EXIF Attribute Error: {filename} : {err}')
        exif_data = {}

    # Get image size
    ratios = win.winfo_screenwidth() / photo.size[0], win.winfo_screenheight() / photo.size[1]
    # Resize background, bigger than screen, then crop
    ratio = max(ratios) * 1.2
    bg_size = int(photo.size[0] * ratio), int(photo.size[1] * ratio)
    left = int((bg_size[0] - win.winfo_screenwidth()) / 2)
    top = int((bg_size[1] - win.winfo_screenheight()) / 2)
    # Background image: Greyscale, Blur and Brightness
    bgi = Image.new('RGBA', bg_size)
    bgi.paste(photo.resize(bg_size, Image.Resampling.LANCZOS).convert('L'), (0, 0))  # noqa
    bgi = bgi.crop((left, top, (left + win.winfo_screenwidth()), (top + win.winfo_screenheight())))
    bgi = bgi.filter(ImageFilter.GaussianBlur(radius=6))
    # Blend white image to fade the background
    bgi = Image.blend(bgi, Image.new('RGBA', bgi.size, color=(255, 255, 255)), 0.7)
    # Add photo to background
    ratio = min(ratios) * 0.95
    fg_width = int(photo.size[0] * ratio)
    fg_height = int(photo.size[1] * ratio)
    photo = photo.resize((fg_width, fg_height), Image.Resampling.LANCZOS)  # noqa Anti-Alias
    left = int((win.winfo_screenwidth() - fg_width) / 2)
    top = int((win.winfo_screenheight() - fg_height) / 2)
    bgi.paste(photo, (left, top))
    # Add captions to image
    if parameters[_CAPTIONS]:
        bgi = _add_captions(parameters, filename, exif_data, bgi)

    return ImageTk.PhotoImage(bgi)


# -----------------------------------------------


def _format_path(path):
    """ Formats a path easier comparison """

    return path.upper().replace('/', '?').replace('\\', '?')


# -----------------------------------------------


def _get_month(mth):
    """ Returns the month number as text """

    return datetime.datetime.strptime(mth, '%m').strftime('%B')


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
        for key, val in parameters.items():
            if key not in kwargs:
                kwargs[key] = val
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
    if font_path and not os.path.isfile(font_path):
        raise Exception(f"Font not found: {font_path}")
    if not font_path:
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

        fmt_path = _format_path(path)
        for i in parameters[_IGNORE]:
            if fmt_path.startswith(i):
                return True
        return False

    # ---

    photos_list = []
    home = parameters[_PATH]

    for root, _, files in os.walk(home):
        if not ignore_path(root):
            for img_name in files:
                if img_name.lower().endswith('.jpg') or img_name.lower().endswith('.jpeg'):
                    img_path = os.path.join(root, img_name)
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
    random_list = []

    if photo_count:
        for _ in range(photo_count):
            rno = random.randrange(len(photo_list))
            random_list.append(photo_list[rno])
            photo_list.pop(rno)

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
    win.geometry(f'{win.winfo_screenwidth()}x{win.winfo_screenheight()}+0+0')
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
        except Exception as err:                # pylint: disable=broad-except
            print(f'Error: {filename}, {err}')  # Catch, print, and carry on
            continue

        parameters[_NEXT_PHOTO] = False
        win.update()

        if parameters[_RUN]:
            win.bind('<Button>', lambda _: _skip_photo(parameters))
            win.bind('<space>', lambda _: _skip_photo(parameters))

        for _ in range(parameters[_DELAY]):
            if not parameters[_RUN] or parameters[_NEXT_PHOTO]:
                break
            win.update()
            time.sleep(1)  # Repeat the sleep to improve bind reactions

        if not parameters[_RUN]:
            break


# -----------------------------------------------

if __name__ == '__main__':
    # For development, testing and debugging
    present('/temp/photoshow/parameters.json')

# -----------------------------------------------
# End.
