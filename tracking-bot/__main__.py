import asyncio
import cv2 as opencv
import numpy as np
from hachi_nio import HachiNIOClient
import RPi.GPIO as GPIO
import time
from gpiozero import Servo

servoA_pin = 14
servoB_pin = 4

servoA = Servo(servoA_pin)
servoB = Servo(servoB_pin)

servoA.value = -1
servoB.value = -1

# deg_0_pulse = 0.5 
# deg_180_pulse = 2.5
# f = 50.0

# period = 1000/f
# k      = 100/period
# deg_0_duty = deg_0_pulse*k
# pulse_range = deg_180_pulse - deg_0_pulse
# duty_range = pulse_range * k

# GPIO.setmode(GPIO.BCM)
# GPIO.setup(servoA_pin,GPIO.OUT)
# pwmA = GPIO.PWM(servoA_pin,f)
# pwmA.start(100)

# GPIO.setmode(GPIO.BCM)
# GPIO.setup(servoB_pin,GPIO.OUT)
# pwmB = GPIO.PWM(servoB_pin,f)
# pwmB.start(100)

def set_angleA(angle):
        #duty = deg_0_duty + (angle/180.0)* duty_range
        #pwmA.ChangeDutyCycle(duty)
        servoA.value = angle
        

def set_angleB(angle):
        #duty = deg_0_duty + (angle/180.0)* duty_range
        #pwmB.ChangeDutyCycle(duty)
        servoB.value = angle

cap = opencv.VideoCapture(0)
cap.set(opencv.CAP_PROP_FRAME_WIDTH, 224)
cap.set(opencv.CAP_PROP_FRAME_HEIGHT, 224)
cap.set(opencv.CAP_PROP_FPS, 36)

loop = None
#addr = "irineuantunes.com"
addr = "192.168.45.5"

_picIsConnected = False
_cmdIsConnected = False

picConn = None
cmdConn = None

#imagem base para leitura do histograma
hsvBase = None
hsvCount = 0

processNext = True

laplacianAVGList = []

def calcHistogram(frame):
    h_bins = 50
    s_bins = 60
    histSize = [h_bins, s_bins]
    h_ranges = [0, 180]
    s_ranges = [0, 256]
    ranges = h_ranges + s_ranges
    channels = [0, 1]

    hsvTest = opencv.cvtColor(frame, opencv.COLOR_BGR2HSV)

    hist_base = opencv.calcHist([hsvBase], channels, None, histSize, ranges, accumulate=False)
    opencv.normalize(hist_base, hist_base, alpha=0, beta=1, norm_type=opencv.NORM_MINMAX)

    hist_test = opencv.calcHist([hsvTest], channels, None, histSize, ranges, accumulate=False)
    opencv.normalize(hist_test, hist_test, alpha=0, beta=1, norm_type=opencv.NORM_MINMAX)
    return opencv.compareHist(hist_base, hist_test, opencv.HISTCMP_CORREL)

def isConnected():
    global _picIsConnected
    global _cmdIsConnected

    return _picIsConnected and _cmdIsConnected

def onConnect():

    if(isConnected()):
        print("ready!")

def checkBlur(image):
    gray = opencv.cvtColor(image, opencv.COLOR_BGR2GRAY)
    return opencv.Laplacian(gray, opencv.CV_64F).var()

def cmd_on_connect(ref):
    print("New Connection! " + str(ref.id))

    global _cmdIsConnected
    global cmdConn

    _cmdIsConnected = True
    cmdConn = ref

    cmdConn.send({"transaction" : "auth"}, "123")

    onConnect();

    #ref.send({"test" : "123"}, "hello")

def cmd_on_data(header, message, ref):
    global processNext

    if header["transaction"] == 'bbox':
        processNext = True
    elif header["transaction"] == 'x':
        set_angleB(float(message.decode("utf-8")));
    elif header["transaction"] == 'y':
        set_angleA(float(message.decode("utf-8")));

def cmd_on_close(ref):
    print("cmd close conn")
    asyncio.create_task(connect_cmd())

def cmd_on_error(ref):
    print("cmd error")

def pic_on_connect(ref):
    print("New Connection! " + str(ref.id))
    global _picIsConnected
    global picConn
    
    _picIsConnected = True
    picConn = ref

    picConn.send({"transaction" : "auth"}, "123")

    onConnect()

    #ref.send({"test" : "123"}, "hello")

def pic_on_data(header, message, ref):
    print(header, ref.id, message.decode("utf-8"))
    # ref.send(header, "hi")

def pic_on_close(ref):
    print("cmd close conn")
    asyncio.create_task(connect_pic())

def pic_on_error(ref):
    print("pic error")

async def connect_pic():
    global loop
    try:
        transport_pic, protocol_pic = await loop.create_connection(
            lambda: HachiNIOClient(pic_on_data, pic_on_connect, client_close=pic_on_close,  client_error=pic_on_error),
            addr, 3001)
    except OSError:
        print("connection failed")
        await asyncio.sleep(3) 
        await connect_pic()

async def connect_cmd():
    global loop
    try:
        transport_cmd, protocol_cmd = await loop.create_connection(
            lambda: HachiNIOClient(cmd_on_data, cmd_on_connect, client_close=cmd_on_close,  client_error=cmd_on_error),
            addr, 3002)
    except OSError:
        print("connection failed")
        await asyncio.sleep(3) 
        await connect_cmd()


async def run_client():
    global loop
    global picConn

    global hsvCount
    global hsvBase
   

    loop = asyncio.get_running_loop()
    await connect_pic()
    await connect_cmd()

    try:
        #print("on wait")
        #await asyncio.sleep(3600)  # Serve for 1 hour.
        while(1):
            global processNext
            ret, frame = cap.read()
            laplacian = checkBlur(frame)

            laplacianAVGList.append(laplacian)

            if len(laplacianAVGList) > 50:
                laplacianAVGList.pop(0)

            laplaceAVG = 0;
            for l in laplacianAVGList:
                laplaceAVG = laplaceAVG + l

            laplaceAVG = laplaceAVG / len(laplacianAVGList)
            
            if(laplacian > laplaceAVG - (laplaceAVG * 0.15)):

                elegibleToTrain = False

                if hsvCount == 0:
                    hsvBase = opencv.cvtColor(frame, opencv.COLOR_BGR2HSV)

                hsvCount += 1

                if hsvCount > 10:

                    histgrm = calcHistogram(frame)

                    if histgrm < .5 :
                        elegibleToTrain = True
                        #zerar para definir nova base de calculo
                        hsvCount = 0
                    else:
                        #nao enviar para 0 para servir de checkpoint
                        hsvCount = 1
                        #print(histgrm)

                print(processNext)
                if processNext:
                    if(isConnected()):
                        print("send")
                        picConn.send({"transaction" : "frame", "train" : elegibleToTrain}, opencv.imencode('.jpg', frame)[1].tobytes())
                        print("sent")
                        processNext = False
                    else:
                        # TODO executar local    
                        print("skip")
                else:
                    #print("skip")
                    x = 1

                await asyncio.sleep(.1)

            else:
                print("Low Laplacian")
                print(laplacian)
            
            cmdConn.send({"transaction" : "laplacian", "avg" : laplaceAVG}, str(laplacian))
    finally:
        #transport_cmd.close()
        #transport_pic.close()
        print("on end")

asyncio.run(run_client())
