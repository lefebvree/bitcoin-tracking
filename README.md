# Bitcoin users re-identification using community detection

## About

Algorithm allowing the re-identification of Bitcoin users from heuristics based on transaction history

## Usage

1. Install python dependencies from requirements file

```shell
pip3 install -r requirements.txt
```

2. Setup [Apache Spark](https://spark.apache.org/downloads.html), an instance will be launched by the PySpark executor

3. Setup [Neo4j](https://neo4j.com/docs/operations-manual/current/installation/) and start it

4. Create a config files in `/app` in the following format :

 - `databaseconfig.py` : PySpark and Neo4j databases configurations
 ```python
#!/usr/bin/env python
pyspark = {
    'hdfs_path': '/path/to_json_file_or_directory',
    'memory': '2g' # Allocated memory for Spark
}
neo4j = {
    'uri': 'bolt://localhost:7687', # Bolt instance URI
    'user': 'neo4j',
    'password': 'password'
}
```

5. Running `main.py` will populate the Neo4j Graph Database with the discovered user
network :

```shell
python3 main.py
```


## Libraries

* Pyspark : https://spark.apache.org/docs/0.9.0/python-programming-guide.html

* Neo4j : https://neo4j.com/


## References

* Tracking bitcoin users activity using community
detection on a network of weak signals - https://arxiv.org/abs/1710.08158

* Community detection in networks: A user guide - https://arxiv.org/abs/1608.00163

* The Unreasonable Effectiveness of Address Clustering - https://arxiv.org/abs/1605.06369
