import sqlite3

DB_NAME = "autordp.db"

class DatabaseManager:
    def __init__(self):
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(DB_NAME, check_same_thread=False)

    def _init_db(self):
        """Cria as tabelas relacionais se elas não existirem"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            
            # Tabela de Ambientes (Grupos)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ambientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL UNIQUE
                );
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conexoes_ambientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ambiente_id INTEGER,
                    nome_exibicao TEXT NOT NULL,
                    ip TEXT NOT NULL,
                    usuario TEXT NOT NULL,
                    FOREIGN KEY (ambiente_id) REFERENCES ambientes(id) ON DELETE CASCADE
                );
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS favoritos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome_exibicao TEXT NOT NULL,
                    ip TEXT NOT NULL,
                    usuario TEXT NOT NULL,
                    data_favoritado DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conexoes_historico (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome_exibicao TEXT NOT NULL,
                    ip TEXT NOT NULL,
                    usuario TEXT NOT NULL,
                    ultima_conexao DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            cursor.execute("CREATE TABLE IF NOT EXISTS config_perfil (id INTEGER PRIMARY KEY, nome_perfil TEXT, resolucao TEXT, tela_cheia INTEGER);")
            cursor.execute("CREATE TABLE IF NOT EXISTS config_tempo (id INTEGER PRIMARY KEY, timeout_segundos INTEGER, keep_alive INTEGER);")
            cursor.execute("CREATE TABLE IF NOT EXISTS config_sistema (id INTEGER PRIMARY KEY, tema_escuro INTEGER);")
            conn.commit()
            
        # Agora o método existe!
        self._seed_initial_data()

    def _seed_initial_data(self):
        """Método para popular dados iniciais se necessário (Evita o AttributeError)"""
        pass # Você pode colocar inserts de configurações padrão aqui se quiser

    # --- AMBIENTES E CONEXÕES ---
    def adicionar_ambiente(self, nome):
        try:
            with self._get_connection() as conn: 
                conn.cursor().execute("INSERT INTO ambientes (nome) VALUES (?);", (nome,))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False

    def listar_ambientes(self):
        with self._get_connection() as conn: 
            return conn.cursor().execute("SELECT * FROM ambientes ORDER BY nome;").fetchall()

    def excluir_ambiente(self, ambiente_id):
        with self._get_connection() as conn: 
            conn.cursor().execute("DELETE FROM ambientes WHERE id = ?;", (ambiente_id,))
            conn.commit()

    def adicionar_conexao_ambiente(self, ambiente_id, nome, ip, usuario):
        with self._get_connection() as conn:
            conn.cursor().execute("""
                INSERT INTO conexoes_ambientes (ambiente_id, nome_exibicao, ip, usuario) 
                VALUES (?, ?, ?, ?);
            """, (ambiente_id, nome, ip, usuario))
            conn.commit()

    def get_conexoes_por_ambiente(self, ambiente_id):
        with self._get_connection() as conn:
            return conn.cursor().execute("""
                SELECT ca.id, ca.ip, ca.usuario, 
                       (SELECT COUNT(*) FROM favoritos f WHERE f.ip = ca.ip AND f.usuario = ca.usuario) as seguro_fav
                FROM conexoes_ambientes ca 
                WHERE ca.ambiente_id = ?;
            """, (ambiente_id,)).fetchall()

    # --- FAVORITOS ---
    def adicionar_favorito(self, nome, ip, usuario):
        with self._get_connection() as conn: 
            conn.cursor().execute("""
                INSERT INTO favoritos (nome_exibicao, ip, usuario) VALUES (?, ?, ?);
            """, (nome, ip, usuario))
            conn.commit()

    def listar_favoritos(self):
        with self._get_connection() as conn: 
            return conn.cursor().execute("SELECT id, nome_exibicao, ip, usuario FROM favoritos ORDER BY nome_exibicao;").fetchall()

    def atualizar_favorito(self, fav_id, nome, ip, usuario):
        with self._get_connection() as conn: 
            conn.cursor().execute("""
                UPDATE favoritos SET nome_exibicao = ?, ip = ?, usuario = ? WHERE id = ?;
            """, (nome, ip, usuario, fav_id))
            conn.commit()

    def excluir_favorito(self, fav_id):
        with self._get_connection() as conn: 
            conn.cursor().execute("DELETE FROM favoritos WHERE id = ?;", (fav_id,))
            conn.commit()

    # --- HISTÓRICO ---
    def registrar_historico(self, nome, ip, usuario):
        with self._get_connection() as conn: 
            cursor = conn.cursor()
            cursor.execute("DELETE FROM conexoes_historico WHERE ip = ? AND usuario = ?;", (ip, usuario))
            cursor.execute("""
                INSERT INTO conexoes_historico (nome_exibicao, ip, usuario) VALUES (?, ?, ?);
            """, (nome, ip, usuario))
            conn.commit()

    def listar_historico(self, limite=10):
        with self._get_connection() as conn: # Usando _get_connection correto
            return conn.cursor().execute("""
                SELECT h.id, h.nome_exibicao, h.ip, h.usuario,
                       (SELECT COUNT(*) FROM favoritos f WHERE f.ip = h.ip AND f.usuario = h.usuario) as e_favorito
                FROM conexoes_historico h
                ORDER BY h.ultima_conexao DESC LIMIT ?;
            """, (limite,)).fetchall()