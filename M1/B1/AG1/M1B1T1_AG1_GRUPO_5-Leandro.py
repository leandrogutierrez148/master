from pyspark.sql import Window
from pyspark.sql import SparkSession
from pyspark.sql import functions as F


def rotulo(i: str):
    print("------- Ejercicio: %s -------" % i)


if __name__ == "__main__":
    """
    M1B1T1_AG1:  Procesamiento de datos con Spark 2.x. Datos de ventas.
    Grupo: 5
    Autores: Jorge Leodeg Ramirez Diaz y Leandro Gutierrez
    Fecha: 19-04-2024
    """
    spark = SparkSession.builder.appName("M1B1T1_AG1").getOrCreate()

    df_purchases = spark.read.json("M1B1/AG1/purchases.json")

    # """
    # 1:  Los 10 productos más comprados.
    # """
    rotulo("1")

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
    rotulo("2")

    total_purchases = df_purchases.\
        count()

    df_purchases\
        .groupBy("item_type")\
        .count()\
        .withColumn("per", F.round((F.col("count")/total_purchases*100), 2))\
        .sort(F.col("count").desc())\
        .show()

    df_purchases.createOrReplaceTempView("purchases")
    sql_purchases = spark.sql('''
                      WITH total AS (
                        SELECT COUNT(*) total
                        FROM purchases
                      )
                      SELECT item_type,
                            COUNT(*) cant,
                            ROUND(cant/total*100,2) as per
                      FROM purchases
                      CROSS JOIN total
                      GROUP BY item_type, total.total
                      ORDER BY cant DESC
                      ''')
    sql_purchases.show()

    """
    3:  Obtener los 3 productos más comprados por cada tipo de producto.
    """
    rotulo("3")

    w = Window.partitionBy("item_type").orderBy(F.col("count").desc())

    df_purchases\
        .groupBy("product_id", "item_type")\
        .count()\
        .withColumn("drank", F.row_number().over(w))\
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
                                ROW_NUMBER() OVER (PARTITION BY item_type ORDER BY cant desc) as ranking
                            FROM base
                        )
                        SELECT * FROM ranking WHERE ranking <= 3
                        ''')
    sql_purchases.show()

    """
    4:  Obtener los productos que son más caros que la media del precio de los productos.
    """
    rotulo("4")

    media = df_purchases.select(F.avg(F.col("price"))).collect()[0][0]

    df_purchases\
        .select("product_id", "item_type", "price")\
        .where(F.col("price").cast("float") > media)\
        .orderBy(F.col("price"))\
        .show()

    df_purchases.createOrReplaceTempView("purchases")
    sql = spark.sql("""
                    SELECT product_id, item_type, price
                    FROM purchases
                    WHERE price > (SELECT AVG(price) FROM purchases)
                    ORDER BY price ASC
                    """)
    sql.show()

    """
    5:  Indicar la tienda que ha vendido más productos.
    """
    rotulo("5")

    df_purchases\
        .groupBy("shop_id")\
        .count()\
        .orderBy(F.col("count"), ascending=False)\
        .limit(1)\
        .show()

    df_purchases.createOrReplaceTempView("purchases")
    sql = spark.sql("""
                    SELECT shop_id, COUNT(1) AS count
                    FROM purchases
                    GROUP BY shop_id
                    ORDER BY count DESC
                    LIMIT 1
                    """)
    sql.show()

    """
    6:  Indicar la tienda que ha facturado más dinero.
    """
    rotulo("6")

    df_purchases\
        .groupBy("shop_id")\
        .agg({"price": "sum"})\
        .orderBy(F.col("sum(price)"), ascending=False)\
        .limit(1)\
        .show()

    df_purchases.createOrReplaceTempView("purchases")
    sql = spark.sql("""
                    SELECT shop_id, SUM(price) AS sum
                    FROM purchases
                    GROUP BY shop_id
                    ORDER BY sum DESC
                    LIMIT 1
                    """)
    sql.show()

    """
    7.1:  ¿En qué área se utiliza más PayPal?
    """
    rotulo("7.1")

    df_purchases\
        .withColumn("area",
                    F.when(F.col("location.lon").between(-180, -108), "Area1")
                    .when(F.col("location.lon").between(-108, -36), "Area2")
                    .when(F.col("location.lon").between(-36, 36), "Area3")
                    .when(F.col("location.lon").between(36, 108), "Area4")
                    .when(F.col("location.lon").between(108, 180), "Area5")
                    .otherwise("Area6")
                    )\
        .groupBy(F.col("area"), F.col("payment_type"))\
        .count()\
        .where(F.col("payment_type") == "paypal")\
        .orderBy(F.col("count"), ascending=False)\
        .show()

    """
    7.2:  ¿Cuáles son los 3 productos más comprados en cada área?
    """
    rotulo("7.2")

    df_purchases.createOrReplaceTempView("purchases")
    sql = spark.sql("""
                    WITH base AS (SELECT
                                product_id,
                                CASE
                                    WHEN location.lon BETWEEN -180 and -108 THEN "Area1"
                                    WHEN location.lon BETWEEN -108 and -36 THEN "Area2"
                                    WHEN location.lon BETWEEN -36 and 36 THEN "Area3"
                                    WHEN location.lon BETWEEN 36 and 108 THEN "Area4"
                                    WHEN location.lon BETWEEN 108 and 180 THEN "Area5"
                                    ELSE "Area6"
                                END AS area,
                                COUNT(1) AS count
                        FROM purchases
                        GROUP BY product_id, area
                    ), ranking AS (
                                SELECT  product_id,
                                    area,
                                    count,
                                    ROW_NUMBER() OVER (PARTITION BY area ORDER BY count DESC, product_id DESC) AS rank
                                FROM base
                    )
                    SELECT * from ranking
                    WHERE rank <= 3
                    """)
    sql.show()

    """
    7.3:  ¿Qué área ha facturado menos dinero?
    """
    rotulo("7.3")

    df_purchases\
        .withColumn("area",
                    F.when(F.col("location.lon").between(-180, -108), "Area1")
                    .when(F.col("location.lon").between(-108, -36), "Area2")
                    .when(F.col("location.lon").between(-36, 36), "Area3")
                    .when(F.col("location.lon").between(36, 108), "Area4")
                    .when(F.col("location.lon").between(108, 180), "Area5")
                    .otherwise("Area6")
                    )\
        .groupBy(F.col("area"))\
        .sum("price")\
        .orderBy(F.col("sum(price)"))\
        .limit(1)\
        .show()

    spark.stop()
