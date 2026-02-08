import sqlite3


class UserDatabase:
    def __init__(self, db_path="users.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')

        # Таблица гитарных строев
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS guitar_tunings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                tuning_name TEXT NOT NULL,
                string1 TEXT NOT NULL,
                string2 TEXT NOT NULL,
                string3 TEXT NOT NULL,
                string4 TEXT NOT NULL,
                string5 TEXT NOT NULL,
                string6 TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(user_id, tuning_name)
            )
        ''')

        conn.commit()
        conn.close()

    def register_user(self, username, password):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Просто сохраняем пароль как есть (без хеширования)
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password)
            )

            user_id = cursor.lastrowid

            default_tunings = [
                ("Стандартный", "E2", "A2", "D3", "G3", "B3", "E4"),
                ("Drop D", "D2", "A2", "D3", "G3", "B3", "E4"),
                ("Open G", "D2", "G2", "D3", "G3", "B3", "D4"),
                ("Полутон ниже", "D#2", "G#2", "C#3", "F#3", "A#3", "D#4"),
            ]

            for tuning_name, s1, s2, s3, s4, s5, s6 in default_tunings:
                cursor.execute(
                    """INSERT INTO guitar_tunings 
                    (user_id, tuning_name, string1, string2, string3, string4, string5, string6) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (user_id, tuning_name, s1, s2, s3, s4, s5, s6)
                )

            conn.commit()
            conn.close()
            return True, "Регистрация успешна!"

        except sqlite3.IntegrityError:
            return False, "Пользователь с таким именем уже существует!"
        except Exception as e:
            return False, f"Ошибка регистрации: {str(e)}"

    def login_user(self, username, password):
        """Авторизация пользователя"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Простая проверка пароля
            cursor.execute(
                "SELECT id, username FROM users WHERE username = ? AND password = ?",
                (username, password)
            )

            user = cursor.fetchone()
            conn.close()

            if user:
                return True, "Успешный вход!", user[0], user[1]
            else:
                return False, "Неверное имя пользователя или пароль!", None, None

        except Exception as e:
            return False, f"Ошибка авторизации: {str(e)}", None, None

    def get_user_tunings(self, user_id):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """SELECT tuning_name, string1, string2, string3, string4, string5, string6 
                FROM guitar_tunings WHERE user_id = ?""",
                (user_id,)
            )

            tunings = cursor.fetchall()
            conn.close()

            # Преобразуем в удобный формат
            result = []
            for name, s1, s2, s3, s4, s5, s6 in tunings:
                result.append({
                    'name': name,
                    'strings': [s1, s2, s3, s4, s5, s6]
                })

            return result

        except Exception as e:
            print(f"Ошибка получения строев: {e}")
            return []

    def save_tuning(self, user_id, tuning_name, strings):
        """Сохранить новый строй"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            s1, s2, s3, s4, s5, s6 = strings

            cursor.execute(
                """INSERT OR REPLACE INTO guitar_tunings 
                (user_id, tuning_name, string1, string2, string3, string4, string5, string6) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (user_id, tuning_name, s1, s2, s3, s4, s5, s6)
            )

            conn.commit()
            conn.close()
            return True, "Строй сохранен!"

        except Exception as e:
            return False, f"Ошибка сохранения строя: {str(e)}"

    def delete_tuning(self, user_id, tuning_name):
        """Удалить строй"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Удаляем только если это не стандартный строй
            if tuning_name in ["Стандартный", "Drop D", "Open G",
                               "Полутон ниже"]:
                return False, "Нельзя удалить стандартный строй"

            cursor.execute(
                "DELETE FROM guitar_tunings WHERE user_id = ? AND tuning_name = ?",
                (user_id, tuning_name)
            )

            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                return True, "Строй удален!"
            else:
                conn.close()
                return False, "Строй не найден"

        except Exception as e:
            return False, f"Ошибка удаления строя: {str(e)}"

    def user_exists(self, username):
        """Проверить существование пользователя"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM users WHERE username = ?",
                           (username,))
            user = cursor.fetchone()
            conn.close()

            return user is not None

        except Exception:
            return False
