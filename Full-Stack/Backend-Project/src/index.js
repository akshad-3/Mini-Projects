import dotenv from "dotenv"
import connectDB from "./db/index.js"

dotenv.config({
    path: './env'
})

connectDB()
.then(()=>{
    app.listen(process.env.PORT || 3000,()=>{
        console.log(`Serve is running at port : ${process.env.PORT}`);
    })
})
.catch((err)=>{
    console.log("mongoDB is connection failed !!!",err);
    
})

// const app = express()

// (async ()=>{
//     try {
//         await mongoose.connect(`${process.env.MONGODB_URI}/${ DB_akshad }`)
//         app.on("error",(error)=>{
//             console.log("error :",error)
//         })
//         app.listen(process.env.PORT,()=>{
//             console.log(`app is listining on port : ${process.env.PORT}`)
//         })
//     } catch (error) {
//         console.error("Error : ",error)
//     }
// })()