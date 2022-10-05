// Enable all letter inputs
let letter_inputs = document.querySelectorAll(".board-cell-input");
letter_inputs.forEach(x => {
    x.removeAttribute("disabled");
});

let lettersInput = document.getElementById("lettersInput");
let solveBtn = document.getElementById("solve-board-btn");

solveBtn.addEventListener("click", x => {
    let letter_inputs = document.querySelectorAll(".board-cell-input");
    let letters_csv = Array.from(letter_inputs).map(x => x.value).join(",");
    lettersInput.setAttribute("value", letters_csv);
});

// Board resizing
let sizeSelect = document.getElementById("sizeSelect");
sizeSelect.addEventListener("change", e => {
    // Delete old board
    board = document.getElementById("board");
    board.textContent = "";
    
    // Generate HTML for resized board
    for (r = 0; r < sizeSelect.value; r++) {
        row_div = document.createElement("div");
        row_div.setAttribute("class", "board-row");
        for (c = 0; c < sizeSelect.value; c++) {
            cell_div = document.createElement("div");
            cell_div.setAttribute("class", "board-cell");
            cell_div.setAttribute("data-pos", `${r},${c}`);
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

async function get_random_board(dice_type, size) {
    const response = await fetch(`api/random?dice_type=${dice_type}&size=${size}`, {
        method: "GET",
        headers: {"Content-type": "application/json;charset=UTF-8"}
    });
    let json = await response.json();
    return json;
}

// Randomize board button
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
