var socket = io();

var go = document.getElementById("go");
go.addEventListener("click", function(e){
    e.preventDefault();
    console.log("Go!");
    socket.emit("start game", {"current_url": window.location.href});
})

var home = document.getElementById("home");
home.addEventListener("click", function(e){
    e.preventDefault();
    socket.emit("return home");
})

socket.on("url redirection", function(data){
    window.location = data.url;
});