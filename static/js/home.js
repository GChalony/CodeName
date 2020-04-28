newGameBtn = document.getElementById("new-game-button")
newGameBtn.addEventListener("click", function(e){
    nickname = document.getElementById("nickname-input").value;
    pseudo = document.getElementById("nickname-input").value;
    col1 = document.getElementById("backcol").value.slice(1);  // Remove #
    col2 = document.getElementById("mouthcol").value.slice(1);
    new_loc = "/new_room?pseudo="+pseudo+"&col1="+col1+"&col2="+col2;
    console.log(new_loc);
    window.location = new_loc;
});