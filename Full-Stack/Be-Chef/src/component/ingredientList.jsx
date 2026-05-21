import React from "react";

const IngredientList = React.forwardRef(function IngredientList(props, ref) {
  const thelistarray = props.ingredients.map((item, index) => (
    <li key={index}>{item}</li>
  ));

  return (
    <section>
      <h2>Ingredients on Table :</h2>
      <ul className="ingredients-list" aria-live="polite">
        {thelistarray}
      </ul>
      {props.ingredients.length > 3 ? (
        <div className="get-recipe-container">
          <div ref={ref}>
            <h3>Excited for recipe?</h3>
          </div>
          <button onClick={props.getrecipe}>
            {props.recipeShown ? "Recipe shown" : "Get a recipe"}
          </button>
        </div>
      ) : undefined}
    </section>
  );
});

export default IngredientList;