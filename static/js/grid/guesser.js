function voteCell(event){
    console.log(event);
    var cell = event.target;
    if (cell.dataset.enabled){
        socket.emit('vote_cell', cell.id);
    }
}

function initGuesser(){
    var cells = document.getElementsByTagName("td"),
        ncells = cells.length;

    for (var i=0; i < ncells; i++){
        var cell = cells[i];
        cell.addEventListener('click', voteCell);
    }

    var pass = document.getElementById("pass");
    pass.addEventListener('click', function(e){
        if (vote_enabled){
            socket.emit('vote_cell', 'none');
        }
    });

    // Votes
    var table = document.getElementById('table');
    socket.on('enable_vote', function(){
        console.log("Enabling vote")
        // Allow user to touch cells and vote
        for (var i=0; i<ncells; i++){
            var cell = cells[i];
            cell.dataset.enabled = "true";
        }
        pass.disabled = false;
    });

    socket.on('disable_vote', function(){
        // Prevent user from voting
        for (var i=0; i<ncells; i++){
            var cell = cells[i];
            cell.dataset.enabled = "false";
        }
        pass.disabled = true;
    });
}

$(function(){
   initGrid();
   initChat();
   initGuesser();
});
