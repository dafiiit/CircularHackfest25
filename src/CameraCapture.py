# Nimmt ein einziges Bild auf
import cv2
import os
import matplotlib.pyplot as plt

class CameraCapture:
    def __init__(self, camera_index=0, test_mode=False, test_image="test_image_screw.jpg"):
        self.camera_index = camera_index
        self.cap = None
        self.test_mode = test_mode
        self.test_images_dir = "test_images"
        self.test_image = test_image

    def _load_test_images(self):
        """Load the specific test image"""
        if not os.path.exists(self.test_images_dir):
            raise Exception(f"Test images directory {self.test_images_dir} does not exist")
        
        test_image_path = os.path.join(self.test_images_dir, self.test_image)
        if not os.path.exists(test_image_path):
            raise Exception(f"Test image {test_image_path} does not exist")

    def open_camera(self):
        """Öffnet die Kamera und gibt True zurück, wenn erfolgreich"""
        if self.test_mode:
            self._load_test_images()
            return True
            
        self.cap = cv2.VideoCapture(self.camera_index)
        return self.cap.isOpened()

    def capture_image(self):
        """Nimmt ein Bild auf und gibt es zurück"""
        if self.test_mode:
            test_image_path = os.path.join(self.test_images_dir, self.test_image)
            frame = cv2.imread(test_image_path)
            if frame is None:
                raise Exception(f"Fehler beim Laden des Testbildes: {test_image_path}")
            return frame
            
        if not self.cap or not self.cap.isOpened():
            if not self.open_camera():
                raise Exception("Kamera konnte nicht geöffnet werden")
        
        ret, frame = self.cap.read()
        if not ret:
            raise Exception("Fehler beim Aufnehmen des Bildes")
        
        return frame

    def save_image(self, frame, filename="./test_images/image03.jpg"):
        """Speichert das übergebene Bild"""
        cv2.imwrite(filename, frame)
        #plt.imsave(filename, frame)
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
        
         
        camera.save_image(frame)
        # Bild anzeigen
        #cv2.imshow("Aufgenommenes Bild", frame)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()
        
            
    except Exception as e:
        print(f"Fehler: {str(e)}")
    finally:
        camera.close()

if __name__ == "__main__":
    main()