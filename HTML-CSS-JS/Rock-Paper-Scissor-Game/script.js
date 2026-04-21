
    const countscore ={
        Win:0,
        Loss:0,
        Tie:0
    };
    function playgame(playermove){
    const randommove = computerchoice();
    let result='';
    if(playermove==='Scissor'){
        if(randommove==='Rock'){
            result='you Loss';
        }
        else if(randommove==='Paper'){
            result='you Win';
        }
        else if(randommove==='Scissor'){
            result='you Tie';
        }
       
    }
    else if(playermove==='Paper'){
        if(randommove==='Rock'){
            result='you Win';
        }
        else if(randommove==='Paper'){
            result='you Tie';
        }
        else if(randommove==='Scissor'){
            result='you Loss';
        }
    }
    else if(playermove==='Rock'){
        if(randommove==='Rock'){
            result='you Tie';
        }
        else if(randommove==='Paper'){
            result='you Loss';
        }
        else if(randommove==='Scissor'){
            result='you Win';
        }
    }

    if(result==='you Win'){
        countscore.Win++;
    }
    else if(result==='you Loss'){
        countscore.Loss++;
    }
    else if(result==='you Tie'){
        countscore.Tie++;
    }
//     alert(`You picked ${playermove} & Computer picked ${randommove} ${result}
// Wins: ${countscore.Win} Losses: ${countscore.Loss} Ties: ${countscore.Tie}`);
    document.getElementById('resultDisplay').innerText =
     `You picked ${playermove}, Computer picked ${randommove}. ${result}`;

    document.getElementById('scoreDisplay').innerText =
    `Wins: ${countscore.Win}, Losses: ${countscore.Loss}, Ties: ${countscore.Tie}`;
    }

    function computerchoice(){
        const randomno = Math.floor(Math.random()*3);
        let randommove = '';
        if(randomno===0){
            randommove='Rock';
        }
        else if(randomno===1){
            randommove='Paper';
        }
        else{
            randommove='Scissor';
        }
        return randommove;
    }