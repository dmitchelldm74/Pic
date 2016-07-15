import sqlite3
def Post(table, vals):
    conn = sqlite3.connect('database')
    c = conn.cursor()
    qm = ""
    for v in vals:
        if qm == "":
            qm += "?"
        else:
            qm += "," + "?"
    ex = 'INSERT INTO ' + table + ' VALUES (' + qm + ')'
    c.execute(ex, vals)
    conn.commit()
    conn.close()
    return ""
