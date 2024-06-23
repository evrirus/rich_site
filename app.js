// const mongoose = require('mongoose');

// main().catch(err => console.log(err));

// const s = (mongoose.startSession());
// console.log(mongoose.model('lalka').findOne({ _id: 9 }).session(s));


const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 3000;

const server = http.createServer((req, res) => {
    console.log('server started');

    res.setHeader('Content-Type', 'text/html');

    let basePath = '';

    switch (req.url) {
        case '/':
        case '/home':
        case '/index.html':
            basePath = createPath('index');
            res.statusCode = 200;
            break;
        case '/about':
        case '/profile':
            res.statusCode = 301;
            res.setHeader('Location', '/profile');
            res.end();
            break;
        default:
            basePath = createPath('error');
            res.statusCode = 404;
            break;
            
    }

    fs.readFile(basePath, (err, data) => {
        if (err) {
            console.log(err);
            res.statusCode = 500;
            res.end();
        } else {
            res.write(data);
            res.end();
        }
    });
});

server.listen(PORT, () => {
    error ? console.log(error) : console.log(`Example app listening on port ${PORT}`);
});
