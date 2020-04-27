var socket = io();

newGameBtn = document.getElementById("new-game-button")
newGameBtn.addEventListener("click", function(e){
    nickname = document.getElementById("nickname-input").value
    socket.emit("create room", {"nickname":nickname});
})

socket.on("url redirection", function(data){
    window.location = data.url;
});
