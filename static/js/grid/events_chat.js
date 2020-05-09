console.log('Initiating events chat');

var event_chat = document.getElementById("events_msglist");

socket.on('add_event', function(msg){
    console.log('Adding event');
    var li = document.createElement("li");
    li.textContent = msg;
    event_chat.append(li);
});
