"""
Главный файл Streamlit-приложения
для анализа зарплат в России.
"""

import pandas as pd
import streamlit as st

from io import BytesIO

# =========================================================
# UI
# =========================================================

from utils.ui import (
    setup_page,
    init_theme,
    load_css,
    show_header
)

# =========================================================
# LOADERS
# =========================================================

from utils.loaders import (
    load_salary,
    load_inflation
)

# =========================================================
# CALCULATIONS
# =========================================================

from utils.calculations import (
    build_deflator,
    adjust_for_inflation,

    create_long_format,

    calculate_growth,
    prepare_growth_long,

    calculate_share_above_inflation,

    calculate_salary_index,
    prepare_index_long,

    calculate_cumulative_inflation,

    calculate_top_growth,

    prepare_boxplot_data,

    calculate_summary_metrics
)

# =========================================================
# CHARTS
# =========================================================

from utils.charts import (
    create_salary_chart,
    add_inflation_line,

    create_growth_chart,

    create_heatmap,

    create_share_chart,

    create_index_chart,

    create_top_growth_chart,

    create_boxplot
)

# =========================================================
# НАСТРОЙКА СТРАНИЦЫ
# =========================================================

setup_page()
init_theme()
load_css()
show_header()

# =========================================================
# ЗАГРУЗКА ФАЙЛОВ
# =========================================================

st.markdown("## 📂 Загрузка данных")

col1, col2 = st.columns(2)

with col1:

    salary_file = st.file_uploader(
        "Файл зарплат (XLSX)",
        type=["xlsx"]
    )

with col2:

    inflation_file = st.file_uploader(
        "Файл инфляции (XLSX)",
        type=["xlsx"]
    )

# =========================================================
# ОСНОВНАЯ ЛОГИКА
# =========================================================

if salary_file and inflation_file:

    # =====================================================
    # ЗАГРУЗКА ДАННЫХ
    # =====================================================

    salary_df = load_salary(salary_file)

    inflation_df = load_inflation(
        inflation_file
    )

    # =====================================================
    # ПОИСК ГОДОВ
    # =====================================================

    year_cols_all = [
        c for c in salary_df.columns
        if c != "Отрасль"
        and c.isdigit()
    ]

    years_in_salary = sorted(
        [int(c) for c in year_cols_all]
    )

    if not years_in_salary:
        st.error(
            """
            Не удалось найти столбцы
            с годами в файле зарплат.
            """
        )
        st.stop()
    st.success("✅ Данные успешно загружены")

    # =====================================================
    # SIDEBAR
    # =====================================================

    st.sidebar.markdown(
        "## ⚙️ Параметры"
    )

    available_years = sorted(
        inflation_df["Год"].unique()
    )

    # -----------------------------------------------------
    # БАЗОВЫЙ ГОД
    # -----------------------------------------------------

    base_year = st.sidebar.selectbox(
        "Базовый год",

        options=available_years,

        index=(
            available_years.index(2020)
            if 2020 in available_years
            else 0
        )
    )

    # -----------------------------------------------------
    # ОТРАСЛИ
    # -----------------------------------------------------

    all_sectors = (
        salary_df["Отрасль"]
        .unique()
        .tolist()
    )

    default_sectors = (
        ["Всего"]

        if "Всего" in all_sectors

        else all_sectors[:5]
    )

    selected_sectors = (
        st.sidebar.multiselect(
            "Отрасли",

            options=all_sectors,

            default=default_sectors
        )
    )

    # -----------------------------------------------------
    # ДИАПАЗОН ЛЕТ
    # -----------------------------------------------------

    year_range = st.sidebar.slider(
        "Диапазон лет",

        min_value=min(years_in_salary),

        max_value=max(years_in_salary),

        value=(
            min(years_in_salary),
            max(years_in_salary)
        )
    )

    # =====================================================
    # ФИЛЬТРАЦИЯ ДАННЫХ
    # =====================================================

    filtered_salary = salary_df[
        salary_df["Отрасль"]
        .isin(selected_sectors)
    ]

    year_cols = [

        str(y)

        for y in range(
            year_range[0],
            year_range[1] + 1
        )

        if str(y) in filtered_salary.columns
    ]

    if not year_cols:

        st.error(
            "Нет данных для выбранного диапазона"
        )

        st.stop()

    # =====================================================
    # НОМИНАЛЬНЫЕ ЗАРПЛАТЫ
    # =====================================================

    df_nominal = (
        filtered_salary[
            ["Отрасль"] + year_cols
        ]
        .set_index("Отрасль")
    )

    # =====================================================
    # ДЕФЛЯТОР
    # =====================================================

    deflator = build_deflator(
        inflation_df,
        base_year
    )

    # =====================================================
    # РЕАЛЬНЫЕ ЗАРПЛАТЫ
    # =====================================================

    df_real = (
        adjust_for_inflation(
            df_nominal.reset_index(),
            base_year,
            deflator
        )
        .set_index("Отрасль")
    )

    # =====================================================
    # ВСЕ ДАННЫЕ БЕЗ ФИЛЬТРОВ
    # =====================================================

    all_nominal = (
        salary_df[
            ["Отрасль"] + year_cols
        ]
        .set_index("Отрасль")
    )

    all_real = (
        adjust_for_inflation(
            all_nominal.reset_index(),
            base_year,
            deflator
        )
        .set_index("Отрасль")
    )

    # =====================================================
    # LONG FORMAT
    # =====================================================

    nominal_long = create_long_format(
        df_nominal,
        "Номинальная"
    )

    real_long = create_long_format(
        df_real,
        "Реальная"
    )

    combined = pd.concat([
        nominal_long,
        real_long
    ])

    # =====================================================
    # TABS
    # =====================================================

    (
        tab1,
        tab2,
        tab3,
        tab4,
        tab5
    ) = st.tabs([
        "📈 Динамика",
        "🔥 Тепловая карта",
        "📋 Таблицы",
        "🔎 Глубокий анализ",
        "📌 Итоги"
    ])

    # =====================================================
    # TAB 1 — ДИНАМИКА
    # =====================================================

    with tab1:
        st.subheader(
            "Сравнение номинальных "
            "и реальных зарплат"
        )

        # -------------------------------------------------
        # ВЫБОР ТИПА ГРАФИКА
        # -------------------------------------------------

        chart_type = st.radio(
            "Тип графика",

            ["Линейный", "Столбчатый"],

            horizontal=True
        )

        # -------------------------------------------------
        # ГРАФИК ЗАРПЛАТ
        # -------------------------------------------------

        fig_salary = create_salary_chart(
            combined,
            chart_type,
            base_year
        )

        st.plotly_chart(
            fig_salary,
            use_container_width=True
        )

        # -------------------------------------------------
        # ТЕМПЫ РОСТА
        # -------------------------------------------------

        st.subheader(
            "Темпы роста зарплат"
        )

        growth = calculate_growth(
            df_nominal
        )

        growth_long = (
            prepare_growth_long(growth)
        )

        fig_growth = create_growth_chart(
            growth_long
        )

        infl_compare = inflation_df[
            inflation_df["Год"].between(
                year_range[0],
                year_range[1]
            )
        ]

        fig_growth = add_inflation_line(
            fig_growth,
            infl_compare
        )

        st.plotly_chart(
            fig_growth,
            use_container_width=True
        )

    # =====================================================
    # TAB 2 — ТЕПЛОВАЯ КАРТА
    # =====================================================

    with tab2:
        st.subheader(
            "Тепловая карта зарплат"
        )

        fig_heat = create_heatmap(
            df_nominal
        )

        st.plotly_chart(
            fig_heat,
            use_container_width=True
        )

    # =====================================================
    # TAB 3 — ТАБЛИЦЫ
    # =====================================================

    with tab3:
        col1, col2 = st.columns(2)

        # -------------------------------------------------
        # НОМИНАЛЬНЫЕ ЗАРПЛАТЫ
        # -------------------------------------------------

        with col1:
            st.subheader(
                "Номинальные зарплаты"
            )

            st.dataframe(
                df_nominal.style.format(
                    "{:,.0f}"
                )
            )

        # -------------------------------------------------
        # РЕАЛЬНЫЕ ЗАРПЛАТЫ
        # -------------------------------------------------

        with col2:
            st.subheader(
                "Реальные зарплаты"
            )

            st.dataframe(
                df_real.style.format(
                    "{:,.0f}"
                )
            )

        # -------------------------------------------------
        # ЭКСПОРТ EXCEL
        # -------------------------------------------------

        output = BytesIO()

        with pd.ExcelWriter(
            output,
            engine="xlsxwriter"
        ) as writer:

            df_nominal.to_excel(
                writer,
                sheet_name="Номинальные"
            )

            df_real.to_excel(
                writer,
                sheet_name="Реальные"
            )

        st.download_button(
            "📥 Скачать Excel",
            data=output.getvalue(),
            file_name="salary_analysis.xlsx",
            mime=(
                "application/vnd.openxmlformats-"
                "officedocument.spreadsheetml.sheet"
            )
        )

    # =====================================================
    # TAB 4 — ГЛУБОКИЙ АНАЛИЗ
    # =====================================================

    with tab4:
        # -------------------------------------------------
        # ДОЛЯ ВЫШЕ ИНФЛЯЦИИ
        # -------------------------------------------------

        st.markdown(
            "### 📊 Доля отраслей "
            "с ростом выше инфляции"
        )

        all_growth = calculate_growth(
            all_nominal
        )

        share_df = (
            calculate_share_above_inflation(
                all_growth,
                inflation_df
            )
        )

        fig_share = create_share_chart(
            share_df
        )

        st.plotly_chart(
            fig_share,
            use_container_width=True
        )

        # -------------------------------------------------
        # ИНДЕКС ЗАРПЛАТ
        # -------------------------------------------------

        st.markdown(
            "### 📈 Индекс "
            "накопленного роста"
        )

        index_nominal = (
            calculate_salary_index(
                df_nominal
            )
        )

        index_long = (
            prepare_index_long(
                index_nominal
            )
        )

        cum_infl_df = (
            calculate_cumulative_inflation(
                inflation_df,
                year_cols
            )
        )

        fig_index = create_index_chart(
            index_long,
            cum_infl_df
        )

        st.plotly_chart(
            fig_index,
            use_container_width=True
        )

        # -------------------------------------------------
        # ЛИДЕРЫ РОСТА
        # -------------------------------------------------

        st.markdown(
            "### 🚀 Лидеры роста зарплат"
        )

        top_nominal = (
            calculate_top_growth(
                all_nominal
            )
        )

        top_real = (
            calculate_top_growth(
                all_real
            )
        )

        col_top1, col_top2 = st.columns(2)

        # -------------------------------------------------
        # НОМИНАЛЬНЫЙ РОСТ
        # -------------------------------------------------

        with col_top1:
            fig_top_nom = (
                create_top_growth_chart(
                    top_nominal,
                    "Номинальный рост"
                )
            )

            st.plotly_chart(
                fig_top_nom,
                use_container_width=True
            )

        # -------------------------------------------------
        # РЕАЛЬНЫЙ РОСТ
        # -------------------------------------------------

        with col_top2:
            fig_top_real = (
                create_top_growth_chart(
                    top_real,
                    "Реальный рост"
                )
            )

            st.plotly_chart(
                fig_top_real,
                use_container_width=True
            )

        # -------------------------------------------------
        # BOXPLOT
        # -------------------------------------------------

        st.markdown(
            "### 📦 Распределение "
            "зарплат по отраслям"
        )

        box_year, box_data = (
            prepare_boxplot_data(
                all_nominal,
                year_cols
            )
        )

        fig_box = create_boxplot(
            box_data,
            box_year
        )

        st.plotly_chart(
            fig_box,
            use_container_width=True
        )

    # =====================================================
    # TAB 5 — ИТОГИ
    # =====================================================

    with tab5:
        st.subheader(
            "📌 Итоговые показатели"
        )

        metrics = (
            calculate_summary_metrics(
                all_nominal,
                inflation_df
            )
        )

        salary_range = (
            f"{metrics['min_salary']:,.0f}"
            f" – "
            f"{metrics['max_salary']:,.0f} ₽"
        )

        col1, col2, col3 = st.columns(3)

        # -------------------------------------------------
        # КОЛОНКА 1
        # -------------------------------------------------

        with col1:

            st.metric(
                (
                    "Минимальная зарплата "
                    f"({metrics['current_year']})"
                ),
                f"{metrics['min_salary']:,.0f} ₽"
            )

            st.metric(
                (
                    "Средняя зарплата "
                    f"({metrics['current_year']})"
                ),
                f"{metrics['avg_salary']:,.0f} ₽"
            )

            st.metric(
                (
                    "Максимальная зарплата "
                    f"({metrics['current_year']})"
                ),
                f"{metrics['max_salary']:,.0f} ₽"
            )

        # -------------------------------------------------
        # КОЛОНКА 2
        # -------------------------------------------------

        with col2:
            st.metric(
                (
                    "Медианная зарплата "
                    f"({metrics['current_year']})"
                ),
                f"{metrics['median_salary']:,.0f} ₽"
            )

            st.metric(
                (
                    "Размах "
                    f"({metrics['current_year']})"
                ),
                salary_range
            )

        # -------------------------------------------------
        # КОЛОНКА 3
        # -------------------------------------------------

        with col3:
            st.metric(
                (
                    "Инфляция "
                    f"({metrics['current_year']})"
                ),
                f"{metrics['inflation']:.1f}%"
            )

            st.metric(
                "Рост за период",
                f"{metrics['total_growth']:.1f}%"
            )

# =========================================================
# ЕСЛИ ФАЙЛЫ НЕ ЗАГРУЖЕНЫ
# =========================================================

else:

    st.info(
        "👆 Загрузите оба Excel-файла"
    )