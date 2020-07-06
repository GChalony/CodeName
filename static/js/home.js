function startGame(e){
    e.preventDefault();
    pseudo = document.getElementById("inputPseudo").value;
    new_loc = "/new_room?pseudo="+pseudo+"&avatar_src="+avatar.src;
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
    if (matches != null && matches.length > 0){
        return matches[0].slice(1, 33)
    }
    return null;
}

function joinRoom(e){
    e.preventDefault();
    var room_id = parseJoinRoomURL(document.getElementById('join-game-url').value);
    if (room_id != null){
        pseudo = document.getElementById("inputPseudo").value;
        new_loc = "/join_room?pseudo="+pseudo+"&room_id="+room_id+"&avatar_src="+avatar.src;
        window.location = new_loc;
    }
    else{
        $.snackbar({content: 'URL invalide'});
        console.log('Url is invalid');
    }
}

var joinForm = document.getElementById('join-form');
joinForm.addEventListener('submit', joinRoom);

setTimeout(function(){
    $.snackbar({content: 'URL invalide'});
    console.log('triggered');
}, 2000);