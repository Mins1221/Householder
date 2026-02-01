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


def insert(data):
    """tuple 형태의 데이터를 받아서 insertData 호출"""
    insertData(*data)


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


def selectMonthlySum(year_month):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        SELECT
            IFNULL(SUM(revenue), 0),
            IFNULL(SUM(expense), 0)
        FROM ledger
        WHERE substr(date, 1, 7) = ?
    """, (year_month,))

    result = c.fetchone()

    c.close()
    conn.close()

    return result  # (revenue_sum, expense_sum)

def selectMonthList():
    conn = get_connection()
    c = conn.cursor()

    c.execute('''
        SELECT DISTINCT substr(date, 1, 7)
        FROM ledger
        ORDER BY 1
    ''')

    rows = c.fetchall()

    c.close()
    conn.close()

    return [row[0] for row in rows]
