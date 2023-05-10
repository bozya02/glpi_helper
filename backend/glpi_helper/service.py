import cv2
import numpy as np
import pyzbar.pyzbar as pyzbar

def read(file):
    inp = np.asarray(bytearray(file), dtype=np.uint8)
    img = cv2.imdecode(inp, cv2.IMREAD_COLOR)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite('gray.jpg', gray)

    edges = cv2.Canny(gray, 50, 150)
    cv2.imwrite('edges.jpg', edges)

    contours, hierarchy = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        approx = cv2.approxPolyDP(contour, 0.01 * cv2.arcLength(contour, True), True)
        if len(approx) == 4:
            rect = cv2.minAreaRect(contour)
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            cv2.drawContours(img, [box], 0, (0, 0, 255), 2)

    decodedObjects = pyzbar.decode(gray)

    content = None
    for obj in decodedObjects:
        content = obj.data.decode('utf-8')
        print("Data: ", content)
    return content
