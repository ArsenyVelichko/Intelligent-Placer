import cv2 as cv

from ObjectsCollection import ObjectsCollection
from ObjectMatching import ObjectMatcher

def main():
    collection = ObjectsCollection('config.txt')
    test_image = cv.imread('test_data/input1.jpg')

    matcher = ObjectMatcher()
    found_objects = matcher.match(collection, test_image)
    for found_object in found_objects:
        print(found_object.name)


if __name__ == '__main__':
    main()
