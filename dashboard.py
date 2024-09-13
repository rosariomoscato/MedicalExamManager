import streamlit as st
from data_processing import get_aggregated_data
from visualization import plot_exam_trends
import gettext

# Set up localization
it = gettext.translation('messages', localedir='locales', languages=['it'])
it.install()
_ = it.gettext

def show_dashboard():
    st.header(_("Dashboard Amministratore"))

    # Aggregate data
    df_aggregated = get_aggregated_data()

    # Display aggregate statistics
    st.subheader(_("Statistiche aggregate"))
    col1, col2 = st.columns(2)
    with col1:
        st.metric(_("Numero totale di esami"), df_aggregated['exam_count'].sum())
    with col2:
        st.metric(_("Tipi di esami unici"), len(df_aggregated))

    # Plot exam trends
    st.subheader(_("Tendenze degli esami"))
    fig = plot_exam_trends(df_aggregated)
    st.plotly_chart(fig)

    # Display raw data
    st.subheader(_("Dati grezzi"))
    st.dataframe(df_aggregated)
