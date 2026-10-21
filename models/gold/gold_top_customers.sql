select
    c.customer_id,
    c.customer_name,
    c.nation,
    c.region,
    count(distinct o.order_id) as orders,
    sum(l.net_revenue) as revenue
from {{ ref('silver_customers') }} c
join {{ ref('silver_orders') }} o on o.customer_id = c.customer_id
join {{ ref('silver_lineitems') }} l on l.order_id = o.order_id
group by 1, 2, 3, 4
