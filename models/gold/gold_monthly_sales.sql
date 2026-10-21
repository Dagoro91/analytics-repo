select
    date_trunc('month', o.order_date) as month,
    count(distinct o.order_id) as orders,
    sum(l.net_revenue) as revenue
from {{ ref('silver_orders') }} o
join {{ ref('silver_lineitems') }} l on l.order_id = o.order_id
group by 1
