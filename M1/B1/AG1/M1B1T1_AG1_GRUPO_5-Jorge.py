from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = SparkSession\
        .builder\
        .appName("M1B1t1_AG1")\
        .getOrCreate()

df_stock = spark.read\
        .option("header", "true")\
        .option("inferSchema", "true")\
        .csv("M1B1/AG1/stock.csv")
df_stock.createOrReplaceTempView("stock")

df_purchases = spark.read\
        .option("header", "true")\
        .option("inferSchema", "true")\
        .json("M1B1/AG1/purchases.json")
df_purchases.createOrReplaceTempView("purchases")


print("1 Los 10 productos más comprados. - Utilizando SQL")
df_resultados = spark.sql("""SELECT product_id, COUNT(*) AS count
                          FROM purchases GROUP BY product_id
                          ORDER BY count DESC LIMIT 10""")
df_resultados.show()


print("2 Porcentaje de compra de cada tipo de producto(item_type) - Utilizando el DataFrame API")
df_ventas_por_item = df_purchases.groupBy("item_type")\
                                .count()\
                                .alias("total_quantity")
total_ventas = df_ventas_por_item.select(F.sum("count"))\
                                .collect()[0][0]
df_resultados = df_ventas_por_item.withColumn("porcentage", F.round((F.col("count")/total_ventas * 100), 2))
df_resultados.show()


print("3 Obtener los 3 productos más comprados por cada tipo de producto. - Utilizando SQL")
df_resultados = spark.sql("""
        WITH ranked AS (
                    SELECT product_id, item_type, COUNT(*) AS count,
                    ROW_NUMBER() OVER (PARTITION BY item_type ORDER BY COUNT(*) DESC) AS row_num
                    FROM purchases
                    GROUP BY product_id, item_type
                )
        SELECT product_id, item_type, count, row_num
        FROM ranked
        WHERE row_num <= 3
        ORDER BY item_type, row_num, product_id """)
df_resultados.show(200)

print("4 Obtener los productos que son más caros que la media del precio de los productos. Utilizando el DataFrame API")
precio_promedio = df_purchases.agg(F.avg('price')).collect()[0][0]
print(precio_promedio)
df_purchases\
    .select("product_id", "item_type", "price")\
    .where(F.col("price").cast("float") > precio_promedio)\
    .orderBy(F.col("price"))\
    .show()

print("5 Indicar la tienda que ha vendido más productos. Usando SQL")
df_resultados = spark.sql("""SELECT shop_id, COUNT(*) AS count
                          FROM purchases
                          GROUP BY shop_id
                          ORDER BY count DESC""")
df_resultados.show(1)


print("6 Indicar la tienda que ha facturado más dinero. Usando el DataFrame API")
df_facturacion = df_purchases.groupBy('shop_id').\
    agg(F.sum('price').alias('sum_price')).\
    orderBy(F.desc('sum_price'))
df_facturacion = df_facturacion.withColumn('sum_price', F.round('sum_price', 2))
df_facturacion.show(1)


print("7 Dividir el mundo en 5 áreas geográficas iguales según la longitud (location.lon) y agrega\
una columna con el nombre del área geográfica")
df_resultados = spark.sql("""SELECT *, CASE\
                          WHEN location.lon > -180 AND location.lon < -108 THEN 'Area1'
                          WHEN location.lon >= -108 AND location.lon < -36 THEN 'Area2'
                          WHEN location.lon >= -36 AND location.lon < 36 THEN 'Area3'
                          WHEN location.lon >= 36 AND location.lon < 108 THEN 'Area4'
                          WHEN location.lon >= 108 AND location.lon <= 180 THEN 'Area5'
                          ELSE 'Latitude incorrecta'END AS area_geografica FROM purchases""")
df_resultados.createOrReplaceTempView("purchases")
df_resultados.show(3)

print("7.1 ¿En qué área se utiliza más PayPal?  Usando SQL")
df_metodos_pago = spark.sql("""SELECT area_geografica, count(payment_type) as num_pagos_paypal
                        FROM purchases WHERE payment_type = 'paypal'
                        GROUP BY area_geografica
                        SORT BY num_pagos_paypal DESC""")
df_metodos_pago.show(1)

print("7.2 ¿Cuáles son los 3 productos más comprados en cada área? Usando API Dataframe")
df_top_X_zona = df_resultados.groupBy("area_geografica", "product_id")\
    .count()
df_top_X_zona = df_top_X_zona.orderBy(F.desc("count"), F.desc("product_id"))
areas = ['Area1', 'Area2', 'Area3', 'Area4', 'Area5']
for area in areas:
    df_top_X_zona.filter(df_top_X_zona["area_geografica"] == area).show(3)

print("7.3 ¿Qué área ha facturado menos dinero? Usando SQL")
df_facturacion = spark.sql("""SELECT area_geografica, ROUND(SUM(price),2) as total_ventas
                        FROM purchases
                        GROUP by area_geografica
                        ORDER BY total_ventas""")
df_facturacion.show(1)

print("8. Indicar los productos que no tienen stock suficiente para las compras realizadas. Usando API")
df_purchase_vs_stock = df_purchases.groupby("product_id")\
                                .count()\
                                .join(df_stock, on="product_id")
df_purchase_vs_stock.filter('count>quantity').show()
