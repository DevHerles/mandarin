import streamlit as st
import random
import time
from typing import Dict, List

# Base de datos expandida de vocabulario por categorías
VOCABULARY_DB = {
    "Saludos y Cortesía": {
        '你好': {'pinyin': 'nǐ hǎo', 'spanish': 'Hola'},
        '再见': {'pinyin': 'zài jiàn', 'spanish': 'Adiós'},
        '谢谢': {'pinyin': 'xiè xie', 'spanish': 'Gracias'},
        '请': {'pinyin': 'qǐng', 'spanish': 'Por favor'},
        '对不起': {'pinyin': 'duì bu qǐ', 'spanish': 'Lo siento'},
        '没关系': {'pinyin': 'méi guān xi', 'spanish': 'No importa'},
        '欢迎': {'pinyin': 'huān yíng', 'spanish': 'Bienvenido'},
    },
    "Números": {
        '一': {'pinyin': 'yī', 'spanish': 'Uno'},
        '二': {'pinyin': 'èr', 'spanish': 'Dos'},
        '三': {'pinyin': 'sān', 'spanish': 'Tres'},
        '四': {'pinyin': 'sì', 'spanish': 'Cuatro'},
        '五': {'pinyin': 'wǔ', 'spanish': 'Cinco'},
        '六': {'pinyin': 'liù', 'spanish': 'Seis'},
        '七': {'pinyin': 'qī', 'spanish': 'Siete'},
        '八': {'pinyin': 'bā', 'spanish': 'Ocho'},
        '九': {'pinyin': 'jiǔ', 'spanish': 'Nueve'},
        '十': {'pinyin': 'shí', 'spanish': 'Diez'},
    },
    "Familia": {
        '爸爸': {'pinyin': 'bà ba', 'spanish': 'Papá'},
        '妈妈': {'pinyin': 'mā ma', 'spanish': 'Mamá'},
        '儿子': {'pinyin': 'ér zi', 'spanish': 'Hijo'},
        '女儿': {'pinyin': 'nǚ ér', 'spanish': 'Hija'},
        '哥哥': {'pinyin': 'gē ge', 'spanish': 'Hermano mayor'},
        '姐姐': {'pinyin': 'jiě jie', 'spanish': 'Hermana mayor'},
        '弟弟': {'pinyin': 'dì di', 'spanish': 'Hermano menor'},
        '妹妹': {'pinyin': 'mèi mei', 'spanish': 'Hermana menor'},
    },
    "Aula": {
        '老师': {'pinyin': 'lǎo shī', 'spanish': 'Profesor/a'},
        '学生': {'pinyin': 'xué sheng', 'spanish': 'Estudiante'},
        '问题': {'pinyin': 'wèn tí', 'spanish': 'Pregunta'},
        '答案': {'pinyin': 'dá àn', 'spanish': 'Respuesta'},
        '汉语': {'pinyin': 'hàn yǔ', 'spanish': 'Chino (idioma)'},
        '明白': {'pinyin': 'míng bai', 'spanish': 'Entender'},
        '说': {'pinyin': 'shuō', 'spanish': 'Hablar/Decir'},
        '听': {'pinyin': 'tīng', 'spanish': 'Escuchar'},
    },
    "Colores": {
        '红色': {'pinyin': 'hóng sè', 'spanish': 'Rojo'},
        '蓝色': {'pinyin': 'lán sè', 'spanish': 'Azul'},
        '绿色': {'pinyin': 'lǜ sè', 'spanish': 'Verde'},
        '黄色': {'pinyin': 'huáng sè', 'spanish': 'Amarillo'},
        '黑色': {'pinyin': 'hēi sè', 'spanish': 'Negro'},
        '白色': {'pinyin': 'bái sè', 'spanish': 'Blanco'},
        '紫色': {'pinyin': 'zǐ sè', 'spanish': 'Morado'},
    },
    "Tiempo": {
        '今天': {'pinyin': 'jīn tiān', 'spanish': 'Hoy'},
        '明天': {'pinyin': 'míng tiān', 'spanish': 'Mañana'},
        '昨天': {'pinyin': 'zuó tiān', 'spanish': 'Ayer'},
        '现在': {'pinyin': 'xiàn zài', 'spanish': 'Ahora'},
        '早上': {'pinyin': 'zǎo shang', 'spanish': 'Mañana (AM)'},
        '晚上': {'pinyin': 'wǎn shang', 'spanish': 'Noche'},
        '年': {'pinyin': 'nián', 'spanish': 'Año'},
        '月': {'pinyin': 'yuè', 'spanish': 'Mes'},
        '天': {'pinyin': 'tiān', 'spanish': 'Día'},
    }
}

def get_random_word(category: str) -> tuple:
    """Obtener una palabra aleatoria de la categoría seleccionada"""
    if category == "Todas las categorías":
        # Combinar todas las categorías
        all_words = {}
        for cat_words in VOCABULARY_DB.values():
            all_words.update(cat_words)
        chinese_word = random.choice(list(all_words.keys()))
        return chinese_word, all_words[chinese_word]
    else:
        words = VOCABULARY_DB[category]
        chinese_word = random.choice(list(words.keys()))
        return chinese_word, words[chinese_word]

def create_audio_component(text: str, auto_play: bool = False):
    """Crear componente de audio que funciona automáticamente"""
    auto_play_script = """
    setTimeout(() => {
        playAudio();
    }, 500);
    """ if auto_play else ""
    
    return f"""
    <div style="text-align: center; margin: 20px 0;">
        <button onclick="playAudio()" 
                style="background: #e74c3c; color: white; border: none; padding: 15px 30px; 
                       border-radius: 25px; font-size: 1.2em; cursor: pointer; 
                       box-shadow: 0 4px 15px rgba(0,0,0,0.2); transition: all 0.3s;">
            🔊 Reproducir Audio
        </button>
    </div>
    <script>
        function playAudio() {{
            // Cancelar cualquier audio previo
            if (window.speechSynthesis) {{
                window.speechSynthesis.cancel();
                
                // Crear nuevo utterance
                const utterance = new SpeechSynthesisUtterance('{text}');
                utterance.lang = 'zh-CN';
                utterance.rate = 0.7;
                utterance.pitch = 1.0;
                utterance.volume = 1.0;
                
                // Reproducir
                window.speechSynthesis.speak(utterance);
            }}
        }}
        
        {auto_play_script}
    </script>
    """

# Configuración de la página
st.set_page_config(
    page_title="学习中文 - Flashcards",
    page_icon="🎴",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def main():
    # CSS personalizado
    st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC&display=swap" rel="stylesheet">
    <style>
        .main-title {
            font-family: 'Noto Serif SC', KaiTi, STKaiti, "KaiTi SC", "KaiTi TC", serif;
            font-size: 3em;
            text-align: center;
            color: #c0392b;
            margin-bottom: 30px;
        }
        .chinese-word {
            font-family: 'Noto Serif SC', KaiTi, STKaiti, "KaiTi SC", "KaiTi TC", serif;
            font-size: 10em;
            text-align: center;
            color: #2c3e50;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 50px;
            border-radius: 20px;
            margin: 30px 0;
            border: 4px solid #3498db;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        .pinyin-translation {
            font-size: 2em;
            text-align: center;
            color: #8e44ad;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            margin: 20px 0;
            font-weight: bold;
        }
        .phase-indicator {
            font-size: 1.0em;
            text-align: center;
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
            font-weight: bold;
        }
        .phase-1 { background: #e8f5e8; color: #27ae60; }
        .phase-2 { background: #fff3cd; color: #f39c12; }
        .phase-3 { background: #f8d7da; color: #c0392b; }
        
        .countdown-timer {
            text-align: center;
            margin: 20px 0;
            padding: 15px;
            background: #f39c12;
            color: white;
            border-radius: 10px;
            font-size: 1.2em;
            font-weight: bold;
        }
        
        .audio-playing {
            text-align: center;
            margin: 20px 0;
            padding: 20px;
            background: #2ecc71;
            color: white;
            border-radius: 10px;
            font-size: 1.3em;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.7; }
            100% { opacity: 1; }
        }
        
        @media (max-width: 768px) {
            .chinese-word {
                font-size: 6em;
                padding: 30px;
            }
            .pinyin-translation {
                font-size: 1.0em;
                padding: 20px;
            }
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Sidebar para configuraciones
    with st.sidebar:
        st.markdown("### ⚙️ Configuraciones")
        
        # Selección de categoría
        categories = ["Todas las categorías"] + list(VOCABULARY_DB.keys())
        selected_category = st.selectbox(
            "📚 Categoría:",
            categories,
            index=0 if 'current_category' not in st.session_state else categories.index(st.session_state.get('current_category', 'Todas las categorías'))
        )
        
        # Configuración de tiempo
        wait_time = st.slider("⏱️ Tiempo de espera (segundos)", 1, 10, 3)
        
        # Avance automático
        auto_advance = st.checkbox("🔄 Avance automático", True)
        
        # Estadísticas
        st.markdown("---")
        st.markdown("### 📊 Estadísticas")
        st.metric("Palabras estudiadas", st.session_state.get('words_studied', 0))
        st.metric("Categoría actual", selected_category)
        st.metric("Tiempo por fase", f"{wait_time}s")
    
    # Inicializar estado
    if 'current_word' not in st.session_state:
        st.session_state.current_word = None
    if 'current_data' not in st.session_state:
        st.session_state.current_data = None
    if 'phase' not in st.session_state:
        st.session_state.phase = 0
    if 'is_playing' not in st.session_state:
        st.session_state.is_playing = False
    if 'phase_start_time' not in st.session_state:
        st.session_state.phase_start_time = None
    if 'words_studied' not in st.session_state:
        st.session_state.words_studied = 0
    if 'current_category' not in st.session_state:
        st.session_state.current_category = selected_category
    if 'last_update' not in st.session_state:
        st.session_state.last_update = time.time()
    
    # Actualizar configuraciones
    st.session_state.wait_time = wait_time
    st.session_state.auto_advance = auto_advance
    
    # Cambio de categoría
    if selected_category != st.session_state.current_category:
        st.session_state.current_category = selected_category
        st.session_state.current_word = None
        st.session_state.phase = 0
        st.session_state.is_playing = False
        st.session_state.phase_start_time = None
    
    # Título principal
    st.markdown('<h1 class="main-title">学习中文 🎴</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2em; color: #7f8c8d;">Flashcards para aprender vocabulario chino</p>', unsafe_allow_html=True)
    
    # Controles principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🎯 Nueva Palabra", key="new_word", use_container_width=True):
            st.session_state.current_word, st.session_state.current_data = get_random_word(st.session_state.current_category)
            st.session_state.phase = 1
            st.session_state.phase_start_time = time.time()
            st.session_state.is_playing = True
            st.rerun()
    
    with col2:
        play_text = "⏸️ Pausar" if st.session_state.is_playing else "▶️ Iniciar"
        if st.button(play_text, key="play_pause", use_container_width=True):
            if st.session_state.current_word:
                st.session_state.is_playing = not st.session_state.is_playing
                if st.session_state.is_playing:
                    st.session_state.phase_start_time = time.time()
                st.rerun()
    
    with col3:
        if st.button("⏭️ Siguiente", key="next_phase", use_container_width=True):
            if st.session_state.current_word:
                if st.session_state.phase < 3:
                    st.session_state.phase += 1
                    st.session_state.phase_start_time = time.time()
                else:
                    # Nueva palabra
                    st.session_state.words_studied += 1
                    st.session_state.current_word, st.session_state.current_data = get_random_word(st.session_state.current_category)
                    st.session_state.phase = 1
                    st.session_state.phase_start_time = time.time()
                st.rerun()
    
    with col4:
        if st.button("🔄 Reiniciar", key="reset", use_container_width=True):
            st.session_state.phase = 0
            st.session_state.is_playing = False
            st.session_state.current_word = None
            st.session_state.phase_start_time = None
            st.session_state.words_studied = 0
            st.rerun()
    
    # Área principal de flashcard
    if st.session_state.current_word is None:
        st.markdown("""
        <div style="text-align: center; padding: 50px; background: #000000; border-radius: 10px; margin: 20px 0;">
            <h2>👋 ¡Bienvenido!</h2>
            <p>Presiona <strong>"🎯 Nueva Palabra"</strong> para comenzar tu sesión de estudio</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Mostrar indicador de fase
        phase_info = {
            1: {"text": "🎯 Fase 1: Identifica la palabra", "class": "phase-1"},
            2: {"text": "📝 Fase 2: Pinyin y traducción", "class": "phase-2"},
            3: {"text": "🔊 Fase 3: Escucha la pronunciación", "class": "phase-3"}
        }
        
        if st.session_state.phase > 0:
            current_phase = phase_info[st.session_state.phase]
            st.markdown(f"""
            <div class="phase-indicator {current_phase['class']}">
                {current_phase['text']}
            </div>
            """, unsafe_allow_html=True)
        
        # Mostrar contenido según la fase
        if st.session_state.phase >= 1:
            # Fase 1: Mostrar palabra china
            st.markdown(f"""
            <div class="chinese-word">
                {st.session_state.current_word}
            </div>
            """, unsafe_allow_html=True)
        
        if st.session_state.phase >= 2:
            # Fase 2: Mostrar pinyin y traducción
            st.markdown(f"""
            <div class="pinyin-translation">
                <div style="font-size: 1.2em; margin-bottom: 10px;">
                    📝 {st.session_state.current_data['pinyin']}
                </div>
                <div style="font-size: 1em;">
                    🇪🇸 {st.session_state.current_data['spanish']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        if st.session_state.phase >= 3:
            # Fase 3: Mostrar audio automático
            st.markdown(f"""
            <div class="audio-playing">
                🔊 ¡Escucha la pronunciación!
            </div>
            """, unsafe_allow_html=True)
            
            # Reproducir audio automáticamente
            audio_html = create_audio_component(st.session_state.current_word, auto_play=True)
            st.components.v1.html(audio_html, height=100)
        
        # Botón de audio manual disponible desde la fase 2
        if st.session_state.phase >= 2 and st.session_state.phase < 3:
            audio_html = create_audio_component(st.session_state.current_word, auto_play=False)
            st.components.v1.html(audio_html, height=100)
        
        # Lógica de avance automático mejorada
        if (st.session_state.is_playing and 
            st.session_state.auto_advance and 
            st.session_state.phase_start_time is not None):
            
            current_time = time.time()
            elapsed_time = current_time - st.session_state.phase_start_time
            remaining_time = st.session_state.wait_time - elapsed_time
            
            if remaining_time > 0:
                # Mostrar countdown
                st.markdown(f"""
                <div class="countdown-timer">
                    ⏳ {'Siguiente fase' if st.session_state.phase < 3 else 'Nueva palabra'} en: {remaining_time:.1f}s
                </div>
                """, unsafe_allow_html=True)
                
                # Placeholder para auto-refresh
                placeholder = st.empty()
                
                # Refresh cada 0.1 segundos
                if current_time - st.session_state.last_update >= 0.1:
                    st.session_state.last_update = current_time
                    time.sleep(0.1)
                    st.rerun()
                    
            else:
                # Tiempo terminado - avanzar
                if st.session_state.phase < 3:
                    st.session_state.phase += 1
                    st.session_state.phase_start_time = time.time()
                else:
                    # Completar palabra y pasar a la siguiente
                    st.session_state.words_studied += 1
                    st.session_state.current_word, st.session_state.current_data = get_random_word(st.session_state.current_category)
                    st.session_state.phase = 1
                    st.session_state.phase_start_time = time.time()
                
                st.rerun()

if __name__ == "__main__":
    main()