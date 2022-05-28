import cv2
print(cv2.__version__)

cam = cv2.VideoCapture(0)

ret, image = cam.read()

cv2.imwrite("poc/pics/image2.jpg", image)
cam.release()

print("Done!")
