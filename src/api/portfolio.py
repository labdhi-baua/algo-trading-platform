from flask import Blueprint, jsonify
from src.paper_trading.portfolio import VirtualPortfolio

portfolio_bp = Blueprint('portfolio', __name__)

# Initialize a single global instance of your portfolio manager
portfolio_manager = VirtualPortfolio(initial_capital=100000)


@portfolio_bp.route('/', methods=['GET'])
def get_portfolio_summary():
    # We pass an empty dict {} as a fallback for price data if no live tick is active
    total_val = portfolio_manager.get_portfolio_value({})
    metrics = portfolio_manager.get_performance_metrics()

    return jsonify({
        "status": "success",
        "cash": portfolio_manager.cash,
        "portfolio_value": total_val,
        "initial_capital": portfolio_manager.initial_capital,
        "metrics": metrics
    })


@portfolio_bp.route('/positions', methods=['GET'])
def get_open_positions():
    # Convert your pandas dataframe summary into a clean dictionary list for the web
    df = portfolio_manager.get_open_positions_summary()
    positions = df.to_dict(orient='records') if not df.empty else []
    return jsonify({"positions": positions})