import mysql.connector

def get_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",               
        password="6luxuanyu6",  
        database="practice_db"   
    )
    return conn
