# ESP32-CAM integration

This is a separate board. MicroPython camera APIs vary by exact board, PSRAM, and firmware build. Implement `camera_adapter.py` for the selected build, capture only after a request, and upload JPEG bytes to `/api/detections/image?device_id=...` with `X-Device-Token`. Protect ESP32 GPIOs from any 5 V ultrasonic echo signal.
