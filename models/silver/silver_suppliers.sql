-- Silver: suppliers enriched with nation.
select
    s.s_suppkey as supplier_id,
    trim(s.s_name) as supplier_name,
    n.n_name as nation
from {{ source('bronze', 'supplier') }} s
join {{ source('bronze', 'nation') }} n on n.n_nationkey = s.s_nationkey
