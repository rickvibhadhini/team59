const express = require('express');
const path = require('path');
const http = require('http');
const socketIO = require('socket.io');

const app = express();
const httpServer = http.createServer(app);
const io = socketIO(httpServer, {
    cors: {
        origin: "http://127.0.0.1:5000",
        methods: ["GET", "POST"]
    }
});

// Serve static files from the "public" directory
app.use(express.static(path.join(__dirname, 'public')));

const users = {};

io.on('connection', socket => {
    socket.on('new-user-joined', name => {
        console.log("New user", name);
        users[socket.id] = name;
        socket.broadcast.emit('user-joined', name);
    });

    socket.on('send', message => {
        socket.broadcast.emit('receive', { message: message, name: users[socket.id] });
    });

    socket.on('typing', (isTyping) => {
        if (isTyping) {
            socket.broadcast.emit('typing', { name: users[socket.id] });
        } else {
            socket.broadcast.emit('typing', null);
        }
    });

    socket.on('disconnect', () => {
        const name = users[socket.id];
        delete users[socket.id];
        socket.broadcast.emit('user-left', name);
    });
});

httpServer.listen(8000, () => {
    console.log('Server running on http://localhost:8000');
});