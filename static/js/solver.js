// Enable all letter inputs
let letter_inputs = document.querySelectorAll(".board-cell input")
letter_inputs.forEach(x => {
    x.removeAttribute("disabled")
})

let lettersInput = document.getElementById("lettersInput")
let solveBtn = document.getElementById("solve-board-btn")

solveBtn.addEventListener("click", x => {
    let letters_csv = Array.from(letter_inputs).map(x => x.value).join(",")
    console.log(letters_csv)
    lettersInput.setAttribute("value", letters_csv)
})