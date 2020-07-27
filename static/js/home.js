function startGame(e){
    e.preventDefault();
    pseudo = document.getElementById("inputPseudo").value;
    new_loc = "/new_room?pseudo="+encodeURI(pseudo)+"&avatar_src="
                +encodeURIComponent(avatar.attributes['src'].value);
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
        new_loc = "/join_room?pseudo="+encodeURI(pseudo)+"&room_id="+encodeURI(room_id)
                    +"&avatar_src="+encodeURIComponent(avatar.attributes['src'].value);
        window.location = new_loc;
    }
    else{
        $.snackbar({content: 'URL invalide'});
        console.log('Url is invalid');
        $('#toast').children()[0].textContent = "Lien invalide";
        $('#toast').toast('show');
    }
}

var joinForm = document.getElementById('join-form');
joinForm.addEventListener('submit', joinRoom);
