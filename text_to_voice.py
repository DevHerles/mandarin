import asyncio
import edge_tts
from edge_tts import Communicate, list_voices
from gtts import gTTS
import os
import time
from pydub import AudioSegment
import argparse


async def generar_audio_chino(
    texto, archivo_salida, voz="zh-CN-XiaoxiaoNeural", velocidad="-40%"
):
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


async def generar_audio_mandarin(texto, archivo_salida, voz_genero="mujer"):
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
    if idioma == "es":
        # Usar edge-tts para español con voz más natural
        voz = "es-MX-DaliaNeural"  # Voz femenina mexicana natural
        communicate = Communicate(texto, voz, rate="-30%")
        await communicate.save(archivo_salida)
    else:
        # Usar gTTS para inglés (funciona bien)
        tts = gTTS(text=texto, lang="en", slow=True)
        tts.save(archivo_salida)


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
        help="Chinese voice gender (hombre for male, mujer for female)",
    )
    parser.add_argument(
        "--repeat",
        type=str,
        choices=["once", "twice"],
        default="twice",
        help="Repeat the text once or twice",
    )
    return parser.parse_args()


async def main():
    # Get the input file and language from command-line arguments
    args = parse_arguments()
    input_file = args.text_file
    target_language = args.language
    voice_gender = args.voice
    repeat = args.repeat

    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' does not exist.")
        exit(1)

    # Read text from the specified file
    with open(input_file, "r", encoding="utf-8") as file:
        lines = file.readlines()

    archivo_mandarin = "output_mandarin.mp3"
    archivo_target = f"output_{target_language}.mp3"
    final_audio = AudioSegment.silent(duration=0)

    print(
        f"🎤 Usando voz china: {'masculina' if voice_gender == 'hombre' else 'femenina'}"
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
            await generar_audio_mandarin(texto_mandarin, archivo_mandarin, voice_gender)

            language_name = "inglés" if target_language == "en" else "español"
            print(
                f"✔ Audio creado ({language_name}): '{texto_target}' → {archivo_target}"
            )
            print(f"✔ Audio creado (mandarín): '{texto_mandarin}' → {archivo_mandarin}")

            # Load the generated audios
            audio_target = AudioSegment.from_mp3(archivo_target)
            audio_mandarin = AudioSegment.from_mp3(archivo_mandarin)

            # Build the audio sequence: Target language (once) → Mandarin word (twice) → Example (if exists) → Translation (if exists)
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
                    f"✔ Audio creado (ejemplo): '{texto_ejemplo}' → {archivo_ejemplo}"
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
                        f"✔ Audio creado (traducción): '{texto_traduccion}' → {archivo_traduccion}"
                    )

            # Add to final audio with longer pause between entries
            final_audio += sequence + AudioSegment.silent(duration=2500)

        else:
            # Modo solo chino: toda la línea es texto chino
            texto_mandarin = line
            voz_dialogo = voice_gender  # Por defecto usar la voz seleccionada

            # Verificar si es diálogo (A: o B:)
            if line.startswith("A:"):
                texto_mandarin = line[2:].strip()  # Remover "A:" y espacios
                voz_dialogo = "mujer"  # A: usa voz femenina
                print(f"🎭 Diálogo A (voz femenina): '{texto_mandarin}'")
            elif line.startswith("B:"):
                texto_mandarin = line[2:].strip()  # Remover "B:" y espacios
                voz_dialogo = "hombre"  # B: usa voz masculina
                print(f"🎭 Diálogo B (voz masculina): '{texto_mandarin}'")

            # Generate Mandarin audio for the text with appropriate voice
            await generar_audio_mandarin(texto_mandarin, archivo_mandarin, voz_dialogo)
            print(
                f"✔ Audio creado (solo mandarín): '{texto_mandarin}' → {archivo_mandarin}"
            )

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
    final_audio.export(
        f"final_output_{input_file}_{voice_gender}_{repeat}.mp3", format="mp3"
    )
    print(
        f"✔ Audio final con pausas creado: 'final_output_{input_file}_{voice_gender}_{repeat}.mp3'"
    )
    print(
        f"🎤 Voz utilizada: {'masculina' if voice_gender == 'hombre' else 'femenina'}"
    )
    print(f"🔁 Repetición: {'una vez' if repeat == 'once' else 'dos veces'}")


if __name__ == "__main__":
    asyncio.run(main())
