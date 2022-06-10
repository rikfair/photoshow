#!/usr/bin/python3
# -----------------------------------------------
"""
    DESCRIPTION:
        Slideshow for photos

    ASSUMPTIONS:
        No assumptions to note

    ACCURACY:
        No accuracy issues to note
"""
# -----------------------------------------------

import json
import os
import random
import re
import time
import tkinter as tk

import piexif
from PIL import ImageTk, Image, ImageDraw, ImageFont, ImageFilter

# -----------------------------------------------

_RE_FOLDER_PREFIX = re.compile(r'^[\d\-~]* ')

# -----------------------------------------------


def _create_image(parameters, win, filename):
    """ Create an image based on the photo """

    photo = Image.open(filename)

    # Get EXIF data to rotate image if necessary
    try:
        exif = dict(photo._getexif().items())  # noqa, using protected class function for convenience
        if 274 in exif and exif[274] not in [0, 1]:
            if exif[274] == 3:
                photo = photo.transpose(Image.Transpose.ROTATE_180)
            elif exif[274] == 6:
                photo = photo.transpose(Image.Transpose.ROTATE_270)
            elif exif[274] == 8:
                photo = photo.transpose(Image.Transpose.ROTATE_90)
            else:
                print(f'274: {exif[274]} : {filename}')
    except AttributeError as e:
        print(f'EXIF Attribute Error: {filename} : {e}')

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
    bg.paste(photo.resize((bg_width, bg_height), Image.Resampling.LANCZOS).convert('L'), (0, 0))  # Anti-Alias
    bg = bg.crop((left, top, (left + win.winfo_screenwidth()), (top + win.winfo_screenheight())))
    bg = bg.filter(ImageFilter.GaussianBlur(radius=6))

    # Blend white image to fade the background
    wi = Image.new('RGBA', bg.size, color=(255, 255, 255))
    bg = Image.blend(bg, wi, 0.7)

    # Add photo to background
    ratio = min(wratio, hratio) * 0.95
    fg_width = int(photo_width * ratio)
    fg_height = int(photo_height * ratio)
    photo = photo.resize((fg_width, fg_height), Image.Resampling.LANCZOS)  # Anti-Alias
    left = int((win.winfo_screenwidth() - fg_width) / 2)
    top = int((win.winfo_screenheight() - fg_height) / 2)
    bg.paste(photo, (left, top))

    # Add captions to image
    caption1, caption2 = _get_captions(parameters, filename, photo)
    if caption1:
        bg = bg.transpose(Image.Transpose.ROTATE_270)
        d = ImageDraw.Draw(bg)
        caption1, caption2 = _get_captions(parameters, filename, photo)
        d.text((21, 11), caption1, font=parameters['font_big'], fill='white')
        d.text((20, 10), caption1, font=parameters['font_big'], fill='darkslateblue')
        d.text((31, 71), caption2, font=parameters['font_small'], fill='white')
        d.text((30, 70), caption2, font=parameters['font_small'], fill='slateblue')
        bg = bg.transpose(Image.Transpose.ROTATE_90)

    return ImageTk.PhotoImage(bg)


# -----------------------------------------------


def _format_path(path):
    """ Formats a path easier comparison """

    return path.upper().replace('/', '?').replace('\\', '?')


# -----------------------------------------------


def _get_captions(parameters, filename, photo):
    """ Extracts text from the filename and the path. """

    caption2 = ''

    if parameters['captions'] == 'directory':
        caption1 = os.path.basename(os.path.dirname(filename))
    elif parameters['captions'] == 'filename':
        caption1 = os.path.basename(filename)
    elif parameters['captions'] == 'detail':
        try:
            exif_dict = piexif.load(photo.info['exif'])
            exif_date = exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal].decode()
            caption1 = f'{_get_month(exif_date[5:7])} {exif_date[:4]}'
            caption2 = os.path.basename(filename)
        except KeyError:
            caption1 = ''
        else:
            description = ''
            if '0th' in exif_dict and piexif.ImageIFD.ImageDescription in exif_dict['0th']:
                description += exif_dict['0th'][piexif.ImageIFD.ImageDescription].decode().strip()
            if not description:
                folder = os.path.basename(os.path.dirname(filename))
                folder_prefix = re.match(_RE_FOLDER_PREFIX, folder)
                if folder_prefix and len(folder_prefix.group(0)) > 8:
                    description = folder.split(' ', 1)[1]
                else:
                    description = folder
            if description:
                caption1 += f': {description}'

    else:
        caption1 = ''

    return caption1, caption2


# -----------------------------------------------


def _get_month(m):
    """ Returns the month number as text """

    return {
        '01': 'January',
        '02': 'Feburary',
        '03': 'March',
        '04': 'April',
        '05': 'May',
        '06': 'June',
        '07': 'July',
        '08': 'August',
        '09': 'September',
        '10': 'October',
        '11': 'November',
        '12': 'December'
    }[m]


# -----------------------------------------------


def _get_next_photo(parameters):
    """ Generator to loop through the photos """

    while True:
        photo_list = _get_photo_list(parameters)  # Refresh the list
        for i in photo_list:
            yield i
        if not parameters['repeat']:
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
    else:
        kwargs['path'] = path

    # Check path exists

    if 'path' not in kwargs:
        raise Exception('No path provided')
    if not os.path.isdir(kwargs['path']):
        raise Exception(f"Path is not a directory: {kwargs['path']}")

    # Check for font if provided

    font_path = kwargs.get('font_path', '')
    font_exists = os.path.isfile(font_path) if font_path else ''
    if font_path and not font_exists:
        raise Exception(f"Font not found: {font_path}")

    # Return provided parameter or default values

    delay_time = int(kwargs.get('delay_time', 15))
    delay_unit = kwargs.get('delay_unit', 'S')

    return {
        'captions': kwargs.get('captions', False),
        'delay': delay_time * {'M': 60}.get(delay_unit, 1),
        'font_big': ImageFont.truetype(font_path, 40) if font_exists else None,
        'font_small': ImageFont.truetype(font_path, 16) if font_exists else None,
        'max_photos': kwargs.get('max_photos', 0),
        'path': kwargs['path'],
        'random': kwargs.get('random', True),
        'repeat': kwargs.get('repeat', True),
        'ignore': [_format_path(os.path.join(path, i)) for i in kwargs.get('ignore', [])],
        'next_photo': False,
        'run': True
    }


# -----------------------------------------------


def _get_photo_list(parameters):
    """ Returns a List of photo paths """

    # ---

    def ignore_path(path):
        """ Checks the ignore list """

        fp = _format_path(path)
        for p in parameters['ignore']:
            if fp.startswith(p):
                return True
        return False

    # ---

    photos_list = []
    home = parameters['path']

    for root, _, files in os.walk(home):
        if not ignore_path(root):
            for img in [f for f in files if f.lower().endswith('.jpg') or f.lower().endswith('.jpeg')]:
                img_path = os.path.join(root, img)
                if not ignore_path(img_path):
                    photos_list.append(img_path)

    if parameters['random']:
        return _get_photo_list_random(parameters, photos_list)

    return photos_list


# -----------------------------------------------


def _get_photo_list_random(parameters, photo_list):
    """
    Gets a list of photos to display
    :return: List of photo filenames
    """

    max_photos = parameters['max_photos']
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

    parameters['next_photo'] = True


# -----------------------------------------------


def _stop(win, parameters):
    """ Stop the slideshow """

    win.destroy()
    parameters['run'] = False


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
    win.bind('<Button>', lambda _: _skip_photo(parameters))
    win.bind('<space>', lambda _: _skip_photo(parameters))
    win.picture_display = tk.Label(win)
    win.picture_display.pack()
    win.focus_set()

    # ---

    for filename in _get_next_photo(parameters):
        try:
            image = _create_image(parameters, win, filename)
            win.picture_display.config(image=image, borderwidth=0, highlightthickness=0)
        except Exception as e:
            print(f'Error: {filename}, {e}')
            continue

        parameters['next_photo'] = False
        win.update()

        for s in range(parameters['delay']):
            if not parameters['run'] or parameters['next_photo']:
                break
            win.update()
            time.sleep(1)  # Repeat the sleep to improve bind reactions

        if not parameters['run']:
            break


# -----------------------------------------------
# End.
