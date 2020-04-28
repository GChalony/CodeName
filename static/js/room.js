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

socket.on("update_room_players", function(room_players){
    console.log("in update_room_players, room_players=", room_players)
    document.getElementById('room players').innerHTML = room_players;
});

// window.addEventListener('beforeunload', function (e) {
//     e.preventDefault();
//     socket.emit("disconnect_from_window_closed");
// })
