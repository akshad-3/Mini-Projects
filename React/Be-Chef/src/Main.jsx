import React from "react";
import RecipeComponent from "./component/beChefrecipe";
import IngredientList from "./component/ingredientList";
import { getRecipeFromMistral } from "./ai"

export default function Main() {
  const [ingredients, setIngredients] = React.useState([])
  const [recipeShown, SetrecipeShown] = React.useState("")
  const [loading, setLoading] = React.useState(false)  
  const [error, setError] = React.useState("")          
  const recipeSection = React.useRef(null)
  console.log(recipeSection)

  React.useEffect(()=>{
    if(recipeShown !== "" && recipeSection.current !== null){
      recipeSection.current.scrollIntoView({behavior:"smooth"})
    }
  },[recipeShown])

  async function getrecipe() {
    setLoading(true)
    setError("")
    try {
      const recipeMarkdown = await getRecipeFromMistral(ingredients)
      console.log("Recipe result:", recipeMarkdown)
      SetrecipeShown(recipeMarkdown)
    } catch (err) {
      console.error("Full error:", err)
      setError(`Error: ${err.message}`)  
    } finally {
      setLoading(false)
    }
  }

  function handleSubmit(formdata) {
    const newIngredient = formdata.get("ingredient")
    setIngredients(prevIngredients => [...prevIngredients, newIngredient])
    SetrecipeShown("")
  }

  return (
    <main>
      <form action={handleSubmit} className="add-ingredient-form">
        <input
          type="text"
          placeholder="e.g tomato"
          aria-label="Add ingredient"
          name="ingredient"
        />
        <button>Add ingredient</button>
      </form>

      {ingredients.length > 0 && <IngredientList
        ref={recipeSection}
        ingredients={ingredients}
        getrecipe={getrecipe}
        recipeShown={recipeShown}
      />}

      {loading && <p>⏳ Getting your recipe, please wait...</p>}  {/* ✅ */}
      {error && <p style={{ color: "red" }}>{error}</p>}           {/* ✅ */}
      {recipeShown && <RecipeComponent recipe={recipeShown} />}
    </main>
  );
}