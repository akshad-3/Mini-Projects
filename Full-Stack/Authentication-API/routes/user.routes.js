import { router } from "express"
import { registerUser } from "../controllers/user.controllers"

const router = Router()

router.post("/register", registerUser)

export default router;