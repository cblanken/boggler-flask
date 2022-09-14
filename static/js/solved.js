let $table = $("#word-table");
let board_cells = document.querySelectorAll(".board-cell");
let path_buttons = document.querySelectorAll("#test-table tr .path-cell button")

// Add table filter board click events
window.operateEvents = {
    'click .path-cell': function (e, value, row, index) {
        console.log(value)
    }
}
board_cells.forEach( cell => {
    cell.addEventListener("click", (event) => {
        $table.bootstrapTable("filterBy", {
            word: [cell.textContent.trim()]
        });
        console.log("Filtering by: " + cell.textContent.trim());
    })
})

function unhighlight_board() {
    cells = document.querySelectorAll("#board [data-pos]")
    cells.forEach(cell => {
        cell.classList.remove("cell-highlight")
        console.log(cell)
    })
}

function toggle_path_highlight(path) {
    path.forEach(cell => {
        c = document.querySelector(`#board [data-pos=\"${cell[0]},${cell[1]}\"]`)
        console.log(c)
        c.classList.toggle("cell-highlight")
    })
}

function get_path_from_string(path_string) {
    let open_braces = [];
    let close_braces = [];
    for (var i=0; i < path_string.length; i++) {
        if (path_string[i] == "(") {
            open_braces.push(i);
        } else if (path_string[i] == ")") {
            close_braces.push(i);
        }
    }

    path = []
    for (var i=0; i < Math.min(open_braces.length, close_braces.length); i++) {
        let r = path_string[open_braces[i]+1]
        let c = path_string[close_braces[i]-1]
        path.push([r, c])
    }

    return path
}
// Add board highlight table click events
$table.bootstrapTable({
    onCheck: function (row, element) {
        // TODO: implement correct API query to avoid doing this weird parsing
        // TODO: current solution only works for single digit indices
        unhighlight_board()
        path = get_path_from_string(row.path)
        console.log(path)
        toggle_path_highlight(path)
    },
    onUncheck: function (row, element) {
        unhighlight_board()
    }
})
