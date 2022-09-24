// Enable all letter inputs
let letter_inputs = document.querySelectorAll(".board-cell-input")
letter_inputs.forEach(x => {
    x.removeAttribute("disabled")
})

let lettersInput = document.getElementById("lettersInput")
let solveBtn = document.getElementById("solve-board-btn")

solveBtn.addEventListener("click", x => {
    let letter_inputs = document.querySelectorAll(".board-cell-input")
    let letters_csv = Array.from(letter_inputs).map(x => x.value).join(",")
    lettersInput.setAttribute("value", letters_csv)
})

// Board resizing
let sizeSelect = document.getElementById("sizeSelect")
sizeSelect.addEventListener("change", e => {
    // Delete old board
    board = document.getElementById("board")
    board.textContent = ""
    
    // Generate HTML for resized board
    for (r = 0; r < sizeSelect.value; r++) {
        row_div = document.createElement("div")
        row_div.setAttribute("class", "board-row")
        for (c = 0; c < sizeSelect.value; c++) {
            cell_div = document.createElement("div")
            cell_div.setAttribute("class", "board-cell")
            cell_div.setAttribute("data-pos", `${r},${c}`)
            input = document.createElement("input")
            input.setAttribute("class", "board-cell-input")
            input.setAttribute("type", "text")
            input.setAttribute("minlength", "1")
            input.setAttribute("maxlength", "2")
            input.setAttribute("value", "")
            cell_div.append(input)
            row_div.append(cell_div)
        }
        board.append(row_div)
    }
})

// Randomize board button
let randomBoardBtn = document.getElementById("randomBoardBtn")
randomBoardBtn.addEventListener("click", e => {
    // TODO: pull random dice from board_randomizer.py
    // alphabet = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','qu','r','s','t','u','v','w','x','y','z']
    // alphabet with matching 4x4 dice distribution
    alphabet = ["a", "a", "a", "a", "a", "a", "a", "a", "b", "b", "b", "c", "c", "c", "d", "d", "d", "d", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "f", "f", "g", "g", "g", "h", "h", "h", "i", "i", "i", "i", "i", "i", "i", "j", "k", "k", "l", "l", "l", "l", "l", "m", "m", "m", "n", "n", "n", "n", "n", "o", "o", "o", "o", "o", "o", "p", "p", "p", "qu", "r", "r", "r", "r", "s", "s", "s", "s", "s", "t", "t", "t", "t", "t", "u", "u", "u", "u", "v", "v", "w", "w", "x", "y", "y", "y", "z"]
    for (let row = 0; row < sizeSelect.value; row++) {
        for (let col = 0; col < sizeSelect.value; col++) {
            let index = parseInt(Math.random() * alphabet.length) % alphabet.length
            letter_input = document.querySelector(`.board-cell[data-pos='${row},${col}']`)
            letter_input.firstElementChild.value = alphabet[index]
        }
    }
})