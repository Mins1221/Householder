import sqlite3
import os

# === DB 경로 고정 ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "household_Ledger.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def createTable():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS ledger (
            serialNo INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            section TEXT,
            title TEXT,
            revenue INTEGER,
            expense INTEGER,
            remark TEXT
        )
    """)

    conn.commit()
    c.close()
    conn.close()


# 🔥 프로그램 시작 시 무조건 테이블 생성
createTable()


def insertData(date, section, title, revenue, expense, remark):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        INSERT INTO ledger(date, section, title, revenue, expense, remark)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (date, section, title, revenue, expense, remark))

    conn.commit()
    c.close()
    conn.close()


def insertManyData(tupleData):
    conn = get_connection()
    c = conn.cursor()

    c.executemany("""
        INSERT INTO ledger(date, section, title, revenue, expense, remark)
        VALUES (?, ?, ?, ?, ?, ?)
    """, tupleData)

    conn.commit()
    c.close()
    conn.close()


def selectAll():
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT * FROM ledger")
    rows = c.fetchall()

    c.close()
    conn.close()
    return rows


def update(vo):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        UPDATE ledger
        SET date = ?, section = ?, title = ?, revenue = ?, expense = ?, remark = ?
        WHERE serialNo = ?
    """, vo)

    conn.commit()
    c.close()
    conn.close()


def delete(key):
    conn = get_connection()
    c = conn.cursor()

    c.execute("DELETE FROM ledger WHERE serialNo = ?", (key,))

    conn.commit()
    c.close()
    conn.close()
