import importlib.resources as pkg_resources

import PIL.Image


def img_from_resource(package: pkg_resources.Package, resource: pkg_resources.Resource):
    with pkg_resources.open_binary(package, resource) as f:
        image = PIL.Image.open(f)
        image.load()
    return image
