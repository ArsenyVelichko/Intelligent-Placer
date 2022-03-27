import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np

from matplotlib.lines import Line2D
from Utils import get_cmap

FLANN_INDEX_KDTREE = 1

# Class for matching objects in the input image to the source set
class ObjectMatcher:
    def __init__(self):
        self.__canny_work_size = (608, 608)
        self.__canny_low_threshold = 100
        self.__canny_high_threshold = 200
        self.__blur_kernel_size = (5,5)
        self.__closing_kernel_size = (5,5)

        self.__sift = cv.SIFT_create()

        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        self.__flann_matcher =  cv.FlannBasedMatcher(index_params, dict())


    def __get_masks(self, img):
        source_size = img.shape[1::-1]

        #Scale the image to a uniform size and find the contours
        resized = cv.resize(img, self.__canny_work_size)
        blur = cv.GaussianBlur(resized, self.__blur_kernel_size, 0)
        canny = cv.Canny(blur, self.__canny_low_threshold, self.__canny_high_threshold)

        #Eliminate small gaps in the contours to make them closed
        kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, self.__closing_kernel_size)
        closing = cv.morphologyEx(canny, cv.MORPH_CLOSE, kernel)
        closing = cv.resize(closing, source_size)

        contours,hierarchy = cv.findContours(closing, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

        #Fill in the insides of all the contours and divide them into individual masks
        masks = []
        for i in range(len(contours)):
            mask = np.zeros(closing.shape, dtype='uint8')
            cv.fillPoly(mask, pts=[contours[i]], color=255)
            masks.append(mask)

        #Return the pairs - mask, contour
        return list(zip(masks, contours))

    def __get_confidence(self, img1, img2):
        #Сalculate the key points and their descriptors
        kp1, des1 = self.__sift.detectAndCompute(img1, None)
        kp2, des2 = self.__sift.detectAndCompute(img2, None)

        matches = self.__flann_matcher.knnMatch(des1, des2, k=2)

        #Filter the matches as shown here
        # https://docs.opencv.org/3.4/d5/d6f/tutorial_feature_flann_matcher.html
        good_count = 0
        for i, (m, n) in enumerate(matches):
            if m.distance < 0.7 * n.distance:
                good_count += 1

        return good_count / len(kp1)


    def match(self, collection, img):
        found_objects = []

        color_map = get_cmap(len(collection))
        unknown_color = np.array([1.0, 0.0, 1.0])
        legend_elements = []
        marked_image = cv.cvtColor(img, cv.COLOR_BGR2RGB)

        #Pair objects in the input image with objects in collection
        # and find the one with the highest confidence
        for i, (mask, contour) in enumerate(self.__get_masks(img)):
            #Cut out the object in the input image
            mask_fg = cv.bitwise_and(img, img, mask=mask)

            max_confidence = 0.1  # lower threshold for confidence
            found_object = None

            for obj in collection.objects():
                #Cut out an object in the image from the collection
                #TODO: Make the collection immediately store the cut objects,
                # and not the entire images, so as not to do the same job several times
                obj_image = obj.image
                obj_mask = self.__get_masks(obj_image)[0][0]
                obj_fg = cv.bitwise_and(obj_image, obj_image, mask=obj_mask)

                confidence = self.__get_confidence(obj_fg, mask_fg)

                if max_confidence < confidence:
                    max_confidence = confidence
                    found_object = obj

            if not found_object is None:
                color = np.array(color_map(i))
                name = found_object.name
                found_objects.append(found_object)

            else:
                name = 'Unknown'
                color = unknown_color

            marked_image = cv.drawContours(marked_image, [contour], 0, 255 * color, 3)
            legend = Line2D([0], [0], marker='o', color=(0, 0, 0, 0),
                            label=name, markerfacecolor=color)
            legend_elements.append(legend)

        fig, ax = plt.subplots()
        ax.imshow(marked_image)
        fig.legend(loc=7, handles=legend_elements)
        plt.tight_layout()
        plt.axis('off')
        plt.show()

        return found_objects