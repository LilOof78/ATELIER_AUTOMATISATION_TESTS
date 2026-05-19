from flask import Flask, jsonify, redirect, render_template, request, url_for

from storage import get_last_run, init_db, list_runs, save_run
from tester.runner import run_all_tests

app = Flask(__name__)
init_db()


@app.route("/")
def index():
    return redirect(url_for("dashboard"))


@app.route("/run")
def run_tests():
    run_data = run_all_tests()
    save_run(run_data)

    if request.args.get("format") == "json":
        return jsonify(run_data)

    return redirect(url_for("dashboard"))


@app.route("/dashboard")
def dashboard():
    runs = list_runs(limit=20)
    last_run = runs[0] if runs else None
    return render_template("dashboard.html", runs=runs, last_run=last_run)


@app.route("/history.json")
def history_json():
    return jsonify(list_runs(limit=50))


@app.route("/health")
def health():
    last_run = get_last_run()

    if not last_run:
        return jsonify({
            "status": "UNKNOWN",
            "message": "Aucun run enregistré pour le moment"
        }), 200

    failed = last_run["summary"]["failed"]

    if failed == 0:
        status = "OK"
    else:
        status = "DEGRADED"

    return jsonify({
        "status": status,
        "api": last_run["api"],
        "timestamp": last_run["timestamp"],
        "summary": last_run["summary"]
    }), 200


if __name__ == "__main__":
    app.run(debug=True)