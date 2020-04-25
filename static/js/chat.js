console.log('Initiating chat')

var socket = io();
socket.on('connect', function() {
    socket.emit('event', {data: 'I\'m connected!'});
});

function sendMsg(){
    var m = document.getElementById("m");
    var txt = m.value;
    console.log("Sending "+ txt);
    socket.emit('message', {'msg': txt});
    m.value = '';
}

var form = document.getElementById("msgform");
form.addEventListener("submit", function(e){
    console.log(e);
    e.preventDefault();
    sendMsg();
});

socket.on('message', function(msg){
    console.log("received : "+msg);
    var li = document.createElement('li');
    li.textContent = msg;
    document.getElementById('messages').append(li);
});