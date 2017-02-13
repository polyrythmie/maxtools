#!/usr/bin/env python
from distutils.core import setup

install_requires = [
    'abjad[development]',
    ]

def main():
    setup(
        author='Ryn El Fa9sa',
        author_email='rynelfa9sa@gmail.com',
        install_requires=install_requires,
        name='maxtools',
        packages=('maxtools',),
        version='0.2',
        zip_safe=False,
        )

if __name__ == '__main__':
    main()
