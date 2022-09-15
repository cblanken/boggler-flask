let $table = $("#word-table");
let board_cells = document.querySelectorAll(".board-cell");
let path_buttons = document.querySelectorAll("#test-table tr .path-cell button")
let arrows = []

// Add table filter board click events
window.operateEvents = {
    'click .path-cell': function (e, value, row, index) {
        console.log(value)
    }
}

function unhighlight_board() {
    cells = document.querySelectorAll("#board [data-pos]")
    cells.forEach(cell => {
        cell.classList.remove("cell-highlight-first-letter")
        cell.classList.remove("cell-highlight")
    })
}

function toggle_path_highlight(path) {
    // Highlight first letter in word
    let cell = path[0]
    let c = document.querySelector(`#board [data-pos=\"${cell[0]},${cell[1]}\"]`)
    // Highlight remainder
    c.classList.toggle("cell-highlight-first-letter")
    path.slice(1,).forEach(cell => {
        c = document.querySelector(`#board [data-pos=\"${cell[0]},${cell[1]}\"]`)
        c.classList.toggle("cell-highlight")
    })
}

function draw_path_connections(path) {
    arrows = []
    for (i=1; i < path.length; i++) {
        // TODO: add alternate handling for diagonal links (from center-to-center)
        cell1 = path[i-1]
        cell2 = path[i]
        c1 = document.querySelector(`#board [data-pos=\"${cell1[0]},${cell1[1]}\"]`)
        c2 = document.querySelector(`#board [data-pos=\"${cell2[0]},${cell2[1]}\"]`)
        arrows.push(new LeaderLine(
            LeaderLine.areaAnchor(c1, {
                x: "25%", y: "25%", width: "50%", height: "50%", radius: 20, color: "#FFFFFF00"
            }),
            LeaderLine.areaAnchor(c2, {
                x: "25%", y: "25%", width: "50%", height: "50%", color: "#FFFFFF00"
            }),
            {
                path: "straight",
                color: "#09008980",
                dash: {
                    animation: true,
                    gap: 8,
                },
                size: 6,
            },
        ))
    }

    return arrows
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

board_cells.forEach( cell => {
    cell.addEventListener("click", (event) => {
        $table.bootstrapTable("filterBy", {
            word: [cell.textContent.trim()]
        });
        console.log("Filtering by: " + cell.textContent.trim());
        cell.classList.toggle("cell-highlight")
    })
})

// Add board highlight table click events
$table.bootstrapTable({
    onCheck: function (row, element) {
        // TODO: implement correct API query to avoid doing this weird parsing
        // TODO: current solution only works for single digit indices
        unhighlight_board()
        arrows.forEach(arrow => arrow.remove() )
        path = get_path_from_string(row.path)
        console.log(path)
        toggle_path_highlight(path)
        draw_path_connections(path)
    },
    onUncheck: function (row, element) {
        unhighlight_board()
    }
})