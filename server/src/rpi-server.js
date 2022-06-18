import hachiNIO from "hachi-nio";

let imageServer;
let controlServer;

let imageServerConnections = {};
let controlServerConnections = {};

let rpiConnections = {};

async function startImageServer(port){
    return new Promise((resolve, reject) => {
        imageServer= new hachiNIO.server(port);

        imageServer.on('server_listening', () => {
            global.logger.info(`Listening RPI-Image-Server at port ${port}`);
            resolve();
        });
        
        imageServer.on('client_connected', (socketClient) => {
            global.logger.info("New RPI-Image-Device: \t id:"+socketClient.id+" origin:"+socketClient.address().address);
            imageServerConnections[socketClient.id] = socketClient;
        });
        
        imageServer.on('client_close', (socketClient) => {
            global.logger.info("RPI-Image-Device DISCONNECTED! \t id:"+socketClient.id);
            delete imageServerConnections[socketClient.id];
        });
        
        imageServer.on("data", (socketClient, header, dataBuffer) => {
            //global.logger.info("MESSAGE RECEIVED! \t id:"+socketClient.id+" message:"+dataBuffer.toString());
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
            controlServerConnections[socketClient.id] = socketClient;
        });
        
        controlServer.on('client_close', (socketClient) => {
            global.logger.info("RPI-Control-Device DISCONNECTED! \t id:"+socketClient.id);
            delete controlServerConnections[socketClient.id];
        });
        
        controlServer.on("data", (socketClient, header, dataBuffer) => {
            //global.logger.info("MESSAGE RECEIVED! \t id:"+socketClient.id+" message:"+dataBuffer.toString());
        });
    });
}

async function startServer(imagePort, controlPort){
    await startImageServer(imagePort);
    await startControlServer(controlPort);
}

export default {startServer}