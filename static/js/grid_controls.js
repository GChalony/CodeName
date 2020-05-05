var socket = io("/grid");

function drawVotes(cell, n){
    // draw votes during voting phase
    cell.style.background = '#'+n+''+n+''+n;
}

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

socket.on('update_votes', function(votes){
    for (var cellCode in votes){
        var cell = getElementsById(cellCode);
        drawVotes(cell, votes[cell]);
    }
});

socket.on('vote_done', function(data){
    // TODO: Reset votes
    console.log(data);
    target = document.getElementById(data.cell);
    target.dataset.enabled = "true";
    target.dataset.code = parseInt(data.value);
});

var players = document.getElementById("players").children,
    nplayers = players.length;

socket.on('change_current_player', function(player_id){
    console.log('Switching'+player_id);
    for (var i=0; i<nplayers; i++){
        var player = players[i];
        if ( player.classList.contains('current-player') ){
            player.classList.remove('current-player');
        }
        if (player.id == player_id){
            player.classList.add('current-player');
        }
    }
});

var title = document.getElementById('toptitle');
socket.on('change_title', function(new_title){
    title.textContent = new_title;
});

var button = document.getElementById('send-hint');
socket.on('toggle_controls', function(){
    console.log('Toggling controls');
    if (button.disabled) {
        button.disabled = false;
    } else {
      button.disabled = true;
    }
});

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
});
socket.on('disable_vote', function(){
    // Prevent user from voting
    for (var i=0; i<ncells; i++){
        var cell = cells[i];
        cell.dataset.enabled = "false";
    }
    vote_enabled = false;
});