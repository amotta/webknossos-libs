import numpy as np
from os import path
from PIL import Image

from .vendor.dm3 import DM3
from .vendor.dm4 import DM4File


class PillowImageReader:
    def read_array(self, file_name, dtype):
        this_layer = np.array(Image.open(file_name), np.dtype(dtype))
        this_layer = this_layer.swapaxes(0, 1)
        this_layer = this_layer.reshape(this_layer.shape + (1,))
        return this_layer

    def read_dimensions(self, file_name):
        with Image.open(file_name) as test_img:
            return (test_img.width, test_img.height)


def to_target_datatype(data: np.ndarray, target_dtype) -> np.ndarray:

    factor = (1 + np.iinfo(data.dtype).max) / (
            1 + np.iinfo(target_dtype).max
    )
    return (data / factor).astype(np.dtype(target_dtype))


class Dm3ImageReader:
    def read_array(self, file_name, dtype):
        dm3_file = DM3(file_name)
        this_layer = to_target_datatype(dm3_file.imagedata, dtype)
        this_layer = this_layer.swapaxes(0, 1)
        this_layer = this_layer.reshape(this_layer.shape + (1,))
        return this_layer

    def read_dimensions(self, file_name):
        test_img = DM3(file_name)
        return (test_img.width, test_img.height)


class Dm4ImageReader:


    def _read_tags(self, dm4file):

        tags = dm4file.read_directory()
        image_data_tag = tags.named_subdirs['ImageList'].unnamed_subdirs[1].named_subdirs['ImageData']
        image_tag = image_data_tag.named_tags['Data']

        return image_data_tag, image_tag


    def _read_dimensions(self, dm4file, image_data_tag):

        width = dm4file.read_tag_data(image_data_tag.named_subdirs['Dimensions'].unnamed_tags[0])
        height = dm4file.read_tag_data(image_data_tag.named_subdirs['Dimensions'].unnamed_tags[1])
        return width, height


    def read_array(self, file_name, dtype):

        print(1, file_name)

        dm4file = DM4File.open(file_name)
        image_data_tag, image_tag = self._read_tags(dm4file)
        width, height = self._read_dimensions(dm4file, image_data_tag)

        data = np.array(dm4file.read_tag_data(image_tag), dtype=np.uint16)
        data = np.reshape(data, (height, width, 1))
        data = to_target_datatype(data, dtype)

        dm4file.close()
        print(2, file_name)

        return data


    def read_dimensions(self, file_name):
        print(3, file_name)

        dm4file = DM4File.open(file_name)
        image_data_tag, _ = self._read_tags(dm4file)
        dimensions = self._read_dimensions(dm4file, image_data_tag)
        dm4file.close()

        print(4, file_name)

        return dimensions


class ImageReader:
    def __init__(self):
        self.readers = {
            ".tif": PillowImageReader(),
            ".tiff": PillowImageReader(),
            ".jpg": PillowImageReader(),
            ".jpeg": PillowImageReader(),
            ".png": PillowImageReader(),
            ".dm3": Dm3ImageReader(),
            ".dm4": Dm4ImageReader(),
        }

    def read_array(self, file_name, dtype):
        _, ext = path.splitext(file_name)
        return self.readers[ext].read_array(file_name, dtype)

    def read_dimensions(self, file_name):
        _, ext = path.splitext(file_name)
        return self.readers[ext].read_dimensions(file_name)


image_reader = ImageReader()
