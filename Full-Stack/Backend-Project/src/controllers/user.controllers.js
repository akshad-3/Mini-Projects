import { asyncHandler } from "../utils/asyncHandler.js";
import { APIerror } from "../utils/APIerror.js"
import { User } from "../models/user.models.js"
import { uploadOnCloudinary } from "../utils/cloudinary.modules.js"
import { APIresponce } from "../utils/APIresponce.js";
import { cache } from "react";

const genarateAccessandRefreshTokens = async(userId)=>{
    try {
        const user = await user.findOne(userId)
        const accessToken = user.generateAccessToken
        const refreshToken = user.generateRefreshToken

        user.refreshToken = refreshToken
        await user.save({validateBeforeSave : false})

        return {accessToken,refreshToken}
    } catch (error) {
        throw new APIerror(500,"somthing went wrong while genarating access and refresh tokens")
        
    }
}

const registerUser = asyncHandler(async(req, res)=>{
    const {fullname, email, username, password} = req.body

    if ([fullname, email, username, password].some((field) => field?.trim() === "")) {
        throw new APIerror(400, "All fields are required")
    }

    const existingUser = await User.findOne({
        $or: [{ username }, { email }]
    })
    if (existingUser) {
        throw new APIerror(409, "User with this email or username already exists")
    }

    const avatarLocalPath = req.files?.avatar?.[0]?.path
    //const coverImagePath = req.files?.coverImage?.[0]?.path
    let coverImagePath;
    if(req.files && Array.isArray(req.files.coverImage) && req.files.coverImage.length > 0){
        coverImagePath = req.files.coverImage[0].path
    }

    if (!avatarLocalPath) {
        throw new APIerror(400, "Avatar is required")
    }

    const avatar = await uploadOnCloudinary(avatarLocalPath)
    const coverImage = await uploadOnCloudinary(coverImagePath)

    if (!avatar) {
        throw new APIerror(400, "Avatar upload failed")
    }

    const user = await User.create({
        fullName: fullname,  
        avatar: avatar.url,
        coverImage: coverImage?.url || "",
        email,
        password,
        username: username.toLowerCase()
    })

    const createdUser = await User.findById(user._id).select("-password -refreshToken")

    if (!createdUser) {
        throw new APIerror(500, "Something went wrong while registering user")
    }

    return res.status(201).json(
        new APIresponce(200, createdUser, "User registered successfully")
    )
})
const loginUser = asyncHandler(async(req,res)=>{
    const {email, username, password} = req.body

    if(!username || !email){
        throw new APIerror(400,"Username or passward required")

    }
    const user = await User.findOne({
        $or: [{username}, {email}]
    })

    if(!user){
        throw new APIerror(404,"this user does not exist")
    }

    const isPasswordvalid = await user.isPasswordCorrect(password)

    if(!isPasswordvalid){
        throw new APIerror(401,"Invalid user Cridentials")
    }

    const {accessToken, refreshToken} = await generateAccessToken(user._id)

    const loggedInUser = await user.findById(user._id).select("-password -refreshToken")

    const options = {
        httponly: true,
        secure: true
    }
    return res.status(200).cookie("accessToken", accessToken , options).cookie("refreshToken",refreshToken, options)
    .json(
        new APIresponce(
            200,
            {
                user : loggedInUser, refreshToken, accessToken

            },
            "user Logged in Successfully "
        )
    )
})

const logOutUser = asyncHandler(async(req, res)=>{
    
})
export { registerUser, loginUser }

