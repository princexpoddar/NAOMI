
import numpy as np
import matplotlib.pyplot as plt

from src.data.pipeline import DataPipeline
from src.core.elasticity import estimate_elasticity, iso_elastic_demand

FIXED_COST = 15

pipeline = DataPipeline()
df = pipeline.load_data()
sku = pipeline.get_sku_dataframe(df, "FOODS_3_090_CA_1")

elasticity = estimate_elasticity(sku)
base_price = float(sku["sell_price"].iloc[-1])
base_demand = float(sku["units_sold"].mean())
unit_cost = float(sku["unit_cost"].iloc[-1])

prices = np.linspace(
    max(unit_cost * 1.05, 0.7 * base_price),
    1.4 * base_price,
    100,
)

profits = []

for p in prices:
    q = iso_elastic_demand(p, base_price, base_demand, elasticity)
    profits.append((p - unit_cost) * q - FIXED_COST)

best_idx = np.argmax(profits)

plt.figure(figsize=(8,5))
plt.plot(prices, profits, linewidth=2, label="Profit Curve")
plt.scatter(
    prices[best_idx],
    profits[best_idx],
    s=80,
    label="Optimal Price",
)

plt.xlabel("Price")
plt.ylabel("Profit")
plt.title("NAOMI Price Optimization")
plt.grid(True)
plt.legend()

plt.show()