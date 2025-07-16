import streamlit as st
import sqlite3
import pandas as pd
import random
import time
import hashlib
import io
from typing import Dict, List, Optional, Tuple

# Configuración de la página
st.set_page_config(
    page_title="学习中文 - Flashcards",
    page_icon="🎴",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Código de acceso (hash SHA-256 de ".Ad3l4nT3$$$$$")
ACCESS_CODE_HASH = "32b1514b28d7aa1aba3cdecbcfe3e370e3afcedd4b9fee1199f2801cc38cfe22"

class VocabularyDB:
    def __init__(self, db_path: str = "vocabulary.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializar base de datos con datos por defecto"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Crear tabla de vocabulario
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vocabulary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chinese TEXT NOT NULL,
                pinyin TEXT NOT NULL,
                spanish TEXT NOT NULL,
                category TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Crear tabla de configuración
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        ''')
        
        # Verificar si ya hay datos
        cursor.execute("SELECT COUNT(*) FROM vocabulary")
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Insertar datos por defecto
            default_data = [
                # Saludos y Cortesía
                ('你好', 'nǐ hǎo', 'Hola', 'Saludos y Cortesía'),
                ('再见', 'zài jiàn', 'Adiós', 'Saludos y Cortesía'),
                ('谢谢', 'xiè xie', 'Gracias', 'Saludos y Cortesía'),
                ('请', 'qǐng', 'Por favor', 'Saludos y Cortesía'),
                ('对不起', 'duì bu qǐ', 'Lo siento', 'Saludos y Cortesía'),
                ('没关系', 'méi guān xi', 'No importa', 'Saludos y Cortesía'),
                ('欢迎', 'huān yíng', 'Bienvenido', 'Saludos y Cortesía'),
                
                # Números
                ('一', 'yī', 'Uno', 'Números'),
                ('二', 'èr', 'Dos', 'Números'),
                ('三', 'sān', 'Tres', 'Números'),
                ('四', 'sì', 'Cuatro', 'Números'),
                ('五', 'wǔ', 'Cinco', 'Números'),
                ('六', 'liù', 'Seis', 'Números'),
                ('七', 'qī', 'Siete', 'Números'),
                ('八', 'bā', 'Ocho', 'Números'),
                ('九', 'jiǔ', 'Nueve', 'Números'),
                ('十', 'shí', 'Diez', 'Números'),
                
                # Familia
                ('爸爸', 'bà ba', 'Papá', 'Familia'),
                ('妈妈', 'mā ma', 'Mamá', 'Familia'),
                ('儿子', 'ér zi', 'Hijo', 'Familia'),
                ('女儿', 'nǚ ér', 'Hija', 'Familia'),
                ('哥哥', 'gē ge', 'Hermano mayor', 'Familia'),
                ('姐姐', 'jiě jie', 'Hermana mayor', 'Familia'),
                ('弟弟', 'dì di', 'Hermano menor', 'Familia'),
                ('妹妹', 'mèi mei', 'Hermana menor', 'Familia'),
                
                # Aula
                ('老师', 'lǎo shī', 'Profesor/a', 'Aula'),
                ('学生', 'xué sheng', 'Estudiante', 'Aula'),
                ('问题', 'wèn tí', 'Pregunta', 'Aula'),
                ('答案', 'dá àn', 'Respuesta', 'Aula'),
                ('汉语', 'hàn yǔ', 'Chino (idioma)', 'Aula'),
                ('明白', 'míng bai', 'Entender', 'Aula'),
                ('说', 'shuō', 'Hablar/Decir', 'Aula'),
                ('听', 'tīng', 'Escuchar', 'Aula'),
                
                # Colores
                ('红色', 'hóng sè', 'Rojo', 'Colores'),
                ('蓝色', 'lán sè', 'Azul', 'Colores'),
                ('绿色', 'lǜ sè', 'Verde', 'Colores'),
                ('黄色', 'huáng sè', 'Amarillo', 'Colores'),
                ('黑色', 'hēi sè', 'Negro', 'Colores'),
                ('白色', 'bái sè', 'Blanco', 'Colores'),
                ('紫色', 'zǐ sè', 'Morado', 'Colores'),
                
                # Tiempo
                ('今天', 'jīn tiān', 'Hoy', 'Tiempo'),
                ('明天', 'míng tiān', 'Mañana', 'Tiempo'),
                ('昨天', 'zuó tiān', 'Ayer', 'Tiempo'),
                ('现在', 'xiàn zài', 'Ahora', 'Tiempo'),
                ('早上', 'zǎo shang', 'Mañana (AM)', 'Tiempo'),
                ('晚上', 'wǎn shang', 'Noche', 'Tiempo'),
                ('年', 'nián', 'Año', 'Tiempo'),
                ('月', 'yuè', 'Mes', 'Tiempo'),
                ('天', 'tiān', 'Día', 'Tiempo'),
            ]
            
            cursor.executemany('''
                INSERT INTO vocabulary (chinese, pinyin, spanish, category)
                VALUES (?, ?, ?, ?)
            ''', default_data)
        
        conn.commit()
        conn.close()
    
    def get_categories(self) -> List[str]:
        """Obtener todas las categorías disponibles"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM vocabulary ORDER BY category")
        categories = [row[0] for row in cursor.fetchall()]
        conn.close()
        return categories
    
    def get_words_by_category(self, category: str) -> List[Dict]:
        """Obtener palabras por categoría"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if category == "Todas las categorías":
            cursor.execute("SELECT chinese, pinyin, spanish, category FROM vocabulary")
        else:
            cursor.execute("SELECT chinese, pinyin, spanish, category FROM vocabulary WHERE category = ?", (category,))
        
        words = []
        for row in cursor.fetchall():
            words.append({
                'chinese': row[0],
                'pinyin': row[1],
                'spanish': row[2],
                'category': row[3]
            })
        
        conn.close()
        return words
    
    def get_random_word(self, category: str) -> Optional[Dict]:
        """Obtener una palabra aleatoria de la categoría"""
        words = self.get_words_by_category(category)
        if words:
            return random.choice(words)
        return None
    
    def add_word(self, chinese: str, pinyin: str, spanish: str, category: str) -> bool:
        """Agregar nueva palabra"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO vocabulary (chinese, pinyin, spanish, category)
                VALUES (?, ?, ?, ?)
            ''', (chinese, pinyin, spanish, category))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Error al agregar palabra: {e}")
            return False
    
    def update_word(self, word_id: int, chinese: str, pinyin: str, spanish: str, category: str) -> bool:
        """Actualizar palabra existente"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE vocabulary 
                SET chinese = ?, pinyin = ?, spanish = ?, category = ?
                WHERE id = ?
            ''', (chinese, pinyin, spanish, category, word_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Error al actualizar palabra: {e}")
            return False
    
    def delete_word(self, word_id: int) -> bool:
        """Eliminar palabra"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM vocabulary WHERE id = ?", (word_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Error al eliminar palabra: {e}")
            return False
    
    def get_all_words(self) -> pd.DataFrame:
        """Obtener todas las palabras como DataFrame"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM vocabulary ORDER BY category, chinese", conn)
        conn.close()
        return df
    
    def import_from_csv(self, csv_data: str) -> Tuple[int, int]:
        """Importar palabras desde CSV"""
        try:
            df = pd.read_csv(io.StringIO(csv_data))
            
            # Verificar columnas requeridas
            required_columns = ['chinese', 'pinyin', 'spanish', 'category']
            if not all(col in df.columns for col in required_columns):
                st.error(f"El CSV debe contener las columnas: {', '.join(required_columns)}")
                return 0, 0
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            added = 0
            errors = 0
            
            for _, row in df.iterrows():
                try:
                    cursor.execute('''
                        INSERT INTO vocabulary (chinese, pinyin, spanish, category)
                        VALUES (?, ?, ?, ?)
                    ''', (row['chinese'], row['pinyin'], row['spanish'], row['category']))
                    added += 1
                except:
                    errors += 1
            
            conn.commit()
            conn.close()
            return added, errors
        except Exception as e:
            st.error(f"Error al importar CSV: {e}")
            return 0, 0
    
    def set_config(self, key: str, value: str):
        """Guardar configuración"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO config (key, value)
            VALUES (?, ?)
        ''', (key, value))
        conn.commit()
        conn.close()
    
    def get_config(self, key: str, default: str = None) -> str:
        """Obtener configuración"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM config WHERE key = ?", (key,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else default

def hash_password(password: str) -> str:
    """Generar hash SHA-256 de la contraseña"""
    return hashlib.sha256(password.encode()).hexdigest()

def check_access():
    """Verificar acceso con código"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.markdown("""
        <div style="text-align: center; padding: 50px;">
            <h2>🔐 Acceso Restringido</h2>
            <p>Por favor, ingresa el código de acceso para continuar</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            access_code = st.text_input("Código de acceso:", type="password", key="access_input")
            
            if st.button("🚪 Ingresar", use_container_width=True):
                if hash_password(access_code) == ACCESS_CODE_HASH:
                    st.session_state.authenticated = True
                    st.success("✅ Acceso autorizado")
                    st.rerun()
                else:
                    st.error("❌ Código incorrecto")
        
        st.stop()

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
            if (window.speechSynthesis) {{
                window.speechSynthesis.cancel();
                const utterance = new SpeechSynthesisUtterance('{text}');
                utterance.lang = 'zh-CN';
                utterance.rate = 0.7;
                utterance.pitch = 1.0;
                utterance.volume = 1.0;
                window.speechSynthesis.speak(utterance);
            }}
        }}
        {auto_play_script}
    </script>
    """

def admin_panel(db: VocabularyDB):
    """Panel de administración de vocabulario"""
    st.markdown("## 🛠️ Panel de Administración")
    
    # Pestañas para diferentes funciones
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Agregar Palabra", "📊 Ver/Editar", "📤 Importar CSV", "📋 Exportar"])
    
    with tab1:
        st.markdown("### Agregar Nueva Palabra")
        
        col1, col2 = st.columns(2)
        
        with col1:
            chinese = st.text_input("Palabra en Chino:", key="add_chinese")
            pinyin = st.text_input("Pinyin:", key="add_pinyin")
        
        with col2:
            spanish = st.text_input("Traducción al Español:", key="add_spanish")
            
            # Obtener categorías existentes
            categories = db.get_categories()
            category_options = categories + ["➕ Nueva categoría"]
            
            category_choice = st.selectbox("Categoría:", category_options, key="add_category_choice")
            
            if category_choice == "➕ Nueva categoría":
                category = st.text_input("Nueva categoría:", key="add_new_category")
            else:
                category = category_choice
        
        if st.button("✅ Agregar Palabra", key="add_word_btn"):
            if chinese and pinyin and spanish and category:
                if db.add_word(chinese, pinyin, spanish, category):
                    st.success("✅ Palabra agregada exitosamente")
                    st.rerun()
            else:
                st.error("❌ Por favor completa todos los campos")
    
    with tab2:
        st.markdown("### Ver y Editar Vocabulario")
        
        # Filtro por categoría
        categories = ["Todas"] + db.get_categories()
        filter_category = st.selectbox("Filtrar por categoría:", categories, key="filter_category")
        
        # Obtener datos
        df = db.get_all_words()
        
        if filter_category != "Todas":
            df = df[df['category'] == filter_category]
        
        # Mostrar tabla editable
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            
            # Seleccionar palabra para editar
            word_ids = df['id'].tolist()
            selected_id = st.selectbox("Seleccionar palabra para editar:", 
                                     [f"{row['chinese']} - {row['spanish']}" for _, row in df.iterrows()],
                                     key="edit_select")
            
            if selected_id:
                selected_row = df.iloc[df.index[df.apply(lambda x: f"{x['chinese']} - {x['spanish']}" == selected_id, axis=1)].tolist()[0]]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    edit_chinese = st.text_input("Chino:", value=selected_row['chinese'], key="edit_chinese")
                    edit_pinyin = st.text_input("Pinyin:", value=selected_row['pinyin'], key="edit_pinyin")
                
                with col2:
                    edit_spanish = st.text_input("Español:", value=selected_row['spanish'], key="edit_spanish")
                    edit_category = st.text_input("Categoría:", value=selected_row['category'], key="edit_category")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("💾 Actualizar", key="update_btn"):
                        if db.update_word(selected_row['id'], edit_chinese, edit_pinyin, edit_spanish, edit_category):
                            st.success("✅ Palabra actualizada")
                            st.rerun()
                
                with col2:
                    if st.button("🗑️ Eliminar", key="delete_btn"):
                        if db.delete_word(selected_row['id']):
                            st.success("✅ Palabra eliminada")
                            st.rerun()
    
    with tab3:
        st.markdown("### Importar desde CSV")
        
        st.info("El CSV debe contener las columnas: chinese, pinyin, spanish, category")
        
        # Ejemplo de formato
        st.markdown("**Ejemplo de formato CSV:**")
        example_csv = """chinese,pinyin,spanish,category
你好,nǐ hǎo,Hola,Saludos
再见,zài jiàn,Adiós,Saludos"""
        st.code(example_csv)
        
        uploaded_file = st.file_uploader("Cargar archivo CSV", type=['csv'])
        
        if uploaded_file is not None:
            # Mostrar preview
            csv_data = uploaded_file.getvalue().decode('utf-8')
            st.markdown("**Vista previa:**")
            preview_df = pd.read_csv(io.StringIO(csv_data))
            st.dataframe(preview_df.head())
            
            if st.button("📥 Importar Datos"):
                added, errors = db.import_from_csv(csv_data)
                if added > 0:
                    st.success(f"✅ {added} palabras importadas exitosamente")
                if errors > 0:
                    st.warning(f"⚠️ {errors} errores durante la importación")
                if added > 0:
                    st.rerun()
    
    with tab4:
        st.markdown("### Exportar Vocabulario")
        
        # Obtener datos
        df = db.get_all_words()
        
        # Opción de filtrar por categoría
        categories = ["Todas"] + db.get_categories()
        export_category = st.selectbox("Exportar categoría:", categories, key="export_category")
        
        if export_category != "Todas":
            df = df[df['category'] == export_category]
        
        # Mostrar estadísticas
        st.metric("Total de palabras a exportar", len(df))
        
        # Preparar CSV
        csv = df.to_csv(index=False)
        
        st.download_button(
            label="📥 Descargar CSV",
            data=csv,
            file_name=f"vocabulario_{export_category.lower().replace(' ', '_')}.csv",
            mime="text/csv"
        )

def main():
    # Verificar acceso
    check_access()
    
    # Inicializar base de datos
    db = VocabularyDB()
    
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
            color: #000000;
            background: #FFFFFF;
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
    
    # Sidebar para navegación
    with st.sidebar:
        st.markdown("### 🎯 Navegación")
        
        # Modo de aplicación
        app_mode = st.selectbox(
            "Seleccionar modo:",
            ["🎴 Flashcards", "🛠️ Administración"],
            key="app_mode"
        )
        
        if app_mode == "🛠️ Administración":
            admin_panel(db)
            return
        
        st.markdown("---")
        st.markdown("### ⚙️ Configuraciones")
        
        # Selección de categoría con persistencia
        categories = ["Todas las categorías"] + db.get_categories()
        saved_category = db.get_config('selected_category', 'Todas las categorías')
        
        try:
            default_index = categories.index(saved_category)
        except ValueError:
            default_index = 0
        
        selected_category = st.selectbox(
            "📚 Categoría:",
            categories,
            index=default_index,
            key="category_select"
        )
        
        # Guardar categoría seleccionada
        if selected_category != saved_category:
            db.set_config('selected_category', selected_category)
        
        # Configuración de tiempo
        wait_time = st.slider("⏱️ Tiempo de espera (segundos)", 1, 10, 3)
        
        # Avance automático
        auto_advance = st.checkbox("🔄 Avance automático", True)
        learning_mode = st.checkbox("📚 Modo Aprendizaje", False)

        # Estadísticas
        st.markdown("---")
        st.markdown("### 📊 Estadísticas")
        st.metric("Palabras estudiadas", st.session_state.get('words_studied', 0))
        st.metric("Categoría actual", selected_category)
        st.metric("Tiempo por fase", f"{wait_time}s")
        
        # Botón de cerrar sesión
        st.markdown("---")
        if st.button("🚪 Cerrar Sesión"):
            st.session_state.authenticated = False
            st.rerun()
    
    # Inicializar estado de sesión
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
    if 'learning_mode' not in st.session_state:
        st.session_state.learning_mode = learning_mode
    
    # Actualizar configuraciones
    st.session_state.wait_time = wait_time
    st.session_state.auto_advance = auto_advance
    st.session_state.learning_mode = learning_mode

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
            word_data = db.get_random_word(st.session_state.current_category)
            if word_data:
                st.session_state.current_word = word_data['chinese']
                st.session_state.current_data = word_data
                if st.session_state.learning_mode:
                    st.session_state.phase = 1  # Learning mode doesn't use phases
                else:
                    st.session_state.phase = 1  # Flashcards mode starts at phase 1
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
                    word_data = db.get_random_word(st.session_state.current_category)
                    if word_data:
                        st.session_state.current_word = word_data['chinese']
                        st.session_state.current_data = word_data
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
        if st.session_state.learning_mode:
            # LEARNING MODE: Show everything at once
            st.markdown(f"""
            <div class="phase-indicator phase-1">
                📚 Modo Aprendizaje: Estudia la palabra completa
            </div>
            """, unsafe_allow_html=True)
            
            # Show Chinese word
            st.markdown(f"""
            <div class="chinese-word">
                {st.session_state.current_word}
            </div>
            """, unsafe_allow_html=True)
            
            # Show pinyin and translation
            st.markdown(f"""
            <div class="pinyin-translation">
                <div style="font-size: 1.2em; margin-bottom: 10px;">
                    📝 {st.session_state.current_data['pinyin']}
                </div>
                <div style="font-size: 1em;">
                    🇪🇸 {st.session_state.current_data['spanish']}
                </div>
                <div style="font-size: 0.8em; margin-top: 10px; opacity: 0.8;">
                    📂 {st.session_state.current_data['category']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Auto-play audio
            audio_html = create_audio_component(st.session_state.current_word, auto_play=True)
            st.components.v1.html(audio_html, height=100)
            
            # Learning mode auto-advance logic
            if (st.session_state.is_playing and 
                st.session_state.auto_advance and 
                st.session_state.phase_start_time is not None):
                
                current_time = time.time()
                elapsed_time = current_time - st.session_state.phase_start_time
                remaining_time = st.session_state.wait_time - elapsed_time
                
                if remaining_time > 0:
                    # Show countdown
                    st.markdown(f"""
                    <div class="countdown-timer">
                        ⏳ Nueva palabra en: {remaining_time:.1f}s
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Refresh every 0.1 seconds
                    if current_time - st.session_state.last_update >= 0.1:
                        st.session_state.last_update = current_time
                        time.sleep(0.1)
                        st.rerun()
                        
                else:
                    # Time's up - next word
                    st.session_state.words_studied += 1
                    word_data = db.get_random_word(st.session_state.current_category)
                    if word_data:
                        st.session_state.current_word = word_data['chinese']
                        st.session_state.current_data = word_data
                        st.session_state.phase_start_time = time.time()
                    st.rerun()
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
                    <div style="font-size: 0.8em; margin-top: 10px; opacity: 0.8;">
                        📂 {st.session_state.current_data['category']}
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
                        word_data = db.get_random_word(st.session_state.current_category)
                        if word_data:
                            st.session_state.current_word = word_data['chinese']
                            st.session_state.current_data = word_data
                            st.session_state.phase = 1
                            st.session_state.phase_start_time = time.time()
                    
                    st.rerun()

if __name__ == "__main__":
    main()