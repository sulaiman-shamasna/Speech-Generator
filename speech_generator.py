import os
import threading
import logging
from tkinter import Tk, Label, Button, Entry, Text, filedialog, END, StringVar, OptionMenu, Scrollbar, RIGHT, Y
import pyttsx3
from gtts import gTTS
from playsound import playsound

# Set up logging
logging.basicConfig(filename='tts_app.log', level=logging.ERROR, format='%(asctime)s:%(levelname)s:%(message)s')

# Supported languages (ISO 639-1 codes)
LANGUAGES = {
    'English': 'en',
    'Spanish': 'es',
    'French': 'fr',
    'German': 'de',
    'Italian': 'it',
    'Portuguese': 'pt',
    'Russian': 'ru',
    'Chinese': 'zh-cn',
    'Japanese': 'ja',
    'Korean': 'ko'
}

class TextToSpeechApp:
    def __init__(self, master):
        self.master = master
        master.title("Advanced Text-to-Speech Converter - Developed by Sulaiman Shamasna")

        # Text Input
        self.label_text = Label(master, text="Enter Text:")
        self.label_text.grid(row=0, column=0, padx=5, pady=5, sticky='nw')

        self.text_input = Text(master, wrap='word', height=15, width=60)
        self.text_input.grid(row=0, column=1, padx=5, pady=5)

        # Scrollbar for Text Input
        self.scrollbar = Scrollbar(master, command=self.text_input.yview)
        self.scrollbar.grid(row=0, column=2, sticky='nsew')
        self.text_input['yscrollcommand'] = self.scrollbar.set

        # Load Text from File Button
        self.button_load = Button(master, text="Load Text File", command=self.load_text_file)
        self.button_load.grid(row=1, column=1, padx=5, pady=5, sticky='w')

        # Language Selection
        self.label_language = Label(master, text="Language:")
        self.label_language.grid(row=2, column=0, padx=5, pady=5, sticky='e')

        self.language_var = StringVar(master)
        self.language_var.set('English')  # default value

        self.dropdown_language = OptionMenu(master, self.language_var, *LANGUAGES.keys())
        self.dropdown_language.grid(row=2, column=1, padx=5, pady=5, sticky='w')

        # Voice Selection (Male/Female)
        self.label_voice = Label(master, text="Voice:")
        self.label_voice.grid(row=3, column=0, padx=5, pady=5, sticky='e')

        self.voice_var = StringVar(master)
        self.voice_var.set('Male')  # default value

        self.dropdown_voice = OptionMenu(master, self.voice_var, 'Male', 'Female')
        self.dropdown_voice.grid(row=3, column=1, padx=5, pady=5, sticky='w')

        # Speak Button
        self.button_speak = Button(master, text="Speak", command=self.speak_text)
        self.button_speak.grid(row=4, column=1, padx=5, pady=5, sticky='w')

        # Save Audio Button
        self.button_save = Button(master, text="Save Audio", command=self.save_audio)
        self.button_save.grid(row=4, column=1, padx=5, pady=5, sticky='e')

        # Initialize TTS engine
        self.engine = pyttsx3.init()
        self.configure_engine()

    def configure_engine(self):
        # Configure voice based on selection
        voices = self.engine.getProperty('voices')
        selected_voice = self.voice_var.get()
        language_code = LANGUAGES[self.language_var.get()]

        # Map language codes to pyttsx3 voice IDs
        voice_id = None
        for voice in voices:
            if language_code in voice.languages:
                if selected_voice == 'Male' and 'male' in voice.name.lower():
                    voice_id = voice.id
                    break
                elif selected_voice == 'Female' and 'female' in voice.name.lower():
                    voice_id = voice.id
                    break

        if voice_id:
            self.engine.setProperty('voice', voice_id)
        else:
            # Default to first available voice
            self.engine.setProperty('voice', voices[0].id)

    def load_text_file(self):
        filetypes = (
            ('Text files', '*.txt'),
            ('All files', '*.*')
        )
        filename = filedialog.askopenfilename(title='Open a text file', initialdir='/', filetypes=filetypes)
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    text = f.read()
                    self.text_input.delete(1.0, END)
                    self.text_input.insert(END, text)
            except Exception as e:
                logging.error(f"Error loading text file: {e}")
                self.text_input.insert(END, "An error occurred while loading the text file.\n")

    def speak_text(self):
        text = self.text_input.get(1.0, END).strip()
        if not text:
            self.text_input.insert(END, "Please enter text to speak.\n")
            return

        threading.Thread(target=self._speak_thread, args=(text,)).start()

    def _speak_thread(self, text):
        self.button_speak.config(state='disabled')
        try:
            self.configure_engine()
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            logging.error(f"Error during speech synthesis: {e}")
            self.text_input.insert(END, "An error occurred during speech synthesis.\n")
        finally:
            self.button_speak.config(state='normal')

    def save_audio(self):
        text = self.text_input.get(1.0, END).strip()
        if not text:
            self.text_input.insert(END, "Please enter text to save.\n")
            return

        filetypes = (
            ('MP3 files', '*.mp3'),
            ('WAV files', '*.wav'),
            ('All files', '*.*')
        )
        filename = filedialog.asksaveasfilename(title='Save audio file', defaultextension='.mp3', filetypes=filetypes)
        if filename:
            threading.Thread(target=self._save_audio_thread, args=(text, filename)).start()

    def _save_audio_thread(self, text, filename):
        try:
            language_code = LANGUAGES[self.language_var.get()]
            selected_voice = self.voice_var.get()

            if language_code == 'en':
                # Use pyttsx3 for English
                self.configure_engine()
                self.engine.save_to_file(text, filename)
                self.engine.runAndWait()
            else:
                # Use gTTS for other languages
                tts = gTTS(text=text, lang=language_code, slow=False)
                tts.save(filename)

            self.text_input.insert(END, f"Audio saved to {filename}\n")
        except Exception as e:
            logging.error(f"Error saving audio: {e}")
            self.text_input.insert(END, "An error occurred while saving the audio.\n")

def main():
    root = Tk()
    app = TextToSpeechApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
