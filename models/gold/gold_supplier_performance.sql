select
    s.supplier_id,
    s.supplier_name,
    s.nation,
    count(*) as lines_delivered,
    sum(l.net_revenue) as revenue,
    avg(date_diff('day', l.commit_date, l.receipt_date)) as avg_delay_days
from {{ ref('silver_suppliers') }} s
join {{ ref('silver_lineitems') }} l on l.supplier_id = s.supplier_id
group by 1, 2, 3
