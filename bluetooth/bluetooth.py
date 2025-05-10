import subprocess
import re
import datetime
from db import get_db_connection

# 새로운 기기를 bluetooth_device 테이블에 추가
def add_device(user_id, mac_address, device_name):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO bluetooth_devices (user_id, mac_address, device_name, registered_at)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE device_name = VALUES(device_name)
        """, (user_id, mac_address, device_name, datetime.datetime.now()))

        conn.commit()
        return True
    except Exception as e:
        print(f"❌ 기기 추가 실패: {e}")
        return False
    finally:
        if conn:
            conn.close()

# 유저의 아이디들을 토대로 맥 주소들을 반환 
def get_mac_addresses_by_user_ids(user_ids):
    """여러 사용자 ID에 대한 블루투스 MAC 주소 맵 조회 (user_id -> mac_address)"""
    if not user_ids:
        return {}

    placeholders = ','.join(['%s'] * len(user_ids))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT user_id, mac_address FROM bluetooth_devices
        WHERE user_id IN ({placeholders})
    """, tuple(user_ids))
    rows = cursor.fetchall()
    conn.close()
    
    return {row['user_id']: row['mac_address'] for row in rows}

# 유저 아이디를 토대로 맥 주소 반환
def get_mac_address_by_user_id(user_id):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT mac_address FROM bluetooth_devices
            WHERE user_id = %s
            LIMIT 1
        """, (user_id,))
        result = cursor.fetchone()
        if result:
            return result['mac_address']
        else:
            print(f"❌ 사용자 ID {user_id}에 대한 MAC 주소가 존재하지 않습니다.")
            return None
    except pymysql.Error as e:
        print(f"❌ MAC 주소 조회 중 오류 발생: {e}")
        return None
    finally:
        if conn:
            conn.close()

