console.log("Initiating chat")

function sendMsg(){
    var m = document.getElementById("m");
    var txt = m.value;
    console.log("Sending "+ txt);
    socket.emit("chat_message", txt);
    m.value = "";
}

var form = document.getElementById("msgform");
form.addEventListener("submit", function(e){
    console.log(e);
    e.preventDefault();
    sendMsg();
});

socket.on("chat_msg", function(msg){
    console.log("received : "+msg);
    var li = document.createElement("li");
    li.textContent = msg;
    document.getElementById("messages").append(li);
});
