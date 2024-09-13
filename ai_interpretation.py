import os
from openai import OpenAI
import gettext

# Set up localization
it = gettext.translation('messages', localedir='locales', languages=['it'])
it.install()
_ = it.gettext

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def get_ai_interpretation(df, exam_type):
    prompt = f"""
    Analizza i seguenti risultati dell'esame '{exam_type}' e fornisci un'interpretazione in italiano:

    Date degli esami: {', '.join(df['exam_date'].astype(str))}
    Risultati: {', '.join(df['result'].astype(str))}
    Unità di misura: {df['unit'].iloc[0]}
    Intervallo di riferimento: {df['reference_range'].iloc[0]}

    Considera le tendenze nel tempo e confronta i risultati con l'intervallo di riferimento.
    Fornisci una spiegazione semplice e chiara, adatta a un paziente.
    """

    try:
        completion = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300
        )
        interpretation = completion.choices[0].message.content
        return interpretation
    except Exception as e:
        return _("Si è verificato un errore durante l'interpretazione AI. Per favore, consulta il tuo medico per un'interpretazione professionale dei risultati.")
