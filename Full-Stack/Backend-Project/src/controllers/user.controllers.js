import { asyncHandler } from "../utils/asyncHandler.js";
import { APIerror } from "../utils/APIerror.js"
import { User } from "../models/user.models.js"
import { uploadOnCloudinary } from "../utils/cloudinary.modules.js"
import { APIresponce } from "../utils/APIresponce.js";
const genarateAccessandRefreshTokens = async(userId)=>{
    try {
        const user = await User.findById(userId)
         if (!user) {
            throw new APIerror(404, "User not found");
        }
        const accessToken = user.generateAccessToken()
        const refreshToken = user.generateRefreshToken()
        user.refreshToken = refreshToken
        await user.save({ validateBeforeSave : false })

        return {accessToken, refreshToken}
    } catch (error) {
        // throw new APIerror(500,"somthing went wrong while genarating access and refresh tokens")
        console.log(error);
        throw new APIerror(
        500,
        "Something went wrong while generating access and refresh tokens"
    );
        
        
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
        throw new APIerror(400
            , "User with this email or username already exists")
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

    if(!username && !email){
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

    const {accessToken, refreshToken} = await genarateAccessandRefreshTokens(user._id)

    const loggedInUser = await User.findById(user._id).select("-password -refreshToken")

    const options = {
        httpOnly: true,
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
    await User.findByIdAndUpdate(
        req.user._id,
        {
            $set: {
                refreshToken: undefined
            }
        },
        {
            new: true
        }
    )
    const options = {
        httpOnly: true,
        secure: true
    }
    return res.status(200)
    .clearCookie("accessToken",options)
    .clearCookie("refreshToken",options)
    .json(new APIresponce(200,{},"user logged out"))

})

const   refreshAccessToken = asyncHandler(async(req, res)=>{
    const incomingRefreshToken = req.cookies.refreshToken || req.body.refreshToken

    if(!incomingRefreshToken){
        throw new APIerror(401,"unauthorized Request")
    }
    try {
        const decodedToken = jwt.verify(
            incomingRefreshToken,
            process.env.REFRESH_TOKEN_SECRET
        )
    
        const user = await User.findById(decodedToken?._id)
    
        if(!user){
            throw new APIerror(401,"Invalid refresh token")
        }
        
        if(incomingRefreshToken !== user?.refreshToken){
            throw new APIerror(401,"refresh token is expired")
        }
        const options = {
            httpOnly = true,
            secure = true
        }
        const {accessToken, newRefreshToken} = await genarateAccessandRefreshTokens(user._id)
    
        return res.status(200)
        .cookie("accessToken", accessToken, options)
        .cookie("refreshToken", newRefreshToken, options)
        .json(
            new APIresponce(
                200,
                {accessToken, refreshToken: newRefreshToken},
                "Access token refreshed"
            )
        )
    } catch (error) {
        throw new APIerror(401,error?.message || "Invalid refresh Token")
    }
    
})

const changeCurrentPassword = asyncHandler(async(req, res)=>{
    const {oldPassword, newPassword} = req.body

    const user = await User.findById(req.user?._id)

    const isPasswordCorrect = await user.isPasswordCorrect(oldPassword)

    if(!isPasswordCorrect){
        throw new APIerror(400,"Invalid old Password")
    }

    user.password = newPassword
    await user.save({validateBeforeSave: false})

    return res
    .status(200)
    .json(new APIresponce(200,{},"Password Changed Successfully"))
})
const getCurrentUser = asyncHandler(async(req, res)=>{
    return res
    .status(200)
    .json(200,req.user,"Current user fetched successfully")
})

const updateAccountDetails = asyncHandler(async(req, res)=> {
    const { fullName, email} = req.body
    if(!fullName || !email){
        throw new APIerror(400,"All feilds are required")
    }
    const user = User.findByIdAndUpdate(
        req.user?._id,
        {
            $set: {
                fullName,
                email: email
            }
        },
        {new :true}
    ).select("-password")
    return res
    .status(200)
    .json(new APIresponce(200,user,"acccount details recived"))
})
const updateUserAvatar = asyncHandler(async(req, res)=>{
    const avatarlocalPath = req.file?.path

    if(!avatarlocalPath){
        throw new APIerror(400,"Avatar file is missing")
    }

    const avatar = await uploadOnCloudinary(avatarlocalPath)

    if(!avatar.url){
        throw new APIerror(400,"Error while uploading on avatar")
    }

    await User.findByIdAndUpdate(
        req.user?._id,
        {
            $set: {
                avatar: avatar.url
            }
        },
        {new:true}  
    ).select("-password")
    return res
    .status(200 )
    .json(
        new APIresponce(200,user,"avatar Img updated successfully")
    )
})

const updateUserCoverImg = asyncHandler(async(req, res)=>{
    const CoverImglocalPath = req.file?.path

    if(!CoverImglocalPath){
        throw new APIerror(400,"Cove Imgae file is missing")
    }

    const coverImg = await uploadOnCloudinary(coverImglocalPath)

    if(!avatar.url){
        throw new APIerror(400,"Error while uploading on Cover Img")
    }

    await User.findByIdAndUpdate(
        req.user?._id,
        {
            $set: {
                coverImg: coverImg.url
            }
        },
        {new:true}  
    ).select("-password")
    return res
    .status(200 )
    .json(
        new APIresponce(200,user,"Cover Img updated successfully")
    )
})

const getUserChannelProfile = asyncHandler(async(req, res)=>{
    const {username}= req.params
    if(!username?.trim()){
        throw new APIerror(400,"Username is missing")
    }
    
})

export { 
    registerUser,
    loginUser,
    logOutUser,
    refreshAccessToken,
    changeCurrentPassword,
    getCurrentUser,
    updateAccountDetails,
    updateUserAvatar,
    updateUserCoverImg
}

