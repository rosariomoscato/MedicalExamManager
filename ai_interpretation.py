import os
from openai import OpenAI
import gettext
import pandas as pd

# Set up localization
it = gettext.translation('messages', localedir='locales', languages=['it'])
it.install()
_ = it.gettext

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def get_ai_interpretation(df, exam_type):
    # Calculate trend
    trend = "stabile"
    if len(df) > 1:
        first_value = df['result'].iloc[0]
        last_value = df['result'].iloc[-1]
        if last_value > first_value:
            trend = "in aumento"
        elif last_value < first_value:
            trend = "in diminuzione"

    # Calculate average, min, and max values
    avg_value = df['result'].mean()
    min_value = df['result'].min()
    max_value = df['result'].max()

    # Get reference range
    reference_range = df['reference_range'].iloc[0]

    prompt = f"""
    Analizza i seguenti risultati dell'esame '{exam_type}' e fornisci un'interpretazione dettagliata in italiano:

    Date degli esami: {', '.join(df['exam_date'].astype(str))}
    Risultati: {', '.join(df['result'].astype(str))}
    Unità di misura: {df['unit'].iloc[0]}
    Intervallo di riferimento: {reference_range}

    Statistiche:
    - Valore medio: {avg_value:.2f}
    - Valore minimo: {min_value:.2f}
    - Valore massimo: {max_value:.2f}
    - Tendenza: {trend}

    Fornisci una spiegazione dettagliata che includa:

    1. Interpretazione generale:
       - Analisi approfondita dei risultati rispetto all'intervallo di riferimento.
       - Spiegazione del significato clinico dell'esame nel contesto della salute generale.
       - Valutazione della tendenza nel tempo e possibili implicazioni per la salute.

    2. Consigli specifici per il paziente:
       a. Cambiamenti nello stile di vita:
          - Dieta: alimenti da includere o evitare, con esempi specifici e motivazioni.
          - Esercizio fisico: tipo, frequenza e intensità consigliati.
          - Gestione dello stress: tecniche di rilassamento o mindfulness appropriate.
       b. Integrazioni alimentari:
          - Suggerimenti su eventuali integratori, dosaggi e benefici attesi.
       c. Monitoraggio:
          - Importanza del monitoraggio continuo e frequenza consigliata per futuri esami.

    3. Analisi delle possibili cause di valori anomali:
       a. Condizioni mediche correlate a questo tipo di esame.
       b. Effetti collaterali di farmaci comuni che potrebbero influenzare i risultati.
       c. Fattori ambientali o legati allo stile di vita (es. stress, qualità del sonno).

    4. Raccomandazioni per approfondimenti:
       - Suggerimenti su quando ripetere l'esame.
       - Eventuali esami complementari utili, con spiegazione del loro valore aggiunto.

    5. Correlazioni con altri parametri di salute:
       - Spiegazione di come questo esame si relaziona con altri indicatori di salute.
       - Esempi di altri esami o parametri che potrebbero essere influenzati o correlati.

    6. Prevenzione e mantenimento di valori ottimali:
       - Pratiche quotidiane e abitudini a lungo termine per migliorare o mantenere i risultati.
       - Esempi concreti di azioni preventive specifiche per questo tipo di esame.

    7. Indicazioni per consultare un medico:
       - Sintomi o situazioni specifiche che richiedono attenzione medica immediata.
       - Spiegazione del perché questi sintomi sono rilevanti per i risultati dell'esame.

    8. Impatto sulla qualità della vita:
       - Breve spiegazione di come i risultati di questo esame possono influenzare la vita quotidiana.
       - Suggerimenti pratici per migliorare la qualità della vita in relazione ai risultati.

    9. Risorse aggiuntive:
       - Suggerimenti su fonti affidabili per ulteriori informazioni (es. siti web di associazioni mediche).
       - Eventuali app o strumenti utili per il monitoraggio o la gestione della salute correlata.

    10. Riassunto e conclusioni:
        - Sintesi dei punti chiave dell'interpretazione.
        - Messaggio finale incoraggiante e rassicurante, enfatizzando l'importanza della consulenza medica.

    Assicurati che la spiegazione sia chiara, dettagliata e comprensibile per un paziente, ma includi anche informazioni mediche rilevanti e aggiornate. Usa un tono rassicurante ma professionale, enfatizzando l'importanza di consultare un medico per un'interpretazione definitiva. Fornisci esempi concreti e pratici per ogni punto, rendendo l'informazione il più possibile applicabile alla vita quotidiana del paziente.

    Formatta l'output utilizzando la sintassi Markdown per migliorare la leggibilità, ad esempio:
    - Usa '##' per i titoli principali
    - Usa '###' per i sottotitoli
    - Usa elenchi puntati e numerati per organizzare le informazioni
    - Usa il grassetto per evidenziare punti importanti
    """

    try:
        completion = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=3000
        )
        interpretation = completion.choices[0].message.content
        return interpretation
    except Exception as e:
        return _("Si è verificato un errore durante l'interpretazione AI. Per favore, consulta il tuo medico per un'interpretazione professionale dei risultati.")

def format_interpretation(interpretation):
    # Add a title and a disclaimer at the beginning
    formatted_interpretation = "# Interpretazione AI dei Risultati dell'Esame\n\n"
    formatted_interpretation += "> **Disclaimer**: Questa interpretazione è generata da un'intelligenza artificiale e non sostituisce il parere di un professionista medico. Consulta sempre il tuo medico per una valutazione completa e accurata dei tuoi risultati.\n\n"
    
    # Add the main content
    formatted_interpretation += interpretation
    
    # Add a final note
    formatted_interpretation += "\n\n---\n\n**Nota finale**: Ricorda che questa interpretazione è basata su un'analisi automatizzata e potrebbe non tenere conto di tutti i fattori individuali. È fondamentale discutere sempre i risultati degli esami con il tuo medico curante."
    
    return formatted_interpretation

# Modify the main function to use the new formatting
def get_enhanced_ai_interpretation(df, exam_type):
    raw_interpretation = get_ai_interpretation(df, exam_type)
    return format_interpretation(raw_interpretation)
