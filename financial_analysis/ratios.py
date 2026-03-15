"""
Financial ratio calculations: liquidity, solvency, profitability.
"""

from typing import Any


def safe_div(num: float | None, denom: float | None, default: float = 0.0) -> float:
    if denom is None or denom == 0:
        return default
    if num is None:
        return default
    return num / denom


def calculate_liquidity(data: dict[str, Any]) -> dict[str, float | str]:
    """Liquidity ratios: Current, Quick, Cash."""
    ca = data.get("current_assets")
    cl = data.get("current_liabilities")
    cash = data.get("cash")
    inv = data.get("inventory")

    current = safe_div(ca, cl)
    quick = safe_div((ca - inv) if (ca is not None and inv is not None) else None, cl)
    cash_ratio = safe_div(cash, cl)

    return {
        "Current Ratio": current if cl else "N/A",
        "Quick Ratio (Acid Test)": quick if cl else "N/A",
        "Cash Ratio": cash_ratio if cl else "N/A",
    }


def calculate_solvency(data: dict[str, Any]) -> dict[str, float | str]:
    """Solvency ratios: Debt-to-Equity, Debt-to-Assets, Interest Coverage."""
    tl = data.get("total_liabilities")
    te = data.get("total_equity")
    ta = data.get("total_assets")
    ebit = data.get("operating_income") or data.get("ebitda")
    int_exp = data.get("interest_expense")

    dte = safe_div(tl, te)
    dta = safe_div(tl, ta)
    ic = safe_div(ebit, int_exp) if int_exp and int_exp != 0 else (None if ebit is None else "N/A")

    return {
        "Debt-to-Equity": dte if (te and te != 0) else "N/A",
        "Debt-to-Assets": dta if ta else "N/A",
        "Interest Coverage": ic if ic is not None else "N/A",
    }


def calculate_profitability(data: dict[str, Any]) -> dict[str, float | str]:
    """Profitability ratios: Net Margin, ROA, ROE, Gross Margin, Operating Margin."""
    ni = data.get("net_income")
    rev = data.get("revenue")
    ta = data.get("total_assets")
    te = data.get("total_equity")
    gp = data.get("gross_profit")
    oi = data.get("operating_income")

    net_margin = safe_div(ni, rev, 0) * 100
    roa = safe_div(ni, ta, 0) * 100
    roe = safe_div(ni, te, 0) * 100
    gross_margin = safe_div(gp, rev, 0) * 100
    op_margin = safe_div(oi, rev, 0) * 100

    return {
        "Net Profit Margin (%)": net_margin if rev else "N/A",
        "Return on Assets (ROA) (%)": roa if ta else "N/A",
        "Return on Equity (ROE) (%)": roe if te else "N/A",
        "Gross Margin (%)": gross_margin if rev else "N/A",
        "Operating Margin (%)": op_margin if rev else "N/A",
    }


def calculate_all_ratios(data: dict[str, Any]) -> dict[str, dict[str, float | str]]:
    """Compute liquidity, solvency, and profitability ratios."""
    return {
        "Liquidity": calculate_liquidity(data),
        "Solvency": calculate_solvency(data),
        "Profitability": calculate_profitability(data),
    }
