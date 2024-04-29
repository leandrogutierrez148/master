from pyspark.sql import Window
from pyspark.sql import SparkSession
from pyspark.sql import functions as F


def rotulo(i: int):
    print("------- Ejercicio: %i -------" % i)


if __name__ == "__main__":
    """
    M1B1T1_AG1:  Procesamiento de datos con Spark 2.x. Datos de ventas.
    Autores: Jorge Leodeg Ramirez Diaz y Leandro Gutierrez
    Fecha: 19-04-2024
    """
    spark = SparkSession.builder.appName("M1B1T1_AI3").getOrCreate()

    df_purchases = spark.read.json("M1B1/AG1/purchases.json")

    # """
    # 1:  Los 10 productos más comprados.
    # """
    rotulo(1)

    df_purchases\
        .groupBy("product_id")\
        .count()\
        .orderBy("count", ascending=False)\
        .limit(10)\
        .show()

    df_purchases.createOrReplaceTempView("purchases")
    sql_purchases = spark.sql('''SELECT product_id, COUNT(*) AS cant
                      FROM purchases
                      GROUP BY product_id
                      ORDER BY cant DESC
                      LIMIT 10''')
    sql_purchases.show()

    """
    2:  Porcentaje de compra de cada tipo de producto (item_type).
    """
    rotulo(2)

    total_purchases = df_purchases.\
        count()

    df_purchases\
        .groupBy("item_type")\
        .count()\
        .withColumn("per", F.col("count")/total_purchases*100)\
        .show()

    df_purchases.createOrReplaceTempView("purchases")
    sql_purchases = spark.sql('''
                      WITH total AS (
                        SELECT COUNT(*) total
                        FROM purchases
                      )
                      SELECT item_type,
                            total.total total,
                            COUNT(*) cant,
                            cant/total*100 as per
                      FROM purchases
                      CROSS JOIN total
                      GROUP BY item_type, total.total
                      ''')
    sql_purchases.show()

    """
    3:  Obtener los 3 productos más comprados por cada tipo de producto.
    """
    rotulo(3)

    w = Window.partitionBy("item_type").orderBy(F.col("count").desc())

    df_purchases\
        .groupBy("product_id", "item_type")\
        .count()\
        .withColumn("drank", F.dense_rank().over(w))\
        .orderBy("item_type", "drank", "product_id")\
        .where(F.col("drank") <= 3)\
        .show()

    df_purchases.createOrReplaceTempView("purchases")
    sql_purchases = spark.sql('''
                        WITH base AS (
                              SELECT product_id, item_type, COUNT(1) AS cant
                              FROM purchases
                              GROUP BY product_id, item_type
                        ), ranking AS (
                            SELECT product_id, item_type,
                                cant,
                                DENSE_RANK() OVER (PARTITION BY item_type ORDER BY cant desc) as ranking
                            FROM base
                        )
                        SELECT * FROM ranking WHERE ranking <= 3
                        ''')
    sql_purchases.show()

    spark.stop()
