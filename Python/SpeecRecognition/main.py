import speech_recognition as sr
import webbrowser
import pyttsx3


recognizer = sr.Recognizer()
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def processcommand(c):
    if "google" in c.lower():
        webbrowser.open("https://google.com")
    elif "youtube" in c.lower():
        webbrowser.open("https://youtube.com")
    elif "linkedin" in c.lower():
        webbrowser.open("https://linkedin.com")
    elif "gmail" in c.lower():
        webbrowser.open("https://gmail.com")
    elif "valorant" in c.lower():
        webbrowser.open("https://www.youtube.com/live/lpd6Qy1gpXg?si=qFzpDvIffa-XqOZk")
if __name__=="__main__":
    speak("Initilizing 123...")
    while True:
        #this will listen for the word Danza
        #and it also obtain the audio form the microphone
        r=sr.Recognizer()
        
        print("Recognizing..")
        try:
            with sr.Microphone() as source:
                print("Listening...")
                audio= r.listen(source,timeout=5,phrase_time_limit=5)
            word= r.recognize_google(audio)
            if(word.lower()=="123"):
                speak("Ya")
                #listen for the command
                with sr.Microphone() as source:
                    print("123 Active...")
                    audio=r.listen(source)
                    command = r.recognize_google(audio)

                    processcommand(command)
        except Exception as e:
            print("ERROR; {0}".format(e))