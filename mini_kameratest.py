import cv2

# Kamera öffnen (bei Mac meist index 0)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Kamera konnte nicht geöffnet werden")
    exit()

# Einzelnes Bild aufnehmen
ret, frame = cap.read()

if ret:
    # Bild speichern
    cv2.imwrite("mac_webcam_bild.jpg", frame)
    print("Bild gespeichert als mac_webcam_bild.jpg")
else:
    print("Fehler beim Aufnehmen des Bildes")

cap.release()