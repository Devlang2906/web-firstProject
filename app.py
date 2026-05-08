from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import json

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
    kategori = db.Column(db.String(100), nullable=True)
    kondisi = db.Column(db.String(50), nullable=True)
    fotos = db.Column(db.Text, nullable=True)  # JSON list foto
    whatsapp = db.Column(db.String(50), nullable=True)
    instagram = db.Column(db.String(100), nullable=True)
    tiktok = db.Column(db.String(100), nullable=True)

    @property
    def foto_list(self):
        if self.fotos:
            return json.loads(self.fotos)
        return []

    @property
    def foto_utama(self):
        lst = self.foto_list
        return lst[0] if lst else None

@app.route("/")
def index():
    produk_list = Produk.query.order_by(Produk.id.desc()).all()
    return render_template("index.html", produk_list=produk_list)

@app.route("/produk")
def semua_produk():
    produk_list = Produk.query.order_by(Produk.id.desc()).all()
    return render_template("produk.html", produk_list=produk_list)

@app.route("/posting", methods=["GET", "POST"])
def posting():
    if request.method == "POST":
        nama = request.form.get('nama', '')
        nama_penjual = request.form.get('nama_penjual', '')
        deskripsi = request.form.get('deskripsi', '')
        harga = request.form.get('harga', '')
        kategori = request.form.get('kategori', '')
        kondisi = request.form.get('kondisi', '')
        whatsapp = request.form.get('whatsapp', '')
        instagram = request.form.get('instagram', '')
        tiktok = request.form.get('tiktok', '')

        foto_filenames = []
        files = request.files.getlist('fotos')
        for file in files:
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                foto_filenames.append(filename)

        produk_baru = Produk(
            nama=nama, nama_penjual=nama_penjual,
            deskripsi=deskripsi, harga=harga,
            kategori=kategori, kondisi=kondisi,
            fotos=json.dumps(foto_filenames),
            whatsapp=whatsapp, instagram=instagram, tiktok=tiktok
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
def serve_foto(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0')