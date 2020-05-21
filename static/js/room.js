var socket = io("/room");  // Connect to namespace /room

var home = document.getElementById("home");
home.addEventListener("click", function(){
    window.location = "/";
});

var go = document.getElementById("go");
go.addEventListener("click", function(e){
    e.preventDefault();
    console.log(socket);
    socket.emit("start_game");
});

/* Received when starting game */
socket.on("url_redirection", function(data){
    window.location = data.url;
});


