import cvlib as cv
import cv2 as opencv
from cvlib.object_detection import draw_bbox

cap = opencv.VideoCapture(0)
cap.set(opencv.CAP_PROP_FRAME_WIDTH, 224)
cap.set(opencv.CAP_PROP_FRAME_HEIGHT, 224)
cap.set(opencv.CAP_PROP_FPS, 36)

count = 1

while(1):
    ret, frame = cap.read()
    print("a") #alto custo computacional
    bbox, label, conf = cv.detect_common_objects(frame)
    output_image = draw_bbox(frame, bbox, label, conf)
    print("b")
    opencv.imwrite("poc/pics/image"+str(count)+".jpg", output_image)
    count = count + 1
    for i, item in enumerate(label):
        print(item)

cap.release()
opencv.destroyAllWindows()
