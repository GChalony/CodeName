var socket = io("/grid");

votes = []

function drawVotes(cell, n){
    // draw votes during voting phase
    cell.style.background = '#3'+n+'3';
    votes.push(cell.id);
}

function undrawVotes(cell){
    cell.removeAttribute("style");
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
    console.log(data);
    votes.forEach(function(cell_id, index, array) {
      undrawVotes(document.getElementById(cell_id));
    });
    console.log(data);
    target = document.getElementById(data.cell);
    target.dataset.enabled = "false";
    target.dataset.votedfor = "true";
    target.dataset.code = parseInt(data.value);
});

var players = document.getElementById("players").children,
    nplayers = players.length;

socket.on('change_current_player', function(player_id){
    console.log('Switching '+player_id);
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

