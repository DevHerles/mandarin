import streamlit as st
import sqlite3
import pandas as pd
import random
import time
import hashlib
import io
from typing import Dict, List, Optional, Tuple
import requests
import re
from urllib.parse import quote
import base64

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
                needs_review BOOLEAN DEFAULT 0,
                archived BOOLEAN DEFAULT 0,
                explanation TEXT,
                literal_translation TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Verificar si la columna needs_review existe, si no, agregarla
        cursor.execute("PRAGMA table_info(vocabulary)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'needs_review' not in columns:
            cursor.execute('ALTER TABLE vocabulary ADD COLUMN needs_review BOOLEAN DEFAULT 0')
        
        if 'archived' not in columns:
            cursor.execute('ALTER TABLE vocabulary ADD COLUMN archived BOOLEAN DEFAULT 0')
    
        if 'explanation' not in columns:
            cursor.execute('ALTER TABLE vocabulary ADD COLUMN explanation TEXT')
            
        if 'literal_translation' not in columns:
            cursor.execute('ALTER TABLE vocabulary ADD COLUMN literal_translation TEXT')

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

    def toggle_word_archived(self, chinese: str, pinyin: str) -> bool:
        """Alternar estado de archivado de una palabra"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Verificar si la columna archived existe
            cursor.execute("PRAGMA table_info(vocabulary)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'archived' not in columns:
                cursor.execute('ALTER TABLE vocabulary ADD COLUMN archived BOOLEAN DEFAULT 0')
                conn.commit()
            
            # Obtener estado actual
            cursor.execute('''
                SELECT COALESCE(archived, 0) FROM vocabulary 
                WHERE chinese = ? AND pinyin = ?
            ''', (chinese, pinyin))
            
            result = cursor.fetchone()
            if result:
                current_state = result[0] or 0  # Asegurar que sea 0 si es None
                new_state = 0 if current_state else 1
                cursor.execute('''
                    UPDATE vocabulary 
                    SET archived = ?
                    WHERE chinese = ? AND pinyin = ?
                ''', (new_state, chinese, pinyin))
                conn.commit()
                conn.close()
                return bool(new_state)
            
            conn.close()
            return False
        except Exception as e:
            st.error(f"Error al cambiar estado de archivado: {e}")
            return False

    def get_word_archived_status(self, chinese: str, pinyin: str) -> bool:
        """Obtener estado de archivado de una palabra"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT archived FROM vocabulary 
                WHERE chinese = ? AND pinyin = ?
            ''', (chinese, pinyin))
            result = cursor.fetchone()
            conn.close()
            return bool(result[0]) if result else False
        except:
            return False

    def get_archived_count(self, category: str = None) -> int:
        """Obtener cantidad de palabras archivadas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if category and category != "Todas las categorías":
            cursor.execute("SELECT COUNT(*) FROM vocabulary WHERE archived = 1 AND category = ?", (category,))
        else:
            cursor.execute("SELECT COUNT(*) FROM vocabulary WHERE archived = 1")
        
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def toggle_word_review(self, chinese: str, pinyin: str) -> bool:
        """Alternar estado de revisión de una palabra"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Obtener estado actual
            cursor.execute('''
                SELECT needs_review FROM vocabulary 
                WHERE chinese = ? AND pinyin = ?
            ''', (chinese, pinyin))
            
            result = cursor.fetchone()
            if result:
                new_state = 0 if result[0] else 1
                cursor.execute('''
                    UPDATE vocabulary 
                    SET needs_review = ?
                    WHERE chinese = ? AND pinyin = ?
                ''', (new_state, chinese, pinyin))
                conn.commit()
                conn.close()
                return bool(new_state)
            
            conn.close()
            return False
        except Exception as e:
            st.error(f"Error al cambiar estado de revisión: {e}")
            return False

    def get_word_review_status(self, chinese: str, pinyin: str) -> bool:
        """Obtener estado de revisión de una palabra"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT needs_review FROM vocabulary 
                WHERE chinese = ? AND pinyin = ?
            ''', (chinese, pinyin))
            result = cursor.fetchone()
            conn.close()
            return bool(result[0]) if result else False
        except:
            return False

    def get_review_words_by_category(self, category: str) -> List[Dict]:
        """Obtener palabras marcadas para revisión por categoría"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if category == "Todas las categorías":
            cursor.execute("SELECT chinese, pinyin, spanish, category, explanation, literal_translation FROM vocabulary WHERE needs_review = 1")
        else:
            cursor.execute("SELECT chinese, pinyin, spanish, category, explanation, literal_translation FROM vocabulary WHERE category = ? AND needs_review = 1", (category,))
        
        words = []
        for row in cursor.fetchall():
            words.append({
                'chinese': row[0],
                'pinyin': row[1],
                'spanish': row[2],
                'category': row[3],
                'explanation': row[4] if len(row) > 4 else '',
                'literal_translation': row[5] if len(row) > 5 else ''
            })
        
        conn.close()
        return words

    def get_review_count(self, category: str = None) -> int:
        """Obtener cantidad de palabras marcadas para revisión"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if category and category != "Todas las categorías":
            cursor.execute("SELECT COUNT(*) FROM vocabulary WHERE needs_review = 1 AND category = ?", (category,))
        else:
            cursor.execute("SELECT COUNT(*) FROM vocabulary WHERE needs_review = 1")
        
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def get_categories(self) -> List[str]:
        """Obtener todas las categorías disponibles"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM vocabulary ORDER BY category")
        categories = [row[0] for row in cursor.fetchall()]
        conn.close()
        return categories
    
    def get_words_by_category(self, category: str, review_only: bool = False, archived_only: bool = False) -> List[Dict]:
        """Obtener palabras por categoría con opciones de filtrado"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Construir consulta base
        base_query = "SELECT chinese, pinyin, spanish, category, explanation, literal_translation FROM vocabulary WHERE"
        conditions = []
        params = []
        
        # Filtro de categoría
        if category != "Todas las categorías":
            conditions.append("category = ?")
            params.append(category)
        
        # Filtros mutuamente excluyentes
        if review_only:
            conditions.append("needs_review = 1 AND archived = 0")
        elif archived_only:
            conditions.append("archived = 1")
        else:
            conditions.append("archived = 0")  # Por defecto, no mostrar archivadas
        
        # Construir consulta final
        if conditions:
            query = f"{base_query} {' AND '.join(conditions)}"
        else:
            query = "SELECT chinese, pinyin, spanish, category, explanation, literal_translation FROM vocabulary WHERE archived = 0"
        
        cursor.execute(query, params)
        
        words = []
        for row in cursor.fetchall():
            words.append({
                'chinese': row[0],
                'pinyin': row[1],
                'spanish': row[2],
                'category': row[3],
                'explanation': row[4] if len(row) > 4 else '',
                'literal_translation': row[5] if len(row) > 5 else ''
            })
        
        conn.close()
        return words
    
    def get_random_word(self, category: str, review_only: bool = False, archived_only: bool = False) -> Optional[Dict]:
        """Obtener una palabra aleatoria de la categoría con opciones de filtrado"""
        words = self.get_words_by_category(category, review_only, archived_only)
        if words:
            return random.choice(words)
        return None
    
    def add_word(self, chinese: str, pinyin: str, spanish: str, category: str, explanation: str = '', literal_translation: str = '') -> bool:
        """Agregar nueva palabra"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO vocabulary (chinese, pinyin, spanish, category, explanation, literal_translation)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (chinese, pinyin, spanish, category, explanation, literal_translation))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Error al agregar palabra: {e}")
            return False
    
    def update_word(self, word_id: int, chinese: str, pinyin: str, spanish: str, category: str, explanation: str = '', literal_translation: str = '') -> bool:
        """Actualizar palabra existente"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE vocabulary 
                SET chinese = ?, pinyin = ?, spanish = ?, category = ?, explanation = ?, literal_translation = ?
                WHERE id = ?
            ''', (chinese, pinyin, spanish, category, explanation, literal_translation, word_id))
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
            df = pd.read_csv(io.StringIO(csv_data), sep='|')
            
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
                    # Obtener valores opcionales
                    explanation = row.get('explanation', '')
                    literal_translation = row.get('literal_translation', '')
                    
                    cursor.execute('''
                        INSERT INTO vocabulary (chinese, pinyin, spanish, category, explanation, literal_translation)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (row['chinese'], row['pinyin'], row['spanish'], row['category'], explanation, literal_translation))
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

    def save_last_flashcard(self, word_data: dict, phase: int = 1):
        """Guardar el estado del último flashcard"""
        try:
            # Convertir word_data a JSON string para almacenamiento
            import json
            flashcard_json = json.dumps(word_data)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Actualizar o insertar el último flashcard
                cursor.execute("""
                    INSERT OR REPLACE INTO config (key, value) 
                    VALUES (?, ?)
                """, ('last_flashcard_data', flashcard_json))
                
                cursor.execute("""
                    INSERT OR REPLACE INTO config (key, value) 
                    VALUES (?, ?)
                """, ('last_flashcard_phase', str(phase)))
                
                conn.commit()
                return True
        except Exception as e:
            st.error(f"Error guardando último flashcard: {e}")
            return False

    def get_last_flashcard(self):
        """Obtener el estado del último flashcard"""
        try:
            import json
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Obtener datos del flashcard
                cursor.execute("SELECT value FROM config WHERE key = ?", ('last_flashcard_data',))
                result = cursor.fetchone()
                
                if result:
                    word_data = json.loads(result[0])
                    
                    # Obtener fase
                    cursor.execute("SELECT value FROM config WHERE key = ?", ('last_flashcard_phase',))
                    phase_result = cursor.fetchone()
                    phase = int(phase_result[0]) if phase_result else 1
                    
                    return {
                        'word_data': word_data,
                        'phase': phase
                    }
                
                return None
        except Exception as e:
            st.error(f"Error obteniendo último flashcard: {e}")
            return None

    def clear_last_flashcard(self):
        """Limpiar el estado del último flashcard"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM config WHERE key IN (?, ?)", 
                            ('last_flashcard_data', 'last_flashcard_phase'))
                conn.commit()
                return True
        except Exception as e:
            st.error(f"Error limpiando último flashcard: {e}")
            return False

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

def create_audio_component(text: str, auto_play: bool = False, times: int = 1, pause_ms: int = 1000, utterance_rate: float = 0.9) -> str:
    """Crear componente de audio que se reproduce varias veces con pausa entre repeticiones"""

    auto_play_script = "playRepeatedAudio();" if auto_play and times > 0 else ""

    return f"""
    <div style="text-align: center; margin: 20px 0;">
        <button onclick="playRepeatedAudio()" style="
            background: #e74c3c;
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 25px;
            font-size: 1.2em;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            transition: all 0.3s;">🔊 Reproducir Audio</button>
    </div>
    <script>
        function playRepeatedAudio() {{
            if (!window.speechSynthesis) return;

            let count = 0;
            const maxTimes = {times};
            const pauseBetween = {pause_ms};

            function speakOnce() {{
                window.speechSynthesis.cancel();
                const utterance = new SpeechSynthesisUtterance('{text}');
                utterance.lang = 'zh-CN';
                utterance.rate = {utterance_rate};
                utterance.pitch = 1.0;
                utterance.volume = 1.0;

                utterance.onend = () => {{
                    count++;
                    if (count < maxTimes) {{
                        setTimeout(speakOnce, pauseBetween);
                    }}
                }};

                window.speechSynthesis.speak(utterance);
            }}

            speakOnce();
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
            spanish = st.text_input("Traducción al Español:", key="add_spanish")
        
        with col2:
            # Obtener categorías existentes
            categories = db.get_categories()
            category_options = categories + ["➕ Nueva categoría"]
            
            category_choice = st.selectbox("Categoría:", category_options, key="add_category_choice")
            
            if category_choice == "➕ Nueva categoría":
                category = st.text_input("Nueva categoría:", key="add_new_category")
            else:
                category = category_choice
        
        # Nuevos campos en área completa
        explanation = st.text_area("Explicación (opcional):", key="add_explanation", 
                                 help="Contexto, uso común, notas culturales, etc.")
        literal_translation = st.text_input("Traducción Literal (opcional):", key="add_literal_translation",
                                          help="Traducción palabra por palabra")
        
        if st.button("✅ Agregar Palabra", key="add_word_btn"):
            if chinese and pinyin and spanish and category:
                if db.add_word(chinese, pinyin, spanish, category, explanation, literal_translation):
                    st.success("✅ Palabra agregada exitosamente")
                    st.rerun()
            else:
                st.error("❌ Por favor completa todos los campos obligatorios")
    
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
            
            # Crear opciones para el selectbox
            word_options = ["Seleccionar palabra..."]
            word_mapping = {}
            
            for idx, row in df.iterrows():
                option_text = f"{row['chinese']} ({row['pinyin']}) - {row['spanish']}"
                word_options.append(option_text)
                word_mapping[option_text] = row['id']
            
            # Seleccionar palabra para editar
            selected_option = st.selectbox(
                "Seleccionar palabra para editar:", 
                word_options,
                key="edit_select"
            )
            
            if selected_option and selected_option != "Seleccionar palabra...":
                word_id = word_mapping[selected_option]
                
                try:
                    selected_row = df[df['id'] == word_id].iloc[0]
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        edit_chinese = st.text_input("Chino:", value=selected_row['chinese'], key="edit_chinese")
                        edit_pinyin = st.text_input("Pinyin:", value=selected_row['pinyin'], key="edit_pinyin")
                        edit_spanish = st.text_input("Español:", value=selected_row['spanish'], key="edit_spanish")
                    
                    with col2:
                        edit_category = st.text_input("Categoría:", value=selected_row['category'], key="edit_category")
                        edit_literal_translation = st.text_input("Traducción Literal:", 
                                                               value=selected_row.get('literal_translation', ''), 
                                                               key="edit_literal_translation")
                    
                    # Campo de explicación en área completa
                    edit_explanation = st.text_area("Explicación:", 
                                                   value=selected_row.get('explanation', ''), 
                                                   key="edit_explanation")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("💾 Actualizar", key="update_btn"):
                            if edit_chinese and edit_pinyin and edit_spanish and edit_category:
                                if db.update_word(selected_row['id'], edit_chinese, edit_pinyin, 
                                                edit_spanish, edit_category, edit_explanation, edit_literal_translation):
                                    st.success("✅ Palabra actualizada")
                                    st.rerun()
                            else:
                                st.error("❌ Por favor completa todos los campos obligatorios")
                    
                    with col2:
                        if st.button("🗑️ Eliminar", key="delete_btn", type="secondary"):
                            st.warning(f"⚠️ ¿Estás seguro de eliminar '{selected_row['chinese']}'?")
                            col2a, col2b = st.columns(2)
                            with col2a:
                                if st.button("✅ Confirmar", key="confirm_delete"):
                                    if db.delete_word(selected_row['id']):
                                        st.success("✅ Palabra eliminada")
                                        st.rerun()
                            with col2b:
                                if st.button("❌ Cancelar", key="cancel_delete"):
                                    st.info("Eliminación cancelada")
                    
                except IndexError:
                    st.error("❌ Error al cargar la palabra seleccionada")
                    
        else:
            if filter_category == "Todas":
                st.info("📭 No hay palabras en la base de datos")
            else:
                st.info(f"📭 No hay palabras en la categoría '{filter_category}'")
            
            if st.button("➕ Agregar Primera Palabra", key="add_first_word"):
                st.info("💡 Ve a la pestaña 'Agregar Palabra' para comenzar")
    
    with tab3:
        st.markdown("### Importar desde CSV")
        
        st.info("El CSV debe contener las columnas obligatorias: chinese,pinyin,spanish,category")
        st.info("Columnas opcionales: explanation,literal_translation")
        
        # Ejemplo de formato actualizado
        st.markdown("**Ejemplo de formato CSV:**")
        example_csv = """chinese|pinyin|spanish|category|explanation|literal_translation
你好|nǐ hǎo|Hola|Saludos|Saludo común usado en cualquier momento|Tú bueno
再见|zài jiàn|Adiós|Saludos|Despedida formal|Otra vez ver"""
        st.code(example_csv)
        
        uploaded_file = st.file_uploader("Cargar archivo CSV", type=['csv'])
        
        if uploaded_file is not None:
            csv_data = uploaded_file.getvalue().decode('utf-8')
            st.markdown("**Vista previa:**")
            preview_df = pd.read_csv(io.StringIO(csv_data), sep='|')
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
        
        df = db.get_all_words()
        
        categories = ["Todas"] + db.get_categories()
        export_category = st.selectbox("Exportar categoría:", categories, key="export_category")
        
        if export_category != "Todas":
            df = df[df['category'] == export_category]
        
        st.metric("Total de palabras a exportar", len(df))
        
        csv = df.to_csv(index=False, sep='|')
        
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
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@500&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@100..900&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@200..900&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Source+Han+Sans+SC&display=swap" rel="stylesheet">
    <style>
        @font-face {
            font-family: KaiTi;
            src: url('https://munihuayucachi.servicios.gob.pe/eeefb172-d17a-4a1e-8276-5ea006fc7770/fonts/KaiTi.woff2') format('woff2');
            font-weight: normal;
            font-style: normal;
            font-display: swap;
        }
        @font-face {
            font-family: Libertine;
            src: url('https://munihuayucachi.servicios.gob.pe/eeefb172-d17a-4a1e-8276-5ea006fc7770/fonts/Libertine.woff2') format('woff2');
            font-weight: normal;
            font-style: normal;
            font-display: swap;
        }
        .stroke-chinese-word {
            font-family: var(--chinese-font), 'Noto Serif SC', serif !important;
            font-size: 2.8em !important;
        }
        .main-title {
            font-family: var(--chinese-font), 'Noto Serif SC', serif !important;
            font-size: 3em;
            text-align: center;
            color: #c0392b;
            margin-bottom: 30px;
        }
        .chinese-word {
            font-family: var(--chinese-font), 'Noto Serif SC', serif !important;
            font-size: 7em;
            text-align: center;
            color: #000000;
            background: #FFFFFF;
            padding: 50px;
            border-radius: 20px;
            margin: 30px 0;
            border: 4px solid #3498db;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            .review-indicator {
                position: absolute; top: 10px; right: 10px; 
                background: #e74c3c; color: white; padding: 5px 10px; 
                border-radius: 15px; font-size: 0.2em;
            }
            .pinyin {
                font-size: 0.3em;
                font-family: var(--chinese-font), sans-serif;
                font-weight: 500;
                p {
                    color: #34495e;
                    margin: 0;
                    align-items: center;
                    text-align: center;
                    font-size: 1.0em;
                    font-family: var(--chinese-font), sans-serif;
                }
            }

            .translation {
                font-size: 0.2em;
                font-family: 'Montserrat', sans-serif;
                p {
                    color: #34495e;
                    margin: 0;
                    align-items: center;
                    text-align: center;
                    font-size: 1.0em;
                    font-family: Libertine, sans-serif;
                }
            }
        }
        .literal-translation {
            background: #e8f4f8;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            font-family: 'Montserrat', sans-serif;
            color: #34495e;
            p {
                color: #34495e;
                margin: 0;
                align-items: center;
                text-align: center;
                font-size: 1.8em;
                font-family: Libertine, sans-serif;
            }
        }
        .explanation {
            background: #e8f4f8;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            font-family: 'Montserrat', sans-serif;
            color: #34495e;
            p {
                color: #34495e;
                margin: 0;
                align-items: center;
                text-align: center;
                font-size: 1.8em;
                font-family: Libertine, sans-serif;
            }
        }
        .review-indicator {
            border-right: 4px solid #e74c3c;
            padding-right: 10px;
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
            font-size: 1.0em;
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
        .listening-mode {
            text-align: center;
            margin: 20px 0;
            padding: 30px;
            background: #3498db;
            color: white;
            border-radius: 10px;
            font-size: 1.5em;
        }
        .text-analysis-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 15px;
            margin: 20px 0;
            color: white;
        }
        .input-text-display {
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 10px;
            margin: 15px 0;
            text-align: center;
            border: 2px solid rgba(255,255,255,0.2);
        }
        .chinese-input-text {
            font-size: 2.8em;
            font-family: var(--chinese-font), 'Noto Serif SC', serif !important;
            margin-bottom: 10px;
        }
        .pinyin-display {
            font-size: 1.3em;
            color: #ffd700;
            margin-bottom: 10px;
        }
        .character-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .character-card {
            background: white;
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.7; }
            100% { opacity: 1; }
        }
        @media (max-width: 768px) and (orientation: portrait) {
            .chinese-word {
                font-size: 4em;
                padding: 10px;
                background: #FFFFFF;
                .pinyin {
                    font-size: 0.3em;
                    font-family: Libertine, sans-serif;
                    font-weight: 500;
                }

                .translation {
                    font-size: 0.3em;
                    font-family: 'Montserrat', sans-serif;
                }
            }
            .pinyin-translation {
                font-size: 1.0em;
                padding: 20px;
            }
            .chinese-input-text {
                font-size: 6em;
                font-family: var(--chinese-font), 'Noto Serif SC', serif !important;
                margin-bottom: 10px;
            }
        }
        @media (max-height: 500px) and (orientation: landscape) and (max-width: 1024px) {
            .chinese-word {
                font-size: 3.8em; /* slightly larger */
                padding: 12px;
                background: #FFFFFF;
            }

            .chinese-word .pinyin {
                font-size: 0.35em;
                font-family: Libertine, sans-serif;
                font-weight: 500;
            }

            .chinese-word .translation {
                font-size: 0.25em;
                font-family: 'Montserrat', sans-serif;
            }

            .pinyin-translation {
                font-size: 1.2em;
                padding: 25px;
            }
            .chinese-input-text {
                font-size: 5.8em;
                font-family: var(--chinese-font), 'Noto Serif SC', serif !important;
                margin-bottom: 10px;
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
        wait_time = st.slider("⏱️ Tiempo de espera (segundos)", 1, 10, 6)
        
        # Configuración de repeticiones
        repeat_count = st.slider("⏱️ Repeticiones (veces)", 1, 3, 2)

        # Configuración de utterance.rate
        utterance_rate = st.slider("⏱️ Velocidad de lectura (0.7 - 1.0)", 0.7, 1.0, 1.0, 0.1)
  
        # Modo de estudio (cambiar a radio buttons)
        st.markdown("**📚 Modo de Estudio:**")
        study_mode = st.radio(
            "Selecciona el modo:",
            ["📚 Modo Aprendizaje", "🎴 Modo Flashcard", "✍️ Modo Escritura", "👂 Modo Escucha", "📝 Análisis de Texto"],
            index=0,  # Por defecto Modo Aprendizaje
            key="study_mode_radio"
        )

        # Extraer los valores booleanos para mantener compatibilidad con el código existente
        learning_mode = study_mode == "📚 Modo Aprendizaje"
        writing_mode = study_mode == "✍️ Modo Escritura"
        listening_mode = study_mode == "👂 Modo Escucha"
        flashcard_mode = study_mode == "🎴 Modo Flashcard"
        text_analysis_mode = study_mode == "📝 Análisis de Texto"

        # Avance automático
        if flashcard_mode or listening_mode:
            st.markdown("✅ 🔄 **Avance automático**")
            auto_advance = True
        else:
            if writing_mode or text_analysis_mode:
                st.markdown("❌ 🔄 **Avance automático**")
                auto_advance = False
            else:
                auto_advance = st.checkbox("🔄 Avance automático", False)

        st.markdown("**📚 Filtro de Palabras:**")
        word_filter = st.radio(
            "Selecciona qué palabras mostrar:",
            ["📚 Palabras normales", "🔄 Solo palabras para repasar", "📦 Solo palabras archivadas"],
            index=0,
            key="word_filter_radio"
        )

        # Selector de fuente
        st.markdown("**🖋️ Tipo de Letra:**")
        font_choice = st.radio(
            "Selecciona la fuente para caracteres chinos:",
            ["KaiTi (Caligráfico)", 
            "Noto Sans SC (Moderno)", 
            "Noto Serif SC (Clásico)", ],
            index=0,
            key="font_selector"
        )

        # Aplicar CSS dinámico según la selección
        if font_choice == "KaiTi (Caligráfico)":
            st.markdown("<style>:root { --chinese-font: KaiTi; }</style>", unsafe_allow_html=True)
        elif font_choice == "Noto Sans SC (Moderno)":
            st.markdown("<style>:root { --chinese-font: 'Noto Sans SC'; }</style>", unsafe_allow_html=True)
        elif font_choice == "Noto Serif SC (Clásico)":
            st.markdown("<style>:root { --chinese-font: 'Noto Serif SC'; }</style>", unsafe_allow_html=True)

        # Mostrar configuraciones solo si NO es modo análisis de texto
        if not text_analysis_mode:
            # Estadísticas
            st.markdown("---")
            st.markdown("### 📊 Estadísticas")
            st.metric("Palabras estudiadas", st.session_state.get('words_studied', 0))
            st.metric("Palabras para repasar", db.get_review_count(selected_category))
            st.metric("Palabras archivadas", db.get_archived_count(selected_category))

        else:
            # Para modo análisis de texto, mostrar información diferente
            st.markdown("---")
            st.markdown("### 📝 Análisis de Texto")
            st.info("En este modo puedes analizar cualquier texto en chino carácter por carácter")
        
        # Botón de cerrar sesión
        st.markdown("---")
        if st.button("🚪 Cerrar Sesión"):
            st.session_state.authenticated = False
            st.rerun()
    
    if text_analysis_mode:
        handle_text_analysis_mode(db, selected_category)
        return

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
    if 'word_history' not in st.session_state:
        st.session_state.word_history = []
    if 'history_index' not in st.session_state:
        st.session_state.history_index = -1
    if 'writing_mode' not in st.session_state:
        st.session_state.writing_mode = writing_mode
    if 'listening_mode' not in st.session_state:
        st.session_state.listening_mode = listening_mode
    if 'flashcard_mode' not in st.session_state:
        st.session_state.flashcard_mode = flashcard_mode
    if 'text_analysis_mode' not in st.session_state:
        st.session_state.text_analysis_mode = text_analysis_mode
    if 'random_order' not in st.session_state:
        st.session_state.random_order = False
    if 'current_word_index' not in st.session_state:
        st.session_state.current_word_index = 0
    if 'current_category_words' not in st.session_state:
        st.session_state.current_category_words = []
    if 'review_filter' not in st.session_state:
        st.session_state.review_filter = False
    if 'archived_filter' not in st.session_state:
        st.session_state.archived_filter = False
    if 'review_filter_state' not in st.session_state:
        st.session_state.review_filter_state = False
    if 'archived_filter_state' not in st.session_state:
        st.session_state.archived_filter_state = False

    # Extraer los valores booleanos
    review_filter = word_filter == "🔄 Solo palabras para repasar"
    archived_filter = word_filter == "📦 Solo palabras archivadas"

    # Mostrar estadísticas según el filtro seleccionado
    if st.session_state.review_filter_state:
        review_count = db.get_review_count(selected_category)
        if review_count > 0:
            st.info(f"📝 {review_count} palabra(s) marcada(s) para repasar en esta categoría")
    elif st.session_state.archived_filter:
        archived_count = db.get_archived_count(selected_category)
        if archived_count > 0:
            st.info(f"📦 {archived_count} palabra(s) archivada(s) en esta categoría")

    # Actualizar configuraciones
    st.session_state.wait_time = wait_time
    st.session_state.repeat_count = repeat_count
    st.session_state.utterance_rate = utterance_rate
    st.session_state.auto_advance = auto_advance
    st.session_state.learning_mode = learning_mode
    st.session_state.writing_mode = writing_mode
    st.session_state.listening_mode = listening_mode
    st.session_state.flashcard_mode = flashcard_mode

    # Cambio de categoría
    if selected_category != st.session_state.current_category:
        st.session_state.current_category = selected_category
        st.session_state.current_word = None
        st.session_state.phase = 0
        st.session_state.is_playing = False
        st.session_state.phase_start_time = None
        # Reiniciar el índice y cargar las palabras de la categoría
        st.session_state.current_word_index = 0
        st.session_state.current_category_words = db.get_words_by_category(selected_category)
    
    if (review_filter != st.session_state.review_filter_state or 
        archived_filter != st.session_state.archived_filter):
        
        # Actualizar estados
        st.session_state.review_filter_state = review_filter
        st.session_state.archived_filter = archived_filter
        
        # Forzar recarga de datos
        st.session_state.current_word = None
        st.session_state.phase = 0
        st.session_state.is_playing = False
        st.session_state.phase_start_time = None
        st.session_state.current_word_index = 0
        st.session_state.current_category_words = []
        
        # Limpiar último flashcard guardado cuando se cambia de filtro
        db.clear_last_flashcard()
        
        # Recargar inmediatamente
        st.rerun()
    
    # Título principal
    st.markdown('<h1 class="main-title">学习中文 🎴</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2em; color: #7f8c8d;">Flashcards para aprender vocabulario chino</p>', unsafe_allow_html=True)
    
    # Controles principales
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    # Checkbox para orden aleatorio o secuencial
    with col6:
        st.session_state.random_order = st.checkbox(
            "🔀 Orden aleatorio", 
            value=st.session_state.random_order,
            help="Mostrar palabras en orden aleatorio o secuencial"
        )
    
    with col1:
        if st.button("🎯 Nueva Palabra", key="new_word", use_container_width=True):
            if (st.session_state.current_word is None and 'session_started' not in st.session_state):
                last_flashcard = db.get_last_flashcard()
                if last_flashcard:
                    # Restaurar el último flashcard
                    word_data = last_flashcard['word_data']
                    saved_phase = last_flashcard['phase']
                    
                    # Guardar en historial
                    st.session_state.word_history.append(word_data)
                    st.session_state.history_index = len(st.session_state.word_history) - 1
                    
                    st.session_state.current_word = word_data['chinese']
                    st.session_state.current_data = word_data
                    
                    # Restaurar la fase guardada
                    if st.session_state.learning_mode:
                        st.session_state.phase = 3  # En modo aprendizaje, mostrar todo
                    else:
                        st.session_state.phase = saved_phase
                    
                    st.session_state.phase_start_time = time.time()
                    st.session_state.is_playing = True
                    st.session_state.session_started = True
                    
                    st.success(f"✅ Flashcard anterior restaurado: {word_data['chinese']}")
                    st.rerun()
            
            # Lógica para obtener nueva palabra según el modo seleccionado
            if st.session_state.random_order:
                # Modo aleatorio
                word_data = db.get_random_word(st.session_state.current_category, 
                                         review_only=st.session_state.review_filter_state, 
                                         archived_only=st.session_state.archived_filter)

            else:
                # Modo secuencial
                if not st.session_state.current_category_words:
                    # Cargar todas las palabras de la categoría si no están cargadas
                    st.session_state.current_category_words = db.get_words_by_category(
                        st.session_state.current_category, 
                        st.session_state.review_filter_state, 
                        st.session_state.archived_filter)
                    st.session_state.current_word_index = 0
                
                if st.session_state.current_word_index < len(st.session_state.current_category_words):
                    word_data = st.session_state.current_category_words[st.session_state.current_word_index]
                    st.session_state.current_word_index += 1
                else:
                    # Si llegamos al final, volvemos al principio
                    st.session_state.current_word_index = 0
                    if st.session_state.current_category_words:
                        word_data = st.session_state.current_category_words[st.session_state.current_word_index]
                        st.session_state.current_word_index += 1
                    else:
                        word_data = None
            
            if word_data:
                # Guardar en historial
                st.session_state.word_history.append(word_data)
                st.session_state.history_index = len(st.session_state.word_history) - 1
                
                st.session_state.current_word = word_data['chinese']
                st.session_state.current_data = word_data
                if st.session_state.learning_mode or st.session_state.writing_mode:
                    st.session_state.phase = 1
                    if st.session_state.phase_start_time is None:
                        st.session_state.phase_start_time = time.time()
                else:
                    st.session_state.phase = 1
                st.session_state.phase_start_time = time.time()
                st.session_state.is_playing = True
                st.session_state.session_started = True
                
                # Guardar el nuevo flashcard
                db.save_last_flashcard(word_data, st.session_state.phase)
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
        if st.button("⏮️ Anterior", key="prev_phase", use_container_width=True):
            # Verificar si hay historial y si no estamos en la primera palabra
            if st.session_state.word_history and st.session_state.history_index > 0:
                # Cancelar cualquier proceso automático en curso
                st.session_state.is_playing = False
                st.session_state.phase_start_time = None
                
                # Ir a la palabra anterior en el historial
                st.session_state.history_index -= 1
                word_data = st.session_state.word_history[st.session_state.history_index]
                
                st.session_state.current_word = word_data['chinese']
                st.session_state.current_data = word_data
                
                # Restaurar la fase original de la palabra
                if st.session_state.learning_mode or st.session_state.writing_mode:
                    # En modo aprendizaje, mostrar la palabra completa
                    st.session_state.phase = 3
                else:
                    # En modo flashcard, ir a la fase 1
                    st.session_state.phase = 1
                
                st.session_state.phase_start_time = time.time()
                st.session_state.is_playing = True
                
                db.save_last_flashcard(word_data, st.session_state.phase)
                st.rerun()
    
    with col4:
        if st.button("⏭️ Siguiente", key="next_phase", use_container_width=True):
            if st.session_state.current_word:
                # Cancelar cualquier proceso automático en curso
                st.session_state.is_playing = False
                st.session_state.phase_start_time = None
                
                if st.session_state.learning_mode or st.session_state.writing_mode:
                    # En modo aprendizaje/escritura, ir directo a nueva palabra
                    st.session_state.words_studied += 1
                    
                    # Usar la lógica de selección de palabras según el modo
                    if st.session_state.random_order:
                        word_data = db.get_random_word(st.session_state.current_category, 
                                         review_only=st.session_state.review_filter_state, 
                                         archived_only=st.session_state.archived_filter)
                        

                    else:
                        # Modo secuencial
                        if not st.session_state.current_category_words:
                            st.session_state.current_category_words = db.get_words_by_category(
                                st.session_state.current_category, 
                                st.session_state.review_filter_state, 
                                st.session_state.archived_filter)
                            st.session_state.current_word_index = 0
                        
                        if st.session_state.current_word_index < len(st.session_state.current_category_words):
                            word_data = st.session_state.current_category_words[st.session_state.current_word_index]
                            st.session_state.current_word_index += 1
                        else:
                            # Si llegamos al final, volvemos al principio
                            st.session_state.current_word_index = 0
                            if st.session_state.current_category_words:
                                word_data = st.session_state.current_category_words[st.session_state.current_word_index]
                                st.session_state.current_word_index += 1
                            else:
                                word_data = None
                    
                    if word_data:
                        # Guardar la nueva palabra en el historial
                        st.session_state.word_history.append(word_data)
                        st.session_state.history_index = len(st.session_state.word_history) - 1
                        
                        st.session_state.current_word = word_data['chinese']
                        st.session_state.current_data = word_data
                        st.session_state.phase = 1
                        st.session_state.phase_start_time = time.time()
                        st.session_state.is_playing = True
                        
                        # Guardar el nuevo flashcard
                        db.save_last_flashcard(word_data, 1)
                        
                elif st.session_state.listening_mode:
                    # Lógica para modo escucha (existente)
                    # ... (código existente para el modo escucha)
                    pass
                    
                else:
                    # MODO FLASHCARD ESTÁNDAR
                    if st.session_state.phase < 3:
                        # Avanzar a la siguiente fase
                        st.session_state.phase += 1
                        st.session_state.phase_start_time = time.time()
                        st.session_state.is_playing = True
                        
                        # Guardar el estado actual
                        if st.session_state.current_data:
                            db.save_last_flashcard(st.session_state.current_data, st.session_state.phase)
                            
                    else:
                        # Fase 3 completada - nueva palabra
                        st.session_state.words_studied += 1
                        
                        # Usar la lógica de selección de palabras según el modo
                        if st.session_state.random_order:
                            word_data = db.get_random_word(st.session_state.current_category, 
                                         review_only=st.session_state.review_filter_state, 
                                         archived_only=st.session_state.archived_filter)

                        else:
                            # Modo secuencial
                            if not st.session_state.current_category_words:
                                st.session_state.current_category_words = db.get_words_by_category(st.session_state.current_category, review_filter, archived_filter)
                                st.session_state.current_word_index = 0
                            
                            if st.session_state.current_word_index < len(st.session_state.current_category_words):
                                word_data = st.session_state.current_category_words[st.session_state.current_word_index]
                                st.session_state.current_word_index += 1
                            else:
                                # Si llegamos al final, volvemos al principio
                                st.session_state.current_word_index = 0
                                if st.session_state.current_category_words:
                                    word_data = st.session_state.current_category_words[st.session_state.current_word_index]
                                    st.session_state.current_word_index += 1
                                else:
                                    word_data = None
                        
                        if word_data:
                            # Guardar la nueva palabra en el historial
                            st.session_state.word_history.append(word_data)
                            st.session_state.history_index = len(st.session_state.word_history) - 1
                            
                            st.session_state.current_word = word_data['chinese']
                            st.session_state.current_data = word_data
                            st.session_state.phase = 1
                            st.session_state.phase_start_time = time.time()
                            st.session_state.is_playing = True
                            
                            # Guardar el nuevo flashcard
                            db.save_last_flashcard(word_data, 1)
                
                st.rerun()

    with col5:
        if st.button("🔄 Reiniciar", key="reset", use_container_width=True):
            st.session_state.phase = 0
            st.session_state.is_playing = False
            st.session_state.current_word = None
            st.session_state.phase_start_time = None
            st.session_state.words_studied = 0
            st.rerun()

    with col6:
        # Mover el checkbox de orden aleatorio aquí si hay espacio, o crear nueva fila
        if st.session_state.current_word and st.session_state.current_data:
            if st.session_state.archived_filter:
                # En modo archivadas, mostrar botón de desarchivar
                if st.button("📤 Desarchivar", key="unarchive_word", use_container_width=True):
                    new_state = db.toggle_word_archived(
                        st.session_state.current_data['chinese'],
                        st.session_state.current_data['pinyin']
                    )
                    st.success("📤 Palabra desarchivada")
                    st.session_state.current_category_words = []
                    time.sleep(0.5)
                    st.rerun()
            else:
                # En otros modos, mostrar botones de repaso y archivar
                col6a, col6b = st.columns(2)
                
                with col6a:
                    # Botón de repaso
                    is_marked = db.get_word_review_status(
                        st.session_state.current_data['chinese'], 
                        st.session_state.current_data['pinyin']
                    )
                    button_text = "✅ Quitar Repaso" if is_marked else "🔄 Marcar Repaso"
                    
                    if st.button(button_text, key="toggle_review", use_container_width=True):
                        new_state = db.toggle_word_review(
                            st.session_state.current_data['chinese'],
                            st.session_state.current_data['pinyin']
                        )
                        
                        if new_state:
                            st.success("✅ Palabra marcada para repasar")
                        else:
                            st.success("❌ Palabra quitada de repaso")
                        
                        time.sleep(0.5)
                        st.rerun()
                
                with col6b:
                    # Botón de archivar
                    if st.button("📦 Archivar", key="archive_word", use_container_width=True):
                        new_state = db.toggle_word_archived(
                            st.session_state.current_data['chinese'],
                            st.session_state.current_data['pinyin']
                        )
                        st.success("📦 Palabra archivada")
                        time.sleep(0.5)
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
        if st.session_state.current_data:
            is_marked = db.get_word_review_status(
                st.session_state.current_data['chinese'], 
                st.session_state.current_data['pinyin']
            )
            
            review_indicator = """
            <div style="position: absolute; top: 10px; right: 10px; 
                        background: #e74c3c; color: white; padding: 5px 10px; 
                        border-radius: 15px; font-size: 0.3em;">
                🔄 Para Repasar
            </div>
            """ if is_marked else ""
        
        if st.session_state.learning_mode or st.session_state.writing_mode:
            # LEARNING MODE o WRITING MODE: Show everything at once
            if st.session_state.writing_mode:
                st.markdown("""
                <div class="phase-indicator phase-1">
                    ✍️ Modo Escritura: Estudia la palabra y practica los trazos
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="phase-indicator phase-1">
                    📚 Modo Aprendizaje: Estudia la palabra completa
                </div>
                """, unsafe_allow_html=True)
                    
            # Show Chinese word
            if st.session_state.writing_mode:
                # Modo escritura: integrar stroke order viewer
                if is_marked:
                    html_content = f"""
                    <div class="chinese-word" style="position: relative;">
                        <div class="review-indicator">
                            🔄
                        </div>
                        <div class="pinyin">
                            {st.session_state.current_data['pinyin']}
                        </div>
                        {st.session_state.current_word}
                        <div class="translation">
                            {st.session_state.current_data['spanish']}
                        </div>
                    </div>
                    """
                else:
                    html_content = f"""
                    <div class="chinese-word" style="position: relative;">
                        <div class="pinyin">
                            {st.session_state.current_data['pinyin']}
                        </div>
                        {st.session_state.current_word}
                        <div class="translation">
                            {st.session_state.current_data['spanish']}
                        </div>
                    </div>
                    """
                
                st.markdown(html_content, unsafe_allow_html=True)
                # Agregar visualización de stroke order
                with st.container():
                    st.markdown("### ✍️ Orden de Trazos")
                    chinese_chars = [char for char in st.session_state.current_word if '\u4e00' <= char <= '\u9fff']
                    
                    if chinese_chars:
                        # Crear columnas para cada carácter
                        cols = st.columns(len(chinese_chars))
                        
                        for i, character in enumerate(chinese_chars):
                            with cols[i]:
                                with st.spinner(f'Cargando trazos para {character}...'):
                                    def fetch_character_data(character):
                                        try:
                                            encoded_char = quote(character)
                                            url = f"http://www.strokeorder.info/mandarin.php?q={encoded_char}"
                                            headers = {
                                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                                            }
                                            response = requests.get(url, headers=headers, timeout=10)
                                            response.raise_for_status()
                                            html = response.text
                                            
                                            # Extraer pinyin
                                            pinyin_match = re.search(r'Pinyin & Definition:.*?<[^>]*>([^<]+)', html, re.DOTALL)
                                            pinyin = pinyin_match.group(1).strip() if pinyin_match else "N/A"
                                            
                                            # Extraer definición en inglés
                                            definition_match = re.search(r'Pinyin & Definition:.*?<[^>]*>[^<]+.*?<[^>]*>([^<]+)', html, re.DOTALL)
                                            definition = definition_match.group(1).strip() if definition_match else "N/A"
        
                                            gif_match = re.search(r'src="([^"]*\.gif[^"]*)"', html)
                                            gif_url = None
                                            
                                            if gif_match:
                                                gif_url = gif_match.group(1)
                                                if gif_url.startswith('/'):
                                                    gif_url = 'http://www.strokeorder.info' + gif_url
                                                elif not gif_url.startswith('http'):
                                                    gif_url = 'http://www.strokeorder.info/' + gif_url
                                            
                                            # Extraer número de trazos
                                            strokes_match = re.search(r'Strokes:.*?(\d+)', html, re.DOTALL)
                                            strokes = strokes_match.group(1) if strokes_match else "N/A"
                                            
                                            # Extraer radical
                                            radical_match = re.search(r'Radical:.*?<[^>]*>([^<]+)', html, re.DOTALL)
                                            radical = radical_match.group(1).strip() if radical_match else "N/A"
                                            return {'gif_url': gif_url, 'pinyin': pinyin, 'definition': definition, 'strokes': strokes, 'radical': radical, 'success': True,}
                                        except Exception as e:
                                            return {'success': False, 'error': str(e)}
                                    
                                    def download_gif(gif_url):
                                        try:
                                            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                                            response = requests.get(gif_url, headers=headers, timeout=10)
                                            response.raise_for_status()
                                            return base64.b64encode(response.content).decode()
                                        except:
                                            return None
                                    
                                    character_data = fetch_character_data(character)
                                    
                                    if character_data['success'] and character_data['gif_url']:
                                        st.markdown(f"<h3 class='stroke-chinese-word' style='text-align: center; color: #1f77b4;'>{character} {character_data['pinyin']} {character_data['definition']}</h3>", unsafe_allow_html=True)
                                        gif_base64 = download_gif(character_data['gif_url'])
                                        if gif_base64:
                                            st.markdown(
                                                f'<div style="text-align: center;"><img src="data:image/gif;base64,{gif_base64}" style="max-width: 100%; border: 2px solid #e0e0e0; border-radius: 10px;"></div>',
                                                unsafe_allow_html=True
                                            )
                                        else:
                                            st.warning(f"⚠️ No se pudo cargar la animación para {character}")
                                    else:
                                        st.warning(f"⚠️ Orden de trazos no disponible para {character}")
            else:
                # Modo aprendizaje normal sin escritura
                st.markdown(f"""
                <div class="chinese-word">
                    <div class="pinyin">
                        {st.session_state.current_data['pinyin']}
                    </div>
                    {st.session_state.current_word}
                    <div class="translation">
                        {st.session_state.current_data['spanish']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Mostrar información adicional si existe
            if st.session_state.current_data.get('literal_translation') or st.session_state.current_data.get('explanation'):
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.session_state.current_data.get('literal_translation'):
                        st.markdown(f"""
                        <div class="literal-translation">
                            <h5>🔤 Traducción Literal:</h5>
                            <p>{st.session_state.current_data['literal_translation']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                with col2:
                    if st.session_state.current_data.get('explanation'):
                        st.markdown(f"""
                        <div class="explanation">
                            <h5>💡 Explicación:</h5>
                            <p>{st.session_state.current_data['explanation']}</p>
                        </div>
                        """, unsafe_allow_html=True)

            # Auto-play audio
            audio_html = create_audio_component(st.session_state.current_word, auto_play=True, times=st.session_state.repeat_count, utterance_rate=st.session_state.utterance_rate)
            st.components.v1.html(audio_html, height=100)
            
            if (st.session_state.is_playing and 
                st.session_state.auto_advance and 
                st.session_state.phase_start_time is not None):
                
                current_time = time.time()
                elapsed_time = current_time - st.session_state.phase_start_time
                remaining_time = st.session_state.wait_time - elapsed_time
                
                if remaining_time > 0:
                    # Mostrar countdown
                    if st.session_state.learning_mode or st.session_state.writing_mode:
                        countdown_text = "Nueva palabra"
                    else:
                        countdown_text = 'Siguiente fase' if st.session_state.phase < 3 else 'Nueva palabra'
                        
                    st.markdown(f"""
                    <div class="countdown-timer">
                        ⏳ {countdown_text} en: {remaining_time:.1f}s
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Refresh cada 0.1 segundos
                    if current_time - st.session_state.last_update >= 0.1:
                        st.session_state.last_update = current_time
                        time.sleep(0.1)
                        st.rerun()
                        
                else:
                    # Tiempo terminado - avanzar según el modo
                    if st.session_state.learning_mode or st.session_state.writing_mode:
                        # En modo aprendizaje/escritura, siempre ir a nueva palabra
                        st.session_state.words_studied += 1
                        
                        # Usar la lógica de selección de palabras según el modo
                        if st.session_state.random_order:
                            word_data = db.get_random_word(st.session_state.current_category, 
                                         review_only=st.session_state.review_filter_state, 
                                         archived_only=st.session_state.archived_filter)

                        else:
                            # Modo secuencial
                            if not st.session_state.current_category_words:
                                st.session_state.current_category_words = db.get_words_by_category(st.session_state.current_category, review_filter, archived_filter)
                                st.session_state.current_word_index = 0
                            
                            if st.session_state.current_word_index < len(st.session_state.current_category_words):
                                word_data = st.session_state.current_category_words[st.session_state.current_word_index]
                                st.session_state.current_word_index += 1
                            else:
                                # Si llegamos al final, volvemos al principio
                                st.session_state.current_word_index = 0
                                if st.session_state.current_category_words:
                                    word_data = st.session_state.current_category_words[st.session_state.current_word_index]
                                    st.session_state.current_word_index += 1
                                else:
                                    word_data = None
                        
                        if word_data:
                            # Guardar en historial
                            st.session_state.word_history.append(word_data)
                            st.session_state.history_index = len(st.session_state.word_history) - 1
                            
                            st.session_state.current_word = word_data['chinese']
                            st.session_state.current_data = word_data
                            st.session_state.phase = 1  # Reiniciar a fase 1 para el próximo ciclo
                            st.session_state.phase_start_time = time.time()
                            
                            # Guardar el nuevo flashcard
                            db.save_last_flashcard(word_data, 1)
                    else:
                        # Modo flashcard estándar
                        if st.session_state.phase < 3:
                            st.session_state.phase += 1
                            st.session_state.phase_start_time = time.time()
                            
                            # Guardar el estado actual
                            if st.session_state.current_data:
                                db.save_last_flashcard(st.session_state.current_data, st.session_state.phase)
                        else:
                            # Completar palabra y pasar a la siguiente
                            st.session_state.words_studied += 1
                            
                            # Usar la lógica de selección de palabras según el modo
                            if st.session_state.random_order:
                                word_data = db.get_random_word(st.session_state.current_category, 
                                         review_only=st.session_state.review_filter_state, 
                                         archived_only=st.session_state.archived_filter)

                            else:
                                # Modo secuencial (código existente)
                                if not st.session_state.current_category_words:
                                    st.session_state.current_category_words = db.get_words_by_category(st.session_state.current_category, review_filter, archived_filter)
                                    st.session_state.current_word_index = 0
                                
                                if st.session_state.current_word_index < len(st.session_state.current_category_words):
                                    word_data = st.session_state.current_category_words[st.session_state.current_word_index]
                                    st.session_state.current_word_index += 1
                                else:
                                    st.session_state.current_word_index = 0
                                    if st.session_state.current_category_words:
                                        word_data = st.session_state.current_category_words[st.session_state.current_word_index]
                                        st.session_state.current_word_index += 1
                                    else:
                                        word_data = None
                            
                            if word_data:
                                # Guardar en historial
                                st.session_state.word_history.append(word_data)
                                st.session_state.history_index = len(st.session_state.word_history) - 1
                                
                                st.session_state.current_word = word_data['chinese']
                                st.session_state.current_data = word_data
                                st.session_state.phase = 1
                                st.session_state.phase_start_time = time.time()
                                
                                # Guardar el nuevo flashcard
                                db.save_last_flashcard(word_data, 1)
                    
                    st.rerun()
        
        elif st.session_state.listening_mode:
            # LISTENING MODE: Special flow for listening practice
            if st.session_state.phase == 1:
                # Phase 1: Just play audio with instructions
                st.markdown("""
                <div class="phase-indicator phase-1">
                    👂 Modo Escucha: Escucha atentamente la pronunciación
                </div>
                <div class="listening-mode">
                    <h2>👂 Escucha la pronunciación</h2>
                    <p>Presta atención al sonido y trata de identificar la palabra</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Auto-play audio
                audio_html = create_audio_component(st.session_state.current_word, auto_play=True, times=st.session_state.repeat_count, utterance_rate=st.session_state.utterance_rate)
                st.components.v1.html(audio_html, height=100)
                
                # Auto-advance after delay
                if st.session_state.is_playing and st.session_state.auto_advance:
                    current_time = time.time()
                    elapsed_time = current_time - st.session_state.phase_start_time
                    remaining_time = st.session_state.wait_time * 1.5 - elapsed_time  # Give more time for listening
                    
                    if remaining_time > 0:
                        st.markdown(f"""
                        <div class="countdown-timer">
                            ⏳ Mostrando palabra en: {remaining_time:.1f}s
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if current_time - st.session_state.last_update >= 0.1:
                            st.session_state.last_update = current_time
                            time.sleep(0.1)
                            st.rerun()
                    else:
                        st.session_state.phase = 2
                        st.session_state.phase_start_time = time.time()
                        st.rerun()
                        
            elif st.session_state.phase == 2:
                # Phase 2: Show the full flashcard
                st.markdown("""
                <div class="phase-indicator phase-2">
                    👂 Modo Escucha: Aquí está la palabra completa
                </div>
                """, unsafe_allow_html=True)
                
                # Show full flashcard
                st.markdown(f"""
                <div class="chinese-word">
                    <div class="pinyin">
                        {st.session_state.current_data['pinyin']}
                    </div>
                    {st.session_state.current_word}
                    <div class="translation">
                        {st.session_state.current_data['spanish']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Show audio button
                audio_html = create_audio_component(st.session_state.current_word, auto_play=True, times=st.session_state.repeat_count, utterance_rate=st.session_state.utterance_rate)
                st.components.v1.html(audio_html, height=100)
                
                # Auto-advance to next word
                if st.session_state.is_playing and st.session_state.auto_advance:
                    current_time = time.time()
                    elapsed_time = current_time - st.session_state.phase_start_time
                    remaining_time = st.session_state.wait_time - elapsed_time
                    
                    if remaining_time > 0:
                        st.markdown(f"""
                        <div class="countdown-timer">
                            ⏳ Nueva palabra en: {remaining_time:.1f}s
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if current_time - st.session_state.last_update >= 0.1:
                            st.session_state.last_update = current_time
                            time.sleep(0.1)
                            st.rerun()
                    else:
                        # Move to next word
                        st.session_state.words_studied += 1
                        word_data = db.get_random_word(st.session_state.current_category, 
                                         review_only=st.session_state.review_filter_state, 
                                         archived_only=st.session_state.archived_filter)

                        if word_data:
                            st.session_state.word_history.append(word_data)
                            st.session_state.history_index = len(st.session_state.word_history) - 1
                            st.session_state.current_word = word_data['chinese']
                            st.session_state.current_data = word_data
                            st.session_state.phase = 1  # Back to listening phase
                            st.session_state.phase_start_time = time.time()
                            st.rerun()
        else:
            # STANDARD FLASHCARD MODE - COPIA EXACTA DEL DISEÑO DE MODO APRENDIZAJE
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
            
            # Verificar si la palabra está marcada para repaso
            is_marked = False
            if st.session_state.current_data:
                is_marked = db.get_word_review_status(
                    st.session_state.current_data['chinese'], 
                    st.session_state.current_data['pinyin']
                )
            
            # MOSTRAR CONTENIDO SEGÚN LA FASE - USANDO LA MISMA ESTRUCTURA QUE MODO APRENDIZAJE
            if st.session_state.phase == 1:
                # Fase 1: Solo palabra china (estructura simplificada)
                st.markdown(f"""
                <div class="chinese-word">
                    {st.session_state.current_word}
                </div>
                """, unsafe_allow_html=True)
                
            elif st.session_state.phase >= 2:
                # Fase 2 y 3: Estructura EXACTA del modo aprendizaje
                if is_marked:
                    # Con indicador de repaso
                    st.markdown(f"""
                    <div class="chinese-word review-indicator" style="position: relative;">
                        <div class="review-indicator">
                            🔄 
                        </div>
                        <div class="pinyin">
                            {st.session_state.current_data['pinyin']}
                        </div>
                        {st.session_state.current_word}
                        <div class="translation">
                            {st.session_state.current_data['spanish']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Sin indicador de repaso - ESTRUCTURA EXACTA DEL MODO APRENDIZAJE
                    st.markdown(f"""
                    <div class="chinese-word">
                        <div class="pinyin">
                            {st.session_state.current_data['pinyin']}
                        </div>
                        {st.session_state.current_word}
                        <div class="translation">
                            {st.session_state.current_data['spanish']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Audio según la fase
            if st.session_state.phase >= 3:
                # Fase 3: Audio automático
                audio_html = create_audio_component(st.session_state.current_word, auto_play=True, times=st.session_state.repeat_count, utterance_rate=st.session_state.utterance_rate)
                st.components.v1.html(audio_html, height=100)
            elif st.session_state.phase >= 2:
                # Fase 2: Botón de audio manual
                audio_html = create_audio_component(st.session_state.current_word, auto_play=False, times=st.session_state.repeat_count, utterance_rate=st.session_state.utterance_rate)
                st.components.v1.html(audio_html, height=100)
            
            # Lógica de avance automático (mantengo la existente sin cambios)
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
                        
                        # Guardar el estado actual
                        if st.session_state.current_data:
                            db.save_last_flashcard(st.session_state.current_data, st.session_state.phase)
                            
                    else:
                        # Completar palabra y pasar a la siguiente
                        st.session_state.words_studied += 1
                        word_data = db.get_random_word(st.session_state.current_category)
                        if word_data:
                            # Guardar la nueva palabra en el historial
                            st.session_state.word_history.append(word_data)
                            st.session_state.history_index = len(st.session_state.word_history) - 1
                            
                            st.session_state.current_word = word_data['chinese']
                            st.session_state.current_data = word_data
                            st.session_state.phase = 1
                            st.session_state.phase_start_time = time.time()
                            
                            # Guardar el nuevo flashcard
                            db.save_last_flashcard(word_data, 1)
                    
                    st.rerun()


def handle_text_analysis_mode(db: VocabularyDB, selected_category: str):
    """Función para manejar el modo análisis de texto"""
    st.markdown('<h2>📝 Análisis de Texto Chino</h2>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2em; color: #7f8c8d;">Analiza cualquier texto chino carácter por carácter o los caracteres únicos de la categoría actual</p>', unsafe_allow_html=True)
    
    # Inicializar estado para modo análisis
    if 'analyzed_text' not in st.session_state:
        st.session_state.analyzed_text = ""
    if 'analysis_result' not in st.session_state:
        st.session_state.analysis_result = None
    
    # Input de texto manual
    col1, col2 = st.columns([4, 1])
    
    with col1:
        input_text = st.text_input(
            "🖊️ Ingresa el texto en chino que quieres analizar:",
            value=st.session_state.analyzed_text,
            placeholder="例如: 他是我的汉语老师",
            key="chinese_text_input"
        )
    
    with col2:
        analyze_button = st.button("🔍 Analizar Texto Manual", key="analyze_text", use_container_width=True)
    
    # Botón para analizar categoría actual
    analyze_category_button = st.button("📚 Analizar Caracteres Únicos de la Categoría Actual", key="analyze_category", use_container_width=True)
    
    # Procesar análisis manual
    if analyze_button and input_text.strip():
        st.session_state.analyzed_text = input_text.strip()
        chinese_count = len([c for c in input_text.strip() if '\u4e00' <= c <= '\u9fff'])
        
        with st.spinner(f"🔄 Analizando {chinese_count} caracteres chinos..."):
            progress_bar = st.progress(0)
            st.session_state.analysis_result = analyze_chinese_text(input_text.strip())
            progress_bar.progress(100)
        st.rerun()
    
    # Procesar análisis de categoría
    if analyze_category_button:
        # Obtener palabras de la categoría actual
        words = db.get_words_by_category(selected_category, review_only=False, archived_only=False)
        
        # Extraer caracteres chinos únicos
        unique_chars = set()
        for word in words:
            for char in word['chinese']:
                if '\u4e00' <= char <= '\u9fff':
                    unique_chars.add(char)
        
        if unique_chars:
            # Convertir a string ordenado
            category_text = ''.join(sorted(unique_chars))
            chinese_count = len(unique_chars)
            
            with st.spinner(f"🔄 Analizando {chinese_count} caracteres únicos de la categoría '{selected_category}'..."):
                progress_bar = st.progress(0)
                st.session_state.analysis_result = analyze_chinese_text(category_text)
                progress_bar.progress(100)
            st.rerun()
        else:
            st.warning(f"⚠️ No hay caracteres chinos en la categoría '{selected_category}'")
    
    # Mostrar resultados
    if st.session_state.analysis_result:
        display_text_analysis(st.session_state.analysis_result)

def get_pinyin_for_text(text):
    """Obtener pinyin para un texto completo usando pypinyin"""
    try:
        # Intentar usar pypinyin si está disponible
        import pypinyin
        pinyin_list = pypinyin.pinyin(text, style=pypinyin.TONE)
        return ' '.join([item[0] for item in pinyin_list])
    except ImportError:
        # Fallback: método alternativo usando web scraping
        try:
            from urllib.parse import quote
            import requests
            import re
            
            encoded_text = quote(text)
            url = f"https://www.chinese-tools.com/tools/converter-pinyin.html"
            
            # Este es un ejemplo, necesitarías implementar el scraping específico
            # Por ahora retornamos un placeholder
            return f"[Pinyin para: {text}]"
        except:
            return f"[Pinyin no disponible para: {text}]"


def analyze_chinese_text(text):
    """Analizar texto chino con procesamiento optimizado"""
    chinese_chars = [char for char in text if '\u4e00' <= char <= '\u9fff']
    
    # Obtener pinyin del texto completo
    full_pinyin = get_pinyin_for_text(text)
    
    analysis_result = {
        'original_text': text,
        'full_pinyin': full_pinyin,
        'characters': [],
        'non_chinese_chars': [char for char in text if not ('\u4e00' <= char <= '\u9fff')]
    }
    
    # Procesar caracteres únicos para evitar duplicados
    unique_chars = list(set(chinese_chars))
    
    # Usar threading para acelerar las requests
    import concurrent.futures
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_char = {executor.submit(fetch_character_data, char): char for char in unique_chars}
        char_data_cache = {}
        
        for future in concurrent.futures.as_completed(future_to_char):
            char = future_to_char[future]
            try:
                data = future.result()
                char_data_cache[char] = data
            except Exception as exc:
                char_data_cache[char] = {'success': False, 'error': str(exc)}
    
    # Construir resultado final manteniendo el orden original
    for character in chinese_chars:
        analysis_result['characters'].append({
            'character': character,
            'data': char_data_cache[character]
        })
    
    return analysis_result


def fetch_character_data(character):
    """Obtener datos de un carácter chino (misma función que ya tienes)"""
    try:
        from urllib.parse import quote
        import requests
        import re
        import base64
        
        encoded_char = quote(character)
        url = f"http://www.strokeorder.info/mandarin.php?q={encoded_char}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        html = response.text
        
        # Extraer información
        pinyin_match = re.search(r'Pinyin & Definition:.*?<[^>]*>([^<]+)', html, re.DOTALL)
        pinyin = pinyin_match.group(1).strip() if pinyin_match else "N/A"
        
        definition_match = re.search(r'Pinyin & Definition:.*?<[^>]*>[^<]+.*?<[^>]*>([^<]+)', html, re.DOTALL)
        definition = definition_match.group(1).strip() if definition_match else "N/A"

        gif_match = re.search(r'src="([^"]*\.gif[^"]*)"', html)
        gif_url = None
        
        if gif_match:
            gif_url = gif_match.group(1)
            if gif_url.startswith('/'):
                gif_url = 'http://www.strokeorder.info' + gif_url
            elif not gif_url.startswith('http'):
                gif_url = 'http://www.strokeorder.info/' + gif_url
        
        strokes_match = re.search(r'Strokes:.*?(\d+)', html, re.DOTALL)
        strokes = strokes_match.group(1) if strokes_match else "N/A"
        
        radical_match = re.search(r'Radical:.*?<[^>]*>([^<]+)', html, re.DOTALL)
        radical = radical_match.group(1).strip() if radical_match else "N/A"
        
        # Descargar GIF
        gif_base64 = None
        if gif_url:
            try:
                gif_response = requests.get(gif_url, headers=headers, timeout=10)
                gif_response.raise_for_status()
                gif_base64 = base64.b64encode(gif_response.content).decode()
            except:
                pass
        
        return {
            'gif_url': gif_url,
            'gif_base64': gif_base64,
            'pinyin': pinyin,
            'definition': definition,
            'strokes': strokes,
            'radical': radical,
            'success': True
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def display_text_analysis(analysis_result):
    """Mostrar los resultados del análisis de texto"""
    
    # Mostrar el texto original y su pinyin
    st.markdown(f"""
    <div class="text-analysis-container">
        <h2>📝 Análisis Completo</h2>
        <div class="input-text-display">
            <div class="chinese-input-text">{analysis_result['original_text']}</div>
            <div class="pinyin-display">🔤 {analysis_result['full_pinyin']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Información general
    total_chars = len(analysis_result['characters'])
    if total_chars > 0:
        st.markdown(f"""
        <div style="text-align: center; margin: 20px 0;">
            <h3>📊 Información del Análisis</h3>
            <p><strong>Caracteres analizados:</strong> {total_chars}</p>
            <p><strong>Caracteres no chinos:</strong> {len(analysis_result['non_chinese_chars'])}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Mostrar cada carácter usando columnas como en modo escritura
    if analysis_result['characters']:
        st.markdown("### ✍️ Análisis de Caracteres y Orden de Trazos")
        
        # Crear columnas para mostrar caracteres (máximo 3 por fila)
        chars_per_row = 4
        for i in range(0, len(analysis_result['characters']), chars_per_row):
            chunk = analysis_result['characters'][i:i + chars_per_row]
            cols = st.columns(len(chunk))
            
            for j, char_info in enumerate(chunk):
                character = char_info['character']
                data = char_info['data']
                
                with cols[j]:
                    if data['success'] and data['gif_base64']:
                        st.markdown(f"<h3 class='stroke-chinese-word' style='text-align: center; color: #1f77b4;'>{character} {data['pinyin']} {data['definition']}</h3>", unsafe_allow_html=True)
                        st.markdown(
                            f'<div style="text-align: center;"><img src="data:image/gif;base64,{data["gif_base64"]}" style="max-width: 100%; border: 2px solid #e0e0e0; border-radius: 10px;"></div>',
                            unsafe_allow_html=True
                        )
                    else:
                        st.warning(f"⚠️ Orden de trazos no disponible para {character}")

if __name__ == "__main__":
    main()
