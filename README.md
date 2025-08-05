# Chino Mandarin Project

## Text to Voice
This project is designed to convert text to voice in Mandarin Chinese. It utilizes Python scripts to process input text files and generate audio outputs.

## Files
- `text_to_voice.py`: Main script for converting text to voice.
- `text.txt`: Contains the text input for conversion.
- `text-es.txt`: Contains the text input for conversion in Spanish.

## text.txt format
- The text file should be in the format of `text | translation`.

### Example
```
什么 | What?
为什么 | Why?
怎么办 | What to do?
```

## text-es.txt format
- The text file should be in the format of `text | translation`.

### Example
```
什么 | ¿Qué?
为什么 | ¿Por qué?
怎么办 | ¿Qué hacer?
```

## Usage
1. Place your text input in `text.txt` or `text-es.txt`.
2. Run `text_to_voice.py` to generate the voice output.

```python
python text_to_voice.py --text_file text-es.txt --language es
```

Or

```python
python text_to_voice.py --text_file text.txt --language en
```

## Output
- `final_output_{input_file}.mp3`: Final audio file with pauses between Mandarin and target language.

## Flashcards
This project is designed to create flashcards for Mandarin Chinese. It utilizes Python scripts to process input text files and generate audio outputs.

## Files
- `flashcards.py`: Main script to create flashcards.
- `dictionary.csv`: Contains the dictionary entries.

## Usage
1. Place your dictionary entries in `dictionary.csv`.
2. Run `flashcards.py` to create the flashcards.

```python
streamlit run flashcards.py
```

## Requirements
- Python 3.x
- Any additional libraries or dependencies should be installed as required by the scripts.

## Author
Herles INC

## License
This project is licensed under the MIT License.
