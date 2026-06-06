import { asyncHandler } from "../utils/asyncHandler.js";
import { APIerror } from "../utils/APIerror.js"
import { User } from "../models/user.models.js"
import { uploadOnCloudinary } from "../utils/cloudinary.modules.js"
import { APIresponce } from "../utils/APIresponce.js";

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
    if(req.files && Array.isArray(req.files.coverImage) && req.files.coverImage > 0){
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

export { registerUser }