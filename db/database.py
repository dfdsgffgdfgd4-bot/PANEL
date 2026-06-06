import sqlite3
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: str = "./data/panel.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
        
    def get_connection(self):
        """Obter conexão com banco de dados"""
        return sqlite3.connect(self.db_path)
    
    def init_db(self):
        """Inicializar tabelas do banco de dados"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabela de keys
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key_code TEXT UNIQUE NOT NULL,
                member_id INTEGER,
                project TEXT NOT NULL,
                hwid TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                used_at TIMESTAMP,
                reset_count INTEGER DEFAULT 0
            )
        """)
        
        # Tabela de whitelist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS whitelist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER UNIQUE NOT NULL,
                added_by INTEGER,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reason TEXT
            )
        """)
        
        # Tabela de blacklist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS blacklist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER UNIQUE NOT NULL,
                added_by INTEGER,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reason TEXT
            )
        """)
        
        # Tabela de roles
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER UNIQUE NOT NULL,
                role_name TEXT,
                given_by INTEGER,
                given_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de stats
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER,
                action TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info("✅ Tabelas criadas/verificadas")
    
    # Métodos para Keys
    def create_key(self, key_code: str, project: str, member_id: int = None) -> bool:
        """Criar uma nova key"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO keys (key_code, project, member_id, status)
                VALUES (?, ?, ?, 'active')
            """, (key_code, project, member_id))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            logger.warning(f"Key {key_code} já existe")
            return False
    
    def get_key(self, key_code: str):
        """Obter informações de uma key"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM keys WHERE key_code = ?", (key_code,))
        result = cursor.fetchone()
        conn.close()
        return result
    
    def get_member_keys(self, member_id: int):
        """Obter todas as keys de um membro"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM keys WHERE member_id = ?", (member_id,))
        results = cursor.fetchall()
        conn.close()
        return results
    
    def reset_hwid(self, key_code: str) -> bool:
        """Resetar HWID de uma key"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE keys 
                SET hwid = NULL, reset_count = reset_count + 1 
                WHERE key_code = ?
            """, (key_code,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Erro ao resetar HWID: {e}")
            return False
    
    # Métodos para Whitelist
    def add_whitelist(self, member_id: int, added_by: int, reason: str = None) -> bool:
        """Adicionar membro à whitelist"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO whitelist (member_id, added_by, reason)
                VALUES (?, ?, ?)
            """, (member_id, added_by, reason))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            logger.warning(f"Membro {member_id} já está na whitelist")
            return False
    
    def is_whitelisted(self, member_id: int) -> bool:
        """Verificar se membro está na whitelist"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM whitelist WHERE member_id = ?", (member_id,))
        result = cursor.fetchone() is not None
        conn.close()
        return result
    
    def remove_whitelist(self, member_id: int) -> bool:
        """Remover membro da whitelist"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM whitelist WHERE member_id = ?", (member_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Erro ao remover da whitelist: {e}")
            return False
    
    # Métodos para Blacklist
    def add_blacklist(self, member_id: int, added_by: int, reason: str = None) -> bool:
        """Adicionar membro à blacklist"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO blacklist (member_id, added_by, reason)
                VALUES (?, ?, ?)
            """, (member_id, added_by, reason))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            logger.warning(f"Membro {member_id} já está na blacklist")
            return False
    
    def is_blacklisted(self, member_id: int) -> bool:
        """Verificar se membro está na blacklist"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM blacklist WHERE member_id = ?", (member_id,))
        result = cursor.fetchone() is not None
        conn.close()
        return result
    
    def remove_blacklist(self, member_id: int) -> bool:
        """Remover membro da blacklist"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM blacklist WHERE member_id = ?", (member_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Erro ao remover da blacklist: {e}")
            return False
    
    # Métodos para Roles
    def give_role(self, member_id: int, role_name: str, given_by: int) -> bool:
        """Atribuir role a um membro"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO roles (member_id, role_name, given_by)
                VALUES (?, ?, ?)
            """, (member_id, role_name, given_by))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Erro ao dar role: {e}")
            return False
    
    def get_member_role(self, member_id: int):
        """Obter role de um membro"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT role_name FROM roles WHERE member_id = ?", (member_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    
    # Métodos para Stats
    def add_stat(self, member_id: int, action: str) -> bool:
        """Adicionar uma ação às estatísticas"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO stats (member_id, action)
                VALUES (?, ?)
            """, (member_id, action))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Erro ao adicionar stat: {e}")
            return False
    
    def get_stats(self, member_id: int = None):
        """Obter estatísticas"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if member_id:
            cursor.execute("SELECT * FROM stats WHERE member_id = ?", (member_id,))
        else:
            cursor.execute("SELECT * FROM stats")
        
        results = cursor.fetchall()
        conn.close()
        return results
