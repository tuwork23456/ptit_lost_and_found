import sys
try:
    import app.main
    print("Import OK")
except Exception as e:
    import traceback
    traceback.print_exc()
    sys.exit(1)
