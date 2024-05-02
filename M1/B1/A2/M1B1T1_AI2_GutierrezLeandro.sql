-- ---------------------------------------------------------------
-- M1B1T1_AI1:  Consultas a bases de datos relacionales con SQL
-- Autor: Leandro Gutierrez
-- Fecha: 02-04-2024
-- ---------------------------------------------------------------

-- ------- Ejercicio: 1 -------
-- ¿Cuántos restaurantes pertenecen a la ciudad (borough) de “Queens”?
db.restaurants.countDocuments({"borough": "Queens"})

-- ------- Ejercicio: 2 -------
-- ¿Cuántos restaurantes tienen el código postal 11374?
db.restaurants.count({"address.zipcode": "11374"})

-- ------- Ejercicio: 3 -------
-- ¿Cuántos restaurantes son de tipo “American” o “Bakery”?
db.restaurants.countDocuments({"cuisine": {$in: ["Bakery","American"]}})

-- ------- Ejercicio: 4 -------
-- ¿Cuántos nombres de restaurantes empiezan por la letra “A”? 
db.restaurants.countDocuments({name: /^A/})

-- ------- Ejercicio: 5 -------
-- ¿Cuáles es el nombre de las 10 empresas mas antiguas?
db.companies.find({founded_year:{$ne: null}},{name:1,founded_year:1}).sort({founded_year: 1})

-- ------- Ejercicio: 6 -------
-- ¿Cuántas empresas se fundaron durante o después del año 2000?
db.companies.countDocuments({founded_year: {$gte:2000}})

-- ------- Ejercicio: 7 -------
-- ¿Cuántas empresas tienen entre 500 y 1000 empleados/as?
db.companies.countDocuments({number_of_employees: {$gt: 500, $lte:1000}})

-- ------- Ejercicio: 8 -------
-- ¿Cuántas empresas no tienen productos informados?
db.companies.countDocuments({products: {$size: 0}})

-- ------- Ejercicio: 9 -------
-- ¿En cuántos mails aparecen las palabras “Wall Street Journal” en el asunto del correo?
db.mails.countDocuments({text: /Wall Street Journal/})

-- ------- Ejercicio: 10 -------
-- ¿Cuántos correos tienen como remitente un correo con dominio @enron.com?
db.mails.countDocuments({sender: /@enron.com$/})