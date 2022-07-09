import hachiNIO from "hachi-nio";
import iaServer from "./ia-server.js"
import fs from "fs";
import uuid from 'node-uuid'

//import AWS from "aws-sdk";

// AWS.config.update({
//     region: "us-east-1",
// });

// const s3 = new AWS.S3({
//     apiVersion: "2006-03-01",
//     params: { Bucket: "habitse" }
// });

let imageServer;
let controlServer;

let imageServerConnections = {};
let controlServerConnections = {};

const TRAIN_DIR = "train_dir";

function onAuth(type, socket, id){

    socket.authId = id;

    if(type == "image"){
        imageServerConnections[id] = socket;
    }else if(type == "control"){
        controlServerConnections[id] = socket;
    }

    if(imageServerConnections[id] && controlServerConnections[id]){
        imageServerConnections[id].isAuth = true;
        controlServerConnections[id].isAuth = true;
    }
}

async function startImageServer(port){
    return new Promise((resolve, reject) => {
        imageServer= new hachiNIO.server(port);

        imageServer.on('server_listening', () => {
            global.logger.info(`Listening RPI-Image-Server at port ${port}`);
            resolve();
        });
        
        imageServer.on('client_connected', (socketClient) => {
            global.logger.info("New RPI-Image-Device: \t id:"+socketClient.id+" origin:"+socketClient.address().address);
        });
        
        imageServer.on('client_close', (socketClient) => {
            global.logger.info("RPI-Image-Device DISCONNECTED! \t id:"+socketClient.id);
            if(socketClient.isAuth){
                delete imageServerConnections[socketClient.authId];
            }
        });
        
        imageServer.on("data", (socketClient, header, dataBuffer) => {
            //global.logger.info("MESSAGE RECEIVED! \t id:"+socketClient.id+" message:"+dataBuffer.toString());

            if(!header.transaction){
                global.logger.error("Transaction not specified");
                return;
            }

            if(!socketClient.isAuth){
                if(header.transaction == "auth"){
                    onAuth("image", socketClient, dataBuffer);
                }
                return;
            }

            switch(header.transaction){
                case "frame":
                    console.log("frame");
                    if (!fs.existsSync(TRAIN_DIR)){
                        fs.mkdirSync(TRAIN_DIR);
                    }
                    console.log(`${TRAIN_DIR}/${uuid.v4()}.jpg`)
                    fs.writeFileSync(`${TRAIN_DIR}/${uuid.v4()}.jpg`, dataBuffer);
                    //comment for while
                    //iaServer.processImage(socketClient.authId, dataBuffer);
                    break;
                default:
                    global.logger.error("RPI: Transaction not recognized");
                    break;
            }
        });
    });
}

async function startControlServer(port){
    return new Promise((resolve, reject) => {
        controlServer= new hachiNIO.server(port);

        controlServer.on('server_listening', () => {
            global.logger.info(`Listening RPI-Control-Server at port ${port}`);
            resolve();
        });
        
        controlServer.on('client_connected', (socketClient) => {
            global.logger.info("New RPI-Control-Device: \t id:"+socketClient.id+" origin:"+socketClient.address().address);
        });
        
        controlServer.on('client_close', (socketClient) => {
            global.logger.info("RPI-Control-Device DISCONNECTED! \t id:"+socketClient.id);
            if(socketClient.isAuth){
                delete controlServerConnections[socketClient.authId];
            }
        });
        
        controlServer.on("data", (socketClient, header, dataBuffer) => {
            //global.logger.info("MESSAGE RECEIVED! \t id:"+socketClient.id+" message:"+dataBuffer.toString());

            if(!header.transaction){
                global.logger.error("Transaction not specified");
                return;
            }

            if(!socketClient.isAuth){
                if(header.transaction == "auth"){
                    onAuth("control", socketClient, dataBuffer);
                }
                return;
            }

            switch(header.transaction){

                default:
                    global.logger.error("RPI: Transaction not recognized");
                    break;
            }
        });
    });
}

async function startServer(imagePort, controlPort){
    await startImageServer(imagePort);
    await startControlServer(controlPort);
}

export default {startServer}