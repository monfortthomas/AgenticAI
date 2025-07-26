import os
import time
import random
import speech_recognition as sr
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout
from PyQt5.QtGui import QPixmap, QMovie, QFont
from PyQt5.QtCore import Qt

from tts.tts import TTSThread
from opencv.focus import FocusThread
from langchain_utils.langchain_utils import (
    setup_langchain_qa,
    generate_question,
    evaluate_answer,
    generate_summary,
    suggest_topics
)
from logger.logger import log_transcripts, log_feedback, log_summary

recognizer = sr.Recognizer()

class InterviewBot(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎤 AI Interviewer Bot")
        self.focus_thread = None
        self.tts_thread = None
        self.movie = None
        self.transcripts = []
        self.feedback_log = []
        self.interview_started = False
        self.qa_chain = setup_langchain_qa("docs/react_guide.txt")
        self.topics = suggest_topics(self.qa_chain)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        avatar_label = QLabel()
        avatar_path = os.path.join(os.path.dirname(__file__), "assets", "avatar.png")
        avatar_img = QPixmap(avatar_path)

        if avatar_img.isNull():
            avatar_label.setText("🤖 Interview Bot")
            avatar_label.setFont(QFont("Arial", 16))
            avatar_label.setAlignment(Qt.AlignCenter)
        else:
            avatar_label.setPixmap(avatar_img.scaledToWidth(250))
            avatar_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(avatar_label)

        gif_path = os.path.join(os.path.dirname(__file__), "assets", "speaking.gif")
        self.movie = QMovie(gif_path)
        self.gif_label = QLabel()
        self.gif_label.setMovie(self.movie)
        self.gif_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.gif_label)

        title = QLabel("Welcome to your AI Interview Session")
        title.setFont(QFont("Arial", 14))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        button = QPushButton("Start Interview")
        button.clicked.connect(self.listen_and_respond)
        layout.addWidget(button)

        self.setLayout(layout)

    def speak(self, text):
        print(f"🔊 Speaking: {text}")
        self.tts_thread = TTSThread(text, self.movie)
        self.tts_thread.start()
        self.tts_thread.wait()

    def listen_and_respond(self):
        if self.interview_started:
            self.speak("The interview has already been completed.")
            return
        self.interview_started = True
        self.start_focus_check()
        self.transcripts = []
        self.feedback_log = []
        

        for i in range(4):
            topic = random.choice(self.topics)
            question = generate_question(topic, self.qa_chain)
            self.speak(question)
            time.sleep(1)

            with sr.Microphone() as source:
                print(f" Listening for answer {i+1}...")
                try:
                    audio = recognizer.listen(source, timeout=10)
                    transcript = recognizer.recognize_google(audio)
                    print(f" Answer {i+1}: {transcript}")
                    self.transcripts.append((question, transcript))
                    self.speak("Thank you for your response.")
                    feedback = evaluate_answer(question, transcript, self.qa_chain)
                    self.feedback_log.append({
                        "question": question,
                        "answer": transcript,
                        "evaluation": feedback
                    })
                except sr.WaitTimeoutError:
                    self.speak("I didn't hear anything. Let's move to the next question.")
                except sr.UnknownValueError:
                    self.speak("Sorry, I couldn't understand that.")
                except sr.RequestError:
                    self.speak("There was a problem with the speech service.")

        self.speak("Thank you. I will now evaluate your focus during the interview.")
        valid_focus = self.stop_focus_check_and_evaluate()

        if not valid_focus:
            return  # Terminate interview early


        if self.transcripts and self.feedback_log:
            log_transcripts(self.transcripts)
            log_feedback(self.feedback_log)
            summary = generate_summary(self.feedback_log, self.qa_chain)
            log_summary(summary)

    def start_focus_check(self):
        self.focus_thread = FocusThread()
        self.focus_thread.start()

    def stop_focus_check_and_evaluate(self):
        if self.focus_thread:
            self.focus_thread.requestInterruption()
            self.focus_thread.quit()
            self.focus_thread.wait()
            score = self.focus_thread.get_focus_score()
            return self.handle_focus_result(score)

    def handle_focus_result(self, score):
        print(f"Focus Score: {score:.2f}%")
        if score > 80:
            self.speak("Great! You were fully engaged during the interview.")
            return True
        elif score > 50:
            self.speak("You seemed partially focused. The interview will still be evaluated.")
            return True
        else:
            self.speak("It looks like you were not focused during the interview. This session will not be considered valid.")
            self.transcripts = []
            self.feedback_log = []
            return False

    def closeEvent(self, event):
        if self.focus_thread and self.focus_thread.isRunning():
            self.focus_thread.requestInterruption()
            self.focus_thread.quit()
            self.focus_thread.wait()
        event.accept()