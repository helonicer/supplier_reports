from confetti import Config
import os

app_path=os.path.dirname(os.path.abspath(__file__))

options = dict(
    app_path=app_path,
    reports_dir=os.path.join(app_path,"reports"),
    debug=True
)

config = Config()
config.extend(options)