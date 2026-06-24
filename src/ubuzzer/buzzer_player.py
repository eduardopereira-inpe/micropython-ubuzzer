import uasyncio as asyncio
from machine import Pin, PWM

class BuzzerPlayer:
    """Async PWM buzzer player otimizado para baixo consumo de RAM."""

    def __init__(self, buzzer_pin: int = 14, volume: int = 600) -> None:
        self.buzzer = PWM(Pin(buzzer_pin))
        self.volume = volume
        self.current_task = None
        self.stop()

    def play_tone(self, frequency: int) -> None:
        if frequency == 0:
            self.stop()
        else:
            self.buzzer.freq(frequency)
            self.buzzer.duty_u16(self.volume)

    def stop(self) -> None:
        self.buzzer.duty_u16(0)

    def deinit(self) -> None:
        self.stop()
        self.buzzer.deinit()

    @staticmethod
    def calculate_duration(tempo: int, note_type: int) -> float:
        whole_note = (60000 / tempo) * 4
        if note_type > 0:
            return whole_note // note_type
        else:
            return (whole_note // abs(note_type)) * 1.5

    async def play_async(self, song_bytes: bytes) -> None:
        try:
            # Reconstrói o tempo a partir dos 2 primeiros bytes
            tempo = (song_bytes[0] << 8) | song_bytes[1]

            # Varre o resto dos bytes de 3 em 3 (Frequência: 2 bytes, Duração: 1 byte)
            for i in range(2, len(song_bytes), 3):
                freq = (song_bytes[i] << 8) | song_bytes[i+1]
                note_type = song_bytes[i+2] - 64  # Remove o offset de 64

                note_duration = self.calculate_duration(tempo, note_type)

                self.play_tone(freq)

                # Toca a nota por 90% do tempo
                await asyncio.sleep_ms(int(note_duration * 0.9))

                # Pequena pausa entre notas
                self.stop()
                await asyncio.sleep_ms(int(note_duration * 0.1))

        except asyncio.CancelledError:
            self.stop()
            raise
        except Exception:
            self.stop()
            raise
        finally:
            self.stop()

    def play(self, song_bytes: bytes) -> None:
        self.stop_song()
        self.current_task = asyncio.create_task(self.play_async(song_bytes))

    def stop_song(self) -> None:
        if self.current_task:
            self.current_task.cancel()
            self.current_task = None
        self.stop()

    def is_playing(self) -> bool:
        return self.current_task is not None and not self.current_task.done()