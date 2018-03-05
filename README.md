# Bitcoin users re-identification using community detection

## About

## Usage

1. Config files in `/app` in the following format :

 - `databaseconfig.py` : PySpark configuration
 ```python
#!/usr/bin/env python
pyspark = {
    'hdfs_path': '/path/to_json_file_or_directory',
    'memory': '5g' # Allocated memory for Spark
}
```


## Libraries

* Pyspark

* Networkx


## References

* Tracking bitcoin users activity using community
detection on a network of weak signals - https://arxiv.org/abs/1710.08158

* Community detection in networks: A user guide - https://arxiv.org/abs/1608.00163

* The Unreasonable Effectiveness of Address Clustering - https://arxiv.org/abs/1605.06369
