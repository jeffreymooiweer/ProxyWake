from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from wakeonlan import send_magic_packet
import logging
import os

app = Flask(__name__, static_folder='frontend/build')
CORS(app)

# Configuratie van de database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///devices.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Logging configureren
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(message)s'
)

# Device model
class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(255), nullable=False)
    ip = db.Column(db.String(15), nullable=False)
    mac = db.Column(db.String(17), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'domain': self.domain,
            'ip': self.ip,
            'mac': self.mac
        }

# Routes

@app.route('/api/devices', methods=['GET', 'POST'])
def manage_devices():
    if request.method == 'GET':
        devices = Device.query.all()
        return jsonify([device.to_dict() for device in devices]), 200
    elif request.method == 'POST':
        data = request.get_json()
        if not data.get('domain') or not data.get('ip') or not data.get('mac'):
            return jsonify({'error': 'Alle velden zijn vereist.'}), 400
        new_device = Device(domain=data['domain'], ip=data['ip'], mac=data['mac'])
        try:
            db.session.add(new_device)
            db.session.commit()
            logging.info(f'Apparaat toegevoegd: {new_device.domain}')
            return jsonify(new_device.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            logging.error(f'Fout bij toevoegen apparaat: {str(e)}')
            return jsonify({'error': 'Fout bij toevoegen apparaat.'}), 500

@app.route('/api/devices/<int:device_id>', methods=['PUT', 'DELETE'])
def modify_device(device_id):
    device = Device.query.get_or_404(device_id)
    if request.method == 'PUT':
        data = request.get_json()
        device.domain = data.get('domain', device.domain)
        device.ip = data.get('ip', device.ip)
        device.mac = data.get('mac', device.mac)
        try:
            db.session.commit()
            logging.info(f'Apparaat bijgewerkt: {device.domain}')
            return jsonify(device.to_dict()), 200
        except Exception as e:
            db.session.rollback()
            logging.error(f'Fout bij bijwerken apparaat: {str(e)}')
            return jsonify({'error': 'Fout bij bijwerken apparaat.'}), 500
    elif request.method == 'DELETE':
        try:
            db.session.delete(device)
            db.session.commit()
            logging.info(f'Apparaat verwijderd: {device.domain}')
            return jsonify({'message': 'Apparaat verwijderd.'}), 200
        except Exception as e:
            db.session.rollback()
            logging.error(f'Fout bij verwijderen apparaat: {str(e)}')
            return jsonify({'error': 'Fout bij verwijderen apparaat.'}), 500

# Serve React App
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path.startswith('api/'):
        return jsonify({'error': 'Resource niet gevonden.'}), 404
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

# Globale foutafhandeling
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource niet gevonden.'}), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Verkeerd verzoek.'}), 400

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Interne serverfout.'}), 500

if __name__ == '__main__':
    db.create_all()
    app.run(host='0.0.0.0', port=5001)
