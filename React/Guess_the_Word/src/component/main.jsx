import { useState } from "react"
import { languages } from "../language"
import clsx from 'clsx'

export default function Main(){
  const [currentWord , useCurrentWord] = useState("akshad")
  const [gussedLetters , setgussedLetters] = useState([])
  console.log(gussedLetters)
  const alphabet = "abcdefghijklmnopqrstuvwxyz"

  function addGussedLetters(letter){
    setgussedLetters(prevLetter =>[...prevLetter , letter])
  }
  const languageElement = languages.map(lang =>{
    const style={
      backgroundColor:lang.backgroundColor,
      color:lang.color
    }
    return(
      <span 
        style={style}
        className="chips"
        key={lang.name}
        >
        {lang.name}
       </span>
    )
  })
  const letterElement = currentWord.split("").map((letter,index) => (
    <span key={index}>{letter.toUpperCase()}</span>
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
      <button className="newgameButton">New Game</button>
    </main>
  )
}