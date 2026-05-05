import { useState } from "react"
import { languages } from "../language"
export default function Main(){
  const [currentWord , useCurrentWord] = useState("react")
  const alphabet = "abcdefghijklmnopqrstuvwxyz"
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
  const alphabetElement = alphabet.split("").map(letter => (
    <button key={letter}>{letter.toUpperCase()}</button>
  ))
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
    </main>
  )
}