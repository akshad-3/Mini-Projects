import mongoose from "mongoose";
import { connect_DB } from "../constants.js"

const connectDB = async () => {
    try {
        const connectionInstance = await mongoose.connect(`${process.env.MONGODB_URI}/${connect_DB}`)
        console.log("MongoDB Connected!!");
    } catch (error) {
        console.error("MongoDB Connection has failed!!");
        console.error(error.message);
        process.exit(1)
    }
}
export default connectDB