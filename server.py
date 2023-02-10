import os
import traceback

from flask import Flask

from global_config_generator import GlobalConfigGenerator

# Flask application
app = Flask(__name__)

config_in_path = os.environ.get(
    'INPUT_CONFIG_PATH', 'config-in/'
).rstrip('/') + '/'


# routes
@app.route("/generate_configs", methods=['POST'])
def generate_configs():
    """Generate all service configs"""
    log_output = ""
    try:
        generator = GlobalConfigGenerator(config_in_path, app.logger)
        generator.write_configs()
        logger = generator.get_logger()

        for entry in logger.log_entries():
            log_output += entry["level"].upper() + ": " + \
                          str(entry["msg"]) + "\n"

        return log_output, 200
    except Exception as e:
        return log_output + "\n\nPython Exception: " + str(e) + "\n" + traceback.format_exc(), 500


# local webserver
if __name__ == '__main__':
    print("Starting GlobalConfigGenerator service...")
    app.run(host='localhost', port=5010, debug=True)
