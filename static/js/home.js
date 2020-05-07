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

// newGameBtn.addEventListener("click", function(e){
//     pseudo = document.getElementById("pseudo-input").value;
//     col1 = document.getElementById("backcol").value.slice(1);  // Remove #
//     col2 = document.getElementById("mouthcol").value.slice(1);
//     new_loc = "/new_room?pseudo="+pseudo+"&col1="+col1+"&col2="+col2;
//     console.log(new_loc);
//     // Simply change loc and redirection will handle the rest
//     window.location = new_loc;

// });

// socket.on("return_user_infos", function(data){
//     console.log("return_user_infos", pseudo)
//     document.getElementById("pseudo-input").value = data.pseudo
//     document.getElementById("backcol").value = data.backcol
//     document.getElementById("mouthcol").value = data.mouthcol
// });


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
