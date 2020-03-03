# Databricks notebook source
from pyspark.sql import SQLContext

sqlContext = SQLContext(spark)

# COMMAND ----------

dw_management = (
    spark.table("this.that")
    .select("some_id")
    .join(spark.table("other.that"), "other_id")
)

# COMMAND ----------

# MAGIC %md
# MAGIC # Markdown heading!
# MAGIC  - And a list element

# COMMAND ----------

# MAGIC %sql
# MAGIC ALTER TABLE this.that SET TBLPROPERTIES (delta.autoOptimize = true);
# MAGIC ALTER TABLE other.that SET TBLPROPERTIES (delta.autoOptimize = true);


# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT country, product, SUM(profit) FROM
# MAGIC sales   left join x on x.id=sales.k GROUP BY country,
# MAGIC product having f > 7 and fk=9 limit 5;
