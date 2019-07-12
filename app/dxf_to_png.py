import dxfgrabber
import cv2
import numpy as np
import sys
#https://gist.github.com/msjamali52/91a96176a1be3313af5d3309cbbf4b06
"""
def absdiff(num1, num2):
    if num1 <= num2:
        return num2 - num1
    else:
        return num1 - num2
"""

def getMinXY(shapes):
    minX, minY = 99999, 99999
    for shape in shapes:
        if shape.dxftype == 'LINE':
            minX = min(minX, shape.start[0], shape.end[0])
            minY = min(minY, shape.start[1], shape.end[1])
        elif shape.dxftype == 'ARC':
            minX = min(minX, shape.center[0])
            minY = min(minY, shape.center[1])

    return minX, minY

def getMaxXY(shapes):
    maxX, maxY = -99999, -99999
    for shape in shapes:
        if shape.dxftype == 'LINE':
            maxX = max(maxX, shape.start[0], shape.end[0])
            maxY = max(maxY, shape.start[1], shape.end[1])
        elif shape.dxftype == 'ARC':
            maxX = max(maxX, shape.center[0])
            maxY = max(maxY, shape.center[1])

    return maxX, maxY

#Translate x,y values as per fourth quadrant i.e positive x and negative y. Update y value to positive, to be used by opencv axes.
# shift origin of image by 100 pixels for better clarity of output image
def getXY(point):
    x, y = point[0], point[1]
    return int(x-minX+100), int(abs(y-maxY)+100)

dxf = dxfgrabber.readfile("GV_12.DXF")
shapes = dxf.entities.get_entities()
minX, minY = getMinXY(shapes)
maxX, maxY = getMaxXY(shapes)
#baseX, baseY = absdiff(minX, 0), absdiff(minY, 0)
#absMaxX, absMaxY = absdiff(maxX, 0), absdiff(maxY, 0)


print(maxX, maxY)
print(minX, minY)
#print(absMaxX, absMaxY)
#print(baseX, baseY)


canvas = np.zeros((512,512,3), np.uint8)
for shape in shapes:
    if shape.dxftype == 'LINE':
        x1, y1 = getXY(shape.start)
        x2, y2 = getXY(shape.end)
        canvas = cv2.line(canvas, (x1,y1), (x2,y2), (255, 0, 255), 1)
    elif shape.dxftype == 'ARC':
        centerX, centerY = getXY(shape.center)
        if (shape.start_angle > 180) and (shape.end_angle < shape.start_angle):
            canvas = cv2.ellipse(canvas, (centerX, centerY), (int(shape.radius), int(shape.radius)), 180, int(shape.start_angle) - 180, 180 + int(shape.end_angle), (0, 0, 255), 1)
        else:
            canvas = cv2.ellipse(canvas, (centerX, centerY), (int(shape.radius), int(shape.radius)), 0, int(360 - shape.start_angle), int(360 - shape.end_angle), (0, 0, 255), 1)
    cv2.imshow('test', canvas)
    cv2.waitKey(50)

# To save canvas use cv2.imwrite()
#cv2.imwrite('res.png', canvas)
cv2.waitKey(0)
cv2.destroyAllWindows()
