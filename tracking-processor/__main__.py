import asyncio
import numpy as np
import cv2
from hachi_nio import HachiNIOClient
import json
import sys

sys.path.append('/home/irineu/darknet/v4/darknet')

import darknet

loop = None
#addr = "irineuantunes.com"
addr="192.168.45.5"

thresh = .25

network, class_names, class_colors = darknet.load_network(
    "/home/irineu/a/img.v4.cfg",
    "/home/irineu/a/img.data",
    "/home/irineu/a/backup/img_last.weights",
    batch_size=1
)

def cmd_on_connect(ref):
    print("New Connection! " + str(ref.id))

    global _cmdIsConnected
    global cmdConn

    _cmdIsConnected = True
    cmdConn = ref

    cmdConn.send({"transaction" : "auth"}, "123")


def image_detection(image_or_path):
    # Darknet doesn't accept numpy images.
    # Create one with image we reuse for each detect

    width = darknet.network_width(network)
    height = darknet.network_height(network)
    darknet_image = darknet.make_image(width, height, 3)

    if type(image_or_path) == "str":
        image = cv2.imread(image_or_path)
    else:
        image = image_or_path
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_resized = cv2.resize(image_rgb, (width, height),
                               interpolation=cv2.INTER_LINEAR)

    darknet.copy_image_from_bytes(darknet_image, image_resized.tobytes())
    detections = darknet.detect_image(network, class_names, darknet_image, thresh=thresh)
    darknet.free_image(darknet_image)
    #image = darknet.draw_boxes(detections, image_resized, class_colors)
    #return cv2.cvtColor(image, cv2.COLOR_BGR2RGB), detections
    return detections

def onProcess(frame, sentFrom):
    print("will process");

    frame = np.asarray(bytearray(frame), dtype="uint8")
    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

    detections = image_detection(frame)
    output = []

    for label, confidence, bbox in detections:
        print(label)
        left, top, right, bottom = darknet.bbox2points(bbox)
        output.append({
            "label": label,
            "confidence": confidence,
            "points": [left, top, right, bottom]
        })

    cmdConn.send({"transaction" : "process", "to": sentFrom}, json.dumps(output))


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
