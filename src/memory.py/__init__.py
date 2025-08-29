import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
import time

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY_4")

neo4j_uri = os.getenv("NEO4J_URI")
neo4j_user = "neo4j"
neo4j_password = os.getenv("NEO4J_PASS")

driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

# Example: Creating a node
def add_person(tx, name):
    tx.run("CREATE (p:Person {name: $name})", name=name)

# Example: Querying data
def get_people(tx):
    result = tx.run("MATCH (p:Person) RETURN p.name AS name")
    return [record["name"] for record in result]


# Using sessions to execute queries
with driver.session() as session:
    # Write transaction (for creating, updating, deleting data)
    held=time.time()
    session.execute_write(add_person, "Alice")
    session.execute_write(add_person, "Bob")
    print(time.time()-held)

    # Read transaction (for querying data)
    people_names = session.execute_read(get_people)
    print(f"People in the database: {people_names}")

# Close the driver when finished
driver.close()