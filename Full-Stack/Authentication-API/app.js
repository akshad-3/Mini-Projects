import express from "express"

const app = express()

app.use(express.json())
app.get("/",(req,res)=>{
    res.send("Server is successfully started")
})

export default app
