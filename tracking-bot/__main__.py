import asyncio
import cvlib as cv
import cv2 as opencv
from cvlib.object_detection import draw_bbox
from hachi_nio import HachiNIOClient

cap = opencv.VideoCapture(0)
cap.set(opencv.CAP_PROP_FRAME_WIDTH, 224)
cap.set(opencv.CAP_PROP_FRAME_HEIGHT, 224)
cap.set(opencv.CAP_PROP_FPS, 36)

loop = None
addr = "192.168.15.4"

_picIsConnected = False
_cmdIsConnected = False

picConn = None
cmdConn = None

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
    print(header, ref.id, message.decode("utf-8"))
    # ref.send(header, "hi")

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

    loop = asyncio.get_running_loop()
    await connect_pic()
    await connect_cmd()

    try:
        #print("on wait")
        #await asyncio.sleep(3600)  # Serve for 1 hour.
        while(1):
            ret, frame = cap.read()
            laplacian = checkBlur(frame)
            if(laplacian > 300):
                if(isConnected()):
                    print('send')
                    picConn.send({"transaction" : "frame"}, opencv.imencode('.jpg', frame)[1].tobytes())
                    print('sent!')
                else:
                    # TODO executar local    
                    print("skip")
                await asyncio.sleep(.1)
            else:
                print("Low Laplacian")
                print(laplacian)
    finally:
        #transport_cmd.close()
        #transport_pic.close()
        print("on end")

asyncio.run(run_client())
