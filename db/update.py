import psycopg2
from psycopg2 import pool
import logging
import os

# Configuração do logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração do pool de conexões
print(os.getenv('PWD'))
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

def upsert_user_data(user_id, img, user_dc, xp, xp_accumulated, lvl, timer, server_id, last_message, name_timer):
    conn = None
    cursor = None
    try:
        logger.info("Tentando obter uma conexão do pool...")
        conn = connection_pool.getconn()
        logger.info("Conexão obtida com sucesso.")
        
        cursor = conn.cursor()
        logger.info("Executando a consulta SQL...")

        cursor.execute(f""" 
            INSERT INTO rank (user_id, img, user_dc, xp, xp_accumulated, lvl, {name_timer}, server_id, last_message)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE
            SET img = EXCLUDED.img,
                user_dc = EXCLUDED.user_dc,
                xp = EXCLUDED.xp,
                xp_accumulated = EXCLUDED.xp_accumulated,
                lvl = EXCLUDED.lvl,
                {name_timer} = EXCLUDED.{name_timer},
                last_message = EXCLUDED.last_message;
        """, (user_id, img, user_dc, xp, xp_accumulated, lvl, timer, server_id, last_message))

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
