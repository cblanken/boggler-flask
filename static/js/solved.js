let $table = $("#word-table");
let board_cells = document.querySelectorAll(".board-cell");
let path_buttons = document.querySelectorAll("#test-table tr .path-cell button")

function unhighlight_board_filter() {
    cells = document.querySelectorAll("#board [data-pos]")
    cells.forEach(cell => {
        cell.classList.remove("cell-highlight-filter")
    })
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
    let arrows = [];
    let arrow_params = {
        path: "straight",
        color: "#09008980",
        dash: {
            animation: true,
            gap: 8,
        },
        size: 6,
    }

    for (i=1; i < path.length; i++) {
        cell1 = path[i-1]
        cell2 = path[i]
        c1 = document.querySelector(`#board [data-pos=\"${cell1[0]},${cell1[1]}\"]`)
        c2 = document.querySelector(`#board [data-pos=\"${cell2[0]},${cell2[1]}\"]`)

        if (cell1[0] === cell2[0] ||
            cell1[1] === cell2[1] 
        ) { // Draw horizontal and vertical arrows between cells
            arrows.push(new LeaderLine(
                LeaderLine.areaAnchor(c1, {
                    x: "25%", y: "25%", width: "50%", height: "50%", color: "#FFFFFF00"
                }),
                LeaderLine.areaAnchor(c2, {
                    x: "25%", y: "25%", width: "50%", height: "50%", color: "#FFFFFF00"
                }),
                arrow_params
            ))
        } else { // Draw diagonal arrows between cells
            if (cell2[1] < cell1[1]) { // c2 left of c1
                x1 = "25%"
                x2 = "75%"
            } else { // c2 right of c1
                x1 = "75%"
                x2 = "25%"
            }
            if (cell2[0] < cell1[0]) { // c2 above c1
                y1 = "25%" 
                y2 = "75%" 
            } else { // c2 below c1
                y1 = "75%"
                y2 = "25%"
            }

            arrows.push(new LeaderLine(
                LeaderLine.pointAnchor(c1, {
                    x: x1, y: y1
                }),
                LeaderLine.pointAnchor(c2, {
                    x: x2, y: y2
                }),
                arrow_params
            ))
        }
    }

    return arrows
}

function remove_arrows(arrows) {
    if (arrows.length > 0) {
        arrows.forEach(arrow => {
            if(arrow !== undefined) { arrow.remove(); } 
        })
    }
}

// Parse path from string in table
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

// Add table filter board click events
window.operateEvents = {}

let remove_filter_btn = document.querySelector("#remove-filter-btn")
remove_filter_btn.addEventListener("click", _ => {
        $table.bootstrapTable("filterBy", {
        }, {
            'filterAlgorithm': (row, filters) => {
                return true
            }
        });
        remove_filter_btn.style.display = "none"
        unhighlight_board_filter()
        unhighlight_board()
        remove_arrows(active_arrows)
        active_arrows = []
})

board_cells.forEach( cell => {
    cell.addEventListener("click", (event) => {
        $table.bootstrapTable("filterBy", {
            pos: cell.dataset.pos
        }, {
            'filterAlgorithm': (row, filters) => {
                pos = filters.pos.split(',')
                return row.path.includes(`${pos[0]}, ${pos[1]}`)
            }
        });
        unhighlight_board_filter()
        unhighlight_board()
        remove_arrows(active_arrows)
        active_arrows = []
        cell.classList.add("cell-highlight-filter")
        remove_filter_btn.style.display = "block"
    })
})

// Add board highlight table click events
let active_arrows = []
$table.bootstrapTable({
    onCheck: function (row, element) {
        // TODO: implement correct API query to avoid doing this weird parsing
        // TODO: current solution only works for single digit indices
        unhighlight_board()
        remove_arrows(active_arrows)
        path = get_path_from_string(row.path)
        toggle_path_highlight(path)
        active_arrows = draw_path_connections(path)
    },
    onUncheck: function (row, element) {
        unhighlight_board()
        remove_arrows(active_arrows)
        active_arrows = []
    }
})