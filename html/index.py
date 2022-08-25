from flask import Flask, render_template
import plotly.graph_objects as go
import json
import plotly
import plotly.io as pio

app = Flask(__name__)


#https://stackoverflow.com/questions/4828406/import-a-python-module-into-a-jinja-template
#https://plotly.com/python/creating-and-updating-figures/
#https://plotly.com/python/renderers/

def create_fig(retailers, skus, title, price_evolution_data):   
    ## create traces
    fig = go.Figure()

    ## navigate for each retail and sku
    for retail, sku in zip(retailers, skus):
        ## select the sku and retail
        query = price_evolution_data.loc[(price_evolution_data['sku'] == sku) & (price_evolution_data['retail'] == retail)]
        price = query["price"] ## get the price
        date = query["date"] ## get the date
        
        fig.add_trace(go.Scatter(x=date.values,
                                 y=price.values,                                
                                 name=retail))
        
    fig.update_traces(mode='lines+markers')
    fig.update_layout(title={
                            'text': title,
                            'y':0.9,
                            'x':0.5,
                            'xanchor': 'center',
                            'yanchor': 'top'})
    
    return fig


@app.route("/")
def pagina_principal():
    retailers = ["wong", "metro", "plaza_vea", "tottus", "vivanda"]
    skus = ["59539001", "59539001", "497497", "inca-kola-gaseosa-10174358/p/", "497497"]
    title = 'INKA COLA 500ML'
    fig = create_fig(retailers, skus, title, price_evolution_data)
    #graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    #fig = fig.show()
    #fig = fig.show(renderer="iframe")
    return render_template('index.html', graphJSON=fig)

if __name__ == '__main__':
    import pandas as pd
    price_evolution_data = pd.read_csv("price_evolution.csv")
    app.run(debug=True)

