function initSpy(){
    // Spy controls
    var controls = document.getElementById("controls");
    var hint = document.getElementById("hint");
    var n = document.getElementById("n");

    if (controls){
        var button = document.getElementById('send-hint');
        socket.on('enable_controls', function(){
            console.log('Enabling controls');
            button.disabled = false;
        });

        controls.addEventListener("submit", function(e){
            e.preventDefault();
            socket.emit("hint", hint.value, n.value);
            hint.value = "";
            n.value = "";
            button.disabled = true;
            return false;
        });
    }
}

$(function(){
   initGrid();
   initChat();
   initSpy();
});