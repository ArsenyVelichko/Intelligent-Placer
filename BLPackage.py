from rtree import index
from shapely.geometry import Polygon
from shapely.affinity import translate
from descartes import PolygonPatch

import numpy as np
import matplotlib.pyplot as plt

# Class for packing polygons in a given polygon using the Bottom-left strategy
class BLPackage:

    def __init__(self, boundary_geom):
        self.__boundary_geom = Polygon(boundary_geom)
        
        self.__packedRTree = index.Index()

        self.__init_split_size = 100
        self.__marching_max_iter = 100


    def __generate_init_places(self, geom):
        bounds = self.__boundary_geom.bounds
        top_left = np.array([bounds[0], bounds[3]]) 

        bound_width = bounds[2] - bounds[0]
        step = bound_width / self.__init_split_size

        # Move the centroid of geom to the top left corner of the bounding rectangle
        geom_centroid = np.array(geom.centroid.coords[0])
        bias = top_left - geom_centroid
        geom = translate(geom, xoff=bias[0], yoff=bias[1])

        # Shift the geom left each time and yield result
        for i in range(self.__init_split_size + 1):
            geom = translate(geom, xoff=step, yoff=0.0)
            yield geom


    def pack(self, geom_list):
        # Sort objects by decreasing area
        geom_list = list(map(Polygon, geom_list))
        geom_list.sort(key=lambda poly: poly.area, reverse=True)

        for geom in geom_list:
            pack_success = False

            # Trying to place an object by changing the initial position of the search
            for init_geom in self.__generate_init_places(geom):
                placed = self.__bottom_left_search(init_geom)

                if not placed is None:
                    self.__add_geom(placed)
                    pack_success = True
                    break

            if not pack_success:
                return False

        return True

    # This function determines with what constant step you need to move
    # in order to reach the bottom left point in a given number of iterations
    def __marching_steps(self, geom):
        bounds = self.__boundary_geom.bounds
        bottom_left = np.array([bounds[0], bounds[1]])

        geom_centroid = np.array(geom.centroid.coords[0]) 
        steps = (bottom_left - geom_centroid) / (self.__marching_max_iter - 1)
        return steps


    def __bottom_left_search(self, geom):
        steps = self.__marching_steps(geom)
        shife_left = lambda geom: translate(geom, xoff=steps[0])   
        shife_bottom = lambda geom: translate(geom, yoff=steps[1])

        # Sequentially shift geom as low as possible and as far to the left as possible.
        place_found = False
        while True:
            moved = False

            geom, step = self.__marching(geom, shife_bottom)
            if step >= 0:
                moved = True

            geom, step = self.__marching(geom, shife_left)
            if step >= 0:
                moved = True

            if not moved:
                break
                
            place_found = True

        if place_found:
            return geom
        return None


    def __add_geom(self, geom):
        id = self.__packedRTree.get_size()
        self.__packedRTree.insert(id, geom.bounds, obj=geom)


    # This function tries to find a position where the object
    # can be placed by shifting it by calling the translate function
    def __marching(self, geom, translate):
        result_step = -1
        result = geom

        for i in range(self.__marching_max_iter):
            geom = translate(geom)
            if not self.__checkOverlap(geom):
                result = geom
                result_step = i
                
        return result, result_step 


    # This function checks for intersection with other objects
    # as well as with the bounding polygon
    def __checkOverlap(self, geom):
        if not geom.within(self.__boundary_geom):
            return True

        for n in self.__packedRTree.intersection(geom.bounds, objects=True):
            if n.object.intersects(geom):
                return True

        return False

    def draw(self):
        fig, ax = plt.subplots()
    
        bounds = self.__boundary_geom.bounds
        patch = PolygonPatch(self.__boundary_geom)
        patch.set_fill(False)

        x_margin = 0.1 * (bounds[2] - bounds[0])
        y_margin = 0.1 * ( bounds[3] - bounds[1])

        left = bounds[0] - x_margin
        right = bounds[2] + x_margin
        bottom = bounds[1] - y_margin
        top = bounds[3] + y_margin

        ax.add_patch(patch)
        ax.set_xlim([left, right])
        ax.set_ylim([bottom, top])

        for n in self.__packedRTree.intersection(bounds, objects=True):
            patch = PolygonPatch(n.object)
            ax.add_patch(patch)

        plt.show()
