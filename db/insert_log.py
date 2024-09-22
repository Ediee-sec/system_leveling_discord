import psycopg2
from psycopg2 import pool
import logging
import os

# Configuração do logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração do pool de conexões
connection_pool = psycopg2.pool.SimpleConnectionPool(
    1,  # Número mínimo de conexões
    20, # Número máximo de conexões
    host=os.getenv('HOST'),
    database=os.getenv('DB'),
    user=os.getenv('USR'),
    password=os.getenv('PASS'),
    port=os.getenv('PORT'),
    connect_timeout=10  # Timeout de 10 segundos
)

# Função para inserir os dados na tabela user_activity_log
def insert_user_activity(data):
    conn = None
    cursor = None
    try:
        logger.info("Tentando obter uma conexão do pool...")
        conn = connection_pool.getconn()
        logger.info("Conexão obtida com sucesso.")
        
        cursor = conn.cursor()
        logger.info("Executando a consulta SQL...")

        cursor.execute("""
            INSERT INTO user_activity_log (datetime, "user", type, xp, multiplier, xp_multiplied, level, channel, content)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data['datetime'], data['user'], data['type'], data['xp'],
            data['multiplier'], data['xp_multiplied'], data['level'],
            data['channel'], data['content']
        ))

        conn.commit()
        logger.info("Consulta executada e dados commitados com sucesso.")
    
    except psycopg2.Error as e:
        logger.error(f"Erro ao executar a operação: {e}")
    
    finally:
        if cursor:
            cursor.close()
            logger.info("Cursor fechado.")
        if conn:
            connection_pool.putconn(conn)
            logger.info("Conexão retornada ao pool.")
        
        # Atualize o log com a contagem de conexões disponíveis
        logger.info(f"Conexões ativas no pool: {connection_pool._pool.qsize() if hasattr(connection_pool._pool, 'qsize') else 'Não disponível'}")


