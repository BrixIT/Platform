from glob import glob
import yaml


def get_packages():
    for file in glob('/opt/platform/packages/*/*/*.yml'):
        yield yaml.safe_load(open(file))
