var socket = io("/room");  // Connect to namespace /room

newGameBtn = document.getElementById("new-game-button")
newGameBtn.addEventListener("click", function(e){
    nickname = document.getElementById("nickname-input").value;
    socket.emit("create_room", {"nickname": nickname});
});

// newGameBtn.addEventListener("click", function(e){
//     pseudo = document.getElementById("nickname-input").value;
//     col1 = document.getElementById("backcol").value.slice(1);  // Remove #
//     col2 = document.getElementById("mouthcol").value.slice(1);
//     new_loc = "/new_room?pseudo="+pseudo+"&col1="+col1+"&col2="+col2;
//     console.log(new_loc);
//     // Simply change loc and redirection will handle the rest
//     window.location = new_loc;

// });


socket.on("url_redirection", function(data){
    console.log(data);
    window.location = data.url;
});

joinGameBtn = document.getElementById("join-game-button")
joinGameBtn.addEventListener("click", function(e){
    room_id = document.getElementById("join-game-link").value;
    nickname = document.getElementById("nickname-input").value;
    socket.emit("join_existing_room", {"nickname": nickname, "room_id": room_id});
});
