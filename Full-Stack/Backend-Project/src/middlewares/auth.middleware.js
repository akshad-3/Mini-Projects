import { asyncHandlers } from "../utils/asyncHandler";

export const verifyJWT = asyncHandlers(async(requestAnimationFrame, res, next)=>{
    const token = req.cookies?.accessToken || req.header("Authorization")?.replace("Bearer ","")
})