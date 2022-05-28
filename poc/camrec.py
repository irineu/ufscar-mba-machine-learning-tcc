import cvlib as cv
import cv2 as opencv

cap = opencv.VideoCapture(0)

while(1):
    ret, frame = cap.read()

    bbox, label, conf = cv.detect_common_objects(frame)
    for i, item in enumerate(label):
        print(item)
    k = opencv.waitKey(30) & 0xFF
    if k == 27:
        break

cap.release()
opencv.destroyAllWindows()
