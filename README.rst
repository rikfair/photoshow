Photoshow - *"Fullscreen continuous slideshow"*
===============================================

.. image:: https://www.codefactor.io/repository/github/rikfair/photoshow/badge/main
   :target: https://www.codefactor.io/repository/github/rikfair/photoshow/overview/main
   :alt: CodeFactor

.. image:: https://github.com/rikfair/photoshow/actions/workflows/pylint.yml/badge.svg
   :target: https://github.com/rikfair/photoshow/actions/workflows/pylint.yml
   :alt: pylint

Another python photo slideshow module. This one was originally designed to run on a spare Raspberry Pi I had available.
With a copy of our photo library on a mounted USB stick,
the Raspberry Pi was plugged into one of the spare HDMI sockets the back of the main family TV, photoshow running continuously.
During the ads or while waiting for a programme to start, we can flick the TV source and get a few random photos to reminisce for a moment or two.

That's how this slideshow module came to be, but it can show any photos. Just point it at a folder and it can slideshow all the photos under it.

The slideshow uses the tkinter fullscreen option. To fill the display space nicely, as images have differing ratios,
a white saturated abstract image is first created from the photo.
This fills the background, with the main photo placed front and centre.
An optional caption can be added based on the Exif data, filename, or folder name to complete each slide.

View the documentation for options and examples
