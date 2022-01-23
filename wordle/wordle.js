const NBSP = "\u00a0"
let maxRow = 6
let maxCol = 5
let currRow = 0
let currCol = 0
let atEOR = false

function drawWordle() {
    let inputBoxes = document.createElement("div")
    for (let row = 0; row < maxRow; row++) {
        let tmpRow = document.createElement("div")
        tmpRow.setAttribute("id", `row${row}`)
        for (let col = 0; col < maxCol; col++ ){
            let input = document.createElement("div")
            input.setAttribute('id', `${row}-${col}`)
            input.setAttribute('class', 'wrong')
            input.appendChild(document.createTextNode(NBSP))       
            tmpRow.append(input)
        }
        inputBoxes.append(tmpRow)
    }
    let insertedBoxes = document.getElementById("wordleForm").append(inputBoxes)

    window.addEventListener('keydown', keyDownHandler)
    let testDiv = document.getElementById("test")
    testDiv.innerHTML = "set by jscript"
}

function incCol() {
    currCol += 1
    if (currCol >= maxCol) currCol = maxCol - 1
}
function incRow() {
    currRow += 1
    if (currRow >= maxRow) currRow = maxRow - 1
}

function decCol() {
    currCol -= 1
    if (currCol < 0) currCol = 0
} 

function currCell() {
    return `${currRow}-${currCol}`
}

function updateWordle(id,i, feedback){
    console.log(id,i,feedback)
    classNames = ["wrong","nearly","exact"]
    document.getElementById(id).className = classNames[feedback]
}

function checkGuess(rowID,guess){
    // feedback = [0,1,2,0,2]
    feedback = [2,2,2,2,2]
    // KEY: 0=wrong, 1=nearly, 2=exact
    const guessIDs = []
    Array.from(document.getElementById(rowID).childNodes).forEach(e => guessIDs.push(e.id))
    console.log(guessIDs)
    guessIDs.forEach((id,i) => updateWordle(id, i, feedback[i]))
    // console.log((prevVal,currVal) => prevVal + currVal, 0)
    const total = feedback.reduce((prevVal,currVal) => prevVal + currVal, 0)
    if (total == 10) alert("You guessed!!")
}

function keyDownHandler(e) {
    const testDiv = document.getElementById("test")
    // keyPressed = e.key.charCodeAt(0)
    // message = `key=${e.key} (${e.key.charCodeAt(0)}, ${e.key.length}),
    //  code=${e.code}; shift key? ${e.shiftKey} [c=${currCol}/${maxCol},
    //  r=${currRow}/${maxRow}]; at
    //  EOR? ${atEOR}`
    // testDiv.innerHTML = message 
    switch (e.code.slice(0,3)) {
        case "Key":
            if (!atEOR) document.getElementById(currCell()).innerHTML = e.key
            if (currCol == (maxCol - 1)) atEOR = true
            incCol()
            break
        case "Bac": 
            if (!atEOR) decCol()
            document.getElementById(currCell()).innerHTML = NBSP
            atEOR = false
            break
        case "Ent":
            const rowID = `row${currRow}`
            // console.log(`current line (id=${rowID}): ${document.getElementById(rowID).innerHTML}`)
            const guess = document.getElementById(rowID).textContent.replace(/\s+/g, '')
            if (guess.length != 5) {
                alert("It needs to have five letters.")
                break
            }
            console.log(`current line (id=${rowID}): ${guess} [${guess.length} char(s)]`)
            checkGuess(rowID,guess)
            incRow()
            currCol = 0
            atEOR = false
            break
        default: 
            console.log(e.key)
    }

}
