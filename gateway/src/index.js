import express from 'express';
import gzip from 'compression';
import morgan from 'morgan';
import cors from 'cors';
import winston from 'winston';
import { Server } from "socket.io";
import { createServer } from "http";
import rpiServer from './rpi-server.js'
import iaServer from './ia-server.js'

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

const httpServer = createServer(app);

const io = new Server(httpServer, { /* options */ });

io.on("connection", (socket) => {
    global.logger.info(`new wsocket connection`)
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
