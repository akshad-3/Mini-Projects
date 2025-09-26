import speech_recognition as sr
import webbrowser
import pyttsx3

recognizer = sr.Recognizer()
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def processcommand(c):
    pass
if __name__=="__main__":
    speak("Initilizing Danza...")
    while true:
        #this will listen for the word Danza
        #and it also obtain the audio form the microphone
        r=sr.Recognizer()