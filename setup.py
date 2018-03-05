import os
from setuptools import setup,find_packages


_INSTALL_REQUIRES = [
    # for the testing framework itself
    "flask",
    "confetti",
    "openpyxl",
    "unicodecsv"
]



setup(
    name = "supplier_reports",
    version = "0.0.4",
    author = "helonicer",
    author_email = "helonicer@gmail.com",
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    install_requires=_INSTALL_REQUIRES,
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    scripts=[
    ],
    entry_points={'console_scripts':['gen_reports=supplier_reports:main']

    },

)
