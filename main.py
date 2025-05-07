from app import app
import routes  # noqa: F401
import routes_invoices  # noqa: F401
import routes_reports  # noqa: F401

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
