import mongoose from "mongoose"
import { DB_akshad } from "../constants.js"

const connectDB = async ()=>{
    try {
        const connectionInstance = await mongoose.connect(`${process.env.MONGODB_URI}/${DB_akshad}`)
        console.log(`\nMongoDB Connection Sucessffull!!! DB Host: ${connectionInstance.connection.host}`)
    } catch (error) {
        console.error("MongoDB connectio failed : ",error);
        process.exit(1)
    }
}

export default connectDB