import plotly.graph_objects as go
import gettext

# Set up localization
it = gettext.translation('messages', localedir='locales', languages=['it'])
it.install()
_ = it.gettext

def plot_exam_results(df, exam_type):
    print(f"Plotting exam results for {exam_type}. DataFrame shape: {df.shape}")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['exam_date'], y=df['result'], mode='lines+markers', name=exam_type))

    # Add reference range if available
    if 'reference_range' in df.columns and df['reference_range'].notna().any():
        ref_range = df['reference_range'].iloc[0]
        if '-' in ref_range:
            try:
                lower, upper = map(lambda x: float(x.replace(',', '.').strip()), ref_range.split('-'))
            except ValueError as e:
                print(f"Error converting reference range to float: {ref_range}")
                print(f"Error details: {e}")
                lower, upper = None, None

            if lower is not None and upper is not None:
                fig.add_hline(y=lower, line_dash="dash", line_color="red", annotation_text=_("Limite inferiore"))
                fig.add_hline(y=upper, line_dash="dash", line_color="red", annotation_text=_("Limite superiore"))
            else:
                print(f"Skipping reference range lines for exam type: {exam_type}")

    fig.update_layout(
        title=_("Risultati dell'esame: {}").format(exam_type),
        xaxis_title=_("Data"),
        yaxis_title=f"{exam_type} ({df['unit'].iloc[0]})",
        hovermode="x unified"
    )
    return fig

def plot_exam_trends(df):
    fig = go.Figure(data=[
        go.Bar(name=_('Numero di esami'), x=df['exam_type'], y=df['exam_count']),
        go.Scatter(name=_('Risultato medio'), x=df['exam_type'], y=df['avg_result'], yaxis='y2')
    ])

    fig.update_layout(
        title=_('Tendenze degli esami'),
        xaxis_title=_('Tipo di esame'),
        yaxis_title=_('Numero di esami'),
        yaxis2=dict(
            title=_('Risultato medio'),
            overlaying='y',
            side='right'
        ),
        barmode='group'
    )

    return fig

def plot_prediction(df, exam_type, prediction_date, predicted_value):
    fig = go.Figure()

    # Plot historical data
    fig.add_trace(go.Scatter(x=df['exam_date'], y=df['result'], mode='lines+markers', name=_("Dati storici")))

    # Plot predicted value
    fig.add_trace(go.Scatter(x=[prediction_date], y=[predicted_value], mode='markers', name=_("Valore previsto"),
                             marker=dict(size=10, color='red', symbol='star')))

    # Add reference range if available
    if 'reference_range' in df.columns and df['reference_range'].notna().any():
        ref_range = df['reference_range'].iloc[0]
        if '-' in ref_range:
            try:
                lower, upper = map(lambda x: float(x.replace(',', '.').strip()), ref_range.split('-'))
            except ValueError as e:
                print(f"Error converting reference range to float: {ref_range}")
                print(f"Error details: {e}")
                lower, upper = None, None

            if lower is not None and upper is not None:
                fig.add_hline(y=lower, line_dash="dash", line_color="green", annotation_text=_("Limite inferiore"))
                fig.add_hline(y=upper, line_dash="dash", line_color="green", annotation_text=_("Limite superiore"))
            else:
                print(f"Skipping reference range lines for exam type: {exam_type}")

    fig.update_layout(
        title=_("Previsione per l'esame: {}").format(exam_type),
        xaxis_title=_("Data"),
        yaxis_title=f"{exam_type} ({df['unit'].iloc[0]})",
        hovermode="x unified"
    )

    return fig
