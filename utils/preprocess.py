"""
Модуль предварительной обработки данных.
"""

import pandas as pd
import re

def prepare_salary_table(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    Подготовка и очистка таблицы зарплат.
    """
    first_col = raw_df.columns[0]

    df = raw_df.rename(
        columns={first_col: "Отрасль"}
    )

    year_mapping = {}

    for col in df.columns[1:]:
        match = re.search(
            r"\b(\d{4})\b",
            str(col)
        )
        if match:
            year_mapping[col] = match.group(1)

    df = df.rename(columns=year_mapping)
    year_cols = list(year_mapping.values())
    keep = ["Отрасль"] + year_cols
    df = df[keep]

    for y in year_cols:
        df[y] = pd.to_numeric(
            df[y],
            errors="coerce"
        )
    df = df.dropna(subset=["Отрасль"])
    df = df.dropna(axis=1, how="all")

    df["Отрасль"] = (
        df["Отрасль"]
        .astype(str)
        .str.strip()
        .str.lstrip("•-–— \t")
    )
    return df

def prepare_inflation_table(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    Подготовка и очистка таблицы инфляции.
    """
    year_col = raw_df.columns[0]

    total_col_candidates = [
        c for c in raw_df.columns
        if "всего" in str(c).lower()
    ]

    total_col = (
        total_col_candidates[0]
        if total_col_candidates
        else raw_df.columns[-1]
    )

    df = raw_df[[year_col, total_col]].copy()

    df.columns = [
        "Год",
        "Инфляция"
    ]

    df["Год"] = pd.to_numeric(
        df["Год"],
        errors="coerce"
    )

    df["Инфляция"] = pd.to_numeric(
        df["Инфляция"],
        errors="coerce"
    )

    df = df.dropna()
    df["Год"] = df["Год"].astype(int)
    return df