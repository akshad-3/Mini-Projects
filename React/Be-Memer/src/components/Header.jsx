import LogoIcon from "../assets/leaf.png"
export default function Header(){
    return(
        <header className="header">
            <img src={LogoIcon} alt="Icon" />
            <h1>Be Memer</h1>
        </header>
    )
}