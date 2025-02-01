import tkinter as tk
from tkinter import filedialog
from tkinter import ttk, messagebox
import os
import logging
from googletrans import Translator, LANGUAGES
from gtts import gTTS
from playsound import playsound
from PIL import Image, ImageTk
import pytesseract
import speech_recognition as sr
import threading

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Run:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Language Translator")
        self.root.geometry("1040x600")
        self.root.resizable(True, True)
        self.root.config(bg="#b2c2cf")
        self.languages = LANGUAGES
        self.language_list = list(self.languages.values())
        self.translator = Translator()
        self.reco = sr.Recognizer()
        self.placing_widgets()
        self.root.mainloop()

    def placing_widgets(self):
        """For widgets on the GUI."""
        # Text Boxes
        self.original_text = tk.Text(self.root, height=10, width=40, bg="#ffffff", font=("Times New Roman", 14))
        self.original_text.grid(row=1, column=1, pady=20, padx=10, rowspan=3)
        self.translated_text = tk.Text(self.root, height=10, width=40, bg="#ffffff", font=("Times New Roman", 14))
        self.translated_text.grid(row=1, column=3, pady=20, padx=10, rowspan=3)

        # Buttons
        self.translate_button = tk.Button(self.root, text="Translate", font=("Times", 23), command=self.translate_it, bg="#4db4d6", fg="black")
        self.translate_button.grid(row=2, column=2, padx=15)
        self.voice_input_button = tk.Button(self.root, text="Voice Input", font=("Times", 23), command=self.voice_input, bg="#4db4d6")
        self.voice_input_button.grid(row=8, column=1, padx=12, pady=10)
        self.voice_output_button = tk.Button(self.root, text="Voice Output", font=("Times", 23), command=self.voice_output, bg="#4db4d6")
        self.voice_output_button.grid(row=8, column=3, padx=12, pady=10)
        self.image_button = tk.Button(self.root, text="Load Image", font=("Times", 23), command=self.load_image, bg="#4db4d6")
        self.image_button.grid(row=8, column=2, padx=12, pady=10)

        # Combo Boxes
        self.original_combo = ttk.Combobox(self.root, width=50, height=10, value=self.language_list)
        self.original_combo.current(21)
        self.original_combo.grid(row=6, column=1, pady=(0, 10))
        self.translated_combo = ttk.Combobox(self.root, width=50, height=10, value=self.language_list)
        self.translated_combo.current(38)
        self.translated_combo.grid(row=6, column=3, pady=(0, 10))

        # Clear Button
        self.clear_button = tk.Button(self.root, text="Clear", command=self.clear, bg="#4db4d6", width=7, height=2)
        self.clear_button.grid(row=3, column=2, pady=(0, 10))

        # Image display
        self.image_label = tk.Label(self.root, bg="white")
        self.image_label.grid(row=1, column=4, rowspan=3, pady=(0, 10))

    def translate_it(self):
        """Translate text from the original language to the selected language."""
        self.translated_text.delete(1.0, tk.END)
        try:
            from_language_key = next(key for key, value in self.languages.items() if value == self.original_combo.get())
            to_language_key = next(key for key, value in self.languages.items() if value == self.translated_combo.get())

            words = self.original_text.get(1.0, tk.END).strip()
            translated_words = self.translator.translate(words, src=from_language_key, dest=to_language_key)
            self.translated_text.insert(1.0, translated_words.text)

        except Exception as e:
            logging.error("Translation error: %s", e)
            messagebox.showerror("Translator", f"Error occurred during translation: {e}")

    def voice_input(self):
        """Capturing voice input and display it in the original_text box."""
        try:
            from_language_key = next(key for key, value in self.languages.items() if value == self.original_combo.get())
            with sr.Microphone() as source:
                self.reco.adjust_for_ambient_noise(source, duration=0.2)
                print("Speak now")
                audio = self.reco.listen(source)
                self.text = self.reco.recognize_google(audio, language=from_language_key)
                self.original_text.insert(1.0, self.text)

        except sr.UnknownValueError:
            logging.error("Speech not recognized")
            messagebox.showerror("Not Recognized", "No speech detected. Please try again.")
        except sr.RequestError as e:
            logging.error("Recognition service request error: %s", e)
            messagebox.showerror("Request Error", f"Error making a request to the recognition service: {e}")

    def voice_output(self):
        """Converting translated text to speech and play it in a separate thread."""
        threading.Thread(target=self._voice_output_thread).start()

    def _voice_output_thread(self):
        try:
            to_language_key = next(key for key, value in self.languages.items() if value == self.translated_combo.get())
            words = self.translated_text.get(1.0, tk.END)
            tts = gTTS(text=words, lang=to_language_key, slow=False)
            temp_file = r"C:\Users\sreej\mini project\captured_voice.mp3"
            tts.save(temp_file)
            playsound(temp_file)
            os.remove(temp_file)
        except Exception as e:
            logging.error("Voice output error: %s", e)
            messagebox.showerror("Voice Output Error", f"Error occurred during voice output: {e}")

    def load_image(self):
        """Load an image, extract text, and display it in the original_text box."""
        try:
            pytesseract.pytesseract.tesseract_cmd = r"C:\Users\sreej\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
            file_path = filedialog.askopenfilename()
            if file_path:
                image = Image.open(file_path)
                text = pytesseract.image_to_string(image, lang='hin')
                self.original_text.delete(1.0, tk.END)
                self.original_text.insert(1.0, text)
                
                image = image.resize((200, 200), Image.LANCZOS)
                image = ImageTk.PhotoImage(image)
                self.image_label.config(image=image)
                self.image_label.image = image

        except FileNotFoundError as fnfe:
            logging.error("File not found: %s", fnfe)
            messagebox.showerror("Error", f"File not found: {fnfe}")
        except PermissionError as pe:
            logging.error("Permission denied: %s", pe)
            messagebox.showerror("Error", f"Permission denied: {pe}")
        except Exception as e:
            logging.error("Error loading image: %s", e)
            messagebox.showerror("Error", f"An error occurred while loading the image: {e}")

    def clear(self):
        """Clearing the content of both text boxes."""
        self.original_text.delete(1.0, tk.END)
        self.translated_text.delete(1.0, tk.END)

if __name__ == "__main__":
    Run()