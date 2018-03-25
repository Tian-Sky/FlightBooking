# All about Database

Mysql, sqlserver, PregreSql

MongoDB, Cassandra, Redis

## Storage

1. Persistent
2. Fast access
3. Accetable cost

### File management

* Row store
	* File -> Pages -> Rows
	* Pros:
		* Storage model similar to logical mode
		* Good for writes
* Column Store
	* Split table into columns
	* Pros:
		* Save I/O cost if read only a few columns
		* Storage efficiency
		* Schema expansion


## Index

Problem: Access data fast
Requirements: As fast as possible
Access methods:

* Sequential scan(slow)
* Index
	* B+ tree (ordered items)
	* R tree (unordered items)
	* HASH


