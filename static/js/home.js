function startGame(e){
    pseudo = document.getElementById("inputPseudo").value;
    backcol = document.getElementById("backcol").value;
    mouthcol = document.getElementById("mouthcol").value;
    new_loc = "/new_room?pseudo="+pseudo+"&col1="+backcol.slice(1)+"&col2="+mouthcol.slice(1);
    console.log(new_loc);
    // Simply change loc and redirection will handle the rest
    window.location = new_loc;
}

newGameBtn = document.getElementById("new-game-button");
newGameBtn.addEventListener("click", startGame);
navNew = document.getElementById("nav-new-room");
navNew.addEventListener("click", startGame);
