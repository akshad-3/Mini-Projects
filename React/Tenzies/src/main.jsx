import Die from "./component/die.jsx"
import { useState,useRef,useEffect } from "react"
import { nanoid } from "nanoid"
import Confetti from 'react-confetti'

export default function main(){
  const [dice , setDice] = useState(generateAllNewDice())
  const buttonRef = useRef(null)
  const gameWon = dice.every(die => die.isHeld) && 
      dice.every(die => die.value === dice[0].value)
  useEffect(() => {
      if (gameWon) {
          buttonRef.current.focus()
      }
  }, [gameWon])
    
  function generateAllNewDice(){
    return new Array(10)
        .fill(0)
         .map(() => ({
              value: Math.ceil(Math.random() * 6), 
              isHeld: false,
              id:nanoid()
          }))
  }
  function hold(id ){
    setDice(oldDice => oldDice.map(die =>
          die.id === id ?
              { ...die, isHeld: !die.isHeld } :
              die
      ))
  }
   function rolltheDice() {
      if (!gameWon) {
          setDice(oldDice => oldDice.map(die =>
              die.isHeld ?
                  die :
                  { ...die, value: Math.ceil(Math.random() * 6) }
        ))
      } else {
          setDice(generateAllNewDice())
      }
    }

const diceElememt = dice.map(dieObj => (<Die key={dieObj.id}  value={dieObj.value } isHeld={dieObj.isHeld} hold={hold} id={dieObj.id}/>))  
  return(
    <main>
        {gameWon && <Confetti />}
        <div className="Die-container">
          {diceElememt}
        </div>
        <button ref={buttonRef} onClick={rolltheDice} >{gameWon ? "New Game" : "Roll"} </button>
    </main>
  )
}