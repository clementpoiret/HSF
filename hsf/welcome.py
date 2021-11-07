import json

import requests
from packaging.version import parse
from rich import print as pprint

from hsf import __version__


def get_version(url_pattern='https://pypi.python.org/pypi/HSF/json'):
    """Returns version of HSF on pypi.python.org using json."""
    req = requests.get(url_pattern)
    version = parse('0')

    if req.encoding:
        if req.status_code == requests.codes.ok:
            j = json.loads(req.text.encode(req.encoding))
            releases = j.get('releases', [])

            for release in releases:
                ver = parse(release)
                if not ver.is_prerelease:
                    version = max(version, ver)

    return version


def welcome():
    pprint(rf"""

    Hippocampal                            Factory
__/\\\________/\\\_____/\\\\\\\\\\\____/\\\\\\\\\\\\\\\_        
 _\/\\\_______\/\\\___/\\\/////////\\\_\/\\\///////////__       
  _\/\\\_______\/\\\__\//\\\______\///__\/\\\_____________      
   _\/\\\\\\\\\\\\\\\___\////\\\_________\/\\\\\\\\\\\_____     
    _\/\\\/////////\\\______\////\\\______\/\\\///////______    
     _\/\\\_______\/\\\_________\////\\\___\/\\\_____________   
      _\/\\\_______\/\\\__/\\\______\//\\\__\/\\\_____________  
       _\/\\\_______\/\\\_\///\\\\\\\\\\\/___\/\\\_____________ 
        _\///________\///____\///////////_____\///______________
                             Segmentation

                  Copyright (c) 2021 POIRET Clément
                                v{__version__}
                             License: MIT

                *************************************
             NeuroSpin | UNIACT/InsermU1141 | CEA Saclay
                *************************************

        """)
    latest = get_version('https://pypi.python.org/pypi/HSF/json')
    if parse(__version__) < latest:
        pprint(rf"""
A new version of HSF is available (v{str(latest)}).
You can update it by running:
$ pip install --upgrade hsf
        """)
    else:
        pprint("You are using the latest version of HSF.")
