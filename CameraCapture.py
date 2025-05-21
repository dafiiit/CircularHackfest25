# Nimmt ein einziges Bild auf
import cv2

class CameraCapture:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.cap = None

    def open_camera(self):
        """Öffnet die Kamera und gibt True zurück, wenn erfolgreich"""
        self.cap = cv2.VideoCapture(self.camera_index)
        return self.cap.isOpened()

    def capture_image(self):
        """Nimmt ein Bild auf und gibt es zurück"""
        if not self.cap or not self.cap.isOpened():
            if not self.open_camera():
                raise Exception("Kamera konnte nicht geöffnet werden")
        
        ret, frame = self.cap.read()
        if not ret:
            raise Exception("Fehler beim Aufnehmen des Bildes")
        
        return frame

    def save_image(self, frame, filename="mac_webcam_bild.jpg"):
        """Speichert das übergebene Bild"""
        cv2.imwrite(filename, frame)
        print(f"Bild gespeichert als {filename}")

    def close(self):
        """Schließt die Kamera"""
        if self.cap:
            self.cap.release()

    def __del__(self):
        """Destruktor - stellt sicher, dass die Kamera geschlossen wird"""
        self.close()

def main():
    camera = CameraCapture()
    
    try:
        # Bild aufnehmen
        frame = camera.capture_image()
        
        # Bild anzeigen
        cv2.imshow("Aufgenommenes Bild", frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        # Nach Speicherung fragen
        save = input("Möchten Sie das Bild speichern? (j/n): ").lower()
        if save == 'j':
            camera.save_image(frame)
            
    except Exception as e:
        print(f"Fehler: {str(e)}")
    finally:
        camera.close()

if __name__ == "__main__":
    main()