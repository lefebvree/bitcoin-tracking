
"""
Driver handling connections with the Neo4j Graph Database,
transactions are handled though clauses and executed by the GraphDatabaseDriver
"""

from neo4j.v1 import GraphDatabase

from .databaseconfig import neo4j as cfg


class GraphDatabaseDriver:
    """ Neo4j Database driver

    """
    def __init__(self):
        self._driver = GraphDatabase.driver(cfg['uri'], auth=(cfg['user'], cfg['password']))

        # Create an Index on Address:address and User:id, fasten MERGE operations by a lot
        with self._driver.session() as session:
            with session.begin_transaction() as tx:
                tx.run("CREATE CONSTRAINT ON (address:Address) ASSERT address.address IS UNIQUE")
                tx.run("CREATE CONSTRAINT ON (user:User) ASSERT user.id IS UNIQUE")

        # New addresses and transactions stored in memory before batch adding
        self.batch_new_addresses = []
        self.batch_new_relations = []

    def close(self):
        self._driver.close()

    def commit_additions(self):
        """ Add new addresses and new relations then clear current batch

        """
        self._add_addresses()
        self.batch_new_addresses.clear()

        self._add_relations()
        self.batch_new_relations.clear()

    def add_address(self, address):
        """ Add a new address for next commit

        :param address: String new address key
        """
        self.batch_new_addresses.append(address)

    def add_relation(self, edge):
        """ Add a new USER relation between two addresses for next commit

        :param edge: List of two address key
        """
        if edge[0] != edge[1]:
            self.batch_new_relations.append(edge)

    def get_address_count(self):
        """ Get number of Addresses nodes in graph

        """
        query = "MATCH (:Address) RETURN count(*) AS address_count"
        with self._driver.session() as session:
            with session.begin_transaction() as tx:
                result = tx.run(query).single()
                return result['address_count']

    def fetch_all_known_addresses(self, callback):
        """ Fetch all addresses from graph and execute callback function for everyone

        :param callback: Function to execute with each address
        """
        query = "MATCH p=(a:Address) " \
                "RETURN a.address AS address "

        with self._driver.session() as session:
            with session.begin_transaction() as tx:
                for record in tx.run(query):
                    # Add addresses to set
                    callback(record['address'])

    def _add_addresses(self):
        """ Create nodes for all addresses in batch_new_addresses

        """
        query = "UNWIND $addresses AS h MERGE (a:Address{ address: h })"
        with self._driver.session() as session:
            with session.begin_transaction() as tx:
                tx.run(query, addresses=self.batch_new_addresses)

    def _add_relations(self):
        """ Create edges for all addresses relations in batch_new_relations

        """
        query = "UNWIND $relations AS a " \
                "MATCH (a1:Address { address: a[0] }) " \
                "MATCH (a2:Address { address: a[1] }) " \
                "MERGE (a1)-[:USER]->(a2)"
        with self._driver.session() as session:

            with session.begin_transaction() as tx:
                tx.run(query, relations=self.batch_new_relations)

    def find_connected_components(self):
        """ Search all connected Address components and assign an user attribute to identify their partition,
        return the number of user partitions found

        """
        query = "CALL algo.unionFind('Address', 'USER', {write:true, partitionProperty:'user'}) " \
                "YIELD setCount " \
                "RETURN setCount"

        with self._driver.session() as session:
            with session.begin_transaction() as tx:
                result = tx.run(query).single()
                return int(result['setCount'])

    def create_user_nodes(self):
        """ Create new user nodes from connected components ids and add relation from addresses to user nodes

        """
        query = "MATCH (address:Address) " \
                "MERGE (user:User { id: address.user }) " \
                "WITH address, user " \
                "CREATE (user)-[r:OWN]->(address)"

        with self._driver.session() as session:
            with session.begin_transaction() as tx:
                tx.run(query)
