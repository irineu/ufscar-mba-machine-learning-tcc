from picamera import PiCamera
import os

camera = PiCamera()

picDir = "poc/pics"

print(os.getcwd() + "/" +picDir)

if not os.path.exists(picDir):
    os.makedirs(os.getcwd() + "/" +picDir)

camera.capture('poc/pics/image.jpg')

print("Done!")


