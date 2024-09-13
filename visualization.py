import plotly.graph_objects as go
import gettext

# Set up localization
it = gettext.translation('messages', localedir='locales', languages=['it'])
it.install()
_ = it.gettext

def plot_exam_results(df, exam_type):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['exam_date'], y=df['result'], mode='lines+markers', name=exam_type))

    # Add reference range if available
    if 'reference_range' in df.columns and df['reference_range'].notna().any():
        ref_range = df['reference_range'].iloc[0]
        if '-' in ref_range:
            lower, upper = map(float, ref_range.split('-'))
            fig.add_hline(y=lower, line_dash="dash", line_color="red", annotation_text=_("Limite inferiore"))
            fig.add_hline(y=upper, line_dash="dash", line_color="red", annotation_text=_("Limite superiore"))

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
