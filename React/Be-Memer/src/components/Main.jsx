import { useState,useEffect } from "react"
export default function Main(){
    const [meme,setMeme] = useState({
        topText: "?",
        bottomText: "?",
        imageUrl: "http://i.imgflip.com/1bij.jpg"
    })
    const [memeData , setmemeData] = useState([])
    useEffect(()=>{
        fetch("https://api.imgflip.com/get_memes")
        .then(res => res.json())
        .then(data=>setmemeData(data.data.memes))  
    },[])
    
    function randOn(){
        const Number = Math.floor(Math.random()*memeData.length)
        const ImgUrl = memeData[Number].url
        
        setMeme(prevMeme=>({
            ...prevMeme,
            imageUrl : ImgUrl
        }))
        }

    function handleChange(event){
        const {value,name} = event.currentTarget
        console.log(value)
        setMeme(prevMeme =>({
            ...prevMeme,
            [name]:value
        }))
    }
    return(
        <main>
            <div className="Maindiv">
            <div className="form">
                <label>Top Text
                    <input
                        type="text"
                        placeholder="?"
                        name="topText"
                        onChange={handleChange}
                        />
                </label>

                <label>Bottom Text
                    <input
                        type="text"
                        placeholder="?"
                        name="bottomText"
                        onChange={handleChange}
                        />
                </label>
                <button onClick={randOn}>Get a new meme image 🖼</button>
            </div>
            <div className="meme">
                <img src={meme.imageUrl} />
                <span className="top">{meme.topText}</span>
                <span className="bottom">{meme.bottomText}</span>
            </div>
            </div>
        </main>
    )
}