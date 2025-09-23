import plotly.graph_objects as go

def create_base_fig(x_vals, y_vals, img_str, cropped_img):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=x_vals,
        y=y_vals,
        mode='markers',
        marker=dict(color='red', size=10),
        name='Overlay Points'
    ))

    fig.update_layout(
        images=[dict(
            source=img_str,
            xref="x",
            yref="y",
            x=0,
            y=0,
            sizex=cropped_img.width,
            sizey=cropped_img.height,
            sizing="stretch",
            opacity=1.0,
            layer="below"
        )],
        xaxis=dict(
            range=[0, cropped_img.width],
            scaleanchor="y",
            scaleratio=1,
            visible=False
        ),
        yaxis=dict(
            range=[cropped_img.height, 0],
            visible=False
        ),
        margin=dict(l=0, r=0, t=0, b=0),
    )
    return fig
