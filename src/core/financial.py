def compute_financial_kpis(price, demand, unit_cost, fixed_costs=0):
    revenue = float(price * demand)
    cogs = float(unit_cost * demand)
    gross_profit = revenue - cogs
    operating_profit = gross_profit - fixed_costs

    gross_margin = float((gross_profit / revenue) * 100) if revenue > 0 else 0.0

    contribution = price - unit_cost
    breakeven = float(fixed_costs / contribution) if contribution > 0 else float("inf")

    return {
        "Revenue": revenue,
        "COGS": cogs,
        "Gross Profit": gross_profit,
        "Operating Profit": operating_profit,
        "Gross Margin %": gross_margin,
        "Breakeven Volume": breakeven,
    }