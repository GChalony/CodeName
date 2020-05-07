var socket = io("/grid");

function drawVotes(cell, n){
    cell.style.background = '#'+n+''+n+''+n;
}

function selectCell(event){
    console.log(event);
    event.target.dataset.selected = "true";
}

function voteCell(event){
    console.log(event);
    socket.emit('vote_cell', event.target.id);
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
    target.dataset.selected = "true";
    target.dataset.code = parseInt(data.value);
});

var players = document.getElementsById("tdplayers").children,
    nplayers = players.length;

socket.on('switch_teams', function(data){
    for (var i=0; i<nplayers; i++){
        var player = players[i];
        if ( player.classList.contains('MyClass') ){
            player.classList.remove('current-player');
        }
        if (player.id == data.current_player_id){
            player.classList.add('current-player');
        }
    }

});

socket.on('change_title', function(new_title){
    // Change title here
});

socket.on('change_controle', function(){
    // Change (or hide) controls here
    // controls.display = 'none';
});