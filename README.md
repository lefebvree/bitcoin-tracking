# Bitcoin users re-identification using community detection

## About

## Usage

1. Config files in `/app` in the following format :

 - `databaseconfig.py` : PySpark and Neo4j databases configurations
 ```python
#!/usr/bin/env python
pyspark = {
    'hdfs_path': '/path/to_json_file_or_directory',
    'memory': '2g' # Allocated memory for Spark
}
neo4j = {
    'uri': 'bolt://localhost:7687',
    'user': 'neo4j',
    'password': 'password'
}
```

2. Running `main.py` will populate the Neo4j Graph Database with the discovered user
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
