# CircularHackfest25
Shared Repository for the Hackathon

Das klingt nach einem spannenden und komplexen Projekt! Damit ihr strukturiert arbeiten könnt und euch nicht im Chaos verliert, hier ein Vorschlag, wie ihr das Projekt aufsetzt und sinnvoll aufteilt.

⸻

🔧 Gesamtkonzept: Systemarchitektur

Hardware-Komponenten:
	•	Raspberry Pi 5 (zentrale Steuereinheit, evtl. auch ROS2 Master/Agent)
	•	FR3 Roboterarm (über ROS2 integriert)
	•	2 Tiefenkameras (z. B. Arducam und )
	•	2 Loadcells (vermutlich über HX711 oder ein I²C-Modul angebunden)
	•	Endeffektor (mit einfachem digitalen Signal AN/AUS steuerbar)

Kommunikation:
	•	Ethernet-Switch verbindet alles (ggf. mit PoE)
	•	ROS2 über DDS (z. B. FastDDS oder CycloneDDS)

⸻

📁 Softwarestruktur

project_root/
├── ros2_ws/                  # ROS2 Workspace
│   ├── src/
│   │   ├── fr3_control/      # ROS2-Paket für FR3
│   │   ├── vision_module/    # ROS2-Paket für Kameradaten
│   │   ├── loadcell_module/  # ROS2-Paket für Loadcell-Integration
│   │   ├── endeffector_control/ # ROS2-Paket für Greifersteuerung
│   │   └── main_orchestrator/   # ROS2-Knoten zur Steuerung des Ablaufs
├── config/                   # YAML-Konfigs für ROS2 Nodes
├── scripts/                  # Helferskripte (Logging, Debugging etc.)
├── docker/                   # Optional: Dev-Container
└── README.md


⸻

👨‍💻 Teamaufteilung (4 Personen)

🧠 1. Orchestrator & State Machine (Koordination aller Module)
	•	Verantwortlich für:
	•	zentrale Steuerlogik
	•	ROS2 Node, der alle anderen Nodes anspricht
	•	State Machines (z. B. über smach oder py_trees)
	•	Logging und Monitoring
	•	Gute Kenntnisse in ROS2-Kommunikation nötig

🤖 2. FR3 Roboterarm & ROS2 Control
	•	Verantwortlich für:
	•	Einrichtung von franka_ros2
	•	Trajektorienplanung (z. B. mit MoveIt 2)
	•	Sicherheitsgrenzen
	•	Nutzung von ROS2 Actions und Services

🎥 3. Vision-System
	•	Verantwortlich für:
	•	Einbindung der Kameras (z. B. via realsense-ros2 oder zed_ros2)
	•	Verarbeitung der Tiefenbilder
	•	Objekterkennung, ggf. mit OpenCV oder ML-Modellen
	•	Output: Positionsdaten, Trigger für Aktionen

⚖️ 4. Loadcells & Endeffektor
	•	Verantwortlich für:
	•	Einbindung der Loadcells (mit geeigneter Bibliothek)
	•	Kalibrierung & Rauschfilterung
	•	Trigger-Logik für den Endeffektor (GPIO/PWM)
	•	ROS2 Service oder Topic zum Ein/Aus-Schalten

⸻

🛠️ Startempfehlungen

1. Setup vorbereiten
	•	Gemeinsames GitHub-Repo aufsetzen
	•	CI/CD einrichten (z. B. mit GitHub Actions für ROS2-Builds)
	•	ROS2 Humble auf dem Raspi5 installieren
	•	SSH-Zugriff und Remote Debugging einrichten

2. Testweise einzelne Module entwickeln
	•	Zuerst “Hello World” Nodes für jeden Hardware-Part
	•	Prüfen: Kommunikation, Datenrate, Latenz

3. ROS2 Struktur festlegen
	•	Klare Messages und Services definieren (evtl. custom)
	•	Gemeinsames Interface-Definition-Paket

4. Entwicklung iterativ durchführen
	•	Zunächst nur simulierte Daten verwenden
	•	Danach reale Hardware testen