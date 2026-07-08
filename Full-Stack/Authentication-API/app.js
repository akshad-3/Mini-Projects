import express from "express"
import userRouter from "./routes/user.routes"
const app = express()

app.use(express.json())
app.use("/",userRouter)
export default app
//this is the comment on day before my examination of OS ie. 7-7-26
//this is the comment on day my examination of OS ie. 8-7-26
