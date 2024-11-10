const socket = io('http://localhost:8000');

const form = document.getElementById('send-container');
const messageInput = document.getElementById('messageInp');
const messageContainer = document.querySelector(".container");
const leaveBtn = document.getElementById('leaveBtn');


let userName = prompt('Enter your name to join:');
if (userName) {
    socket.emit('new-user-joined', userName);
} else {
    alert('Name cannot be empty');
    window.location.reload(); // Reload if no name is provided
}

form.addEventListener('submit', (e) => {
    e.preventDefault();
    const message = messageInput.value;
    append(`You: ${message}`, 'right');
    socket.emit('send', message);
    messageInput.value = '';
});

leaveBtn.addEventListener('click', () => {
    socket.emit('user-left', userName); // Notify other users
    socket.disconnect(); // Disconnect the socket
    window.location.href = '/'; // Redirect to the home route
});


const append = (message, position) => {
    const messageElement = document.createElement('div');
    messageElement.innerText = message;
    messageElement.classList.add('message');
    messageElement.classList.add(position);
    messageContainer.append(messageElement);
    messageContainer.scrollTop = messageContainer.scrollHeight; // Auto-scroll to the latest message
};

const displayNotification = (message) => {
    const notificationElement = document.createElement('div');
    notificationElement.innerText = message;
    notificationElement.classList.add('notification');
    messageContainer.append(notificationElement);
    messageContainer.scrollTop = messageContainer.scrollHeight; // Auto-scroll to the latest message
};

socket.on('user-joined', name => {
    displayNotification(`${name} joined the chat`);
});

socket.on('user-left', name => {
    displayNotification(`${name} left the chat`);
});

socket.on('receive', data => {
    append(`${data.name}: ${data.message}`, 'left');
});