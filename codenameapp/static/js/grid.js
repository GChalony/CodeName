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

socket.on('update_votes', function(votes){
    for (var cellCode in votes){
        var cell = getElementsById(cellCode);
        drawVotes(cell, votes[cell]);
    }
});

socket.on('vote_done', function(code, value){
    console.log(console, value);
    target = document.getElementsById(code);
    target.dataset.selected = "true";
    target.dataset.code = value;
});

var cells = document.getElementsByTagName("td"),
    ncells = cells.length;

for (var i=0; i<ncells; i++){
    var cell = cells[i];
    cell.addEventListener('click', voteCell);
}
