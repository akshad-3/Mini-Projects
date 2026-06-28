import mongoose from "mongoose";
import { Schema } from "mongoose";

const userSchema = new Schema({
    username: {
        type: String,
        require: true,
        unique : true,
        trim: true,
        lowercase: true
    },
    email: {
      type: String,
      required: true,
      unique: true,
      trim: true,
      lowercase: true,
    },

    fullName: {
      type: String,
      required: true,
      trim: true,
    },

    password: {
      type: String,
      required: true,
    },
    refreshToken: {
      type: String,
      default: "",
    },
},
    {
        timestamps: true,
    }
)

export const User = mongoose.model("User",userSchema)