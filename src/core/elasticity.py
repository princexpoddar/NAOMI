
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


def estimate_elasticity(df_sku: pd.DataFrame) -> float:
    """
    Estimate price elasticity using log-log OLS regression.

    Required columns:
        sell_price
        units_sold
    """

    df = df_sku.copy()

    df = df[
        (df["sell_price"] > 0)
        & (df["units_sold"] > 0)
    ]

    x = np.log(df["sell_price"]).values.reshape(-1, 1)
    y = np.log(df["units_sold"]).values

    model = LinearRegression()
    model.fit(x, y)

    elasticity = float(model.coef_[0])

    return elasticity


def iso_elastic_demand(
    p_candidate,
    p_base,
    q_base,
    elasticity,
):
    """
    Predict demand for a candidate price.

    Q = Q0 * (P/P0)^Ed
    """

    return q_base * (p_candidate / p_base) ** elasticity