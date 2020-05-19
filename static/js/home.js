var socket = io("/room");  // Connect to namespace /room
console.log("ON HOME JS PAGE")
socket.emit("get_user_infos");

newGameBtn = document.getElementById("new-game-button")
newGameBtn.addEventListener("click", function(e){
    socket.emit("create_room", {
        "pseudo": document.getElementById("pseudo-input").value,
        "backcol": document.getElementById("backcol").value,
        "mouthcol": document.getElementById("mouthcol").value
    });
});



socket.on("url_redirection", function(data){
    console.log(data);
    window.location = data.url;
});

joinGameBtn = document.getElementById("join-game-button")
joinGameBtn.addEventListener("click", function(e){
    socket.emit("join_existing_room", {
        "pseudo": document.getElementById("pseudo-input").value,
        "backcol": document.getElementById("backcol").value,
        "mouthcol": document.getElementById("mouthcol").value,
        "room_id": document.getElementById("join-game-link").value
    });
});
