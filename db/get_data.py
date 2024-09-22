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

def get_user_data(user_id, server_id, timer):
    conn = None
    cursor = None
    try:
        logger.info("Tentando obter uma conexão do pool...")
        conn = connection_pool.getconn()
        logger.info("Conexão obtida com sucesso.")
        
        cursor = conn.cursor()
        logger.info("Executando a consulta SQL...")

        cursor.execute(
            f"SELECT img, user_dc, xp, xp_accumulated, lvl, {timer}, last_message FROM rank WHERE user_id = %s AND server_id = %s",
            (user_id, server_id)
        )
        result = cursor.fetchone()
        
        if result:
            data = {
                'img': result[0],
                'user_dc': result[1],
                'xp': result[2],
                'xp_accumulated': result[3],
                'lvl': result[4],
                f'{timer}': result[5],
                'server_id': server_id,
                'last_message': result[6]
            }
            logger.info(f"Dados retornados: {data}")
            return data
        else:
            logger.info("Nenhum dado encontrado para os parâmetros fornecidos.")
            return None
    
    except psycopg2.Error as e:
        logger.error(f"Erro ao executar a operação: {e}")
        return None
    
    finally:
        if cursor:
            cursor.close()
            logger.info("Cursor fechado.")
        if conn:
            connection_pool.putconn(conn)
            logger.info("Conexão retornada ao pool.")
