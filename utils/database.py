import sqlite3
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path="./data/panel.db"):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        """Obter conexão com banco de dados"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Inicializar banco de dados com todas as tabelas"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabela de Keys
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key_code TEXT UNIQUE NOT NULL,
                member_id INTEGER NOT NULL,
                project TEXT NOT NULL,
                hwid TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                used_at TIMESTAMP,
                reset_count INTEGER DEFAULT 0
            )
        """)
        
        # Tabela de Whitelist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS whitelist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER UNIQUE NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de Blacklist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS blacklist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER UNIQUE NOT NULL,
                reason TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de Stats
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de Roles
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER UNIQUE NOT NULL,
                role_name TEXT NOT NULL,
                assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info("✅ Database inicializado")
    
    # ===== KEYS =====
    def create_key(self, key_code, project, member_id):
        """Criar uma nova key"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO keys (key_code, member_id, project, status)
                VALUES (?, ?, ?, 'active')
            """, (key_code, member_id, project))
            
            conn.commit()
            conn.close()
            logger.info(f"✅ Key criada: {key_code}")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao criar key: {e}")
            return False
    
    def get_key(self, key_code):
        """Obter informações de uma key"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM keys WHERE key_code = ?", (key_code,))
            key = cursor.fetchone()
            
            conn.close()
            return key
        except Exception as e:
            logger.error(f"❌ Erro ao obter key: {e}")
            return None
    
    def get_member_keys(self, member_id):
        """Obter todas as keys de um membro"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM keys WHERE member_id = ?", (member_id,))
            keys = cursor.fetchall()
            
            conn.close()
            return keys
        except Exception as e:
            logger.error(f"❌ Erro ao obter keys do membro: {e}")
            return []
    
    def reset_hwid(self, key_code):
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
            logger.info(f"✅ HWID resetado: {key_code}")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao resetar HWID: {e}")
            return False
    
    def revoke_key(self, key_code):
        """Revogar uma key"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE keys 
                SET status = 'revoked'
                WHERE key_code = ?
            """, (key_code,))
            
            conn.commit()
            conn.close()
            logger.info(f"✅ Key revogada: {key_code}")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao revogar key: {e}")
            return False
    
    # ===== WHITELIST =====
    def add_whitelist(self, member_id):
        """Adicionar à whitelist"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR IGNORE INTO whitelist (member_id)
                VALUES (?)
            """, (member_id,))
            
            conn.commit()
            conn.close()
            logger.info(f"✅ Membro adicionado à whitelist: {member_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao adicionar à whitelist: {e}")
            return False
    
    def remove_whitelist(self, member_id):
        """Remover da whitelist"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM whitelist WHERE member_id = ?", (member_id,))
            
            conn.commit()
            conn.close()
            logger.info(f"✅ Membro removido da whitelist: {member_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao remover da whitelist: {e}")
            return False
    
    def is_whitelisted(self, member_id):
        """Verificar se está na whitelist"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM whitelist WHERE member_id = ?", (member_id,))
            result = cursor.fetchone()
            
            conn.close()
            return result is not None
        except Exception as e:
            logger.error(f"❌ Erro ao verificar whitelist: {e}")
            return False
    
    # ===== BLACKLIST =====
    def add_blacklist(self, member_id, reason=""):
        """Adicionar à blacklist"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR IGNORE INTO blacklist (member_id, reason)
                VALUES (?, ?)
            """, (member_id, reason))
            
            conn.commit()
            conn.close()
            logger.info(f"✅ Membro adicionado à blacklist: {member_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao adicionar à blacklist: {e}")
            return False
    
    def remove_blacklist(self, member_id):
        """Remover da blacklist"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM blacklist WHERE member_id = ?", (member_id,))
            
            conn.commit()
            conn.close()
            logger.info(f"✅ Membro removido da blacklist: {member_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao remover da blacklist: {e}")
            return False
    
    def is_blacklisted(self, member_id):
        """Verificar se está na blacklist"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM blacklist WHERE member_id = ?", (member_id,))
            result = cursor.fetchone()
            
            conn.close()
            return result is not None
        except Exception as e:
            logger.error(f"❌ Erro ao verificar blacklist: {e}")
            return False
    
    # ===== STATS =====
    def add_stat(self, member_id, action):
        """Adicionar uma estatística"""
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
            logger.error(f"❌ Erro ao adicionar stat: {e}")
            return False
    
    def get_stats(self):
        """Obter todas as estatísticas"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT member_id, COUNT(*) as count, action
                FROM stats
                GROUP BY member_id
                ORDER BY count DESC
            """)
            
            stats = cursor.fetchall()
            conn.close()
            return stats
        except Exception as e:
            logger.error(f"❌ Erro ao obter stats: {e}")
            return []
    
    def get_member_stats(self, member_id):
        """Obter stats de um membro específico"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM stats 
                WHERE member_id = ?
                ORDER BY timestamp DESC
            """, (member_id,))
            
            stats = cursor.fetchall()
            conn.close()
            return stats
        except Exception as e:
            logger.error(f"❌ Erro ao obter stats do membro: {e}")
            return []
    
    # ===== ROLES =====
    def add_role(self, member_id, role_name):
        """Adicionar role a um membro"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO roles (member_id, role_name)
                VALUES (?, ?)
            """, (member_id, role_name))
            
            conn.commit()
            conn.close()
            logger.info(f"✅ Role adicionada: {member_id} -> {role_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao adicionar role: {e}")
            return False
    
    def get_role(self, member_id):
        """Obter role de um membro"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM roles WHERE member_id = ?", (member_id,))
            role = cursor.fetchone()
            
            conn.close()
            return role
        except Exception as e:
            logger.error(f"❌ Erro ao obter role: {e}")
            return None
