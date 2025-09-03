import asyncio
import edge_tts
from edge_tts import Communicate, list_voices
from gtts import gTTS
import os
import time
from pydub import AudioSegment
import argparse
import re


# Voice configurations
MALE_VOICES = [
    "zh-CN-YunxiNeural", 
    "zh-CN-YunjianNeural",
]

FEMALE_VOICES = [
    "zh-CN-XiaoxiaoNeural",
    "zh-CN-XiaomoNeural",
    "zh-CN-XiaoqiuNeural"
]


async def generar_audio_chino(
    texto, archivo_salida, voz="zh-CN-XiaoxiaoNeural", velocidad="-20%"
):
    """
    Genera audio en chino con velocidad reducida

    Parámetros:
    texto (str): Texto en caracteres chinos
    archivo_salida (str): Nombre del archivo .mp3
    voz (str): Modelo de voz
    velocidad (str): Velocidad reducida (ej: -40%)
    """
    communicate = Communicate(texto, voz, rate=velocidad)
    await communicate.save(archivo_salida)


async def generar_audio_mandarin_con_voz(texto, archivo_salida, voz_especifica):
    """
    Genera audio en chino mandarín utilizando una voz específica

    Parámetros:
    texto (str): Texto en caracteres chinos
    archivo_salida (str): Nombre del archivo .mp3
    voz_especifica (str): Voz específica a utilizar
    """
    communicate = Communicate(texto, voz_especifica, rate="-20%")
    await communicate.save(archivo_salida)


async def generar_audio_mandarin(texto, archivo_salida, voz_genero="mujer", rate="-20%"):
    """
    Genera audio en chino mandarín utilizando edge-tts

    Parámetros:
    texto (str): Texto en caracteres chinos
    archivo_salida (str): Nombre del archivo .mp3
    voz_genero (str): 'hombre' para voz masculina, 'mujer' para voz femenina
    """
    # Seleccionar voz según el género
    if voz_genero == "hombre":
        voz = "zh-CN-YunjianNeural"  # Voz masculina china
    else:
        voz = "zh-CN-XiaoxiaoNeural"  # Voz femenina china (por defecto)

    communicate = Communicate(texto, voz, rate=rate)
    await communicate.save(archivo_salida)


async def generar_audio_idioma(texto, archivo_salida, idioma):
    """
    Genera audio en el idioma especificado usando edge-tts para español o gTTS para inglés

    Parámetros:
    texto (str): Texto en el idioma objetivo
    archivo_salida (str): Nombre del archivo .mp3
    idioma (str): 'en' para inglés, 'es' para español
    """
    if idioma == "es":
        # Usar edge-tts para español con voz más natural
        voz = "es-MX-DaliaNeural"  # Voz femenina mexicana natural
        communicate = Communicate(texto, voz, rate="-30%")
        await communicate.save(archivo_salida)
    else:
        # Usar gTTS para inglés (funciona bien)
        tts = gTTS(text=texto, lang="en", slow=True)
        tts.save(archivo_salida)


def parse_character_genders(character_genders_str):
    """
    Parse character gender assignments from command line string
    
    Parámetros:
    character_genders_str (str): String like "Linna:female,MaDawei:male,SonJuan:male"
    
    Returns:
    dict: Mapping of character names to genders
    """
    gender_map = {}
    if character_genders_str:
        pairs = character_genders_str.split(',')
        for pair in pairs:
            if ':' in pair:
                char_name, gender = pair.split(':', 1)
                gender_map[char_name.strip()] = gender.strip().lower()
    return gender_map


def assign_voices(character_genders):
    """
    Assign specific voices to characters based on their genders
    
    Parámetros:
    character_genders (dict): Mapping of character names to genders
    
    Returns:
    dict: Mapping of character names to specific voice models
    """
    voice_assignments = {}
    male_voice_index = 0
    female_voice_index = 0
    
    for char_name, gender in character_genders.items():
        if gender == 'male':
            if male_voice_index < len(MALE_VOICES):
                voice_assignments[char_name] = MALE_VOICES[male_voice_index]
                male_voice_index += 1
            else:
                # Cycle back to first male voice if we run out
                voice_assignments[char_name] = MALE_VOICES[0]
        else:  # female or any other value defaults to female
            if female_voice_index < len(FEMALE_VOICES):
                voice_assignments[char_name] = FEMALE_VOICES[female_voice_index]
                female_voice_index += 1
            else:
                # Cycle back to first female voice if we run out
                voice_assignments[char_name] = FEMALE_VOICES[0]
    
    return voice_assignments


def parse_arguments():
    parser = argparse.ArgumentParser(description="Convert text to speech with pauses.")
    parser.add_argument(
        "--text_file", type=str, help="Path to the input text file", default="text.txt"
    )
    parser.add_argument(
        "--language",
        type=str,
        choices=["en", "es"],
        default="en",
        help="Language for the second column (en for English, es for Spanish)",
    )
    parser.add_argument(
        "--voice",
        type=str,
        choices=["hombre", "mujer"],
        default="mujer",
        help="Default Chinese voice gender (hombre for male, mujer for female)",
    )
    parser.add_argument(
        "--repeat",
        type=str,
        choices=["once", "twice"],
        default="twice",
        help="Repeat the text once or twice",
    )
    parser.add_argument(
        "--character-genders",
        type=str,
        help="Character gender assignments (e.g., 'Linna:female,MaDawei:male,SonJuan:male')",
        default=""
    )
    parser.add_argument(
        "--voice-rate",
        type=str,
        help="Voice rate",
        default="-10%"
    )
    return parser.parse_args()


async def main():
    # Get the input file and language from command-line arguments
    args = parse_arguments()
    input_file = args.text_file
    target_language = args.language
    voice_gender = args.voice
    repeat = args.repeat
    character_genders_str = args.character_genders
    voice_rate = args.voice_rate

    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' does not exist.")
        exit(1)

    # Parse character gender assignments
    character_genders = parse_character_genders(character_genders_str)
    voice_assignments = assign_voices(character_genders)
    
    # Print voice assignments
    if voice_assignments:
        print("🎭 Asignaciones de voces por personaje:")
        for char_name, voice in voice_assignments.items():
            gender_str = "masculina" if voice in MALE_VOICES else "femenina"
            print(f"   {char_name}: {voice} ({gender_str})")
        print()

    # Read text from the specified file
    with open(input_file, "r", encoding="utf-8") as file:
        lines = file.readlines()

    archivo_mandarin = "output_mandarin.mp3"
    archivo_target = f"output_{target_language}.mp3"
    final_audio = AudioSegment.silent(duration=0)

    print(
        f"🎤 Voz china por defecto: {'masculina' if voice_gender == 'hombre' else 'femenina'}"
    )

    for line in lines:
        line = line.strip()
        if not line:  # Saltar líneas vacías
            continue

        # Verificar si hay separador |
        if "|" in line:
            # Modo con separador: procesar columnas
            parts = line.split("|")
            texto_target = parts[0].strip()  # Inglés/Español (primera columna)
            texto_mandarin = parts[1].strip()  # Palabra china (segunda columna)

            # Check if there's a third column (example in Chinese)
            has_example = len(parts) >= 3 and parts[2].strip()
            texto_ejemplo = parts[2].strip() if has_example else None

            # Check if there's a fourth column (example translation)
            has_translation = len(parts) >= 4 and parts[3].strip()
            texto_traduccion = parts[3].strip() if has_translation else None

            # Generate target language audio (English/Spanish)
            await generar_audio_idioma(texto_target, archivo_target, target_language)

            # Generate Mandarin audio for the word with selected voice gender
            await generar_audio_mandarin(texto_mandarin, archivo_mandarin, voice_gender, voice_rate)

            language_name = "inglés" if target_language == "en" else "español"
            print(
                f"✓ Audio creado ({language_name}): '{texto_target}' → {archivo_target}"
            )
            print(f"✓ Audio creado (mandarín): '{texto_mandarin}' → {archivo_mandarin}")

            # Load the generated audios
            audio_target = AudioSegment.from_mp3(archivo_target)
            audio_mandarin = AudioSegment.from_mp3(archivo_mandarin)

            # Build the audio sequence
            if repeat == "twice":
                sequence = (
                    audio_target
                    + AudioSegment.silent(duration=1500)
                    + audio_mandarin
                    + AudioSegment.silent(duration=1500)
                    + audio_mandarin
                )
            else:
                sequence = (
                    audio_target + AudioSegment.silent(duration=1500) + audio_mandarin
                )

            # Add example if it exists
            if has_example:
                archivo_ejemplo = "output_ejemplo.mp3"
                await generar_audio_mandarin(
                    texto_ejemplo, archivo_ejemplo, voice_gender
                )
                audio_ejemplo = AudioSegment.from_mp3(archivo_ejemplo)
                if repeat == "twice":
                    sequence += (
                        AudioSegment.silent(duration=1500)
                        + audio_ejemplo
                        + AudioSegment.silent(duration=1500)
                        + audio_ejemplo
                    )
                else:
                    sequence += AudioSegment.silent(duration=1500) + audio_ejemplo
                print(
                    f"✓ Audio creado (ejemplo): '{texto_ejemplo}' → {archivo_ejemplo}"
                )

                # Add translation of example if it exists
                if has_translation:
                    archivo_traduccion = f"output_traduccion_{target_language}.mp3"
                    await generar_audio_idioma(
                        texto_traduccion, archivo_traduccion, target_language
                    )
                    audio_traduccion = AudioSegment.from_mp3(archivo_traduccion)
                    if repeat == "twice":
                        sequence += (
                            AudioSegment.silent(duration=1500)
                            + audio_traduccion
                            + AudioSegment.silent(duration=1500)
                            + audio_traduccion
                        )
                    else:
                        sequence += (
                            AudioSegment.silent(duration=1500) + audio_traduccion
                        )
                    print(
                        f"✓ Audio creado (traducción): '{texto_traduccion}' → {archivo_traduccion}"
                    )

            # Add to final audio with longer pause between entries
            final_audio += sequence + AudioSegment.silent(duration=2500)

        else:
            # Modo solo chino: buscar patrón de personaje
            character_match = re.match(r'^([^:]+):\s*(.+)$', line)
            
            if character_match:
                # Diálogo con personaje
                character_name = character_match.group(1).strip()
                texto_mandarin = character_match.group(2).strip()
                
                # Determinar la voz específica para este personaje
                if character_name in voice_assignments:
                    voz_especifica = voice_assignments[character_name]
                    gender_str = "masculina" if voz_especifica in MALE_VOICES else "femenina"
                    print(f"🎭 {character_name} (voz {gender_str}): '{texto_mandarin}'")
                else:
                    # Usar voz por defecto si el personaje no está asignado
                    if voice_gender == "hombre":
                        voz_especifica = MALE_VOICES[0]
                        gender_str = "masculina por defecto"
                    else:
                        voz_especifica = FEMALE_VOICES[0]
                        gender_str = "femenina por defecto"
                    print(f"🎭 {character_name} (voz {gender_str}): '{texto_mandarin}'")
                
                # Generate Mandarin audio with the specific voice
                await generar_audio_chino(texto_mandarin, archivo_mandarin, voz_especifica, voice_rate)
                
            else:
                # Línea sin personaje: usar lógica original (A: B:) o texto directo
                if line.startswith("A:"):
                    texto_mandarin = line[2:].strip()
                    voz_dialogo = "mujer"
                    print(f"🎭 Diálogo A (voz femenina): '{texto_mandarin}'")
                    await generar_audio_mandarin(texto_mandarin, archivo_mandarin, voz_dialogo)
                elif line.startswith("B:"):
                    texto_mandarin = line[2:].strip()
                    voz_dialogo = "hombre"
                    print(f"🎭 Diálogo B (voz masculina): '{texto_mandarin}'")
                    await generar_audio_mandarin(texto_mandarin, archivo_mandarin, voz_dialogo)
                else:
                    # Texto directo sin personaje
                    texto_mandarin = line
                    await generar_audio_mandarin(texto_mandarin, archivo_mandarin, voice_gender)
                    print(f"✓ Audio creado (solo mandarín): '{texto_mandarin}' → {archivo_mandarin}")

            # Load the generated audio
            audio_mandarin = AudioSegment.from_mp3(archivo_mandarin)

            # Add the audio once or twice with pause in between for repetition
            if repeat == "twice":
                sequence = (
                    audio_mandarin + AudioSegment.silent(duration=1500) + audio_mandarin
                )
            else:
                sequence = audio_mandarin

            # Add to final audio with longer pause between entries
            final_audio += sequence + AudioSegment.silent(duration=2500)

    # Save the final audio with pauses
    output_filename = f"final_output_{input_file}_{voice_gender}_{repeat}.mp3"
    final_audio.export(output_filename, format="mp3")
    print(f"✓ Audio final con pausas creado: '{output_filename}'")
    print(f"🎤 Voz por defecto utilizada: {'masculina' if voice_gender == 'hombre' else 'femenina'}")
    print(f"🔁 Repetición: {'una vez' if repeat == 'once' else 'dos veces'}")
    
    if voice_assignments:
        print("\n🎭 Resumen de voces utilizadas:")
        for char_name, voice in voice_assignments.items():
            gender_str = "masculina" if voice in MALE_VOICES else "femenina"
            print(f"   {char_name}: {voice} ({gender_str})")


if __name__ == "__main__":
    asyncio.run(main())