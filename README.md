#  MicroPython Buzzer Player & Song Converter

An ultra-optimized, asynchronous PWM buzzer player for MicroPython (`uasyncio`), designed to prevent `MemoryError` issues on memory-constrained microcontrollers (like ESP32, ESP8266, or Raspberry Pi Pico).

---

##  Why This Project?

Traditional MicroPython buzzer scripts store songs as massive lists of text strings (e.g., `['NOTE_G4', '4', 'NOTE_D5', '-2']`). In MicroPython, each string and list element carries a heavy memory overhead. When dealing with long melodies, this quickly depletes the RAM, triggering unexpected crashes.

**The Solution:** This project completely eliminates the need for a `notes.py` dictionary on your microcontroller. Instead, songs are drafted as plain text on your computer, compressed into an ultra-compact **`bytes` array**, and deployed to the microcontroller using minimal RAM.

###  Storage Efficiency Comparison

| Format Type | Data Structure | RAM Footprint | Microcontroller Overhead |
| :--- | :--- | :--- | :--- |
| **Traditional** | List of Strings & Objects |  Very High (KBs) | High (Requires `notes.py` dictionary) |
| **Optimized (This)** | Single `bytes` object |  **Low (Bytes)** | **None** (Frequency is embedded) |

---

## 🔄 Workflow


```

[ Composition (Text on PC) ] ──> [ Conversion Script (PC) ] ──> [ Final Code (Bytes on MicroPython) ]

```

---

## 🛠️ Step 1: Draft Your Song (On Your Computer)

Create your melody on your computer using a human-readable list format. Follow this exact structure:

```python
my_new_song = [
    'Song Title',       # [0] Metadata / Title
    120,                # [1] Tempo (BPM)
    'NOTE_C4', '4',     # [2 & 3] Note and Duration
    'NOTE_E4', '4',     # [4 & 5] Note and Duration
    'REST', '2',        # A Pause/Silence
    'NOTE_G4', '-4',    # Dotted Note (Negative Value)
]

```

###  Syntax Rules:

* **Notes:** Use standard musical notation constants (e.g., `NOTE_C4`, `NOTE_DS4` for Dó sharp).
* **Pauses:** Use the exact string `'REST'` for silences.
* **Regular Durations:** `4` (Quarter note), `8` (Eighth note), `16` (Sixteenth note), etc.
* **Dotted Durations:** Negative numbers represent dotted notes, which increase the duration by 50% (e.g., `-4` is a dotted quarter note).

---

##  Step 2: Convert to Bytes (On Your Computer)

Run this Python script **on your PC** to compress your song array into a tight sequence of raw bytes.

Use expost_song_to_bytes from melodies in scripts folder.
```python
from melodies import export_song_to_bytes

# --- INSERT YOUR SONG LIST BELOW TO CONVERT ---
sample_song = ['Quick Demo', 140, 'NOTE_C4', '4', 'NOTE_E4', '4', 'REST', '2']

resulting_bytes = export_song_to_bytes(sample_song)
print(f"\n Copy the line below into your MicroPython code:\n")
print(f"MY_SONG_BYTES = {resulting_bytes}")

```

Running this on your computer will output a line like this:

```python
MY_SONG_BYTES = b'\x00\x8c\x01\x06D\x01JD\x00\x00B'

```

---

##  Step 3: Play on MicroPython

Copy the outputted byte literal (`b'...'`) and paste it directly into your MicroPython implementation.

### Implementation Example (`main.py`)

```python
import uasyncio as asyncio
from ubuzzer import BuzzerPlayer

star_trek_intro = b'\x00P\x01&8\x01\x88P\x02\x0b<\x01\xeeH\x01\x880\x01J0\x01\xb80\x02KB'


async def main():
    # Initialize player on Pin 14
    player = BuzzerPlayer(buzzer_pin=5, volume=600)
    
    print("Playing melody in the background...")
    player.play(star_trek_intro)
    
    # Keep running other tasks alongside the audio playback
    while player.is_playing():
        await asyncio.sleep(1)
        
    print("Song finished!")

asyncio.run(main())

```

---

##  How It Works (Technical Breakdown)

Instead of instantiating Python objects dynamically, the song data is processed byte-by-byte linearly:

1. **Header (Bytes 0-1):** A 16-bit integer storing the song's Tempo (BPM).
2. **Note Packet (3-byte window):**
* **Byte 1 & 2:** High and low parts of a 16-bit integer representing the frequency ($0$ to $65535\text{ Hz}$). A `0` means a `REST` (silence).
* **Byte 3:** An 8-bit unsigned integer encoding the note type/duration. An offset of $+64$ is added to eliminate native signed integer parsing overhead inside the playback stream.



