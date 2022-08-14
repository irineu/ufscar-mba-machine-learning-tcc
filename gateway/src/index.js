import express from 'express';
import gzip from 'compression';
import morgan from 'morgan';
import cors from 'cors';
import winston from 'winston';
import { Server } from "socket.io";
import { createServer } from "http";
import rpiServer from './rpi-server.js'
import iaServer from './ia-server.js'
import fs from 'fs';

const port = process.argv[2] || 3000;

global.logger =  winston.createLogger({
    transports: [
        new winston.transports.Console({
            level: 'info',
            format: winston.format.combine(
              winston.format.colorize(),
              winston.format.simple()
            )
          })
    ]
});

let app = express();

app.use(gzip())
    .use(express.urlencoded({ extended: true }))
    .use(express.json())
    .use(morgan('dev'));

app.use(express.static('html'));
app.use('/train_dir',express.static('train_dir'));

const httpServer = createServer(app);

const io = new Server(httpServer, { /* options */ });

global.mode = "NONE";
global.trainBounds = null;
global.imageMap = {};
global.TRAIN_DIR = "train_dir";

io.on("connection", (socket) => {
    global.logger.info(`new wsocket connection`);

    setTimeout(()=>{
        var files = fs.readdirSync('./train_dir');
        socket.emit("index",files);
    }, 3000);

    socket.on("mode", (mode, bounds)=>{
        global.mode = mode;

        if(global.mode == "TRAIN_MANUAL"){

        }
    });  

    socket.on("delete", (path)=>{
        path = path.substr(path.indexOf("train"));
        fs.unlinkSync(path);
    });  
});

httpServer.listen(port);

/*app.listen(port, () => {
    global.logger.info(`Listening HTTP at port ${port}`)
});*/

global.io = io;

(async ()=>{
    await rpiServer.startServer(3001, 3002);
    await iaServer.startServer(3003);
})()
