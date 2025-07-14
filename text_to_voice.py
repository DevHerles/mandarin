import asyncio
import edge_tts
from edge_tts import Communicate, list_voices
from gtts import gTTS
import os
import time
from pydub import AudioSegment
import argparse

async def generar_audio_chino(texto, archivo_salida, voz="zh-CN-XiaoxiaoNeural", velocidad="-40%"):
    """
    Genera audio en chino con velocidad reducida
    
    Parámetros:
    texto (str): Texto en caracteres chinos
    archivo_salida (str): Nombre del archivo .mp3
    voz (str): Modelo de voz
    velocidad (str): Velocidad reducida (ej: -40%)
    """
    # Configurar voz con velocidad reducida
    voz_ajustada = voz
    
    communicate = Communicate(texto, voz_ajustada)
    await communicate.save(archivo_salida)

def generar_audio_mandarin(texto, archivo_salida):
    """
    Genera audio en chino mandarín utilizando gTTS
    
    Parámetros:
    texto (str): Texto en caracteres chinos
    archivo_salida (str): Nombre del archivo .mp3
    """
    language = 'zh'
    tts = gTTS(text=texto, lang=language, slow=True)
    tts.save(archivo_salida)
    # os.system("mpg321 " + archivo_salida)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Convert text to speech with pauses.')
    parser.add_argument('--text_file', type=str, help='Path to the input text file', default='text.txt')
    return parser.parse_args()

if __name__ == "__main__":
    # Get the input file from command-line arguments
    args = parse_arguments()
    input_file = args.text_file
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' does not exist.")
        exit(1)

    # Read text from the specified file
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    archivo_mandarin = "output_mandarin.mp3"
    archivo_english = "output_english.mp3"
    final_audio = AudioSegment.silent(duration=0)
    for line in lines:
        parts = line.strip().split("/")
        if len(parts) == 2:
            texto_mandarin = parts[0].strip()
            texto_english = parts[1].strip()
            # Generate Mandarin audio
            generar_audio_mandarin(texto_mandarin, archivo_mandarin)
            # Generate English audio
            tts_english = gTTS(text=texto_english, lang='en', slow=True)
            tts_english.save(archivo_english)
            print(f"✔ Audio creado (mandarín): '{texto_mandarin}' → {archivo_mandarin}")
            print(f"✔ Audio creado (inglés): '{texto_english}' → {archivo_english}")
            # Load the generated audios
            audio_mandarin = AudioSegment.from_mp3(archivo_mandarin)
            audio_english = AudioSegment.from_mp3(archivo_english)
            # Append to the final audio with a 1.5-second pause between Mandarin and English
            final_audio += audio_english + AudioSegment.silent(duration=1500) + audio_mandarin + AudioSegment.silent(duration=1500) + audio_mandarin + AudioSegment.silent(duration=2000)

    # Save the final audio with pauses
    final_audio.export(f"final_output_{input_file}.mp3", format="mp3")
    print(f"✔ Audio final con pausas creado: 'final_output_{input_file}.mp3'")
