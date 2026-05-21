export default function BeChefRecipe({ recipe }) {
  return (
    <section>
      <h2>Suggested Recipe</h2>
      <div style={{ whiteSpace: "pre-wrap", fontFamily: "inherit" }}>{recipe}</div>

    </section>
  );
}