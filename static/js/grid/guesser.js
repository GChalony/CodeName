function initGuesser(){
    function voteCell(event){
        console.log(event);
        if (vote_enabled){
            socket.emit('vote_cell', event.target.id);
        }
    }

    var cells = document.getElementsByTagName("td"),
        ncells = cells.length;

    for (var i=0; i<ncells; i++){
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
    var vote_enabled = false;
    var table = document.getElementById('table');
    socket.on('enable_vote', function(){
        console.log("Enabling vote")
        // Allow user to touch cells and vote
        for (var i=0; i<ncells; i++){
            var cell = cells[i];
            cell.dataset.enabled = "true";
        }
        vote_enabled = true;
        pass.disabled = false;
    });

    socket.on('disable_vote', function(){
        // Prevent user from voting
        for (var i=0; i<ncells; i++){
            var cell = cells[i];
            cell.dataset.enabled = "false";
        }
        vote_enabled = false;
        pass.disabled = true;
    });
}

$(function(){
   initGrid();
   initChat();
   initGuesser();
});
