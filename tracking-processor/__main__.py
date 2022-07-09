import asyncio
import numpy as np
import cvlib as cv
import cv2 as opencv
from cvlib.object_detection import draw_bbox
from hachi_nio import HachiNIOClient
import json

loop = None
addr = "192.168.15.4"

def cmd_on_connect(ref):
    print("New Connection! " + str(ref.id))

    global _cmdIsConnected
    global cmdConn

    _cmdIsConnected = True
    cmdConn = ref

    cmdConn.send({"transaction" : "auth"}, "123")

def onProcess(frame, sentFrom):
    print("will process");

    frame = np.asarray(bytearray(frame), dtype="uint8")
    frame = opencv.imdecode(frame, opencv.IMREAD_COLOR)

    bbox, label, conf = cv.detect_common_objects(frame)
    for i, item in enumerate(label):
        print(item)

    print(sentFrom);

    cmdConn.send({"transaction" : "process", "to": sentFrom}, json.dumps(bbox))


def cmd_on_data(header, message, ref):
    #print(header, ref.id, message.decode("utf-8"))

    switchCase = {
        "proccess" : lambda: onProcess(message, header["from"])
    }

    selection = switchCase[header["transaction"]]
    if selection is not None:
        selection()

def cmd_on_close(ref):
    print("cmd close conn")
    asyncio.create_task(connect_cmd())

def cmd_on_error(ref):
    print("cmd error")

async def connect_cmd():
    global loop
    try:
        transport_cmd, protocol_cmd = await loop.create_connection(
            lambda: HachiNIOClient(cmd_on_data, cmd_on_connect, client_close=cmd_on_close,  client_error=cmd_on_error),
            addr, 3003)
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
    await connect_cmd()

    try:
        print("on wait")
        await asyncio.sleep(3600)  # Serve for 1 hour.
    finally:
        print("on end")

asyncio.run(run_client())