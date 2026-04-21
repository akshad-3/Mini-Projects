export async function getRecipeFromMistral(ingredientsArr) {
  const API_KEY = import.meta.env.VITE_COHERE_API_KEY;

  const response = await fetch("https://api.cohere.com/v2/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${API_KEY}`
    },
    body: JSON.stringify({
      model: "command-r-plus-08-2024",
      messages: [
        {
          role: "user",
          content: `Create a recipe using these ingredients: ${ingredientsArr.join(", ")}. Format it nicely with ingredients and steps.`
        }
      ]
    })
  });

  const data = await response.json();
  if (data.error) throw new Error(data.error.message);
  return data.message?.content?.[0]?.text || "No recipe generated.";
}