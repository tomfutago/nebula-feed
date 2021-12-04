import psycopg2
from datetime import datetime
from nebula_feed import config

conn = psycopg2.connect(config.db_url, sslmode="require")

# Open a cursor to perform database operations
cur = conn.cursor()

# Execute a command: this creates a new table
#cur.execute("create table ClaimedPlanets (TokenId int not null, PlanetName varchar(50) not null, ClaimedDate timestamp not null);")

#cur.execute("insert into ClaimedPlanets(TokenId, PlanetName, ClaimedDate) values (%s, %s, %s);",
#    (100, "test", datetime.now()))

#cur.execute("truncate table ClaimedPlanets;")

cur.execute("select * from ClaimedPlanets;")
test = cur.fetchall()
print(test)

# Make the changes to the database persistent
conn.commit()

# Close communication with the database
cur.close()
conn.close()

