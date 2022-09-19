import hachiNIO from "hachi-nio";
import iaServer from "./ia-server.js"
import fs from "fs";
import uuid from 'node-uuid'

let imageServer;
let controlServer;

let imageServerConnections = {};
let controlServerConnections = {};

function onAuth(type, socket, id){

    console.log(id);

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
                    onAuth("image", socketClient, dataBuffer.toString());
                }
                return;
            }

            switch(header.transaction){
                case "frame":
                    if (!fs.existsSync(global.TRAIN_DIR)){
                        fs.mkdirSync(global.TRAIN_DIR);
                    }
                    
                    if(header.train){
                        console.log(header.train)
                        if(global.mode == "TRAIN_MANUAL"){
                            //Se elegível para treinar, salva
                            let cwh = 224;
                            let dist = global.zLevel * 5 + 30;
                            let wh = 224/2;

                            let a = Math.round(parseFloat(wh/cwh) * 1000000) / 1000000
                            let b = Math.round(parseFloat(dist/cwh) * 1000000) / 1000000
                            

                            let name = `${global.TRAIN_DIR}/${global.activeObj}/${uuid.v4()}`;
                            fs.writeFileSync(name + ".jpg", dataBuffer);
                            fs.writeFileSync(name + ".txt", `0 ${a} ${a} ${b} ${b}`);
                            global.io.emit("train_frame",name + ".jpg");
                        }else{
                            global.imageMap[socketClient.authId] = dataBuffer;
                        } 
                    }

                    global.io.emit("frame", dataBuffer.toString("base64"));
                    if(global.mode == "NONE"){
                        //comment for while
                        iaServer.processImage(socketClient.authId, dataBuffer);
                    }else{
                         //pocs
                        setTimeout(() => {
                            let cmdSocket = controlServerConnections[socketClient.authId]
                            hachiNIO.send(cmdSocket, {transaction : "reply"}, "ok");
                        }, 50);
                    }

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
                case "laplacian":
                    global.io.emit("laplacian", dataBuffer.toString(), header.avg);
                    break;
                default:
                    global.logger.error("RPI: Transaction not recognized");
                    break;
            }
        });
    });
}

function axis(data){
    console.log("axis", data)
    global.axis += data;
    let id = Object.keys(controlServerConnections)[0];
    hachiNIO.send(controlServerConnections[id], {transaction : "x"}, global.axis.toString());
}

function yaw(data){
    console.log("yaw", data)
    global.yaw += data;
    let id = Object.keys(controlServerConnections)[0];
    hachiNIO.send(controlServerConnections[id], {transaction : "y"}, global.yaw.toString());
}

async function startServer(imagePort, controlPort){
    await startImageServer(imagePort);
    await startControlServer(controlPort);
}

export default {startServer, imageServerConnections, controlServerConnections, axis, yaw}