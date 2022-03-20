from BLPackage import BLPackage
from shapely.geometry import Polygon


polygon1 = Polygon([(0, 0), (0.3, 1.8), (2, 2), (2, 0), (0.5, -1)])
polygon2 = Polygon([(0, 1), (1, 1), (1.3, -0.5), (0, 0)])
polygon3 = Polygon([(0, 0.2), (0.5, -0.3), (0.4, 0.2)])

# print(polygon2.within(polygon1))
bl = BLPackage(polygon1)
bl.pack([polygon2, polygon3, polygon3, polygon3])
bl.draw()
# fig,ax = plt.subplots()

# patch1 = PolygonPatch(polygon1)
# patch2 = PolygonPatch(polygon2)

# ax.add_patch(patch1)
# ax.add_patch(patch2)
# ax.set_xlim([0,3])
# ax.set_ylim([0,3])
 


# bias = np.array(polygon2.bounds[-2:]) - np.array(polygon2.centroid.coords[0])

# polygon2 = translate(polygon2, bias[0], bias[1])


# fig,ax = plt.subplots()

# patch1 = PolygonPatch(polygon1)
# patch2 = PolygonPatch(polygon2)

# ax.add_patch(patch1)
# ax.add_patch(patch2)
# ax.set_xlim([0,3])
# ax.set_ylim([0,3])