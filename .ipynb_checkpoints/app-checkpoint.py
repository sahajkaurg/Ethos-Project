from flask import Flask, render_template, request
from pymongo import MongoClient

app = Flask(__name__)
client = MongoClient("mongodb://localhost:27017/")
db = client["ethos_db"]
collection = db["raw_transactions"]

@app.route("/", methods=["GET", "POST"])
def index():
    analysis = None
    if request.method == "POST":
        wallet = request.form.get("wallet_address")
        # Query MongoDB for this specific wallet
        txs = list(collection.find({"from": wallet}))
        
        if txs:
            count = len(txs)
            avg_gas = sum(float(t['gasPrice']) for t in txs) / count
            analysis = {
                "address": wallet,
                "count": count,
                "avg_gas": round(avg_gas / 1e9, 2) # Convert to Gwei
            }
            
    return render_template("index.html", analysis=analysis)

if __name__ == "__main__":
    app.run(debug=True)