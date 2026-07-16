from flask import Blueprint, jsonify
from src.paper_trading.portfolio import VirtualPortfolio

metrics_bp = Blueprint('metrics', __name__)
# Uses the same underlying logic rules from your engine
portfolio_manager = VirtualPortfolio()

@metrics_bp.route('/', methods=['GET'])
def get_live_metrics():
    return jsonify({
        "status": "success",
        "performance": portfolio_manager.get_performance_metrics()
    })