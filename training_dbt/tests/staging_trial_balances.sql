select
    gl_number,
    gl_name,
    year,
    month,
    period_amount
from {{ ref('staging_trial_balances') }}
where month < 1 or month > 12
