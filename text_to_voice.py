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

async def generar_audio_mandarin(texto, archivo_salida):
    """
    Genera audio en chino mandarín utilizando edge-tts
    
    Parámetros:
    texto (str): Texto en caracteres chinos
    archivo_salida (str): Nombre del archivo .mp3
    """
    voz = "zh-CN-XiaoxiaoNeural"
    communicate = Communicate(texto, voz, rate="-40%")
    await communicate.save(archivo_salida)

async def generar_audio_idioma(texto, archivo_salida, idioma):
    """
    Genera audio en el idioma especificado usando edge-tts para español o gTTS para inglés
    
    Parámetros:
    texto (str): Texto en el idioma objetivo
    archivo_salida (str): Nombre del archivo .mp3
    idioma (str): 'en' para inglés, 'es' para español
    """
    if idioma == 'es':
        # Usar edge-tts para español con voz más natural
        voz = "es-MX-DaliaNeural"  # Voz femenina mexicana natural
        communicate = Communicate(texto, voz, rate="-30%")
        await communicate.save(archivo_salida)
    else:
        # Usar gTTS para inglés (funciona bien)
        tts = gTTS(text=texto, lang='en', slow=True)
        tts.save(archivo_salida)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Convert text to speech with pauses.')
    parser.add_argument('--text_file', type=str, help='Path to the input text file', default='text.txt')
    parser.add_argument('--language', type=str, choices=['en', 'es'], default='en', 
                       help='Language for the second column (en for English, es for Spanish)')
    return parser.parse_args()

async def main():
    # Get the input file and language from command-line arguments
    args = parse_arguments()
    input_file = args.text_file
    target_language = args.language
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' does not exist.")
        exit(1)

    # Read text from the specified file
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    archivo_mandarin = "output_mandarin.mp3"
    archivo_target = f"output_{target_language}.mp3"
    final_audio = AudioSegment.silent(duration=0)
    
    for line in lines:
        parts = line.strip().split("|")
        if len(parts) == 2:
            texto_mandarin = parts[0].strip()
            texto_target = parts[1].strip()
            
            # Generate Mandarin audio
            await generar_audio_mandarin(texto_mandarin, archivo_mandarin)
            
            # Generate target language audio
            await generar_audio_idioma(texto_target, archivo_target, target_language)
            
            language_name = "inglés" if target_language == "en" else "español"
            print(f"✔ Audio creado (mandarín): '{texto_mandarin}' → {archivo_mandarin}")
            print(f"✔ Audio creado ({language_name}): '{texto_target}' → {archivo_target}")
            
            # Load the generated audios
            audio_mandarin = AudioSegment.from_mp3(archivo_mandarin)
            audio_target = AudioSegment.from_mp3(archivo_target)
            
            # Append to the final audio with a 1.5-second pause between target language and Mandarin
            final_audio += audio_target + AudioSegment.silent(duration=1500) + audio_mandarin + AudioSegment.silent(duration=1500) + audio_mandarin + AudioSegment.silent(duration=2000)

    # Save the final audio with pauses
    final_audio.export(f"final_output_{input_file}.mp3", format="mp3")
    print(f"✔ Audio final con pausas creado: 'final_output_{input_file}.mp3'")

if __name__ == "__main__":
    asyncio.run(main())