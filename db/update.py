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
    password=os.getenv('PWD'),
    port=os.getenv('PORT'),
    connect_timeout=10  # Timeout de 10 segundos
)

def upsert_user_data(user_id, img, user_dc, xp, xp_accumulated, lvl, timer, server_id):
    conn = None
    cursor = None
    try:
        logger.info("Tentando obter uma conexão do pool...")
        conn = connection_pool.getconn()
        logger.info("Conexão obtida com sucesso.")
        
        cursor = conn.cursor()
        logger.info("Executando a consulta SQL...")

        cursor.execute(""" 
            INSERT INTO rank (user_id, img, user_dc, xp, xp_accumulated, lvl, timer, server_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE
            SET img = EXCLUDED.img,
                user_dc = EXCLUDED.user_dc,
                xp = EXCLUDED.xp,
                xp_accumulated = EXCLUDED.xp_accumulated,
                lvl = EXCLUDED.lvl,
                timer = EXCLUDED.timer;
        """, (user_id, img, user_dc, xp, xp_accumulated, lvl, timer, server_id))

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
