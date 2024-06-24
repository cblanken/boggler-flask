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
    const response = await fetch(`/api/random?dice_type=${dice_type}&size=${size}`, {
        method: "GET",
        headers: {"Content-type": "application/json;charset=UTF-8"}
    });
    let json = await response.json();
    return json;
}

let sizeSelect = document.getElementById("sizeSelect");
let randomBoardBtn = document.getElementById("randomBoardBtn");
let randomDiceSelect = document.getElementById("diceSelect");
randomBoardBtn.addEventListener("click", e => {
    get_random_board(randomDiceSelect.value, sizeSelect.value)
    .then(json => {
        for (let row = 0; row < sizeSelect.value; row++) {
            for (let col = 0; col < sizeSelect.value; col++) {
                letter_input = document.querySelector(`.board-cell[data-pos='${row}, ${col}']`)
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

// Solve button
boardForm = document.getElementById("board-options");
// solveBtn.addEventListener("click", x => {
boardForm.addEventListener("submit", e => {
    let letter_inputs = document.querySelectorAll(".board-cell-input");
    let letters = Array.from(letter_inputs).map(x => x.value).join(",");
    lettersInput.setAttribute("value", letters);

    let rows, cols;
    rows = cols = document.getElementById("sizeSelect").value;

    toggle_board_controls();
    return true;
});

// Board resizing
sizeSelect.addEventListener("change", e => {
    // Delete old board
    board = document.getElementById("board");
    board.textContent = "";
    DEFAULT_LETTER_SIZE = `calc(${BASE_LETTER_SIZE} * 4 / ${sizeSelect.value}`;
    DEFAULT_GAP_SIZE = `calc(${BASE_GAP_SIZE} * 4 / ${sizeSelect.value})`;
    root.style.setProperty("--letter-size", DEFAULT_LETTER_SIZE)
    root.style.setProperty("--cell-gap", DEFAULT_GAP_SIZE)
    // Generate HTML for resized board
    for (r = 0; r < sizeSelect.value; r++) {
        row_div = document.createElement("div");
        row_div.setAttribute("class", "board-row");
        for (c = 0; c < sizeSelect.value; c++) {
            cell_div = document.createElement("div");
            cell_div.setAttribute("class", "board-cell");
            cell_div.setAttribute("data-pos", `${r}, ${c}`);
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

