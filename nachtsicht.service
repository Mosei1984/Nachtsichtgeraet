[Unit]
Description=NightCam Touch Nachtsicht-Autostart
After=multi-user.target
StartLimitIntervalSec=60
StartLimitBurst=3

[Service]
Type=simple
User=root
WorkingDirectory=/opt/nachtsicht
ExecStartPre=/bin/sleep 10
ExecStart=/usr/bin/python3 /opt/nachtsicht/nachtsicht_fullscreen.py
Restart=on-failure
RestartSec=15
TimeoutStartSec=30
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
