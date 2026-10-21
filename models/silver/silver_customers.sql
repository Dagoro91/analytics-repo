-- Silver: cleaned and conformed customers, enriched with nation and region.
with ranked as (
    select
        c_custkey      as customer_id,
        trim(c_name)   as customer_name,
        c_nationkey    as nation_id,
        c_mktsegment   as market_segment,
        cast(c_acctbal as decimal(12, 2)) as account_balance,
        row_number() over (partition by c_custkey order by c_custkey) as rn
    from {{ source('bronze', 'customer') }}
)
select
    r.customer_id,
    r.customer_name,
    n.n_name as nation,
    g.r_name as region,
    r.market_segment,
    r.account_balance
from ranked r
join {{ source('bronze', 'nation') }} n on n.n_nationkey = r.nation_id
join {{ source('bronze', 'region') }} g on g.r_regionkey = n.n_regionkey
where r.rn = 1
