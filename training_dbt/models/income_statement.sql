
with tb as (
    select * from {{ ref('staging_trial_balances') }}
),

income_statement as (
    select
        year,
        month,
        sum(
            case
                when category = 'Revenue'
                then period_amount
                else 0
            end
        ) as revenue,
        sum(
            case
                when category = 'Expense'
                then period_amount
                else 0
            end
        ) as expense
    from tb
    group by year, month
    order by year, month
)

select * from income_statement