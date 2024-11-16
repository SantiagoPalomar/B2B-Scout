import psycopg2


def main():
    conn = psycopg2.connect('postgres://avnadmin:AVNS_nEfx8XN1vdiYhATDyS2@pg-195b295a-nicolasdavid2409-dd5b.d.aivencloud.com:27225/defaultdb?sslmode=require')

    query_sql = 'SELECT VERSION()'

    cur = conn.cursor()
    cur.execute(query_sql)

    version = cur.fetchone()[0]
    print(version)


if __name__ == "__main__":
    main()