from flask import Blueprint, jsonify
from src.paper_trading.database import PaperTradingDatabase

trades_bp = Blueprint('trades', __name__)
db = PaperTradingDatabase()

@trades_bp.route('/history', methods=['GET'])
def get_trade_history():
    try:
        all_trades = db.get_all_trades()
        return jsonify({
            "status": "success",
            "count": len(all_trades),
            "history": all_trades
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500