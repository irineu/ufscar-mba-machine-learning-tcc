import express from 'express';
import gzip from 'compression';
import morgan from 'morgan';
import cors from 'cors';
import winston from 'winston';
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

app.listen(port, () => {
    global.logger.info(`Listening HTTP at port ${port}`)
});

(async ()=>{
    await rpiServer.startServer(3001, 3002);
    await iaServer.startServer(3003);
})()
