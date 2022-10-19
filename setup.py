import os
import sys

_home = os.path.dirname(os.path.abspath(__file__))
print(f'Home: {_home}')
sys.path.insert(0, os.path.abspath(f'{_home}/src/'))

# ---

import setuptools

import photoshow

# ---

def read(fname):
    return open(f'{_home}/{fname}').read()

# ---

setuptools.setup(
    name = "photoshow",
    version = photoshow.__version__,
    author = "rikfair",
    author_email = "mail4rik-pypi@yahoo.com",
    description = "Full screen photo slideshow",
    long_description=read('README.rst'),
    long_description_content_type = "text/x-rst",
    url = "https://github.com/rikfair/photoshow",
    project_urls = {
        "Bug Tracker": "https://github.com/rikfair/photoshow/issues",
        "Documentation": "https://photoshow.readthedocs.io/"
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Multimedia :: Graphics :: Presentation",
        "Topic :: Multimedia :: Graphics :: Viewers",
    ],
    license = "MIT",
    install_requires = ["piexif>=1.1.3", "Pillow>=9.1.0"],
    package_dir = {"": "src"},
    packages = setuptools.find_packages(where="src"),
    python_requires = ">=3.7",
)
