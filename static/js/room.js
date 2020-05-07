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
socket.emit("get_players_in_room")

socket.on("response_players_in_room", function(data){
    console.log("in response_players_in_room, data=", data);
    players = data.players

    var ul_t1 = document.getElementById("t1");
    document.getElementById("t1").innerHTML = "";
    for (var i = 0; i < players.length; i++) {
        var li = document.createElement("li");
        li.setAttribute('id', players[i].id);
        li.appendChild(document.createTextNode(players[i].pseudo));
        ul_t1.appendChild(li);
    }

});

