import cv2
def onMouse(event, x, y, flags, params):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(x, y)

img = cv2.imread('omura.png')
cv2.imshow('omura', img)
cv2.setMouseCallback('omura', onMouse)
cv2.waitKey(0)


