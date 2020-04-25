var socket = io();

function startGame(){
    console.log("Going to grid !");
    socket.emit('start game', {"current_url": window.location.href});
}

var go = document.getElementById("go");
go.addEventListener("click", function(e){
    e.preventDefault();
    console.log('Go6!');
    startGame();
    // Sent some kind of request to the backend to be redirected to the grid

})


socket.on('start game response', function(data){
    console.log("front side start game response");
    console.log("data11", data)
    window.location = data.url;
});
