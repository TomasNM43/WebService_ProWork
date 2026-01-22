import sys
sys.stdout = sys.stderr

try:
    import cx_Oracle
    print("cx_Oracle importado OK", flush=True)
except Exception as e:
    print(f"ERROR cx_Oracle: {e}", flush=True)
    raise

try:
    from constants import DSN
    print(f"DSN: {DSN}", flush=True)
except Exception as e:
    print(f"ERROR constants: {e}", flush=True)
    raise

from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    return "Test OK"

print("App iniciada correctamente", flush=True)
