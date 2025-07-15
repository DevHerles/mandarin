import streamlit as st
import re
import time

# Diccionario de caracteres comunes con su pinyin
PINYIN_DICT = {
    '老': 'lǎo', '师': 'shī', '你': 'nǐ', '可': 'kě', '以': 'yǐ', '再': 'zài', 
    '说': 'shuō', '一': 'yī', '遍': 'biàn', '吗': 'ma', '用': 'yòng', 
    '汉': 'hàn', '语': 'yǔ', '怎': 'zěn', '么': 'me', '我': 'wǒ', 
    '有': 'yǒu', '个': 'ge', '问': 'wèn', '题': 'tí', '请': 'qǐng', 
    '这': 'zhè', '不': 'bù', '明': 'míng', '白': 'bái', '是': 'shì', 
    '什': 'shén', '意': 'yì', '思': 'sī', '进': 'jìn', '来': 'lái',
    '我': 'wǒ', '你': 'nǐ', '他': 'tā', '她': 'tā', '它': 'tā', "们": "men",
}

def get_pinyin(char):
    """Obtener el pinyin de un carácter"""
    return PINYIN_DICT.get(char, '?')

# Configuración de la página
st.set_page_config(
    page_title="练习汉字笔顺",
    page_icon="📝",
    layout="centered"
)

# Frases del aula
phrases = [
    {
        "chinese": "老师，你可以再说一遍吗？",
        "pinyin": "lǎoshī, nǐ kěyǐ zài shuō yí biàn ma?",
        "spanish": "Profesor/a, ¿puedes repetirlo otra vez?"
    },
    {
        "chinese": "老师，用汉语怎么说？",
        "pinyin": "lǎoshī, yòng hànyǔ zěnme shuō?",
        "spanish": "Profesor/a, ¿cómo se dice en chino?"
    },
    {
        "chinese": "老师，我有一个问题。",
        "pinyin": "lǎoshī, wǒ yǒu yí ge wèntí.",
        "spanish": "Profesor/a, tengo una pregunta."
    },
    {
        "chinese": "请问，这个我不明白。",
        "pinyin": "qǐngwèn, zhè ge wǒ bù míngbai.",
        "spanish": "Disculpe, esto no lo entiendo."
    },
    {
        "chinese": "请问，这是什么意思？",
        "pinyin": "qǐngwèn, zhè shì shénme yìsi?",
        "spanish": "Disculpe, ¿qué significa esto?"
    },
    {
        "chinese": "老师，我可以进来吗？",
        "pinyin": "lǎoshī, wǒ kěyǐ jìnlái ma?",
        "spanish": "Profesor/a, ¿puedo entrar?"
    },
    {
        "chinese": "我, 你, 您, 他, 她, 它, 们",
        "pinyin": "wǒ, nǐ, nín, tā, tā, tā, men",
        "spanish": "yo, tú/usted (informal), usted (formal), él, ella, eso (objeto/animal), nosotros/as, vosotros/ustedes (plural), ellos (mixto), ellas (femenino), ellos (objetos)"
    }
]

def get_chinese_chars(text):
    """Extraer solo caracteres chinos del texto"""
    return re.findall(r'[\u4e00-\u9fff]', text)

def main():
    # CSS para fuente KaiTi
    st.markdown("""
    <style>
        .chinese-text {
            font-family: KaiTi, STKaiti, "KaiTi SC", "KaiTi TC", serif;
        }
        .main-title {
            font-family: KaiTi, STKaiti, "KaiTi SC", "KaiTi TC", serif;
            font-size: 2.5em;
            text-align: center;
            color: #2c3e50;
        }
        .phrase-display {
            font-family: KaiTi, STKaiti, "KaiTi SC", "KaiTi TC", serif;
        }
        .current-char {
            font-family: KaiTi, STKaiti, "KaiTi SC", "KaiTi TC", serif;
            font-size: 16em;
            text-align: center;
            background:rgb(0, 0, 0);
            padding: 10px;
            border-radius: 10px;
            border: 3px solid #007bff;
            margin: 20px 0;
        }
        .char-button {
            font-family: KaiTi, STKaiti, "KaiTi SC", "KaiTi TC", serif;
            font-size: 1.2em;
        }
        .progress-container {
            background: #f0f2f6;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            border: 2px solid #e0e0e0;
        }
        .progress-label {
            font-size: 1.1em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1 class="main-title">练习汉字笔顺</h1>', unsafe_allow_html=True)
    
    # Inicializar estado
    if 'selected_phrase' not in st.session_state:
        st.session_state.selected_phrase = 0
    if 'current_char_index' not in st.session_state:
        st.session_state.current_char_index = 0
    if 'auto_play' not in st.session_state:
        st.session_state.auto_play = False
    
    # Selección de frase
    phrase_options = [f"{p['chinese']} - {p['spanish']}" for p in phrases]
    selected_idx = st.selectbox(
        "Selecciona una frase:",
        range(len(phrases)),
        format_func=lambda x: phrase_options[x],
        key="phrase_selector"
    )
    
    if selected_idx != st.session_state.selected_phrase:
        st.session_state.selected_phrase = selected_idx
        st.session_state.current_char_index = 0
        st.session_state.auto_play = False
    
    current_phrase = phrases[st.session_state.selected_phrase]
    chinese_chars = get_chinese_chars(current_phrase['chinese'])
    
    # Mostrar frase actual
    st.markdown(f"""
    <div class="phrase-display" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 20px; border-radius: 10px; color: white; text-align: center; margin: 20px 0;">
        <h2 style="margin: 0; font-size: 1.8em; font-family: KaiTi, STKaiti, 'KaiTi SC', 'KaiTi TC', serif;">{current_phrase['chinese']}</h2>
        <h3 style="margin: 10px 0; font-size: 1.2em;">{current_phrase['pinyin']}</h3>
        <p style="margin: 0;">{current_phrase['spanish']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if chinese_chars:
        # Controles
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("⏮️ Anterior", disabled=st.session_state.current_char_index == 0):
                st.session_state.current_char_index -= 1
                st.session_state.auto_play = False
        
        with col2:
            if st.button("⏭️ Siguiente", disabled=st.session_state.current_char_index >= len(chinese_chars) - 1):
                st.session_state.current_char_index += 1
                st.session_state.auto_play = False
        
        with col3:
            if st.button("🔄 Reiniciar"):
                st.session_state.current_char_index = 0
                st.session_state.auto_play = False
        
        with col4:
            if st.button("▶️ Auto" if not st.session_state.auto_play else "⏸️ Pausar"):
                st.session_state.auto_play = not st.session_state.auto_play
        
        # Progress bar interactivo tipo reproductor de audio
        # st.markdown('<div class="progress-container">', unsafe_allow_html=True)
        # st.markdown('<div class="progress-label">🎯 Progreso - Desliza para navegar:</div>', unsafe_allow_html=True)
        
        # Slider interactivo
        selected_position = st.slider(
            "",
            min_value=0,
            max_value=len(chinese_chars) - 1,
            value=st.session_state.current_char_index,
            step=1,
            key="progress_slider"
        )
        
        # Actualizar posición si el slider cambió
        if selected_position != st.session_state.current_char_index:
            st.session_state.current_char_index = selected_position
            st.session_state.auto_play = False
        
        # Mostrar información del progreso
        current_char = chinese_chars[st.session_state.current_char_index]
        current_pinyin = get_pinyin(current_char)
        
        # Mostrar pinyin del carácter actual
        st.markdown(f"""
        <div style="text-align: center; font-size: 1.5em; color: #007bff; 
                    margin: 5px 0; font-weight: bold;">
            {current_pinyin}
        </div>
        """, unsafe_allow_html=True)
        
        # Carácter actual
        st.markdown(f'<div class="current-char">{current_char}</div>', unsafe_allow_html=True)
        
        # Auto-play
        if st.session_state.auto_play:
            if st.session_state.current_char_index < len(chinese_chars) - 1:
                time.sleep(2)
                st.session_state.current_char_index += 1
                st.rerun()
            else:
                st.session_state.auto_play = False
                st.success("🎉 ¡Completado!")

if __name__ == "__main__":
    main()