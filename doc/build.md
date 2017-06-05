
# BUILDER

## Required ##

    Python 3.6
    Firefox Nightly
    NodeJS
        npm
        jpm
    Thunderbird


## Commands ##

** build a language **

    make.py LANG
        generate the LibreOffice extension and the package folder.
        LANG is the lang code (ISO 639).

        This script uses the file `config.ini` in the folder `gc_lang/LANG`.

** First build **

    Type:
        make.py LANG -js

    This command is required to generate all necessary files.

** options **

    -b --build_data
        Launch the script `build_data.py` in the folder `gc_lang/LANG`.

    -d --dict
        Generate the indexable binary dictionary from the lexicon in the folder `lexicons`.

    -js --javascript
        Also generate JavaScript extensions.
        Without this option only Python modules, data and extensions are generated.

    -t --tests
        Run unit tests.

    -i --install
        Install the LibreOffice extension.

    -fx --firefox
        Launch Firefox Nightly.
        Unit tests can be lanched from Firefox, with CTRL+SHIFT+F12.

    -tb --thunderbird
        Launch Thunderbird.


## Examples ##

    Full rebuild:
        make.py LANG -b -d -js

    After modifying grammar rules:
        make.py LANG -t

    If you modify the lexicon:
        make.py LANG -d -js

    If you modify your script build_data.py:
        make.py LANG -b -js