// Page load reset controls
document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("board-options").reset();
})

// Enable all letter inputs
let letter_inputs = document.querySelectorAll(".board-cell-input");
letter_inputs.forEach(x => {
    x.removeAttribute("readonly");
});

let lettersInput = document.getElementById("lettersInput");
let solveBtn = document.getElementById("solve-board-btn");

// Board randomization
async function get_random_board(dice_type, size) {
    const response = await fetch(`api/random?dice_type=${dice_type}&size=${size}`, {
        method: "GET",
        headers: {"Content-type": "application/json;charset=UTF-8"}
    });
    let json = await response.json();
    return json;
}

let randomBoardBtn = document.getElementById("randomBoardBtn");
let randomDiceSelect = document.getElementById("diceSelect");
randomBoardBtn.addEventListener("click", e => {
    get_random_board(randomDiceSelect.value, sizeSelect.value)
    .then(json => {
        for (let row = 0; row < sizeSelect.value; row++) {
            for (let col = 0; col < sizeSelect.value; col++) {
                letter_input = document.querySelector(`.board-cell[data-pos='${row},${col}']`)
                letter_input.firstElementChild.value = json.board[row][col]
            }
        }
    });
});

// Solving board loading animation and control toggle
function toggle_board_controls() {
    let solveBtnTxt = document.getElementById("solve-btn-txt")
    let solvingSpinner = document.getElementById("solving-spinner")
    solveBtnTxt.toggleAttribute("hidden")
    solvingSpinner.toggleAttribute("hidden")
    solveBtn.toggleAttribute("disabled")
}

// Check update status of solve board task
async function update_solve_progress(url, task_id) {
    const response = await fetch(url);
    const json = await response.json();
    
    if (json["status"] == "SUCCESS") {
        toggle_board_controls()
        window.location = `/board/solved/${task_id}`;
        return;
    }
    // Poll for completed solve task
    setTimeout(function() {
        update_solve_progress(url, task_id);
    }, 250)
}

// Solve board task start execution
async function start_board_solve_task(rows, cols, letters, dictionary, max_len) {
    toggle_board_controls()
    let board_data = {
        rows,
        cols,
        letters,
        dictionary,
        max_len,
    }
    
    let options = {
        method: "POST",
        body: JSON.stringify(board_data),
        headers: {
            "Content-Type": "application/json"
        },
    }
    fetch("solve/task", options).then(async response => {
        response.json().then(json => {
            update_solve_progress(json["status_url"], json["task_id"])
        })
    })
}

// Solve button
solveBtn.addEventListener("click", x => {
    let letter_inputs = document.querySelectorAll(".board-cell-input");
    let letters = Array.from(letter_inputs).map(x => x.value).join(",");
    lettersInput.setAttribute("value", letters);

    let rows, cols;
    rows = cols = document.getElementById("sizeSelect").value;
    let dictionary = document.getElementById("dictionarySelect").value;
    let max_len = document.getElementById("maxLengthSelect").value;

    start_board_solve_task(rows, cols, letters, dictionary, max_len)
});

// Board resizing
let sizeSelect = document.getElementById("sizeSelect");
sizeSelect.addEventListener("change", e => {
    // Delete old board
    board = document.getElementById("board");
    board.textContent = "";
    let gap_scale = 40;
    board.style["gap"] = `${gap_scale / sizeSelect.value}px`
    // Generate HTML for resized board
    for (r = 0; r < sizeSelect.value; r++) {
        row_div = document.createElement("div");
        row_div.setAttribute("class", "board-row");
        row_div.style["gap"] = `${gap_scale / sizeSelect.value}px`
        for (c = 0; c < sizeSelect.value; c++) {
            cell_div = document.createElement("div");
            cell_div.setAttribute("class", "board-cell");
            cell_div.setAttribute("data-pos", `${r},${c}`);
            let letter_size = 10 / sizeSelect.value;
            cell_div.style["font-size"] = `${letter_size}rem`;
            cell_div.style["board-radius"] = "1px";
            input = document.createElement("input");
            input.setAttribute("class", "board-cell-input");
            input.setAttribute("type", "text");
            input.setAttribute("minlength", "1");
            input.setAttribute("maxlength", "2");
            input.setAttribute("value", "");
            cell_div.append(input);
            row_div.append(cell_div);
        }
        board.append(row_div);
    }
});
