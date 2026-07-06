from flask import Blueprint, jsonify, render_template_string

from openapi.spec import build_openapi_spec
from utils.http import get_proxywake_base_url

bp = Blueprint('docs', __name__)

SWAGGER_UI_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>ProxyWake API Docs</title>
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css" />
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
  <script>
    window.ui = SwaggerUIBundle({
      url: '/api/openapi.json',
      dom_id: '#swagger-ui',
      deepLinking: true,
      presets: [SwaggerUIBundle.presets.apis],
    });
  </script>
</body>
</html>
"""


@bp.route('/api/openapi.json')
def openapi_json():
    return jsonify(build_openapi_spec(get_proxywake_base_url()))


@bp.route('/api/docs')
def swagger_ui():
    return render_template_string(SWAGGER_UI_HTML)
