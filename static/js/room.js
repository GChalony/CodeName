var socket = io("/room");  // Connect to namespace /room

var home = document.getElementById("home");
home.addEventListener("click", function(){
    socket.emit("leave_room", {"current_url": window.location.href});
    // window.location = "/";
});

var go = document.getElementById("go");
go.addEventListener("click", function(e){
    e.preventDefault();
    console.log("Go!");
    console.log(socket);
    socket.emit("start_game");
});

socket.on("url_redirection", function(data){
    console.log(data);
    window.location = data.url;
});

var go = document.getElementById("debug_button");
go.addEventListener("click", function(e){
    e.preventDefault();
    console.log("click debug_button!");
    // socket.emit("on_debug_button");
    socket.emit("debug_button", {"current_url": window.location.href});
});

socket.on("get_players_in_room", function(data){
    console.log("in get_players_in_room, data=", data);
    // var li = document.createElement("li");
    // li.textContent = msg;
    // document.getElementById("messages").append(li);
});
