from machine import Pin
import time
import neopixel
import usb_hid
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

# =========================
# USB HID (Volume Control)
# =========================
cc = ConsumerControl(usb_hid.devices)

# =========================
# MATRIX SETUP
# =========================
COL_PINS = [0, 1, 2, 3]
ROW_PINS = [4, 6, 7]

cols = [Pin(p, Pin.OUT) for p in COL_PINS]
rows = [Pin(p, Pin.IN, Pin.PULL_DOWN) for p in ROW_PINS]

# =========================
# KEYMAP (frei belegbar!)
# =========================
keymap = [
    ["K1", "K2", "K3", "K4"],
    ["K5", "K6", "K7", "K8"],
    ["K9", "K10", "K11", "K12"],
]

key_state = [[False]*4 for _ in range(3)]

# =========================
# LED SETUP
# =========================
NUM_LEDS = 16
np = neopixel.NeoPixel(Pin(26), NUM_LEDS)

def clear_leds():
    for i in range(NUM_LEDS):
        np[i] = (0, 0, 0)
    np.write()

# Startup Status
np[15] = (0, 50, 0)   # Betriebsbereit LED
np.write()

# =========================
# ENCODER SETUP
# =========================
enc_a = Pin(27, Pin.IN, Pin.PULL_UP)
enc_b = Pin(28, Pin.IN, Pin.PULL_UP)
enc_btn = Pin(29, Pin.IN, Pin.PULL_UP)

last_a = enc_a.value()
btn_last = True

# =========================
# LED EFFECTS
# =========================
led_pos = 0
def running_light():
    global led_pos
    for i in range(12):
        np[i] = (0, 0, 10)
    np[led_pos] = (0, 50, 50)
    led_pos = (led_pos + 1) % 12
    np.write()

# =========================
# MATRIX SCAN
# =========================
def scan_keys():
    for c, col in enumerate(cols):
        col.value(1)
        time.sleep_us(20)

        for r, row in enumerate(rows):
            pressed = row.value()
            if pressed and not key_state[r][c]:
                key_state[r][c] = True
                on_key_press(r, c)

            if not pressed and key_state[r][c]:
                key_state[r][c] = False

        col.value(0)

# =========================
# KEY ACTION
# =========================
def on_key_press(r, c):
    key = keymap[r][c]
    print("Pressed:", key)

    # Beispiel-Aktionen
    if key == "K1":
        np[12] = (50, 0, 0)   # Status LED
    elif key == "K2":
        np[13] = (0, 50, 0)
    elif key == "K3":
        np[14] = (0, 0, 50)
    elif key == "K4":
        clear_leds()

    np.write()

# =========================
# ENCODER HANDLING
# =========================
def handle_encoder():
    global last_a, btn_last

    a = enc_a.value()
    b = enc_b.value()

    if a != last_a:
        if b != a:
            cc.send(ConsumerControlCode.VOLUME_INCREMENT)
        else:
            cc.send(ConsumerControlCode.VOLUME_DECREMENT)
        last_a = a

    btn = enc_btn.value()
    if not btn and btn_last:
        print("Encoder Button Pressed")
        # Extra-Funktion
        for i in range(12):
            np[i] = (50, 0, 50)
        np.write()

    btn_last = btn

# =========================
# MAIN LOOP
# =========================
last_led = time.ticks_ms()

while True:
    scan_keys()
    handle_encoder()

    if time.ticks_diff(time.ticks_ms(), last_led) > 80:
        running_light()
        last_led = time.ticks_ms()

    time.sleep_ms(2)
