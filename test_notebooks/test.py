# Databricks notebook source
from pyspark.sql import SQLContext

sqlContext = SQLContext(spark)

# COMMAND ----------

dw_management = (
  spark.table("this.that").select("some_id").join(spark.table("other.that"), "other_id")
)

# COMMAND ----------

# MAGIC %md
# MAGIC # Markdown heading!
# MAGIC  - And a list element

# COMMAND ----------

# MAGIC %sql
# MAGIC ALTER TABLE this.that
# MAGIC SET TBLPROPERTIES (delta.autoOptimize = TRUE);
# MAGIC
# MAGIC
# MAGIC ALTER TABLE other.that
# MAGIC SET TBLPROPERTIES (delta.autoOptimize = TRUE);

# COMMAND ----------

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
