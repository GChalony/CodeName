function startGame(e){
    e.preventDefault();
    updateAvatarData();
    new_loc = "/new_room?pseudo="+pseudo+"&col1="+backcol.slice(1)+"&col2="+mouthcol.slice(1);
    console.log(new_loc);
    // Simply change loc and redirection will handle the rest
    window.location = new_loc;
}

newGameBtn = document.getElementById("new-game-button");
newGameBtn.addEventListener("click", startGame);
navNew = document.getElementById("nav-new-room");
navNew.addEventListener("click", startGame);

// JOIN ROOM

function parseJoinRoomURL(url){
    var matches = url.match('\/[a-z|0-9]{32}\/room');
    if (matches.length > 0){
        return matches[0].slice(1, 33)
    }
    return null;
}

function joinRoom(e){
    e.preventDefault();
    updateAvatarData();
    var room_id = parseJoinRoomURL(document.getElementById('join-game-url').value);
    if (room_id != null){
        new_loc = "/join_room?pseudo="+pseudo+"&col1="+backcol.slice(1)+"&col2="+mouthcol.slice(1)+"&room_id="+room_id;
        window.location = new_loc;
    }
    else{
        // TODO say url invalid
        console.log('Url is invalid');
    }
}

var joinForm = document.getElementById('join-form');
joinForm.addEventListener('submit', joinRoom);
