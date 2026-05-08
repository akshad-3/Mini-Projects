import { useState } from "react"
import { languages } from "../language"
import clsx from 'clsx'

export default function Main(){
  const [currentWord , useCurrentWord] = useState("akshad")
  const [gussedLetters , setgussedLetters] = useState([])
  const alphabet = "abcdefghijklmnopqrstuvwxyz"

  const wrongGuessCount = gussedLetters.filter(letter => !currentWord.includes(letter)).length
  console.log(wrongGuessCount)

  const isGameWon = 
    currentWord.split("").every(letter => gussedLetters.includes(letter))
  const isGameLost = wrongGuessCount >= languages.length-1

  const isGameOver = isGameWon || isGameLost



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
  const letterElement = currentWord.split("").map((letter,index) => (
    <span key={index}>{gussedLetters.includes(letter) ? letter.toUpperCase() : ""}</span>
  ))
  const alphabetElement = alphabet.split("").map(letter => {
    const isGuessed = gussedLetters.includes(letter)
    const isCorrect = isGuessed && currentWord.includes(letter)
    const isWrong = isGuessed && !currentWord.includes(letter)

    return (
      <button 
        key={letter}
        className={clsx('btn' , isCorrect && 'activate' , isWrong && 'disable')}
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
      <section className="game-status">
        <h2>You Win</h2>
        <p>Well Done !</p>
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
      {isGameOver && <button className="newgameButton">New Game</button>}
    </main>
  )
}