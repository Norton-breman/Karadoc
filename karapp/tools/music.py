from mutagen import File
import base64

def get_metadata(filepath):
    try:
        audio_file = File(filepath)
        if audio_file is None:
            return None

        metadata = {
            'title': None,
            'artist': None,
            'album': None,
            'artwork': None
        }

        # Extraction des métadonnées selon le format
        if hasattr(audio_file, 'tags') and audio_file.tags:
            tags = audio_file.tags

            # MP3 (ID3)
            if 'TIT2' in tags:
                metadata['title'] = str(tags['TIT2'][0])
            if 'TPE1' in tags:
                metadata['artist'] = str(tags['TPE1'][0])
            if 'TALB' in tags:
                metadata['album'] = str(tags['TALB'][0])
            if 'APIC:' in tags:
                artwork = tags['APIC:'].data
                metadata['artwork'] = base64.b64encode(artwork).decode('utf-8')

            # MP4/M4A
            elif '\xa9nam' in tags:
                metadata['title'] = str(tags['\xa9nam'][0])
            if '\xa9ART' in tags:
                metadata['artist'] = str(tags['\xa9ART'][0])
            if '\xa9alb' in tags:
                metadata['album'] = str(tags['\xa9alb'][0])
            if 'covr' in tags:
                artwork = tags['covr'][0]
                metadata['artwork'] = base64.b64encode(artwork).decode('utf-8')

        return metadata

    except Exception as e:
        print(f"Erreur lors de l'extraction des métadonnées de {filepath}: {e}")
        return None
