var socket = io("/room");

var go = document.getElementById("go");
go.addEventListener("click", function(e){
    e.preventDefault();
    console.log("Go!");
    console.log(socket);
    socket.emit("start_game");
});

var home = document.getElementById("home");
home.addEventListener("click", function(){
    window.location = "/";
});

socket.on("url_redirection", function(data){
    console.log(data);
    window.location = data.url;
});