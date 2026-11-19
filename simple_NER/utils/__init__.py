from os import listdir
from os.path import expanduser, isfile, join

from simple_NER.settings import RESOURES_DIR


def resolve_resource_file(res_name, lang="en-us"):
    """Convert a resource into an absolute filename.

    Resource names are in the form: 'filename.ext'
    or 'path/filename.ext'

    The system wil look for simple_NER/res/res_name first, and
    if not found will look in language subfolders

    Args:
        res_name (str): a resource path/name
    Returns:
        str: path to resource or None if no resource found
    """

    # First look for fully qualified file (e.g. a user setting)
    if isfile(res_name):
        return res_name

    # Next look for /simple_NER/res/res_name
    filename = expanduser(join(RESOURES_DIR, res_name))
    if isfile(filename):
        return filename

    # Next look for /simple_NER/res/{lang}/res_name
    data_dir = join(RESOURES_DIR, lang)
    filename = expanduser(join(data_dir, res_name))
    if isfile(filename):
        return filename

    # Next look for /simple_NER/res/{lang_short}/res_name
    data_dir = join(RESOURES_DIR, lang.split("-")[0])
    filename = expanduser(join(data_dir, res_name))
    if isfile(filename):
        return filename

    # Next look for /simple_NER/res/{lang-short}-XX/res_name
    data_dir = join(RESOURES_DIR)
    for folder in listdir(data_dir):
        if folder.startswith(lang.split("-")[0]):
            filename = expanduser(join(data_dir, folder, res_name))
            if isfile(filename):
                return filename

    return None  # Resource cannot be resolved

