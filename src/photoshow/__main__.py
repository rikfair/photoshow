"""

DESCRIPTION:
    Enables the slideshow for photos to run via the command line using python -m

ASSUMPTIONS:
    No assumptions to note

LIMITATIONS:
    No accuracy issues to note

"""
# -----------------------------------------------

import sys

import photoshow

# -----------------------------------------------
# pylint: disable=broad-exception-raised
# -----------------------------------------------


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise Exception('Path or parameter file argument expected')

    print('Presenting photoshow')
    photoshow.present(sys.argv[1])
    print('Completed photoshow')


# -----------------------------------------------
# End.
