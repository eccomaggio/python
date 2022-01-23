const NBSP = "\u00a0"
let maxRow = 6
let maxCol = 5
let currRow = 0
let currCol = 0
let atEOR = false
const key = "robot"

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
    // console.log(id,i,feedback)
    classNames = ["wrong","nearly","exact"]
    document.getElementById(id).className = classNames[feedback]
}

function replaceAt(string,i,replacement){
    if (i >= string.length) alert("index is out of bounds")
    const head = string.slice(0,i)
    const tail = string.slice(i + replacement.length)
    return head + replacement + tail
}

function compareToKey(letter,i,KFCombo){
    const tmp = KFCombo[0].indexOf(letter)
    let match 
    if (tmp == -1) {
        match = 0
    }
    else if (tmp == i){
        match = 2
        KFCombo[0] = replaceAt(KFCombo[0],tmp,"*")
    }
    else {
        match = 1
        KFCombo[0] = replaceAt(KFCombo[0],tmp,"*")
    }
    KFCombo[1][i] = match
    // console.log(`**** ${letter} appears at index ${tmp} in key ${KFCombo[0]}, match=${match}:${KFCombo[1]}`)
    return KFCombo
}

function checkGuess(rowID,guess){
    const guessArr = Array.from(guess)
    let KFCombo = [key,[0,0,0,0,0]]
    guessArr.forEach((letter,i) => compareToKey(letter,i,KFCombo))
    const feedback = KFCombo[1]
    // KEY: 0=wrong, 1=nearly, 2=exact
    const guessIDs = []
    Array.from(document.getElementById(rowID).childNodes).forEach(e => guessIDs.push(e.id))
    guessIDs.forEach((id,i) => updateWordle(id, i, feedback[i]))
    const total = feedback.reduce((prevVal,currVal) => prevVal + currVal, 0)
    if (total == 10) alert(`You guessed in ${currRow + 1}.`)
}

function keyDownHandler(e) {
    const testDiv = document.getElementById("test")
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
            const guess = document.getElementById(rowID).textContent.replace(/\s+/g, '')
            if (guess.length != 5) {
                alert("It needs to have five letters.")
                break
            }
            // console.log(`current line (id=${rowID}): ${guess} [${guess.length} char(s)]`)
            checkGuess(rowID,guess)
            incRow()
            currCol = 0
            atEOR = false
            break
        default: 
            console.log(e.key)
    }

}
