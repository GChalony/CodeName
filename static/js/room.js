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

/* Need to
 - Add listener on buttons to send "change_position" event with position code
 - Add function to update team display when receiving "teams_changed" event
    - Need to add / hide buttons if spot available
 */
function askChangePosition(event){
    var pos = event.target.dataset.pos;
    socket.emit("change_position", pos);
}


