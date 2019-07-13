"""
A module to handle Futrli configuration files.

Configuration files are looked for at the root of the current user's
home directory, in a file called ``.futrli``, by default.

Configuration files are JSON format, with a top-level dictionary that
includes configuration such as email, password, and organisation_id
(note the spelling of organisation, to match Futrli).

"""
import os.path
import json
import logging

DEFAULT_FILENAME = '~/.futrli'


def get_configuration(filename=None):
    """Returns Futrli configuration as a dictionary.

    If configuration isn't found, return an empty dict.
    """
    if not filename:
        filename = DEFAULT_FILENAME
    config_file = os.path.expanduser(filename)
    try:
        with open(config_file, 'r') as c_file:
            return json.load(c_file)
    except OSError:
        logging.getLogger('futrli').warning(
            'No configuration found at location: %s', filename)
        return {}
