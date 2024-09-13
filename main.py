import streamlit as st
import gettext
import os
from auth import login, create_user
from database import init_db, load_json_files, check_database_content
from data_processing import get_patient_data, get_exam_details
from visualization import plot_exam_results
from ai_interpretation import get_enhanced_ai_interpretation
from dashboard import show_dashboard
import datetime

# Set up localization
locales_dir = os.path.abspath("locales")
it = gettext.translation('messages', localedir=locales_dir, languages=['it'])
it.install()
_ = it.gettext

# Initialize the database
init_db()

# Load JSON files
load_json_files("Esami")
print("Data loading completed. Checking database content...")
check_database_content()
print(f"GUI date input format: {type(datetime.date.today())} - {datetime.date.today()}")

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
            start_date = st.date_input(_("Data di inizio"))
            end_date = st.date_input(_("Data di fine"))

            if st.button(_("Visualizza risultati")):
                available_exams = get_patient_data(patient_name, start_date, end_date)
                
                if not available_exams:
                    st.info(_("Nessun esame trovato per i criteri selezionati."))
                else:
                    st.subheader(_("Esami disponibili"))
                    selected_exam = st.selectbox(_("Seleziona un esame"), available_exams)
                    
                    if st.button(_("Mostra dettagli esame")):
                        # Fetch detailed data for the selected exam
                        exam_results = get_exam_details(patient_name, start_date, end_date, selected_exam)
                        
                        # Plot the exam results
                        fig = plot_exam_results(exam_results, selected_exam)
                        st.plotly_chart(fig)

                        # Generate and display AI interpretation
                        interpretation = get_enhanced_ai_interpretation(exam_results, selected_exam)
                        with st.expander(_("Interpretazione AI dettagliata"), expanded=True):
                            st.markdown(interpretation)

                        # Provide download option for AI interpretation
                        st.download_button(
                            label=_("Scarica interpretazione AI"),
                            data=interpretation,
                            file_name=f"interpretazione_ai_{selected_exam}.txt",
                            mime="text/plain"
                        )

                        st.warning(_("Ricorda: L'interpretazione AI è solo indicativa. Consulta sempre il tuo medico per una valutazione professionale."))

if __name__ == "__main__":
    main()

# Reload JSON files at the end of the script
load_json_files("Esami")
