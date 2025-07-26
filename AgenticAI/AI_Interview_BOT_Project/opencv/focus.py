import cv2
from PyQt5.QtCore import QThread

class FocusThread(QThread):
    def __init__(self):
        super().__init__()
        self.focused_frames = 0
        self.total_frames = 0

    def run(self):
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        cap = cv2.VideoCapture(0)

        while not self.isInterruptionRequested():
            ret, frame = cap.read()
            if not ret:
                break
            self.total_frames += 1
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

            if len(faces) > 0:
                self.focused_frames += 1
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

            cv2.imshow("Focus Detection", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    def get_focus_score(self):
        if self.total_frames == 0:
            return 0
        return (self.focused_frames / self.total_frames) * 100