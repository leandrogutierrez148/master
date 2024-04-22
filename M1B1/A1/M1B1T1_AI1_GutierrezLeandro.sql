-- ---------------------------------------------------------------
-- M1B1T1_AI1:  Consultas a bases de datos relacionales con SQL
-- Autor: Leandro Gutierrez
-- Fecha: 02-04-2024
-- ---------------------------------------------------------------

-- ------- Ejercicio: 1 -------
-- ¿Cuáles son los datos de los almacenes que tiene la compañía?
select  w.warehouse_id,
        w.warehouse_name,
        l.city||', '||c.country_name||', '|| r.region_name
from warehouses w
inner join locations l on l.location_id = w.location_id
inner join countries c on c.country_id = l.country_id
inner join regions r on r.region_id = c.region_id;

-- ------- Ejercicio: 2 -------
-- ¿Cuál es el nombre del producto que tiene más stock en Asia?
with ranking as (
	select  p.product_id,
	        p.product_name,
	    	sum(i.quantity)
	from products p
	inner join inventories i on i.product_id = p.product_id
	inner join warehouses w on w.warehouse_id = i.warehouse_id
	inner join locations l on l.location_id = w.location_id
	inner join countries c on c.country_id = l.country_id
	inner join regions r on r.region_id = c.region_id
	where r.region_name = 'Asia' 
	group by p.product_id, p.product_name, r.region_id
	order by sum(i.quantity) desc
)
select * from ranking where rownum = 1;

-- ------- Ejercicio: 3 -------
-- ¿Cuál es el producto que ha vendido más unidades durante 2016?
with ranking as (
	select  p.product_id,
	        p.product_name,
	        sum(oi.quantity) venta
	from orders o
	inner join order_items oi on oi.order_id = o.order_id
	inner join products p on p.product_id = oi.product_id
	where extract(year from o.order_date) = '2016'
	and o.status = 'Shipped'
	group by p.product_id, p.product_name
	order by venta desc
)
select * from ranking where rownum = 1;

-- ------- Ejercicio: 4 -------
-- ¿Cuál es la categoría de productos que ha vendido más unidades durante 2017?
with ranking as (
	select  c.category_id,
	        c.category_name,
	        sum(oi.quantity) venta
	from orders o
	inner join order_items oi on oi.order_id = o.order_id
	inner join products p on p.product_id = oi.product_id
	inner join product_categories c on c.category_id = p.category_id
	where extract(year from o.order_date) = '2017'
	and o.status = 'Shipped'
	group by c.category_id, c.category_name
	order by venta desc
)
select * from ranking where rownum = 1;

-- ------- Ejercicio: 5 -------
-- ¿Cuál es el nombre del cliente cuyo gasto ha sido más alto en 2015?
with ranking as (
	select  c.customer_id,
	    	c.name,
	        sum(oi.quantity * oi.unit_price) venta
	from orders o
	inner join order_items oi on oi.order_id = o.order_id
	inner join products p on p.product_id = oi.product_id
	inner join customers c on c.customer_id = o.customer_id
	where extract(year from o.order_date) = '2015'
	and o.status = 'Shipped'
	group by c.customer_id, c.name
	order by venta desc
)
select * from ranking where rownum = 1;

-- ------- Ejercicio: 6 -------
-- ¿Cuánto ha facturado la compañía en cada uno de los años de los que tiene datos?
select 	extract(year from o.order_date) as año,
    	sum(oi.quantity * oi.unit_price) venta
from orders o
inner join order_items oi on oi.order_id = o.order_id
and o.status = 'Shipped'
group by extract(year from o.order_date)
order by año asc;

-- ------- Ejercicio: 7 -------
-- ¿Cuáles son los nombres de los productos cuyo precio es superior la media?
select 	p.product_id,
    	p.product_name,
    	list_price
from products p
where list_price > (select avg(list_price) from products)
order by list_price asc;

-- ------- Ejercicio: 8 -------
-- ¿Cuáles son los empleados (nombre y apellido) que han facturado más de 50.000 $ durante 2017?
select  e.employee_id,
    	(e.first_name || ' ' || e.last_name) as nombre_completo,
        sum(oi.quantity * oi.unit_price) as venta
from orders o
inner join order_items oi on oi.order_id = o.order_id
inner join employees e on e.employee_id = o.salesman_id
where extract(year from o.order_date) = '2017'
and o.status = 'Shipped'
group by e.employee_id, (e.first_name || ' ' || e.last_name)
having sum(oi.quantity * oi.unit_price) > 50000
order by venta asc;

-- ------- Ejercicio: 9 -------
-- ¿Cuánto clientes no tienen persona de contacto?
select count(customer_id)
from customers 
where customer_id not in (select customer_id from contacts);

-- ------- Ejercicio: 10 -------
-- ¿Cuál es el Manager (nombre y apellido identificado por el campo manager_id) que menos ha facturado durante 2017?
with ranking as (
	select  m.employee_id,
	    	(m.first_name || ' ' || m.last_name) as nombre_completo,
	        sum(oi.quantity * oi.unit_price) as venta
	from orders o
	inner join order_items oi on oi.order_id = o.order_id
	inner join employees e on e.employee_id = o.salesman_id
	inner join employees m on m.employee_id = e.manager_id
	where extract(year from o.order_date) = '2017'
	and o.status = 'Shipped'
	group by m.employee_id, (m.first_name || ' ' || m.last_name)
	order by venta asc
)
select * from ranking where rownum = 1;

