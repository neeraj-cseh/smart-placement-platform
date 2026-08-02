import sqlite3

def check_db():
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cursor.fetchall()]
    
    print(f"Searching {len(tables)} tables for 'Computer'...")
    for table in tables:
        try:
            cursor.execute(f"PRAGMA table_info({table});")
            cols = [c[1] for c in cursor.fetchall()]
            
            for col in cols:
                query = f"SELECT `{col}` FROM `{table}` WHERE `{col}` LIKE '%Computer%';"
                cursor.execute(query)
                results = cursor.fetchall()
                if results:
                    print(f"Found match in table: {table}, column: {col}")
                    for r in results[:5]:
                        print("  ->", r[0])
        except Exception as e:
            pass
            
    conn.close()

if __name__ == '__main__':
    check_db()
