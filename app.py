# main.py
from app_factory import create_app
from log import setup_root_logger

setup_root_logger()
app = create_app()

if __name__ == '__main__':
    # you can parameterize host/port or read from env
    app.run(use_reloader=False, debug=True, host='0.0.0.0', port=5000, threaded=True)