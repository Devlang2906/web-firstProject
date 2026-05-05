from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
db = SQLAlchemy(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class Produk(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(200), nullable=False)
    nama_penjual = db.Column(db.String(200), nullable=False)
    deskripsi = db.Column(db.Text, nullable=False)
    harga = db.Column(db.String(100), nullable=False)
    foto = db.Column(db.String(300), nullable=True)
    whatsapp = db.Column(db.String(50), nullable=True)
    instagram = db.Column(db.String(100), nullable=True)
    tiktok = db.Column(db.String(100), nullable=True)

@app.route("/")
def index():
    produk_list = Produk.query.order_by(Produk.id.desc()).all()
    return render_template("index.html", produk_list=produk_list)

@app.route("/posting", methods=["GET", "POST"])
def posting():
    if request.method == "POST":
        nama = request.form.get('nama', '')
        nama_penjual = request.form.get('nama_penjual', '')
        deskripsi = request.form.get('deskripsi', '')
        harga = request.form.get('harga', '')
        whatsapp = request.form.get('whatsapp', '')
        instagram = request.form.get('instagram', '')
        tiktok = request.form.get('tiktok', '')
        foto = None

        file = request.files.get('foto')
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            foto = filename

        produk_baru = Produk(
            nama=nama, nama_penjual=nama_penjual,
            deskripsi=deskripsi, harga=harga,
            foto=foto, whatsapp=whatsapp,
            instagram=instagram, tiktok=tiktok
        )
        db.session.add(produk_baru)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template("posting.html")

@app.route("/produk/<int:id>")
def detail_produk(id):
    produk = Produk.query.get_or_404(id)
    return render_template("detail_produk.html", produk=produk)

@app.route("/hapus/<int:id>")
def hapus_produk(id):
    produk = Produk.query.get_or_404(id)
    db.session.delete(produk)
    db.session.commit()
    return redirect(url_for('index'))

@app.route("/foto/<filename>")
def foto(filename):
    from flask import send_from_directory
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
from flask import send_from_directory

@app.route('/uploads/<filename>')
def foto(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
    