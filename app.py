from flask import Flask, render_template, request, Response
from blockchain_utils import (
    get_wallet_transfers, 
    process_analysis, 
    is_valid_ethereum_address
)
import io

app = Flask(__name__)

# Global variable to temporarily store data for export (for demo purposes)
last_analysis_df = None

@app.route('/', methods=['GET', 'POST'])
def index():
    global last_analysis_df
    result = None
    
    if request.method == 'POST':
        address = request.form.get('wallet_address', '').strip()
        
        if not is_valid_ethereum_address(address):
            result = {"error": "Invalid Ethereum Address format."}
        else:
            raw_data = get_wallet_transfers(address)
            analysis = process_analysis(raw_data)
            
            if "df" in analysis:
                last_analysis_df = analysis.pop("df") # Remove DF from dict for frontend
            
            result = analysis
            result["address"] = address

    return render_template('index.html', result=result)

@app.route('/download')
def download():
    """Route to download the analyzed transactions as a CSV."""
    global last_analysis_df
    if last_analysis_df is not None:
        proxy = io.StringIO()
        last_analysis_df.to_csv(proxy, index=False)
        return Response(
            proxy.getvalue(),
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=ethos_analysis.csv"}
        )
    return "No data available", 404

if __name__ == '__main__':
    app.run(debug=True)