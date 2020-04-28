newGameBtn = document.getElementById("new-game-button")
newGameBtn.addEventListener("click", function(e){
    nickname = document.getElementById("nickname-input").value
    window.location = "/new_room"
});