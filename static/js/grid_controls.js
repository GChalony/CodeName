var socket = io("/grid");

function drawVotes(cell, n){
    // draw votes during voting phase
    cell.style.background = '#3'+n+'3';
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
    console.log("updating votes"+votes);
    for (var cellCode in votes){
        var cell = document.getElementById(cellCode);
        console.log(cell);
        console.log(votes);
        console.log(votes[cellCode]);
        drawVotes(cell, votes[cellCode]);
    }
});

socket.on('vote_done', function(data){
    // TODO: Reset votes
    console.log(data);
    target = document.getElementById(data.cell);
    target.dataset.enabled = "false";
    target.dataset.votedfor = "true";
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


// Spy controls
var controls = document.getElementById("controls");
if (controls){
    var button = document.getElementById('send-hint');
    socket.on('toggle_controls', function(){
        console.log('Toggling controls');
        if (button.disabled) {
            button.disabled = false;
        } else {
          button.disabled = true;
        }
    });
    controls.addEventListener("submit", function(e){
        e.preventDefault();
        var hint = document.getElementById("hint");
        var n = document.getElementById("n");
        socket.emit("hint", hint.value, n.value);
        hint.value = "";
        n.value = "";
        button.disabled = true;
        return false;
    });
}


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
});
socket.on('disable_vote', function(){
    // Prevent user from voting
    for (var i=0; i<ncells; i++){
        var cell = cells[i];
        cell.dataset.enabled = "false";
    }
    vote_enabled = false;
});

