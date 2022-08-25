import plotly.io as pio
import plotly.graph_objects as go

print(pio.renderers)

fig = go.Figure(
    data=[go.Bar(y=[2, 1, 3])],
    layout_title_text="A Figure Displayed with the 'svg' Renderer"
)
a  = fig.show(renderer="iframe")
print(a)