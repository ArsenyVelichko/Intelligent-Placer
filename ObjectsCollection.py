import numpy as np
import cv2 as cv

from configparser import ConfigParser
from dataclasses import dataclass
from Utils import parse_poly

class ObjectsCollection:

    @dataclass
    class ObjectInfo:
        name: str
        image: np.ndarray
        polygon: np.ndarray


    def __init__(self, config_path):
        parser = ConfigParser()
        parser.read(config_path)

        self.__objects = []
        for name in parser.sections():
            image_path = parser[name]['image']
            image = cv.imread(image_path)

            polygon = parse_poly(parser[name]['polygon'])

            info = self.ObjectInfo(name, image, np.array(polygon))
            self.__objects.append(info)

        print("Number of loaded objects: {}".format(len(self.__objects)))

    def __len__(self):
        return len(self.__objects)

    def objects(self):
        return self.__objects