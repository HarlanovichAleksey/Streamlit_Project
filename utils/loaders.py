import pandas as pd
import streamlit as st

from utils.preprocess import (
    prepare_salary_table,
    prepare_inflation_table
)


@st.cache_data
def load_salary(file):
    """
    Загрузка и очистка файла зарплат.
    """

    return prepare_salary_table(
        pd.read_excel(file)
    )


@st.cache_data
def load_inflation(file):
    """
    Загрузка и очистка файла инфляции.
    """

    return prepare_inflation_table(
        pd.read_excel(file)
    )


def load_salary_data(path: str):
    """
    Загрузка Excel-файла зарплат.
    """

    return pd.read_excel(path)


def load_inflation_data(path: str):
    """
    Загрузка Excel-файла инфляции.
    """

    return pd.read_excel(path)