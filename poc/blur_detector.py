
import cv2

def checkBlur(path):
    image = cv2.imread(path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()


print(checkBlur("./pics/25.jpg"))
print(checkBlur("./pics/29.jpg"))
print(checkBlur("./pics/75.jpg"))
print(checkBlur("./pics/78.jpg"))