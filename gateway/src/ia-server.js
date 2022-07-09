import hachiNIO from "hachi-nio";
import rpiServer from "./rpi-server.js"

let server;

let iaConnections = {};
let taskMap = {};

function startServer(port){
    server= new hachiNIO.server(port);

    server.on('server_listening', () => {
        global.logger.info(`Listening IA-Server at port ${port}`);
    });
    
    server.on('client_connected', (socketClient) => {
        global.logger.info("New IA-Processor: \t id:"+socketClient.id+" origin:"+socketClient.address().address);
        iaConnections[socketClient.id] = socketClient;
    });
    
    server.on('client_close', (socketClient) => {
        global.logger.info("IA-Processor DISCONNECTED! \t id:"+socketClient.id);
        delete iaConnections[socketClient.id];
    });
    
    server.on("data", (socketClient, header, dataBuffer) => {
        //global.logger.info("MESSAGE RECEIVED! \t id:"+socketClient.id+" message:"+dataBuffer.toString());

        switch(header.transaction){
            case "auth":
                global.logger.info("IA-Processor Auth! \t alias:"+dataBuffer.toString());
                //TODO reusar o alias futuramente
                break;
            case "process":
                global.logger.info(JSON.stringify(header) + " - " +dataBuffer.toString());
                global.logger.info(Object.keys( rpiServer.controlServerConnections));
                let cmdSocket = rpiServer.controlServerConnections[header.to]
                hachiNIO.send(cmdSocket, {transaction : "bbox"}, dataBuffer);
                break;
            default:
                    global.logger.error("IA: Transaction not recognized " + header.transaction);
                    break;
        }
    });
}

function processImage(rpiID, buffer){
    /*if(mainIAServer == {}){
        global.warn.info("There is no IA Servers Available");
        return;
    }*/
    let mainIAServer = iaConnections[Object.keys(iaConnections)[0]];
    global.logger.info("IA: sending frame for proccess.. " + rpiID)
    hachiNIO.send(mainIAServer, {transaction : "proccess", from: rpiID}, buffer);
}

export default {startServer, processImage}