-- Silver: typed and deduplicated orders.
with ranked as (
    select
        o_orderkey   as order_id,
        o_custkey    as customer_id,
        o_orderstatus as order_status,
        cast(o_totalprice as decimal(14, 2)) as total_price,
        cast(o_orderdate as date) as order_date,
        o_orderpriority as order_priority,
        row_number() over (partition by o_orderkey order by o_orderkey) as rn
    from {{ source('bronze', 'orders') }}
)
select order_id, customer_id, order_status, total_price, order_date, order_priority
from ranked
where rn = 1
