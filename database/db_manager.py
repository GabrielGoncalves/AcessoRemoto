import sqlite3

DB_NAME = "remotedesk.db"

class DatabaseManager:
    def __init__(self):
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(DB_NAME, check_same_thread=False)

    def _init_db(self):
        """Cria as tabelas relacionais e limpa esquemas obsoletos"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            
            # ==========================================
            # 1. LIMPEZA DE TABELAS ANTIGAS (MIGRAÇÃO)
            # ==========================================
            cursor.execute("DROP TABLE IF EXISTS config_perfil;")
            cursor.execute("DROP TABLE IF EXISTS config_tempo;")
            cursor.execute("DROP TABLE IF EXISTS config_sistema;")
            
            # ==========================================
            # 2. CONFIGURAÇÕES GERAIS (CHAVE-VALOR)
            # ==========================================
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS configuracoes (
                    chave TEXT PRIMARY KEY,
                    valor TEXT
                );
            """)

            # ==========================================
            # 3. IDENTIDADES (ENTIDADES ESTRUTURADAS)
            # ==========================================
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios_recorrentes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL UNIQUE
                );
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dominios_corporativos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dominio TEXT NOT NULL UNIQUE
                );
            """)
            
            # ==========================================
            # 4. AMBIENTES E CONEXÕES (ORIGINAIS MANTIDAS)
            # ==========================================
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
            
            conn.commit()
            
        self._seed_initial_data()

    def _seed_initial_data(self):
        """Popula os dados padrões da aplicação na primeira execução"""
        with self._get_connection() as conn:
            conn.cursor().execute("INSERT OR IGNORE INTO configuracoes (chave, valor) VALUES ('tema', 'cyberpunk');")
            conn.commit()


    # ==========================================
    # MÉTODOS DE CONFIGURAÇÕES (CHAVE-VALOR)
    # ==========================================
    def obter_configuracao(self, chave, valor_padrao=None):
        with self._get_connection() as conn:
            res = conn.cursor().execute("SELECT valor FROM configuracoes WHERE chave = ?", (chave,)).fetchone()
            return res[0] if res else valor_padrao

    def salvar_configuracao(self, chave, valor):
        with self._get_connection() as conn:
            conn.cursor().execute("""
                INSERT OR REPLACE INTO configuracoes (chave, valor)
                VALUES (?, ?)
            """, (chave, str(valor)))
            conn.commit()

    def obter_tema(self) -> str:
        return self.obter_configuracao("tema", "cyberpunk")

    def salvar_tema(self, nome_tema: str):
        self.salvar_configuracao("tema", nome_tema)


    # ==========================================
    # MÉTODOS DE IDENTIDADES
    # ==========================================
    def adicionar_usuario(self, nome: str) -> bool:
        try:
            with self._get_connection() as conn:
                conn.cursor().execute("INSERT INTO usuarios_recorrentes (nome) VALUES (?);", (nome,))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False

    def listar_usuarios(self):
        with self._get_connection() as conn:
            return conn.cursor().execute("SELECT id, nome FROM usuarios_recorrentes ORDER BY nome;").fetchall()

    def excluir_usuario(self, user_id: int):
        with self._get_connection() as conn:
            conn.cursor().execute("DELETE FROM usuarios_recorrentes WHERE id = ?;", (user_id,))
            conn.commit()

    def adicionar_dominio(self, dominio: str) -> bool:
        try:
            with self._get_connection() as conn:
                conn.cursor().execute("INSERT INTO dominios_corporativos (dominio) VALUES (?);", (dominio,))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False

    def listar_dominios(self):
        with self._get_connection() as conn:
            return conn.cursor().execute("SELECT id, dominio FROM dominios_corporativos ORDER BY dominio;").fetchall()

    def excluir_dominio(self, dom_id: int):
        with self._get_connection() as conn:
            conn.cursor().execute("DELETE FROM dominios_corporativos WHERE id = ?;", (dom_id,))
            conn.commit()


    # ==========================================
    # MÉTODOS: AMBIENTES E CONEXÕES
    # ==========================================
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
                SELECT ca.id, ca.nome_exibicao, ca.ip, ca.usuario, 
                       (SELECT COUNT(*) FROM favoritos f WHERE f.ip = ca.ip AND f.usuario = ca.usuario) as seguro_fav
                FROM conexoes_ambientes ca 
                WHERE ca.ambiente_id = ?;
            """, (ambiente_id,)).fetchall()
        
    def excluir_conexao_ambiente(self, conexao_id):
        with self._get_connection() as conn:
            conn.cursor().execute("DELETE FROM conexoes_ambientes WHERE id = ?;", (conexao_id,))
            conn.commit()


    # ==========================================
    # MÉTODOS: FAVORITOS
    # ==========================================
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


    # ==========================================
    # MÉTODOS: HISTÓRICO
    # ==========================================
    def registrar_historico(self, nome, ip, usuario):
        with self._get_connection() as conn: 
            cursor = conn.cursor()
            cursor.execute("DELETE FROM conexoes_historico WHERE ip = ? AND usuario = ?;", (ip, usuario))
            cursor.execute("""
                INSERT INTO conexoes_historico (nome_exibicao, ip, usuario) VALUES (?, ?, ?);
            """, (nome, ip, usuario))
            conn.commit()

    def listar_historico(self, limite=10):
        with self._get_connection() as conn:
            return conn.cursor().execute("""
                SELECT h.id, h.nome_exibicao, h.ip, h.usuario,
                       (SELECT COUNT(*) FROM favoritos f WHERE f.ip = h.ip AND f.usuario = h.usuario) as e_favorito,
                       strftime('%d/%m/%Y às %H:%M', h.ultima_conexao) as ultima_conexao
                FROM conexoes_historico h
                ORDER BY h.ultima_conexao DESC LIMIT ?;
            """, (limite,)).fetchall()
        
    def limpar_historico_completo(self):
        try:
            with self._get_connection() as conn:
                conn.execute("DELETE FROM conexoes_historico") 
            return True
        except Exception as e:
            print(f"Erro ao limpar histórico: {e}")
            return False
        
    def limpar_historico_por_retencao(self, dias: int):
        try:
            with self._get_connection() as conn:
                if dias == 0:
                    conn.cursor().execute("DELETE FROM conexoes_historico")
                elif dias > 0:
                    conn.cursor().execute(f"DELETE FROM conexoes_historico WHERE ultima_conexao <= datetime('now', '-{dias} days')")
                conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao executar rotina de limpeza automática: {e}")
            return False