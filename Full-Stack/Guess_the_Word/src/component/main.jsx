import { useState } from "react"
import { languages } from "../language"
import clsx from 'clsx'
import { getFarewellText , getRandomWord} from "../utils.js"

export default function Main(){
  const [currentWord , useCurrentWord] = useState(getRandomWord())
  const [gussedLetters , setgussedLetters] = useState([])
  const alphabet = "abcdefghijklmnopqrstuvwxyz"

  const wrongGuessCount = gussedLetters.filter(letter => !currentWord.includes(letter)).length

  const isGameWon = 
    currentWord.split("").every(letter => gussedLetters.includes(letter))
  const isGameLost = wrongGuessCount >= languages.length-1
  const isGameOver = isGameWon || isGameLost
  const lastGuessedLetter = gussedLetters[gussedLetters.length - 1]
  const isLastGuessIncorrect = lastGuessedLetter && !currentWord.includes(lastGuessedLetter)
  console.log(isLastGuessIncorrect)

  function startNewGame() {
        useCurrentWord(getRandomWord())
        setgussedLetters([])
    }

  const languageElement = languages.map((lang,index) =>{
    const isLanguageLost = index < wrongGuessCount
    const style={
      backgroundColor:lang.backgroundColor,
      color:lang.color
    }
    return(
      <span 
        style={style}
        className={clsx('chips' , isLanguageLost && 'lost')}
        key={lang.name}
        >
        {lang.name}
       </span>
    )
  })
  const letterElement = currentWord.split("").map((letter,index) => {
    const shouldShowletter = isGameLost || gussedLetters.includes(letter)
    const missingLetters = 
      clsx(
          isGameLost && !gussedLetters.includes(letter) && "missing-letters"
      )
    return(
      <span key={index} className={missingLetters}>{ shouldShowletter ? letter.toUpperCase() : ""}</span>
    )
})
  const alphabetElement = alphabet.split("").map(letter => {
    const isGuessed = gussedLetters.includes(letter)
    const isCorrect = isGuessed && currentWord.includes(letter)
    const isWrong = isGuessed && !currentWord.includes(letter)

    return (
      <button 
        key={letter}
        className={clsx('btn' , isCorrect && 'activate' , isWrong && 'disable')}
        disabled={isGameOver}
        onClick={() => setgussedLetters(
          prevletter => prevletter.includes(letter) ? prevletter : [...prevletter , letter]
        )}
        >
        {letter.toUpperCase()}
      </button>
    )
})
return(
<main>
      <section className={clsx('Nothing',isGameWon && 'game-status' , isGameLost && 'game-lost',isLastGuessIncorrect && !isGameOver && 'fairwell')}>
        <h2>{isGameWon ? "You Win" : isGameLost ? "You Lost" : isLastGuessIncorrect ? getFarewellText(languages[wrongGuessCount - 1 ].name) : ""}</h2>
        {isGameWon && <p>Well Done</p>}
        {isGameLost && <p>You Better Start Learning Assembly!</p>}
      </section>
      <section className="language-chips">
        {languageElement}
      </section>
      <section className="word">
        {letterElement}
      </section>
      <section className="keyboard">
        {alphabetElement}
      </section>
      {isGameOver && <button className="newgameButton" onClick={startNewGame}>New Game</button>}
    </main>
  )
}