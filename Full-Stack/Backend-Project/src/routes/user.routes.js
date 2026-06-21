import { Router } from "express";
import { upload } from "../middlewares/multer.middleware.js"
import { APIerror } from "../utils/APIerror.js"
import { verifyJWT } from "../middlewares/auth.middleware.js";
import { loginUser, logOutUser, registerUser, refreshAccessToken} from "../controllers/user.controllers.js";

const router = Router()
router.route("/register").post(
    upload.fields([
        {
            name: "avatar",
            maxCount: 1
        },
        {
            name: "coverImage",
            maxCount: 1
        }
    ]),
    registerUser
)
router.route("/login").post(loginUser);
router.route("/logout").post(verifyJWT, logOutUser)
router.route("/refresh-token").post(refreshAccessToken)
export default router