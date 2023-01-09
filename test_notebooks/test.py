# Databricks notebook source
from pyspark.sql import SQLContext

sqlContext = SQLContext(spark)

# COMMAND ----------

# DBTITLE 1,Title for a python cell
dw_management = (
    spark.table("this.that")
    .select("some_id")
    .join(spark.table("other.that"), "other_id")
)


def test_func(input_param):
    """
    :param   input_param: input
    """
    return None

# COMMAND ----------

# MAGIC %md
# MAGIC # Markdown heading!
# MAGIC  - And a list element

# COMMAND ----------

# MAGIC %sh
# MAGIC ls -l

# COMMAND ----------

# MAGIC %sql
# MAGIC ALTER TABLE this.that
# MAGIC SET TBLPROPERTIES (delta.autoOptimize = TRUE);
# MAGIC 
# MAGIC 
# MAGIC ALTER TABLE other.that
# MAGIC SET TBLPROPERTIES (delta.autoOptimize = TRUE);

# COMMAND ----------

# DBTITLE 1,Title for an SQL cell
# MAGIC %sql
# MAGIC SELECT country,
# MAGIC        product,
# MAGIC        SUM(profit)
# MAGIC FROM sales
# MAGIC LEFT JOIN x ON x.id=sales.k
# MAGIC GROUP BY country,
# MAGIC          product
# MAGIC HAVING f > 7
# MAGIC AND fk=9
# MAGIC LIMIT 5;

# COMMAND ----------

# MAGIC %sql  -- nofmt
# MAGIC CREATE OR REPLACE VIEW abc.test AS
# MAGIC   (SELECT foo.bar,
# MAGIC           foo.fizz,  -- a comment
# MAGIC           foo.fizzbar,
# MAGIC           foo.bazz
# MAGIC    FROM cba.tset foo);
# MAGIC 
# MAGIC 
# MAGIC CREATE OR REPLACE VIEW asd.dsa AS
# MAGIC   (SELECT bar.foo,
# MAGIC           COLLECT_SET(bar.fizz)[0],
# MAGIC           FIRST(bar.baz)
# MAGIC    FROM dsa.asd bar
# MAGIC    GROUP BY bar.fizzbuzz);

# COMMAND ----------

# MAGIC %sql
# MAGIC 
# MAGIC 
# MAGIC SELECT id from test_table LIMIT 1
# MAGIC -- 3 NewLines after %sql

# COMMAND ----------

# MAGIC %sql
# MAGIC 
# MAGIC SELECT id from test_table LIMIT 1
# MAGIC -- 2 NewLines after %sql

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT id from test_table LIMIT 1
# MAGIC -- 1 NewLines after %sql

# COMMAND ----------

# MAGIC %sql SELECT id from test_table LIMIT 1
# MAGIC -- SPACE after %sql

# COMMAND ----------

# MAGIC %sql	SELECT id from test_table LIMIT 1
# MAGIC -- TAB after %sql
