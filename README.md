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
1. What? | 什么 | 你吃什么？ | What do you eat?
2. Why? | 为什么 | 你为什么来？ | Why did you come?
3. What to do? | 怎么办 | 我不知道怎么办 | I don't know what to do
```

## text-es.txt format
- The text file should be in the format of `text | translation`.

### Example
```
1. ¿Qué? | 什么 | 你吃什么？ | ¿Qué comes?
2. ¿Por qué? | 为什么 | 你为什么来？ | ¿Por qué viniste?
3. ¿Qué hacer? | 怎么办 | 我不知道怎么办 | No sé qué hacer
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

## Create a dialog
This project is designed to create a dialog between characters in Mandarin Chinese. It utilizes Python scripts to process input text files and generate audio outputs.

```python
python ttv.py --text_file dialog-sample.txt --language es --repeat once --character-genders "Linna:female,MaDawei:male,SonJuan:male,Xiaoli:female"
```

## Dialog format
- The dialog file should be in the format of `character: text`.

### Example
```
LuYuping: 你们好！ 请进！
LinNa: 您好！你们家真漂亮！
LuYuping: 谢谢。请坐。你们喝什么？我们家有茶和咖啡。
LinNa: 我喝咖啡。
SonJua: 我要茶。
SonJua: 这张照片真漂亮！这是你女儿吗？
LuYuping: 是。这是我女儿。
SonJua: 你女儿今年几岁？
LuYuping: 五岁。今天她有钢琴课，不在家。
LinNa: 中国的孩子真忙！
LuYuping: 是啊。晚上她还有英语课。
```

## Requirements
- Python 3.x
- Any additional libraries or dependencies should be installed as required by the scripts.

## Author
Herles INC

## License
This project is licensed under the MIT License.
