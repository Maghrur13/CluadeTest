"""
Configuration for financial statement line item extraction.
Add alternative labels for your PDF format if extraction fails.
"""

# Balance Sheet items - map internal key to possible PDF labels (case-insensitive)
BALANCE_SHEET_ITEMS = {
    "current_assets": [
        "total current assets",
        "cari aktivlər", "cəmi cari aktivlər", "cari aktivlər cəmi", "cari aktiv",
        "qısamüddətli aktivlər", "qisa muddetli aktivler", "cəmi qısamüddətli aktivlər", "cemi qisa muddetli aktivler"
    ],
    "total_assets": [
        "total assets",
        "cəmi aktivlər", "ümumi aktivlər", "aktivlərin cəmi", "cemi aktivler"
    ],
    "current_liabilities": [
        "total current liabilities",
        "cari öhdəliklər", "cəmi cari öhdəliklər", "cari öhdəliklərin cəmi", "qısamüddətli öhdəliklər",
        "cəmi qısamüddətli öhdəliklər", "cemi qisa muddetli ohdelikler"
    ],
    "total_liabilities": [
        "total liabilities",
        "cəmi öhdəliklər", "ümumi öhdəliklər", "öhdəliklərin cəmi", "cemi ohdelikler"
    ],
    "total_equity": [
        "total equity", "shareholders' equity", "stockholders' equity",
        "total stockholders' equity",
        "kapital", "ümumi kapital", "cəmi kapital", "səhmdarların kapitalı", "mülkiyyət kapitalı",
        "cəmi kapital", "cemi kapital"
    ],
    "cash": [
        "cash and cash equivalents", "cash", "cash equivalents",
        "nağd pul və nağd pul ekvivalentləri", "nağd pul", "pul vəsaitləri", "pul vəsaitləri və ekvivalentləri"
    ],
    "inventory": [
        "inventory", "inventories",
        "ehtiyatlar", "mal-material ehtiyatları", "mallar", "material ehtiyatları"
    ],
}

# Income Statement items
INCOME_STATEMENT_ITEMS = {
    "revenue": [
        "revenue", "total revenue", "sales", "net sales", "total sales",
        "gəlir", "gəlirlər", "satış gəliri", "satışdan gəlir", "xalis satışlar", "ümumi gəlir",
        "müştərilərlə müqavilələr üzrə gəlirlər", "musterilerle muqavileler uzre gelirler"
    ],
    "gross_profit": [
        "gross profit", "gross margin",
        "ümumi mənfəət", "val mənfəət", "brüt mənfəət"
    ],
    "operating_income": [
        "operating income", "income from operations", "ebit",
        "əməliyyat mənfəəti", "əməliyyat gəliri", "əsas fəaliyyət mənfəəti", "əsas əməliyyat mənfəəti"
    ],
    "net_income": [
        "net income", "net profit", "profit for the year", "net earnings",
        "xalis mənfəət", "xalis gəlir", "ilin mənfəəti", "dövrün mənfəəti", "mənfəət",
        "il üzrə mənfəət", "il uzre menfeet"
    ],
    "interest_expense": [
        "interest expense", "interest paid",
        "faiz xərci", "faiz xərcləri", "faiz üzrə xərclər", "faiz ödənişləri",
        "faiz xərcləri", "maliyyə xərcləri", "maliyye xercleri"
    ],
    "ebitda": [
        "ebitda", "adjusted ebitda",
        "favi", "favi̇", "faiz, amortizasiya və vergilərdən əvvəl mənfəət"
    ],
}
