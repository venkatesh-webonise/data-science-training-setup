-- Test: Validate month extraction
-- This test will fail if month is not between 1 and 12
-- Returns the actual invalid month values for debugging

select
    gl_number,
    gl_name,
    year,
    month,
    period_amount
from {{ ref('staging_trial_balances') }}
where month < 1 or month > 12
