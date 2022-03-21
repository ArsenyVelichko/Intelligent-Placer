import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np

FLANN_INDEX_KDTREE = 1

class ObjectMatcher:
    def __init__(self):
        self.__sift = cv.SIFT_create()
        self.__canny_work_size = (608, 608)
        self.__canny_low_threshold = 100
        self.__canny_high_threshold = 200
        self.__blur_kernel_size = (5,5)
        self.__closing_kernel_size = (5,5)


    def __get_masks(self, img):
        source_size = img.shape[1::-1]
        resized = cv.resize(img, self.__canny_work_size)
        blur = cv.GaussianBlur(resized, self.__blur_kernel_size, 0)
        canny = cv.Canny(blur, self.__canny_low_threshold, self.__canny_high_threshold)

        kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, self.__closing_kernel_size)
        closing = cv.morphologyEx(canny, cv.MORPH_CLOSE, kernel)
        closing = cv.resize(closing, source_size)

        # plt.imshow(closing,cmap='gray'),plt.show()
        contours,hierarchy = cv.findContours(closing, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

        masks = []
        for i in range(len(contours)):
            mask = np.zeros(closing.shape, dtype='uint8')
            cv.fillPoly(mask, pts=[contours[i]], color=255)
            # plt.imshow(mask, cmap='gray'), plt.show()
            masks.append(mask)

        return masks

    def __get_confidence(self, img1, img2):
        kp1, des1 = self.__sift.detectAndCompute(img1, None)
        kp2, des2 = self.__sift.detectAndCompute(img2, None)

        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        flann = cv.FlannBasedMatcher(index_params, dict())
        matches = flann.knnMatch(des1, des2, k=2)

        # matchesMask = [[0, 0] for i in range(len(matches))]
        good_count = 0
        for i, (m, n) in enumerate(matches):
            if m.distance < 0.7 * n.distance:
                good_count += 1
                # matchesMask[i] = [1, 0]

        # draw_params = dict(matchColor=(0, 255, 0),
        #                    singlePointColor=(255, 0, 0),
        #                    matchesMask=matchesMask,
        #                    flags=cv.DrawMatchesFlags_DEFAULT)
        # img3 = cv.drawMatchesKnn(img1, kp1, img2, kp2, matches, None, **draw_params)
        # plt.imshow(img3, ), plt.show()

        return good_count / len(kp1)


    def match(self, collection, img):
        found_objects = []
        masks = self.__get_masks(img)

        for i in range(len(masks)):
            mask_fg = cv.bitwise_and(img, img, mask=masks[i])

            max_confidence = 0.1  # low threshold for confidence
            found_object = None

            for obj in collection.objects():
                obj_image = obj.image
                obj_mask = self.__get_masks(obj_image)[0]
                obj_fg = cv.bitwise_and(obj_image, obj_image, mask=obj_mask)

                confidence = self.__get_confidence(obj_fg, mask_fg)

                if max_confidence < confidence:
                    max_confidence = confidence
                    found_object = obj

            if not found_object is None:
                found_objects.append(found_object)

        return found_objects