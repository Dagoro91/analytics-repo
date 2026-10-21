-- Silver: typed line items with a computed net revenue column.
select
    l_orderkey   as order_id,
    l_linenumber as line_number,
    l_suppkey    as supplier_id,
    cast(l_quantity as integer) as quantity,
    cast(l_extendedprice as decimal(14, 2)) as extended_price,
    cast(l_discount as decimal(4, 2)) as discount,
    cast(l_extendedprice * (1 - l_discount) as decimal(14, 2)) as net_revenue,
    cast(l_shipdate as date)    as ship_date,
    cast(l_commitdate as date)  as commit_date,
    cast(l_receiptdate as date) as receipt_date,
    l_shipmode as ship_mode
from {{ source('bronze', 'lineitem') }}
