from glob import glob
import yaml
import urllib.parse
import os


def get_packages():
    for file in glob('/opt/platform/packages/*/*/*.yml'):
        yield yaml.safe_load(open(file))


def build_package_filename(url):
    # <scheme>://<netloc>/<path>;<params>?<query>#<fragment>
    scheme, host, path, params, query, fragment = urllib.parse.urlparse(url)
    package_file = "/opt/platform/packages/{}/{}".format(host, path.replace('.git', '.yml'))
    return package_file


def has_package(url):
    return os.path.isfile(build_package_filename(url))


def get_package(url):
    return yaml.safe_load(open(build_package_filename(url)))
