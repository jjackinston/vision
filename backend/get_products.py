import psycopg2
conn = psycopg2.connect(host='localhost', port=5432, dbname='sellervision', user='sellervision', password='sellervision')
cur = conn.cursor()

# Check competitors columns + sample
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='competitors' AND table_schema='public'")
print("competitor cols:", [r[0] for r in cur.fetchall()])
cur.execute("SELECT id, brand, asin, marketplace FROM public.competitors LIMIT 3")
for r in cur.fetchall(): print(" comp:", r)

# Check listings
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='listings' AND table_schema='public'")
cols = [r[0] for r in cur.fetchall()]
print("\nlisting cols:", cols)
cur.execute("SELECT id, marketplace, title FROM public.listings LIMIT 3")
for r in cur.fetchall(): print(" listing:", r)

# Check suppliers
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='suppliers' AND table_schema='public'")
print("\nsupplier cols:", [r[0] for r in cur.fetchall()])
cur.execute("SELECT id, name, country FROM public.suppliers LIMIT 3")
for r in cur.fetchall(): print(" supplier:", r)

conn.close()
