
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

    def close(self):
        self._driver.close()

    def create_transaction_clause(self):
        """ Create and return a TransactionClause which will be executed with this driver

        """
        return Neo4jTransactionClause(self)

    def run_clause(self, c):
        """ Create a session and run clause statements applying clause parameters

        :param c: Neo4jClause to run
        """
        with self._driver.session() as session:
            session.write_transaction(self._write_clause_transaction, c)

    @staticmethod
    def _write_clause_transaction(tx, clause):
        tx.run(clause.get_statement(), clause.parameters)

    def address_exists(self, address_hash):
        """ Check if a Bitcoin address is present in Graph database

        :param address_hash: address public key
        """
        with self._driver.session() as session:
            return session.write_transaction(self._address_exists, address_hash)

    @staticmethod
    def _address_exists(tx, address_hash):
        result = tx.run("MATCH (address:Address) "
                        "WHERE address.hash = $hash "
                        "RETURN address ", hash=address_hash)

        result = result.single()
        return result is not None and result[0] is not None


class Neo4jClause:
    """ Statements and arguments o be executed with GraphDatabaseDriver driver

    :param database_driver: Neo4j GraphDatabaseDriver
    """
    def __init__(self, database_driver):
        self.statements = []
        self.parameters = {}
        self._driver = database_driver

    def get_statement(self):
        """ Join each clause statements as a single String

        """
        return " ".join(self.statements)

    def execute(self):
        """ Run clause statements applying parameters

        """
        self._driver.run_clause(self)


class Neo4jTransactionClause(Neo4jClause):
    """ Clause adding bitcoin known addresses and relations to Neo4j graph

    """
    def __init__(self, database_driver):
        super().__init__(database_driver)
        # Dictionary of clause's addresses with their statement node alias
        self.addresses = {}
        self.alias_index = 0

    def add_address(self, address_hash):
        """ New Bitcoin address to add to the graph database

        :param address_hash: key of bitcoin address
        """
        # Address are assigned an alias in the format a0, a1, a2... in the clause statements
        address_parameter = "a{}".format(self.alias_index)
        self.addresses[address_hash] = address_parameter
        self.alias_index += 1

        self.statements.append("MERGE (a{0}:Address {{ hash: ${0} }}) ".format(address_parameter))
        self.parameters[address_parameter] = address_hash

    def add_edge_between(self, address1, address2, optional_property=None):
        """ Add a USER relation to the graph database between two known addresses

        :param address1: key of bitcoin address
        :param address2: key of bitcoin address
        :param optional_property: string to add as relation attribute
        """
        if address1 == address2:
            return

        a1 = self.addresses[address1]
        a2 = self.addresses[address2]

        if optional_property is None:
            self.statements.append("MERGE (a{0})-[:USER]->(a{1}) ".format(a1, a2))
        else:
            self.statements.append("MERGE (a{0})-[:USER {{ {2} }}]->(a{1}) ".format(a1, a2, optional_property))
