import streamlit as st


def setup_page():
    """
    Настройка параметров страницы Streamlit.
    """

    st.set_page_config(
        page_title="Проект: анализ зарплат в России",
        page_icon="🎚",
        layout="centered",
        initial_sidebar_state="collapsed"
    )


def init_theme():
    """
    Инициализация темы интерфейса.
    """

    if "theme" not in st.session_state:
        st.session_state.theme = "light"


def toggle_theme():
    """
    Переключение темы интерфейса.
    """

    if st.session_state.theme == "light":
        st.session_state.theme = "dark"
    else:
        st.session_state.theme = "light"


def load_css():
    """
    Загрузка CSS-стилей приложения.
    """

    with open(
        "styles.css",
        encoding="utf-8"
    ) as f:

        base_css = f.read()

    if st.session_state.theme == "dark":

        theme_css = """
        :root {
            --bg-main:
                linear-gradient(
                    180deg,
                    #020617 0%,
                    #0f172a 100%
                );

            --text-main: #f8fafc;

            --card-bg: #111827;

            --border: #1e293b;

            --hero:
                linear-gradient(
                    135deg,
                    #1d4ed8,
                    #312e81
                );

            --input-bg: #0f172a;

            --metric-bg: #111827;

            --tab-bg: #111827;

            --toolbar-bg: #f8fafc;

            --toolbar-text: #111827;
        }
        """

    else:

        theme_css = """
        :root {
            --bg-main:
                linear-gradient(
                    180deg,
                    #dbeafe 0%,
                    #bfdbfe 100%
                );

            --text-main: #0f172a;

            --card-bg: #ffffff;

            --border: #dbeafe;

            --hero:
                linear-gradient(
                    135deg,
                    #38bdf8,
                    #2563eb
                );

            --input-bg: #ffffff;

            --metric-bg: #ffffff;

            --tab-bg: #ffffff;

            --toolbar-bg: #020617;

            --toolbar-text: #ffffff;
        }
        """

    st.markdown(
        f"""
        <style>
        {theme_css}
        {base_css}
        </style>
        """,
        unsafe_allow_html=True
    )


def show_header():
    """
    Отображение шапки приложения.
    """

    top1, top2 = st.columns([8, 1])

    with top2:

        icon = (
            "🌙"
            if st.session_state.theme == "light"
            else "☀️"
        )

        st.button(
            icon,
            on_click=toggle_theme,
            use_container_width=True
        )

    st.markdown(
        """
<div class="hero">

<h1>
📈 Проект: анализ зарплат в России 💸
</h1>

<p>
Интерактивная аналитика зарплат
с учётом инфляции
</p>

</div>
        """,
        unsafe_allow_html=True
    )