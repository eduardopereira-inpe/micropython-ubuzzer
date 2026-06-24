from .exporter import export_song_to_bytes

def get_melody_catalog():
	from .melodies import MELODY_CATALOG

	return MELODY_CATALOG


__all__ = ["get_melody_catalog", "export_song_to_bytes"]

