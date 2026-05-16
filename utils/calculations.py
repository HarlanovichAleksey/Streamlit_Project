"""
Модуль с функциями аналитических расчётов.
"""

import pandas as pd
import numpy as np
import streamlit as st


# =========================================================
# ДЕФЛЯТОР
# =========================================================

def build_deflator(
    inflation_df: pd.DataFrame,
    base_year: int
) -> pd.Series:
    """
    Построение дефлятора относительно базового года.
    """

    years = inflation_df["Год"].values

    rates = (
        inflation_df["Инфляция"].values / 100.0
    )

    inf_dict = dict(zip(years, rates))

    all_years = sorted(inf_dict.keys())

    deflator = pd.Series(
        1.0,
        index=all_years
    )

    if base_year not in deflator.index:

        st.warning(
            f"Базовый год {base_year} отсутствует"
        )

        base_year = all_years[0]

    # -----------------------------------------------------
    # ВПЕРЁД
    # -----------------------------------------------------

    for y in range(
        base_year + 1,
        max(all_years) + 1
    ):

        prev = y - 1

        if (
            y in deflator.index
            and prev in deflator.index
        ):

            deflator[y] = (
                deflator[prev]
                * (1 + inf_dict.get(y, 0))
            )

    # -----------------------------------------------------
    # НАЗАД
    # -----------------------------------------------------

    for y in range(
        base_year - 1,
        min(all_years) - 1,
        -1
    ):

        nxt = y + 1

        if (
            y in deflator.index
            and nxt in deflator.index
        ):

            deflator[y] = (
                deflator[nxt]
                / (1 + inf_dict.get(nxt, 0))
            )

    return deflator


# =========================================================
# РЕАЛЬНЫЕ ЗАРПЛАТЫ
# =========================================================

def adjust_for_inflation(
    nominal_df: pd.DataFrame,
    base_year: int,
    deflator: pd.Series
) -> pd.DataFrame:
    """
    Корректировка зарплат на инфляцию.
    """

    real = nominal_df.copy()

    year_cols = [
        c for c in nominal_df.columns
        if c != "Отрасль"
        and c.isdigit()
    ]

    for col in year_cols:

        y = int(col)

        if y in deflator.index:

            real[col] = (
                real[col] / deflator[y]
            )

        else:

            real[col] = np.nan

    return real


# =========================================================
# LONG DATA
# =========================================================

def create_long_format(
    df: pd.DataFrame,
    salary_type: str
) -> pd.DataFrame:
    """
    Перевод таблицы в long-формат.
    """

    long_df = (
        df
        .reset_index()
        .melt(
            id_vars="Отрасль",
            var_name="Год",
            value_name="Зарплата"
        )
    )

    long_df["Год"] = (
        long_df["Год"]
        .astype(int)
    )

    long_df["Тип"] = salary_type

    return long_df


# =========================================================
# ТЕМПЫ РОСТА
# =========================================================

def calculate_growth(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Расчёт темпов роста зарплат.
    """

    return (
        df.pct_change(axis=1) * 100
    )


def prepare_growth_long(
    growth_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Подготовка growth-data
    для графиков.
    """

    growth_long = (
        growth_df
        .reset_index()
        .melt(
            id_vars="Отрасль",
            var_name="Год",
            value_name="Рост, %"
        )
    )

    growth_long["Год"] = (
        growth_long["Год"]
        .astype(int)
    )

    growth_long = growth_long.dropna()

    return growth_long


# =========================================================
# ДОЛЯ ВЫШЕ ИНФЛЯЦИИ
# =========================================================

def calculate_share_above_inflation(
    growth_df: pd.DataFrame,
    inflation_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Расчёт доли отраслей,
    у которых рост выше инфляции.
    """

    infl_years = (
        inflation_df[
            inflation_df["Год"].isin(
                [
                    int(y)
                    for y in growth_df.columns
                ]
            )
        ]
        .set_index("Год")["Инфляция"]
    )

    beat_infl = pd.DataFrame(
        index=growth_df.index
    )

    for y in growth_df.columns:

        year_int = int(y)

        if year_int in infl_years.index:

            beat_infl[y] = (
                growth_df[y]
                > infl_years[year_int]
            )

    share_beat = (
        beat_infl.mean(axis=0) * 100
    )

    share_df = (
        share_beat.reset_index()
    )

    share_df.columns = [
        "Год",
        "Доля отраслей, %"
    ]

    share_df["Год"] = (
        share_df["Год"]
        .astype(int)
    )

    return share_df


# =========================================================
# ИНДЕКС ЗАРПЛАТ
# =========================================================

def calculate_salary_index(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Индекс зарплат
    относительно первого года.
    """

    first_year = df.columns[0]

    return (
        df.div(
            df[first_year],
            axis=0
        ) * 100
    )


def prepare_index_long(
    index_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Подготовка индексных данных
    для графика.
    """

    index_long = (
        index_df
        .reset_index()
        .melt(
            id_vars="Отрасль",
            var_name="Год",
            value_name="Индекс зарплат"
        )
    )

    index_long["Год"] = (
        index_long["Год"]
        .astype(int)
    )

    return index_long


# =========================================================
# НАКОПЛЕННАЯ ИНФЛЯЦИЯ
# =========================================================

def calculate_cumulative_inflation(
    inflation_df: pd.DataFrame,
    year_cols: list[str]
) -> pd.DataFrame:
    """
    Индекс накопленной инфляции.
    """

    infl_series = (
        inflation_df
        .set_index("Год")["Инфляция"]
    )

    years_index = [
        int(y)
        for y in year_cols
    ]

    cum_infl = pd.Series(
        100.0,
        index=years_index
    )

    for i in range(1, len(years_index)):

        y = years_index[i]
        prev_y = years_index[i - 1]

        if y in infl_series.index:

            cum_infl[y] = (
                cum_infl[prev_y]
                * (1 + infl_series[y] / 100)
            )

        else:

            cum_infl[y] = (
                cum_infl[prev_y]
            )

    result = cum_infl.reset_index()

    result.columns = [
        "Год",
        "Индекс цен"
    ]

    return result


# =========================================================
# ТОП РОСТА
# =========================================================

def calculate_top_growth(
    df: pd.DataFrame,
    top_n: int = 10
) -> pd.DataFrame:
    """
    Расчёт лидеров роста зарплат.
    """

    first_year = df.columns[0]
    last_year = df.columns[-1]

    growth = (
        (
            df[last_year]
            / df[first_year]
        ) - 1
    ) * 100

    growth = (
        growth
        .replace([np.inf, -np.inf], np.nan)
        .dropna()
    )

    top_growth = (
        growth
        .sort_values(ascending=False)
        .head(top_n)
        .reset_index()
    )

    top_growth.columns = [
        "Отрасль",
        "Рост"
    ]

    return top_growth


# =========================================================
# BOXPLOT DATA
# =========================================================

def prepare_boxplot_data(
    df: pd.DataFrame,
    year_cols: list[str]
):
    """
    Подготовка данных
    для boxplot.
    """

    box_year = (
        "2025"
        if "2025" in df.columns
        else year_cols[-1]
    )

    box_data = (
        df[box_year]
        .dropna()
    )

    return box_year, box_data


# =========================================================
# ИТОГОВЫЕ МЕТРИКИ
# =========================================================

def calculate_summary_metrics(
    df: pd.DataFrame,
    inflation_df: pd.DataFrame
) -> dict:
    """
    Расчёт итоговых метрик.
    """

    first_year = df.columns[0]
    current_year = df.columns[-1]

    current_salary = df[current_year]

    infl_last = inflation_df[
        inflation_df["Год"]
        == int(current_year)
    ]["Инфляция"].values

    inflation_value = (
        infl_last[0]
        if len(infl_last) > 0
        else 0
    )

    total_growth = (
        (
            current_salary.mean()
            /
            df[first_year].mean()
        ) - 1
    ) * 100

    return {
        "current_year": current_year,
        "min_salary": current_salary.min(),
        "max_salary": current_salary.max(),
        "avg_salary": current_salary.mean(),
        "median_salary": current_salary.median(),
        "inflation": inflation_value,
        "total_growth": total_growth
    }