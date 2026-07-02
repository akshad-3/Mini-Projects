import { User } from "../models/user.model.js"

const registerUser = async(req, res)=>{
    try {
        const {username, fullname, email, password} = req.body
        if(!username || !fullname || !email || !password){
            return res.status(400).json({
                success: false,
                Message: "All fields are required"
            })
        }
        const existingUser = await User.findOne({
            $or:[{username},{email}]
        })
        if(existingUser){
            return res.status(409).json({
                success: false,
                message: "This user already exist"
            })
        }
        const user = await User.create({
            username,
            fullName,
            email,
            password
        })
        return res.status(201).json({
            success: true,
            message: "user registered successfully",
            data: user
        })
    } catch (error) {
        return res.status(500).json({
            success: false,
            message: error.message
        })
    }
}

export { registerUser }