import requests
import os
import pandas as pd
import numpy as np
import re
import io
from dotenv import load_dotenv

load_dotenv()

# Configuration
ALCHEMY_KEY = os.getenv("ALCHEMY_API_KEY")
ALCHEMY_URL = f"https://eth-mainnet.g.alchemy.com/v2/{ALCHEMY_KEY}"

def is_valid_ethereum_address(address):
    """Checks if the string is a valid Hexadecimal Ethereum address."""
    pattern = re.compile(r'^0x[a-fA-F0-9]{40}$')
    return bool(pattern.match(address))

def get_wallet_transfers(wallet_address):
    """Fetches 1,000 transactions from Alchemy."""
    payload = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "alchemy_getAssetTransfers",
        "params": [{
            "fromAddress": wallet_address,
            "category": ["external", "erc20"],
            "maxCount": "0x3E8" 
        }]
    }
    try:
        response = requests.post(ALCHEMY_URL, json=payload)
        if response.status_code == 200:
            return response.json().get("result", {}).get("transfers", [])
        return []
    except Exception as e:
        print(f"API Error: {e}")
        return []

def calculate_risk_score(vol, cnt, assets):
    """
    Calculates a risk score from 0-100.
    High Volume + Low Asset Diversity = Market Manipulator Risk.
    High Count + Low Volume = Bot/Spam Risk.
    """
    score = 0
    if vol > 1000: score += 40  # Whale volatility risk
    if cnt > 500: score += 30   # Bot activity risk
    if assets < 2 and cnt > 10: score += 30 # Lack of diversity risk
    return min(score, 100)

def process_analysis(transactions):
    """Full Behavioral and Risk Analysis Engine."""
    if not transactions:
        return {
            "category": "New/Inactive Wallet",
            "volume": 0,
            "count": 0,
            "assets": 0,
            "risk_score": 0
        }

    df = pd.DataFrame(transactions)
    df['value'] = df['value'].astype(float).fillna(0)
    
    vol = df['value'].sum()
    cnt = len(df)
    assets = df['asset'].nunique() if 'asset' in df.columns else 1
    
    # ML Labeling
    if vol > 500: label = "Institutional Whale"
    elif cnt > 700: label = "High-Frequency Bot"
    elif assets > 10: label = "Diversified Collector"
    elif vol > 1: label = "Active Retail User"
    else: label = "Casual User"

    return {
        "category": label,
        "volume": round(vol, 2),
        "count": cnt,
        "assets": assets,
        "risk_score": calculate_risk_score(vol, cnt, assets),
        "df": df # Keep for export
    }