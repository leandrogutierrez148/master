from pyspark.sql import SparkSession
from pyspark.sql import functions as F


def rotulo(i: int):
    print("------- Ejercicio: %i -------" % i)


if __name__ == "__main__":
    """
    M1B1T1_AI3:  Procesamiento de datos con Spark 2.x. Natalidad EE.UU.
    Autor: Leandro Gutierrez
    Fecha: 03-04-2024
    """
    spark = SparkSession.builder.appName("M1B1T1_AI3").getOrCreate()

    df = spark.read.format("csv")\
        .option("header", "true")\
        .option("inferSchema", "true")\
        .load("M1/B1/A3/natality.csv")

    """
    1:  Obtén en qué 10 estados nacieron más bebés en 2003.
    """
    rotulo(1)

    # DataFrame
    df.filter(df.year == 2003)\
        .groupBy("year", "state")\
        .count()\
        .orderBy("count", ascending=False)\
        .limit(10)\
        .show()

    # SQL
    df.createOrReplaceTempView("natality")
    sqlDF = spark.sql('''SELECT year, state, COUNT(*) as count
                      FROM natality
                      WHERE year = 2003
                      GROUP BY year, state
                      ORDER BY count desc
                      LIMIT 10''')
    sqlDF.show()

    """
    2:  Obtén la media de peso de los bebés por año y estado.
    """
    rotulo(2)

    # DataFrame
    df.groupBy("year", "state")\
        .agg({"weight_pounds": "avg"})\
        .sort("year", "state").show()

    # SQL
    df.createOrReplaceTempView("natality")
    sql = spark.sql('''
                    SELECT year, state, AVG(weight_pounds)
                    FROM natality
                    GROUP BY year, state
                    ORDER BY year, state ASC
                    ''')
    sql.show()

    """
    3:  Evolución por año y por mes del número de niños y niñas nacidas
        (Resultado por separado con una sola consulta cada registro debe tener 4 columnas:
        año, mes, numero de niños nacidos, numero de niñas nacidas).
    """
    rotulo(3)

    # DataFrame
    df.groupBy(df.year, "month")\
        .agg(
            F.count(F.when(df.is_male, 1)).alias("males"),
            F.count(F.when(df.is_male == "false", 1)).alias("females"))\
        .sort("year", "month").show()

    # SQL
    df.createOrReplaceTempView("natality")
    sql = spark.sql('''
                    SELECT  year, month,
                            SUM(IF(is_male = true, 1, 0)) AS males,
                            SUM(IF(is_male = true, 0, 1)) AS females
                    FROM natality
                    GROUP BY year, month
                    ORDER BY year, month ASC
                    ''')
    sql.show()

    """
    4:  Obtén los tres meses de 2005 en que nacieron más bebés.
    """
    rotulo(4)

    # DataFrame
    df.where(F.col("year") == "2005")\
        .groupBy("year", "month")\
        .count()\
        .sort("count", ascending=False)\
        .limit(3).show()

    # SQL
    df.createOrReplaceTempView("natality")
    sql = spark.sql('''
                    SELECT year, month, COUNT(*) as cantidad
                    FROM natality
                    WHERE year = 2005
                    GROUP BY year, month
                    ORDER BY cantidad DESC
                    LIMIT 3
                    ''')
    sql.show()

    """
    5:  Obtén los estados donde las semanas de gestación son superiores a la media de EE. UU.
    """
    rotulo(5)

    # DataFrame
    df.select(F.avg("gestation_weeks")).show()
    avg_gest = df.select(F.avg("gestation_weeks")).collect()[0][0]

    df.groupBy("state")\
        .agg({"gestation_weeks": "avg"})\
        .where((F.col("avg(gestation_weeks)").cast("float") > avg_gest) & (F.col("state") != "Null"))\
        .show()

    # SQL
    df.createOrReplaceTempView("natality")
    sql = spark.sql('''
                    SELECT state, AVG(gestation_weeks)
                    FROM natality
                    GROUP BY state
                    HAVING AVG(gestation_weeks) > (SELECT AVG(gestation_weeks) FROM natality)
                        AND state IS NOT NULl
                    ''')
    sql.show()

    """
    6:  Obtén los cinco estados donde la media de edad de las madres ha sido mayor.
    """
    rotulo(6)

    # DataFrame
    df.groupBy("state")\
        .agg({"mother_age": "avg"})\
        .orderBy("avg(mother_age)", ascending=False)\
        .limit(5)\
        .show()

    # SQL
    df.createOrReplaceTempView("natality")
    sql = spark.sql('''
                    SELECT state, AVG(mother_age)
                    FROM natality
                    GROUP BY state
                    ORDER BY 2 DESC
                    LIMIT 5
                    ''')
    sql.show()

    """
    7:  Indica cómo influye en el peso del bebé y las semanas de gestación
        que la madre haya tenido un parto múltiple (campo plurality) a las que no lo han tenido.
    """
    rotulo(7)

    # DataFrame
    df.groupBy("plurality")\
        .agg({
            "weight_pounds": "avg",
            "gestation_weeks": "avg"
            })\
        .orderBy("plurality")\
        .show()

    # SQL
    df.createOrReplaceTempView("natality")
    sql = spark.sql('''
                    SELECT plurality, AVG(weight_pounds), AVG(gestation_weeks)
                    FROM natality
                    GROUP BY plurality
                    ORDER BY plurality
                    ''')
    sql.show()

    spark.stop()
