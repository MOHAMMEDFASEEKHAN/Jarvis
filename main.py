import speech_recognition as sr
import webbrowser
import pyaudio
import pyttsx3
import musicLibrary
import os
from dotenv import load_dotenv
from google import genai
from news import get_news
from gtts import gTTS
import pygame
import time 

load_dotenv()

recognizer = sr.Recognizer()
engine = pyttsx3.init()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# OLD SPEAK FUNCTION
def speak_old(text):
    engine.stop()
    engine.setProperty("volume", 1.0)
    engine.say(text)
    engine.runAndWait()


# NEW SPEAK FUNCTION - gTTS + pygame
def speak(text):
    print("Speaking:", text)

    tts = gTTS(text=text, lang="en")
    tts.save("temp.mp3")

    pygame.mixer.init()
    pygame.mixer.music.load("temp.mp3")
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    pygame.mixer.music.unload()
    pygame.mixer.quit()

    if os.path.exists("temp.mp3"):
        os.remove("temp.mp3")


# GEMINI
def ask_gemini(question):
    if not question or not isinstance(question, str):
        return "Please ask a valid question."

    max_attempts = 5
    for attempt in range(max_attempts):
        try:
            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=(
                    "Answer conversationally and concisely, as if speaking aloud. "
                    "Avoid Markdown formatting. User's question: "
                    f"{question}"
                )
            )

            if hasattr(response, "text") and response.text:
                return response.text

            if hasattr(response, "candidates") and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, "content") and hasattr(candidate.content, "parts"):
                    text_parts = []
                    for part in candidate.content.parts:
                        if hasattr(part, "text"):
                            text_parts.append(part.text)
                    if text_parts:
                        return "".join(text_parts)

            return "Sorry, I could not generate a response."

        except Exception as e:
            print(f"Gemini attempt {attempt + 1} failed:", e)

            if attempt < max_attempts - 1:
                # 503 responses are usually temporary; retry with exponential backoff.
                time.sleep(min(2 ** (attempt + 1), 30))

    return "Sorry, Gemini is not responding right now."

# COMMAND PROCESSING
def processcommand(c):

    if "open google" in c.lower():
        webbrowser.open("https://google.com")

    elif "open linkedin" in c.lower() or "open linkdin" in c.lower():
        webbrowser.open("https://linkedin.com")

    elif "open youtube" in c.lower():
        webbrowser.open("https://youtube.com")

    elif "open github" in c.lower():
        webbrowser.open("https://github.com")

    elif c.lower().startswith("play"):
        song = c.lower().split(" ")[1]
        link = musicLibrary.music[song]
        webbrowser.open(link)

    elif "news" in c.lower():
        headlines = get_news()

        if headlines:
            for headline in headlines:
                speak(headline)
        else:
            speak("Sorry, I could not fetch the news.")
        
    else:
        response = ask_gemini(c)
        speak(response)


# MAIN PROGRAM
if __name__ == "__main__":

    speak("Initializing Jarvis..")

    while True:

        r = sr.Recognizer()

        print("recognizing....")

        try:

            # WAIT FOR Nova
            with sr.Microphone() as source:

                print("Say something!")

                r.adjust_for_ambient_noise(source, duration=0.5)

                audio = r.listen(
                    source,
                    timeout=5,
                    phrase_time_limit=3
                )

            word = r.recognize_google(audio)

            print("You said:", word)

            # WAKE WORD
            if word.lower() == "Jarvis":

                speak("Yes, I'm listening...")

                with sr.Microphone() as source:

                    print("Jarvis Active...")

                    audio = r.listen(
                        source,
                        timeout=5,
                        phrase_time_limit=6
                    )

                command = r.recognize_google(audio)

                print("Command:", command)

                processcommand(command)

        except sr.UnknownValueError:

            print("Could not understand audio")

        except sr.WaitTimeoutError:

            print("Listening timed out")

        except Exception as e:

            print("Error:", e)