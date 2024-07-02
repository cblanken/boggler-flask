let $table = $("#word-table");
let board_cells = document.querySelectorAll(".board-cell");
let board_cells_inputs = document.querySelectorAll(".board-cell-input");
let path_buttons = document.querySelectorAll("#test-table tr .path-cell button");

// Share board link button
let copyUrlBtn = document.getElementById("copyBoardUrlBtn");
let copyUrlBtnIcon = document.getElementById("copyBoardUrlBtnIcon");
let copyUrlBtnText = document.getElementById("copyBoardUrlBtnText");
let board_hash = copyUrlBtn.dataset["board_hash"]
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

    navigator.clipboard.writeText(encodeURI(`${window.location.origin}/board/solved/${board_hash}`));
});

// Update URL
history.replaceState(null, "", encodeURI(`${window.location.origin}/board/solved/${board_hash}`));

const dictionaries = await fetch(`${window.location.origin}/api/dictionaries`).then(res => res.json());
const board_data = await fetch(`${window.location.origin}/board/api/solved/${copyUrlBtn.dataset["board_hash"]}`).then(res => res.json());

// Add word lengths to word data
board_data["words"] = board_data?.words?.map(row => row.concat(row[0].length)) || {};

let words_datatable = new DataTable("#word-table", {
    lengthMenu: [
        [10, 25, 50, 100, -1],
        [10, 25, 50, 100, 'All'],
    ],
    columns: [
        { title: 'Word' },
        { title: "Path" },
        { title: '<span class="bi-book-half" style="margin-right: 0.5rem;"></span>Dictionaries' },
        { title: "Length" },
        { title: "Definitions" },
    ],
    columnDefs: [
        {
            target: 1,
            visible: false,
        },
        {
            target: 2,
            visible: true,
        },
        {
            target: 4,
            render: (data, type, row) => {
                let html = `
                    <a rel="noopener noreferrer" target="_blank" href="https://www.dictionary.com/browse/${row[0]}"><svg width="5mm" height="5mm" viewBox="0 0 10.223001 11.01918"><path d="M 5.063901,0.03997366 0.13741,3.6557552e-6 C 0.11932,-1.1834424e-4 0.10154,0.00280366 0.08493,0.01020366 c -0.01662,0.0074 -0.03182,0.01702 -0.04471,0.02971 -0.01281,0.01274 -0.02284,0.02791 -0.02982,0.04475 C 0.0028,0.10134366 0,0.11936366 0,0.13753366 V 8.7100267 c 1.1e-5,0.02669 0.0076,0.05299 0.02026,0.07608 0.01324,0.02321 0.0322,0.04246 0.05519,0.05595 l 3.694472,2.1606843 c 0.01845,0.0106 0.03948,0.01644 0.06067,0.01644 0.02136,0 0.04222,-0.0064 0.06074,-0.01635 0.01847,-0.0106 0.03382,-0.02619 0.04457,-0.04478 0.0106,-0.0185 0.01631,-0.03964 0.01632,-0.06112 V 2.8807997 c 8e-6,-0.02742 -0.0079,-0.05426 -0.02124,-0.07782 -0.01394,-0.02356 -0.0338,-0.04294 -0.05761,-0.05612 L 1.909323,1.6655667 c -0.01628,-0.0093 -0.02875,-0.02365 -0.03545,-0.04112 -0.0074,-0.01748 -0.0076,-0.03678 -7.01e-4,-0.05438 0.007,-0.01761 0.01832,-0.03258 0.0344,-0.04204 0.01609,-0.0096 0.03483,-0.01307 0.05319,-0.01 l 3.543052,0.611575 c 0.03255,0.0062 0.06209,0.02242 0.0833,0.04779 0.02131,0.02538 0.03285,0.05742 0.0328,0.09067 v 7.216684 c 1.8e-5,0.02007 0.0034,0.03978 0.01242,0.05802 0.0086,0.01825 0.02021,0.03451 0.03502,0.04773 0.015,0.01322 0.03251,0.02313 0.05139,0.02888 0.01909,0.0065 0.03899,0.008 0.05875,0.0043 2.623358,-0.29547 4.411597,-2.153998 4.44505,-4.731994 0.03621,-2.88776 -2.084816,-4.81197704 -5.158707,-4.85228204 z" fill="white" id="path46" style="fill:#00248b;fill-opacity:1;stroke-width:0.102852"/></svg></a>
                    <a rel="noopener noreferrer" target="_blank" href="https://www.wordnik.com/words/${row[0]}"><svg width="5.6mm" height="5mm" viewBox="0 0 8.9474049 8.1470804" version="1.1" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg"> <defs id="defs945"> <linearGradient inkscape:collect="always" id="linearGradient4043"> <stop style="stop-color:#dd300e;stop-opacity:1;" offset="0" id="stop4039" /> <stop style="stop-color:#ffb449;stop-opacity:1;" offset="1" id="stop4041" /> </linearGradient> <linearGradient inkscape:collect="always" id="linearGradient2528"> <stop style="stop-color:#ff6600;stop-opacity:0;" offset="0" id="stop2526" /> <stop style="stop-color:#ffb449;stop-opacity:1;" offset="1" id="stop2524" /> </linearGradient> <linearGradient inkscape:collect="always" xlink:href="#linearGradient2528" id="linearGradient2530" x1="51.980804" y1="115.08858" x2="144.6356" y2="115.08858" gradientUnits="userSpaceOnUse" spreadMethod="pad" /> <linearGradient inkscape:collect="always" xlink:href="#linearGradient4043" id="linearGradient4037" gradientUnits="userSpaceOnUse" x1="189.49008" y1="50.149723" x2="125.68763" y2="-13.403745" spreadMethod="pad" gradientTransform="matrix(0.06828328,0.06828328,-0.06828328,0.06828328,88.814867,103.97481)" /> </defs> <g inkscape:label="Layer 1" inkscape:groupmode="layer" id="layer1" transform="translate(-93.834505,-111.01504)"> <g id="g1290" style="opacity:1;fill:url(#linearGradient2530);fill-opacity:1"> <path id="path1721" style="fill:url(#linearGradient4037);fill-opacity:1;stroke-width:0.02555" d="m 100.18774,111.01504 c -0.743928,0 -1.412746,0.31007 -1.88492,0.80847 -0.471549,-0.4918 -1.135835,-0.79719 -1.874137,-0.79719 -1.437171,0 -2.594178,1.15701 -2.594178,2.59418 0,0.7373 0.304569,1.40076 0.795196,1.87219 l -6.99e-4,7e-4 3.668678,3.66873 3.59173,-3.59173 c 0.54736,-0.47493 0.8925,-1.17627 0.8925,-1.96117 0,-1.43717 -1.157,-2.59418 -2.59417,-2.59418 z"/></g></g></svg></a>
                    <a rel="noopener noreferrer" target="_blank" href="https://www.merriam-webster.com/dictionary/${row[0]}"><img src="/static/images/merriam-webster.svg" alt="Merriam Webster Dictionary" width="20mm" height="20mm"></a>
                    <a rel="noopener noreferrer" target="_blank" href="https://www.collinsdictionary.com/us/dictionary/english/${row[0]}"><img src="/static/images/www.collinsdictionary.com.ico" alt="Collins Dictionary" width="20mm" height="20mm"></a>
                    <a rel="noopener noreferrer" target="_blank" href="https://en.wiktionary.org/wiki/${row[0]}"><img src="/static/images/www.wiktionary.org.ico" alt="Wiktionary" width="20mm" height="20mm"></a>
                    <a rel="noopener noreferrer" target="_blank" href="https://www.google.com/search?q=define+${row[0]}"><img src="/static/images/google.svg" alt="Google" width="20mm" height="20mm"></a>
                `
                return html
            }
        }
    ],
    data: board_data["words"],
});

words_datatable.ready(() => {
    let spinner = document.querySelector(".datatable-spinner");
    spinner.classList.add("fade-out");
    document.querySelector(".datatable-wrapper")?.classList.add("fade-in");
})

document.querySelectorAll("#dictionary-checkboxes input").forEach(input => {
    input.addEventListener("change", (e) => {
        let ids = Array.from(document.querySelectorAll("#dictionary-checkboxes input")).filter(x => x?.checked).map(x => x.dataset["id"])
        if (ids.length === 0) {
            words_datatable.column(2).search().draw()
        } else {
            words_datatable.column(2).search(new RegExp(ids.join("|"))).draw()
        }
    });
})

document.querySelectorAll("#dictionary-checkboxes button").forEach(btn => {
    btn.addEventListener("click", (e) => {
        let input = e.target.querySelector("input[type='checkbox']")
        input.checked = !input.checked;
        input.dispatchEvent(new Event("change"));
    })
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

    for (let i=1; i < path.length; i++) {
        let cell1 = path[i-1];
        let cell2 = path[i];
        let c1 = document.querySelector(`#board [data-pos=\"${cell1[0]}, ${cell1[1]}\"] input`);
        let c2 = document.querySelector(`#board [data-pos=\"${cell2[0]}, ${cell2[1]}\"] input`);
        let x1, x2, y1, y2;

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

    let path = []
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
        words_datatable.column(1).search("").draw()
        remove_filter_btn.style.display = "none";
        unhighlight_board_filter();
        unhighlight_board();
        remove_arrows(active_arrows);
        active_arrows = [];
})

board_cells.forEach( cell => {
    cell.addEventListener("click", () => {
        words_datatable.column(1).search(p => p.includes(cell.dataset.pos)).draw()
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
    let path = get_path_from_string(data[1]);
    toggle_path_highlight(path);
    active_arrows = draw_path_connections(path);
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
