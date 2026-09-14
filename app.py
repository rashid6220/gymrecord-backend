from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# SQLite डेटाबेस सेटअप
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'gym_records.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Member मॉडल (टेबल स्ट्रक्चर)
class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    address = db.Column(db.String(250), nullable=True)
    fee = db.Column(db.Float, nullable=False, default=0.0)
    due = db.Column(db.Float, nullable=False, default=0.0)
    join_date = db.Column(db.String(20), nullable=False)
    close_date = db.Column(db.String(20), nullable=False)
    photo = db.Column(db.Text, nullable=True) # Base64 स्ट्रिंग के रूप में फोटो

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "address": self.address or "N/A",
            "fee": self.fee,
            "due": self.due,
            "join_date": self.join_date,
            "close_date": self.close_date,
            "photo": self.photo or ""
        }

# डेटाबेस टेबल बनाना
with app.app_context():
    db.create_all()

# ----------------- ROUTES -----------------

# 1. मुख्य पेज लोड करने के लिए
@app.route('/')
def home():
    return render_template('index.html')

# 2. सभी मेंबर्स का डेटा गेट (GET) करने की API
@app.route('/api/members', methods=['GET'])
def get_members():
    try:
        members = Member.query.order_by(Member.id.desc()).all()
        return jsonify([member.to_dict() for member in members]), 200
    except Exception as e:
        print("Error fetching members:", str(e))
        return jsonify({"error": "Failed to fetch data"}), 500

# 3. नया मेंबर ऐड (POST) करने की API
@app.route('/api/add_member', methods=['POST'])
def add_member():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Invalid request body"}), 400

        # फील्ड्स चेक करें
        name = data.get('name')
        phone = data.get('phone')
        join_date = data.get('join_date')
        close_date = data.get('close_date')

        if not name or not phone or not join_date or not close_date:
            return jsonify({"error": "Name, phone, join date, and close date are required."}), 400

        new_member = Member(
            name=name,
            phone=phone,
            address=data.get('address', ''),
            fee=float(data.get('fee', 0)),
            due=float(data.get('due', 0)),
            join_date=join_date,
            close_date=close_date,
            photo=data.get('photo', '')
        )

        db.session.add(new_member)
        db.session.commit()

        return jsonify({"message": "Member added successfully!", "member": new_member.to_dict()}), 201

    except Exception as e:
        db.session.rollback()
        print("Error adding member:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)