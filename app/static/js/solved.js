let $table = $("#word-table");
let board_cells = document.querySelectorAll(".board-cell");
let board_cells_inputs = document.querySelectorAll(".board-cell-input");
let path_buttons = document.querySelectorAll("#test-table tr .path-cell button");

let words_datatable = new DataTable("#word-table", {
    lengthMenu: [
        [15, 30, 50, 100, -1],
        [15, 30, 50, 100, 'All'],
    ],
    columnDefs: [
        {
            target: 2,
            sortable: false,
        },
        {
            target: 3,
            visible: false,
        },
    ],
});

words_datatable.ready(() => {
    document.getElementById("word-table").style["display"] = "block";
    let spinner = document.getElementById("word-table-spinner");
    spinner.style["display"] = "none";
    spinner.classList.remove("d-flex");
})

function unhighlight_board_filter() {
    board_cells_inputs.forEach(cell => {
        cell.classList.remove("cell-highlight-filter");
    })
}
function unhighlight_board() {
    board_cells_inputs.forEach(cell => {
        cell.classList.remove("cell-highlight-first-letter");
        cell.classList.remove("cell-highlight");
    })
}

function toggle_path_highlight(path) {
    // Highlight first letter in word
    let cell = path[0];
    let c = document.querySelector(`#board [data-pos=\"${cell[0]}, ${cell[1]}\"] input`);
    // Highlight remainder
    c.classList.toggle("cell-highlight-first-letter");
    path.slice(1,).forEach(cell => {
        c = document.querySelector(`#board [data-pos=\"${cell[0]}, ${cell[1]}\"] input`);
        c.classList.toggle("cell-highlight");
    })
}

function draw_path_connections(path) {
    let arrows = [];
    let cells = document.querySelectorAll(".board-cell");
    let cell_input = document.querySelector(".board-cell-input");
    let font_size = getComputedStyle(cell_input).getPropertyValue("font-size").slice(0,-2);
    const arrow_scale = 1/7;
    let arrow_params = {
        path: "straight",
        color: "#09008980",
        dash: {
            animation: true,
            gap: 8,
        },
        size: font_size * arrow_scale,
    }

    for (i=1; i < path.length; i++) {
        let cell1 = path[i-1];
        let cell2 = path[i];
        let c1 = document.querySelector(`#board [data-pos=\"${cell1[0]}, ${cell1[1]}\"] input`);
        let c2 = document.querySelector(`#board [data-pos=\"${cell2[0]}, ${cell2[1]}\"] input`);

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
            ));
        } else { // Draw diagonal arrows between cells
            if (cell2[1] < cell1[1]) { // c2 left of c1
                x1 = "25%";
                x2 = "75%";
            } else { // c2 right of c1
                x1 = "75%";
                x2 = "25%";
            }
            if (cell2[0] < cell1[0]) { // c2 above c1
                y1 = "25%";
                y2 = "75%";
            } else { // c2 below c1
                y1 = "75%";
                y2 = "25%";
            }

            arrows.push(new LeaderLine(
                LeaderLine.pointAnchor(c1, {
                    x: x1, y: y1
                }),
                LeaderLine.pointAnchor(c2, {
                    x: x2, y: y2
                }),
                arrow_params
            ));
        }
    }

    return arrows;
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
    for (var i=1; i < path_string.length - 1; i++) {
        if (path_string[i] == "[" || path_string[i] == "(") {
            open_braces.push(i);
        } else if (path_string[i] == "]" || path_string[i] == ")") {
            close_braces.push(i);
        }
    }

    path = []
    for (var i=0; i < Math.min(open_braces.length, close_braces.length); i++) {
        let r = path_string[open_braces[i]+1];
        let c = path_string[close_braces[i]-1];
        path.push([r, c]);
    }

    return path;
}

// Add table filter board click events
window.operateEvents = {};

let remove_filter_btn = document.querySelector("#remove-filter-btn");
remove_filter_btn.addEventListener("click", _ => {
        words_datatable.column(3).search("").draw()
        remove_filter_btn.style.display = "none";
        unhighlight_board_filter();
        unhighlight_board();
        remove_arrows(active_arrows);
        active_arrows = [];
})

board_cells.forEach( cell => {
    cell.addEventListener("click", () => {
        words_datatable.column(3).search(p => p.includes(cell.dataset.pos)).draw()
        unhighlight_board_filter();
        unhighlight_board();
        remove_arrows(active_arrows);
        active_arrows = [];
        cell.firstElementChild.classList.add("cell-highlight-filter");
        remove_filter_btn.style.display = "block";
    })
});

// Add board highlight table click events
let active_arrows = [];
words_datatable.on("click", "tbody tr", function() {
    let data = words_datatable.row(this).data();
    
    unhighlight_board();
    remove_arrows(active_arrows);
    path = get_path_from_string(data[3]);
    toggle_path_highlight(path);
    active_arrows = draw_path_connections(path);

});

// Share board link button
let copyUrlBtn = document.getElementById("copyBoardUrlBtn");
let copyUrlBtnIcon = document.getElementById("copyBoardUrlBtnIcon");
let copyUrlBtnText = document.getElementById("copyBoardUrlBtnText");
copyUrlBtn.addEventListener("click", e => {
    copyUrlBtn.classList.remove("btn-primary");
    copyUrlBtn.classList.add("btn-success");
    copyUrlBtnIcon.classList.remove("bi-clipboard");
    copyUrlBtnIcon.classList.add("bi-clipboard-check");
    let btnText = copyUrlBtnText.textContent;
    copyUrlBtnText.textContent = "Copied!";

    setTimeout(_ => {
        copyUrlBtn.classList.add("btn-primary");
        copyUrlBtn.classList.remove("btn-success");
        copyUrlBtnIcon.classList.add("bi-clipboard");
        copyUrlBtnIcon.classList.remove("bi-clipboard-check");
        copyUrlBtnText.textContent = btnText;
    }, 1500);

    let board_hash = copyUrlBtn.dataset["board_hash"]
    navigator.clipboard.writeText(encodeURI(`${window.location.origin}/board/solved/${board_hash}`));
});

// Scroll-to-top popup button
let scrollToTopBtn = document.getElementById("scroll-to-top-btn");
scrollToTopBtn.addEventListener("click", (e) => {
    window.scrollTo(0, 0);
});

// Scroll board-in-picture
let board_height = document.getElementById("board").getBoundingClientRect().height;
let boardAndFilterBtn = document.getElementById("board-and-filter-btn");
let timeout = false;
const reset_letter_size = () => {
    root.style.setProperty("--letter-size", DEFAULT_LETTER_SIZE);
    root.style.setProperty("--letter-size-mobile", DEFAULT_LETTER_SIZE_MOBILE);
}

document.addEventListener("scroll", (e) => {
    if (!timeout) {
        window.requestAnimationFrame(() => {
            if (root.scrollTop > board_height) {
                root.style.setProperty("--letter-size-mobile", `${DEFAULT_LETTER_SIZE} / 2.5`);
                scrollToTopBtn.style["display"] = "block";
                boardAndFilterBtn.classList.add("board-in-picture");

                // Currently removing arrows on scroll for mobile 
                // to prevent unachored arrows
                // TODO: adapt leader lines for scroll
                remove_arrows(active_arrows);
                active_arrows = [];
            } else {
                reset_letter_size();
                scrollToTopBtn.style["display"] = "none";
                boardAndFilterBtn.classList.remove("board-in-picture");
            }
            timeout = false;
        })
    }
    timeout = true;
});

async function get_board_data(board_hash) {
    const response = await fetch(`${window.location.origin}/board/api/solved/${board_hash}`, {
        method: "GET",
        headers: {"Content-type": "application/json;charset=UTF-8"}
    });
    let json = await response.json();
    return json;
}

// Board heatmap
function toggle_heatmap() {
    const copyUrlBtn = document.getElementById("copyBoardUrlBtn");
    const hash = copyUrlBtn.dataset["board_hash"]
    get_board_data(hash)
    .then(json => {
        let rows = json["rows"];
        let cols = json["cols"];
        // Calculate how many times each letter is used for a given board
        let cell_counts = new Array(cols);
        let cell_colors = new Array(cols);
        for (let i = 0; i < cell_counts.length; i++) {
            cell_counts[i] = new Array(rows);
            cell_colors[i] = new Array(rows);
            cell_counts[i].fill(0);
            cell_colors[i].fill(0);
        }
        let words = json["words"];
        words.forEach((word) => {
            let path = JSON.parse(word[1]);
            path.forEach((cell_pos) => {
                cell_counts[cell_pos[0]][cell_pos[1]] += 1;
                cell_colors[cell_pos[0]][cell_pos[1]] += 1;
            })
        })
        
        let max = Math.max(...cell_counts.flat());
        for (let row = 0; row < cell_counts.length; row++) {
            for (let col = 0; col < cell_counts[row].length; col++) {
                // Scale count for HSL hue value
                cell_colors[row][col] = Math.floor(cell_counts[row][col] / max * 120);
            }
        }

        let heatmap_counts = document.querySelectorAll(".heatmap-count > div");
        heatmap_counts.forEach((count) => {
            let heatmap_container = count.parentElement;
            let parent = heatmap_container.parentElement;
            let cell = parent.querySelector(".board-cell-input");
            let pos = parent.getAttribute("data-pos").split(',').map(x => parseInt(x))
            count.textContent = cell_counts[pos[0]][pos[1]];
            let count_style = window.getComputedStyle(heatmap_container);
            let cell_style = window.getComputedStyle(cell);
            let theme = document.documentElement.getAttribute("data-theme");
            let lightness = getComputedStyle(document.documentElement).getPropertyValue("--heatmap-lightness")
            if (count_style.display == "none") {
                heatmap_container.style.setProperty("display", "flex", count_style.getPropertyPriority("display"));
                cell.style.setProperty("background-color", `hsl(${cell_colors[pos[0]][pos[1]]}, 50%, ${lightness})`, cell_style.getPropertyPriority("background-color"));
            } else {
                heatmap_container.style.setProperty("display", "none", count_style.getPropertyPriority("display"));
                cell.style.removeProperty("background-color");
            }
        })
    });
}

let heatMapBtn = document.getElementById("heatMapBtn");
heatMapBtn.addEventListener("click", (e) => {
    toggle_heatmap();
    heatMapCheckBox.checked = !heatMapCheckBox.checked;
})

if (heatMapCheckBox.checked) {
    // Disply heatmap on load if already enabled
    toggle_heatmap();
}
