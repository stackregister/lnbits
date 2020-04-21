import importlib

from flask import Flask
from flask_assets import Environment, Bundle
from flask_compress import Compress
from flask_talisman import Talisman
from os import getenv
from werkzeug.middleware.proxy_fix import ProxyFix

from .core import core_app, migrations as core_migrations
from .helpers import ExtensionManager


app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
valid_extensions = [ext for ext in ExtensionManager().extensions if ext.is_valid]


# optimization & security
# -----------------------

Compress(app)
Talisman(
    app,
    force_https=getenv("LNBITS_WITH_ONION", 0) == 0,
    content_security_policy={
        "default-src": [
            "'self'",
            "'unsafe-eval'",
            "'unsafe-inline'",
            "blob:",
            "api.opennode.co",
            "fonts.googleapis.com",
            "fonts.gstatic.com",
            "github.com",
            "avatars2.githubusercontent.com",
        ]
    },
)


# blueprints / extensions
# -----------------------

app.register_blueprint(core_app)

for ext in valid_extensions:
    try:
        ext_module = importlib.import_module(f"lnbits.extensions.{ext.code}")
        app.register_blueprint(getattr(ext_module, f"{ext.code}_ext"), url_prefix=f"/{ext.code}")
    except Exception:
        raise ImportError(f"Please make sure that the extension `{ext.code}` follows conventions.")


# filters
# -------

app.jinja_env.globals["DEBUG"] = app.config["DEBUG"]
app.jinja_env.globals["EXTENSIONS"] = valid_extensions
app.jinja_env.globals["SITE_TITLE"] = getenv("LNBITS_SITE_TITLE", "LNbits")


# assets
# ------

assets = Environment(app)
assets.url = app.static_url_path
assets.register("base_css", Bundle("scss/base.scss", filters="pyscss", output="css/base.css"))


# commands
# --------

@app.cli.command("migrate")
def migrate_databases():
    """Creates the necessary databases if they don't exist already; or migrates them."""
    core_migrations.migrate()

    for ext in valid_extensions:
        try:
            ext_migrations = importlib.import_module(f"lnbits.extensions.{ext.code}.migrations")
            ext_migrations.migrate()
        except Exception:
            raise ImportError(f"Please make sure that the extension `{ext.code}` has a migrations file.")


# init
# ----

if __name__ == "__main__":
    app.run()
