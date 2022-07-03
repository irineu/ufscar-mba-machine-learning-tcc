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

def checkBlur(image):
    gray = opencv.cvtColor(image, opencv.COLOR_BGR2GRAY)
    return opencv.Laplacian(gray, opencv.CV_64F).var()

def cmd_on_connect(ref):
    print("New Connection! " + str(ref.id))
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
            addr, 3002)
    except OSError:
        print("connection failed")
        await asyncio.sleep(3) 
        await connect_pic()

async def connect_cmd():
    global loop
    try:
        transport_pic, protocol_pic = await loop.create_connection(
            lambda: HachiNIOClient(pic_on_data, pic_on_connect, client_close=pic_on_close,  client_error=pic_on_error),
            addr, 3002)
    except OSError:
        print("connection failed")
        await asyncio.sleep(3) 
        await connect_cmd()


async def run_client():
    global loop
    loop = asyncio.get_running_loop()
    await connect_pic()
    await connect_cmd()

    try:
        #print("on wait")
        #await asyncio.sleep(3600)  # Serve for 1 hour.
        count = 1
        while(1):
            ret, frame = cap.read()
            laplacian = checkBlur(frame)
            if(laplacian > 800):
                opencv.imwrite(str(count)+".jpg", frame)
                count = count + 1
                await asyncio.sleep(.1)
            else:
                print(laplacian)
    finally:
        #transport_cmd.close()
        #transport_pic.close()
        print("on end")

asyncio.run(run_client())