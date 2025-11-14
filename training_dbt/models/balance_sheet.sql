{{
    config(
        materialized='table'
    )
}}

with staging as (
    select * from {{ ref('staging_trial_balances') }}
),

balance_sheet_totals as (
    select
        year,
        month,
        sum(case when category = 'Asset' then period_amount else 0 end) as total_assets,
        sum(case when category = 'Liability' then period_amount else 0 end) as total_liabilities,
        sum(case when category = 'Equity' then period_amount else 0 end) as total_equity
    from staging
    group by year, month
),

balance_sheet_with_equation as (
    select
        year,
        month,
        total_assets,
        total_liabilities,
        total_equity,
        total_liabilities + total_equity as total_liabilities_and_equity,
        abs(total_assets - (total_liabilities + total_equity)) < 0.01 as accounting_equation_valid
    from balance_sheet_totals
),

latest_period as (
    select
        year,
        month,
        total_assets,
        total_liabilities,
        total_equity,
        total_liabilities_and_equity,
        accounting_equation_valid,
        rank() over (order by year desc, month desc) as period_rank
    from balance_sheet_with_equation
)

select
    year,
    month,
    total_assets,
    total_liabilities,
    total_equity,
    total_liabilities_and_equity,
    accounting_equation_valid
from latest_period
where period_rank = 1
