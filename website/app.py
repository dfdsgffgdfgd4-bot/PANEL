from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import sqlite3
import os
import logging
from datetime import datetime
from functools import wraps

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Diretório do banco de dados
DB_PATH = "../data/panel.db"

# Configurações
SCRIPT_PATH = "./scripts/irish_lagger.exe"
MAX_IPS_PER_KEY = 3

def get_db_connection():
    """Obter conexão com banco de dados"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_client_ip():
    """Obter IP do cliente"""
    if request.environ.get('HTTP_CF_CONNECTING_IP'):
        return request.environ.get('HTTP_CF_CONNECTING_IP')
    return request.remote_addr

def verify_key(f):
    """Decorator para verificar key e IP"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        data = request.get_json()
        
        if not data or 'key' not in data:
            return jsonify({'error': 'Key não fornecida'}), 400
        
        key_code = data.get('key').upper()
        client_ip = get_client_ip()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar se a key existe e está ativa
        cursor.execute("SELECT * FROM keys WHERE key_code = ?", (key_code,))
        key = cursor.fetchone()
        
        if not key:
            conn.close()
            logger.warning(f"Key inválida tentada: {key_code} de IP: {client_ip}")
            return jsonify({'error': 'Key inválida'}), 401
        
        key_id, key_code_db, member_id, project, hwid, status, created_at, used_at, reset_count = key
        
        if status != 'active':
            conn.close()
            logger.warning(f"Key inativa: {key_code} de IP: {client_ip}")
            return jsonify({'error': 'Key inativa ou revogada'}), 401
        
        # Verificar blacklist
        cursor.execute("SELECT * FROM blacklist WHERE member_id = ?", (member_id,))
        if cursor.fetchone():
            conn.close()
            logger.warning(f"Membro blacklisted tentou usar key: {key_code} de IP: {client_ip}")
            return jsonify({'error': 'Acesso negado'}), 403
        
        conn.close()
        
        return f(key_code=key_code, client_ip=client_ip, *args, **kwargs)
    
    return decorated_function

@app.route('/', methods=['GET'])
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/api/check-key', methods=['POST'])
@verify_key
def check_key(key_code, client_ip):
    """Verificar se a key é válida"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT k.*, r.role_name 
        FROM keys k 
        LEFT JOIN roles r ON k.member_id = r.member_id
        WHERE k.key_code = ?
    """, (key_code,))
    
    key = cursor.fetchone()
    conn.close()
    
    if key:
        return jsonify({
            'valid': True,
            'project': key['project'],
            'role': key['role_name'],
            'created_at': key['created_at']
        }), 200
    
    return jsonify({'valid': False, 'error': 'Key inválida'}), 401

@app.route('/api/download-script', methods=['POST'])
@verify_key
def download_script(key_code, client_ip):
    """Baixar o script (apenas com key válida e IP registrado)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM keys WHERE key_code = ?", (key_code,))
    key = cursor.fetchone()
    
    if not key:
        conn.close()
        return jsonify({'error': 'Key inválida'}), 401
    
    # Registrar download
    cursor.execute("""
        UPDATE keys 
        SET hwid = ?, used_at = ?
        WHERE key_code = ?
    """, (client_ip, datetime.now(), key_code))
    
    # Adicionar stat
    cursor.execute("""
        INSERT INTO stats (member_id, action)
        VALUES (?, ?)
    """, (key['member_id'], f"Download do script - IP: {client_ip}"))
    
    conn.commit()
    conn.close()
    
    logger.info(f"Script baixado - Key: {key_code}, IP: {client_ip}")
    
    if os.path.exists(SCRIPT_PATH):
        return send_file(
            SCRIPT_PATH,
            as_attachment=True,
            download_name='irish_lagger.exe'
        )
    
    return jsonify({'error': 'Script não encontrado'}), 404

@app.route('/api/register-ip', methods=['POST'])
@verify_key
def register_ip(key_code, client_ip):
    """Registrar IP para a key"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM keys WHERE key_code = ?", (key_code,))
    key = cursor.fetchone()
    
    if not key:
        conn.close()
        return jsonify({'error': 'Key inválida'}), 401
    
    # Verificar se IP já está registrado
    hwid_list = key['hwid'].split(',') if key['hwid'] else []
    
    if client_ip in hwid_list:
        return jsonify({'message': 'IP já registrado'}), 200
    
    if len(hwid_list) >= MAX_IPS_PER_KEY:
        conn.close()
        logger.warning(f"Limite de IPs atingido - Key: {key_code}, IP: {client_ip}")
        return jsonify({'error': f'Limite de {MAX_IPS_PER_KEY} IPs atingido. Use /resethwid para resetar'}), 403
    
    hwid_list.append(client_ip)
    new_hwid = ','.join(hwid_list)
    
    cursor.execute("""
        UPDATE keys 
        SET hwid = ?
        WHERE key_code = ?
    """, (new_hwid, key_code))
    
    conn.commit()
    conn.close()
    
    logger.info(f"IP registrado - Key: {key_code}, IP: {client_ip}")
    
    return jsonify({
        'message': 'IP registrado com sucesso',
        'ip': client_ip,
        'ips_registrados': len(hwid_list),
        'limite': MAX_IPS_PER_KEY
    }), 200

@app.route('/api/status', methods=['POST'])
@verify_key
def status(key_code, client_ip):
    """Obter status da key"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM keys WHERE key_code = ?", (key_code,))
    key = cursor.fetchone()
    
    hwid_list = key['hwid'].split(',') if key['hwid'] else []
    
    conn.close()
    
    return jsonify({
        'status': key['status'],
        'project': key['project'],
        'ips_registrados': len(hwid_list),
        'limite_ips': MAX_IPS_PER_KEY,
        'reset_count': key['reset_count'],
        'created_at': key['created_at']
    }), 200

@app.route('/api/info', methods=['GET'])
def info():
    """Informações públicas"""
    return jsonify({
        'project': 'Irish Lagger',
        'version': '1.0.0',
        'max_ips_per_key': MAX_IPS_PER_KEY
    }), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Rota não encontrada'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Erro interno: {error}")
    return jsonify({'error': 'Erro interno do servidor'}), 500

if __name__ == '__main__':
    logger.info("🚀 Iniciando servidor Flask...")
    app.run(debug=True, host='0.0.0.0', port=5000)
