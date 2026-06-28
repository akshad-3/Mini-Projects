import dotenv from "dotenv";
import app from "./app.js"
import ConnectDB from "./db/index.js"
dotenv.config()

const PORT = process.env.PORT || 8000
ConnectDB()
    .then(()=>{
        app.listen(PORT,()=>{
            console.log(`server is running on the port http://localhost:${PORT || 8000}`);   
        });
    })
    .catch((error)=>{
        console.error("Server is failed to start...");
    })