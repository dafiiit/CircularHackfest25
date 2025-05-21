# CircularHackfest25
Shared Repository for the Hackathon

conda create -n franka-env python=3.10
conda activate franka-env
pip install -r requirements.txt

pip install pyrealsense.py

pip install ultralytics


sudo python3 /usr/local/bin/pwm_daemon.py

Build the daemon:
- sudo nano /usr/local/bin/pwm_daemon.py
Launch the daemon:
- sudo python3 /usr/local/bin/pwm_daemon.py