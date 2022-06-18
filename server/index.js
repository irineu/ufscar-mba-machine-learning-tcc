import express from 'express';
import gzip from 'compression';
import morgan from 'morgan';
import cors from 'cors';
import zmq from 'zeromq';

const port = process.argv[2] || 3000;
const portZMQ = process.argv[3] || 3001;

let sock = new zmq.Push

sock.bindSync("tcp://127.0.0.1:3000");

console.log(`Listening ZMQ at port ${portZMQ}`)

let app = express();

app.use(gzip())
    .use(express.urlencoded({ extended: true }))
    .use(express.json())
    .use(morgan('dev'));

app.listen(port, () => {
    console.log(`Listening HTTP at port ${port}`)
});

    