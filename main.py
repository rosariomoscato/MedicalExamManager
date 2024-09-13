import streamlit as st
import gettext
import os
from auth import login, create_user
from database import init_db, load_json_files
from data_processing import get_patient_data, get_exam_types
from visualization import plot_exam_results
from ai_interpretation import get_ai_interpretation
from dashboard import show_dashboard

# Set up localization
locales_dir = os.path.abspath("locales")
it = gettext.translation('messages', localedir=locales_dir, languages=['it'])
it.install()
_ = it.gettext

# Initialize the database
init_db()

# Load JSON files
load_json_files("Esami")

st.set_page_config(page_title=_("Sistema di Gestione Esami Medici"), layout="wide")

def main():
    st.title(_("Sistema di Gestione Esami Medici"))

    # Sidebar for authentication
    with st.sidebar:
        st.header(_("Autenticazione"))
        auth_option = st.radio(_("Scegli un'opzione"), [_("Accedi"), _("Registrati")])

        if auth_option == _("Accedi"):
            username = st.text_input(_("Nome utente"))
            password = st.text_input(_("Password"), type="password")
            if st.button(_("Accedi")):
                user = login(username, password)
                if user:
                    st.session_state.user = user
                    st.success(_("Accesso effettuato con successo!"))
                else:
                    st.error(_("Nome utente o password non validi."))
        else:
            username = st.text_input(_("Nome utente"))
            password = st.text_input(_("Password"), type="password")
            role = st.selectbox(_("Ruolo"), ["paziente", "admin"])
            if st.button(_("Registrati")):
                if create_user(username, password, role):
                    st.success(_("Utente registrato con successo! Ora puoi accedere."))
                else:
                    st.error(_("Errore durante la registrazione. Il nome utente potrebbe essere già in uso."))

    # Main content
    if 'user' in st.session_state:
        user = st.session_state.user
        st.write(_("Benvenuto, {}! (Ruolo: {})").format(user['username'], user['role']))

        if user['role'] == 'admin':
            show_dashboard()
        else:
            patient_name = user['username']
            exam_types = get_exam_types()
            selected_exam = st.selectbox(_("Seleziona il tipo di esame"), exam_types)
            start_date = st.date_input(_("Data di inizio"))
            end_date = st.date_input(_("Data di fine"))

            if st.button(_("Visualizza risultati")):
                results = get_patient_data(patient_name, selected_exam, start_date, end_date)
                if results:
                    st.subheader(_("Risultati degli esami"))
                    fig = plot_exam_results(results, selected_exam)
                    st.plotly_chart(fig)

                    if st.button(_("Ottieni interpretazione AI")):
                        interpretation = get_ai_interpretation(results, selected_exam)
                        st.subheader(_("Interpretazione AI"))
                        st.write(interpretation)
                else:
                    st.info(_("Nessun risultato trovato per i criteri selezionati."))

if __name__ == "__main__":
    main()