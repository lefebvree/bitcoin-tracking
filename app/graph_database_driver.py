

from neo4j.v1 import GraphDatabase

from .databaseconfig import neo4j as cfg


class GraphDatabaseDriver:
    """

    """
    def __init__(self):
        self._driver = GraphDatabase.driver(cfg['uri'], auth=(cfg['user'], cfg['password']))

    def close(self):
        self._driver.close()

    def create_transaction_clause(self):
        return Neo4jTransactionClause(self)

    def run_clause(self, c):
        with self._driver.session() as session:
            session.write_transaction(self._write_clause_transaction, c)

    @staticmethod
    def _write_clause_transaction(tx, clause):
        tx.run(clause.get_statement(), clause.parameters)

    def address_exists(self, address_hash):
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
    """

    """
    def __init__(self, database_driver):
        self.statements = []
        self.parameters = {}
        self._driver = database_driver

    def get_statement(self):
        return " ".join(self.statements)

    def execute(self):
        self._driver.run_clause(self)


class Neo4jTransactionClause(Neo4jClause):
    """

    """
    def __init__(self, database_driver):
        super().__init__(database_driver)
        self.addresses = {}
        self.param_index = 0

    def add_address(self, address_hash):
        address_parameter = "a{}".format(self.param_index)
        self.addresses[address_hash] = address_parameter
        self.param_index += 1

        self.statements.append("MERGE (a{0}:Address {{ hash: ${0} }}) ".format(address_parameter))
        self.parameters[address_parameter] = address_hash

    def add_edge_between(self, address1, address2):
        a1 = self.addresses[address1]
        a2 = self.addresses[address2]

        self.statements.append("MERGE (a{0})-[:USER]->(a{1}) ".format(a1, a2))
