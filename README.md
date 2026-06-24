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

```python
# conversor.py (RUN THIS ON YOUR COMPUTER)

NOTES_DICT = {
    "NOTE_B0": 31, "NOTE_C1": 33, "NOTE_CS1": 35, "NOTE_D1": 37, "NOTE_DS1": 39, "NOTE_E1": 41, 
    "NOTE_F1": 44, "NOTE_FS1": 46, "NOTE_G1": 49, "NOTE_GS1": 52, "NOTE_A1": 55, "NOTE_AS1": 58, 
    "NOTE_B1": 62, "NOTE_C2": 65, "NOTE_CS2": 69, "NOTE_D2": 73, "NOTE_DS2": 78, "NOTE_E2": 82, 
    "NOTE_F2": 87, "NOTE_FS2": 93, "NOTE_G2": 98, "NOTE_GS2": 104, "NOTE_A2": 110, "NOTE_AS2": 117, 
    "NOTE_B2": 123, "NOTE_C3": 131, "NOTE_CS3": 139, "NOTE_D3": 147, "NOTE_DS3": 156, "NOTE_E3": 165, 
    "NOTE_F3": 175, "NOTE_FS3": 185, "NOTE_G3": 196, "NOTE_GS3": 208, "NOTE_A3": 220, "NOTE_AS3": 233, 
    "NOTE_B3": 247, "NOTE_C4": 262, "NOTE_CS4": 277, "NOTE_D4": 294, "NOTE_DS4": 311, "NOTE_E4": 330, 
    "NOTE_F4": 349, "NOTE_FS4": 370, "NOTE_G4": 392, "NOTE_GS4": 415, "NOTE_A4": 440, "NOTE_AS4": 466, 
    "NOTE_B4": 494, "NOTE_C5": 523, "NOTE_CS5": 554, "NOTE_D5": 587, "NOTE_DS5": 622, "NOTE_E5": 659, 
    "NOTE_F5": 698, "NOTE_FS5": 740, "NOTE_G5": 784, "NOTE_GS5": 831, "NOTE_A5": 880, "NOTE_AS5": 932, 
    "NOTE_B5": 988, "NOTE_C6": 1047, "NOTE_CS6": 1109, "NOTE_D6": 1175, "NOTE_DS6": 1245, "NOTE_E6": 1319, 
    "NOTE_F6": 1397, "NOTE_FS6": 1480, "NOTE_G6": 1568, "NOTE_GS6": 1661, "NOTE_A6": 1760, "NOTE_AS6": 1865, 
    "NOTE_B6": 1976, "NOTE_C7": 2093, "NOTE_CS7": 2217, "NOTE_D7": 2349, "NOTE_DS7": 2489, "NOTE_E7": 2637, 
    "NOTE_F7": 2794, "NOTE_FS7": 2960, "NOTE_G7": 3136, "NOTE_GS7": 3322, "NOTE_A7": 3520, "NOTE_AS7": 3729, 
    "NOTE_B7": 3951, "NOTE_C8": 4186, "NOTE_CS8": 4435, "NOTE_D8": 4699, "NOTE_DS8": 4978
}

def export_song_to_bytes(song_list):
    output = bytearray()
    tempo = int(song_list[1])
    
    # 1. Encode Tempo into the first 2 Bytes
    output.append((tempo >> 8) & 0xFF)
    output.append(tempo & 0xFF)
    
    # 2. Encode notes sequentially (2 bytes frequency + 1 byte duration)
    for i in range(2, len(song_list), 2):
        note_name = song_list[i]
        duration = int(song_list[i+1])
        
        freq = 0 if note_name == "REST" else NOTES_DICT[note_name]
        
        output.append((freq >> 8) & 0xFF)
        output.append(freq & 0xFF)
        output.append(duration + 64) # Offset of 64 to safely handle negative values
        
    return bytes(output)

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



