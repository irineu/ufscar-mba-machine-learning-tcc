import hachiNIO from "hachi-nio";

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
    });
}

function processImage(rpiID, buffer){

}

export default {startServer}