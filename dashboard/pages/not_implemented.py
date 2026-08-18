from __future__ import annotations

import streamlit as st


def render(title: str = "Coming Soon", message: str = "Not implemented yet.") -> None:
    st.title(title)
    st.info(message)
    st.write("This section will be enabled when the corresponding research modules are implemented.")
