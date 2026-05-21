
import logo from "./assets/logo.png"
export default function Header(){
    return(
        <header className="header-section">
            <img className="header-logo"src={logo} alt="Site-logo" />
            <h1 className="header-text">
                Be Chef
            </h1>
        </header>
    )
}