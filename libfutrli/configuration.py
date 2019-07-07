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


def get_configuration(filename='~/.futrli'):
    """Returns Futrli configuration as a dictionary.

    If configuration isn't found, return an empty dict.
    """
    config_file = os.path.expanduser(filename)
    try:
        with open(config_file, 'r') as c_file:
            return json.load(c_file)
    except OSError:
        return {}
