-- ---------------------------------------------------------------
-- M1B1T2_AI1. Plataforma como servicio (PaaS) en AWS
-- Autor: Leandro Gutierrez
-- Fecha: 28-04-2024
-- ---------------------------------------------------------------
SELECT * FROM partidos.partidos p;


-- ------- Ejercicio: 1 -------
-- ¿Cuántos goles ha marcado el Barcelona?
SELECT 	SUM(CASE 
				WHEN local = 'Barcelona' THEN goles_local
				ELSE goles_visitante 
			END) as goles
FROM partidos.partidos p 
WHERE local = 'Barcelona' OR visitante = 'Barcelona';

-- ------- Ejercicio: 2 -------
-- ¿Cuántos partidos han terminado 0-0?
SELECT COUNT(1)
FROM partidos.partidos p 
WHERE goles_local = 0 AND goles_visitante  = 0;

-- ------- Ejercicio: 3 -------
-- ¿En qué temporada se han marcado más goles?
SELECT 	temporada,
		SUM(goles_local + goles_visitante) as goles	
FROM partidos.partidos p 
GROUP BY temporada
ORDER BY goles DESC
LIMIT 1;

-- ------- Ejercicio: 4 -------
-- ¿Cuál es el equipo que tiene el record de meter más goles como local? ¿Y cómo visitante?
WITH goles_local AS(
	SELECT 	local AS equipo, 
			SUM(goles_local) goles,
			DENSE_RANK() OVER(ORDER BY SUM(goles_local) DESC) AS ranking
	FROM partidos.partidos p 
	GROUP BY local
), goles_visitante AS(
	SELECT 	visitante AS equipo,
			SUM(goles_visitante) goles,
			DENSE_RANK() OVER(ORDER BY SUM(goles_visitante) DESC) AS ranking
	FROM partidos.partidos 
	GROUP BY visitante 
)
SELECT 'como local' AS "goleador", equipo, goles, ranking
FROM goles_local gl
WHERE ranking = 1
UNION ALL 
SELECT 'como visitante', equipo, goles, ranking
FROM goles_visitante gv
WHERE ranking = 1;

-- ------- Ejercicio: 5 -------
-- ¿Cuál son las 3 décadas en las que más goles se metieron?
SELECT 	EXTRACT(DECADE FROM TO_DATE(fecha, 'DD/MM/YYYY'))*10 AS decada,
		SUM(goles_local + goles_visitante) goles
FROM partidos.partidos p 
GROUP BY decada
ORDER BY goles DESC
LIMIT 3;

-- ------- Ejercicio: 6 -------
-- ¿Qué equipo es el mejor local en los últimos 5 años?
WITH ranking AS (
	SELECT 	local equipo, 
			SUM(CASE  
					WHEN goles_local > goles_visitante  THEN 1
					ELSE 0
				END) ganados,
			RANK() OVER (PARTITION BY local ORDER BY temporada DESC) AS tempo
	FROM partidos.partidos p 
	GROUP BY local, temporada
)
SELECT equipo, SUM(ganados) ganados_total
FROM ranking
WHERE tempo <= 5
GROUP BY equipo
ORDER BY ganados_total DESC 
LIMIT 1;

-- ------- Ejercicio: 7 -------
-- ¿Cuál es la media de victorias por temporada en los equipos que han estado menos de 10 temporadas en 1ª división?
-- El resultado tiene que ser una tabla con dos columnas: Equipo | Media de victorias por temporada
WITH victorias_local AS (
	SELECT 	local equipo, 
			temporada,
			SUM(CASE  
					WHEN goles_local > goles_visitante  THEN 1
					ELSE 0
				END) ganados
	FROM partidos.partidos p 
	GROUP BY local, temporada
), victorias_visitante AS (
	SELECT 	visitante  equipo, 
			temporada,
			SUM(CASE  
					WHEN goles_visitante > goles_local  THEN 1
					ELSE 0
				END) ganados
	FROM partidos.partidos p 
	GROUP BY visitante, temporada
)
SELECT 	vl.equipo, 
		SUM(vl.ganados+vv.ganados)/COUNT(1) media
FROM victorias_local vl
INNER JOIN victorias_visitante vv ON vv.equipo = vl.equipo AND vl.temporada = vv.temporada
GROUP BY vl.equipo
HAVING COUNT(1) < 10
ORDER BY equipo ASC;

-- ------- Ejercicio: 8 -------
-- ¿Quién ha estado más temporadas en 1ª División: Barcelona o Real Madrid?
SELECT 	local, 
		COUNT(DISTINCT temporada)
FROM partidos.partidos
WHERE local IN ('Barcelona', 'Real Madrid')
GROUP BY LOCAL;

-- ------- Ejercicio: 9 -------
-- ¿Cuál es el record de goles como visitante en una temporada del Real Madrid?
SELECT visitante , temporada, SUM(goles_visitante) goles
FROM partidos.partidos p 
WHERE visitante = 'Real Madrid'
GROUP BY visitante, temporada
ORDER BY goles DESC 
LIMIT 1;

-- ------- Ejercicio: 10 -------
-- ¿En qué temporada se marcaron más goles en Cataluña?
WITH goles_bcn AS (
	SELECT 	local equipo, 
			temporada,
			SUM(goles_local+goles_visitante) total_goles,
			SUM(goles_local) goles_hechos,
			SUM(goles_visitante) goles_recibidos  
	FROM partidos.partidos p 
	WHERE local IN ('Barcelona', 'Espanyol')
	GROUP BY local, temporada
), mejor_temporada AS (
	SELECT	temporada, 
			SUM(total_goles) total_goles,
			SUM(goles_hechos) total_goles_hechos,
			SUM(goles_recibidos) total_goles_recibidos
	FROM goles_bcn
	GROUP BY temporada
	ORDER BY total_goles DESC 
	LIMIT 1
), total AS (
	SELECT 1 orden, m.temporada, g.equipo, g.goles_hechos, g.goles_recibidos, g.total_goles
	FROM goles_bcn g
	INNER JOIN mejor_temporada m ON m.temporada = g.temporada
	UNION 
	SELECT 2 orden, temporada, 'Total', total_goles_hechos, total_goles_recibidos, total_goles 
	FROM mejor_temporada 
	ORDER BY orden
)
SELECT temporada, equipo, goles_hechos, goles_recibidos, total_goles 
FROM total;
