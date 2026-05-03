const greetings = [
    "Hello!",
    "Hola!",       // Spanish
    "Bonjour!",    // French
    "Ciao!",       // Italian
    "Hallo!",      // German
    "Olá!",        // Portuguese
    "こんにちは!", // Japanese (Konnichiwa)
    "안녕하세요!",   // Korean (Annyeonghaseyo)
    "你好!",        // Chinese (Ni hao)
    "नमस्ते!",      // Hindi (Namaste)
  ];
  
  let current = 0;
  const helloText = document.getElementById('hello-text');
  
  function showNextGreeting() {
    helloText.textContent = greetings[current];
    current = (current + 1) % greetings.length; // loop back to start
  }
  
  // Change greeting every 2 seconds
  setInterval(showNextGreeting, 2000);
  
  // Initialize first greeting
  showNextGreeting();
  const texts = ["I am a Student", "I am a Developer", "I am a Designer"];
  let count = 0;
  let index = 0;
  let currentText = "";
  
  (function type() {
    if (count === texts.length) count = 0;
    currentText = texts[count];
    
    document.getElementById('typing-text').textContent = currentText.slice(0, ++index);
    
    if (index === currentText.length) {
      count++;
      index = 0;
      setTimeout(type, 1500); // Pause before next phrase
    } else {
      setTimeout(type, 100); // Typing speed
    }
  })();