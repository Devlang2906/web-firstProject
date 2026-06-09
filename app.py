from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
import cloudinary
import cloudinary.uploader

app = Flask(__name__)

database_url = os.environ.get('DATABASE_URL', 'postgresql://postgres:Gilang123@localhost:5432/unpas_db')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = 'unpastrade2026'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
db = SQLAlchemy(app)

cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET')
)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nim = db.Column(db.String(20), unique=True, nullable=False)
    nama = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Produk(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(200), nullable=False)
    nama_penjual = db.Column(db.String(200), nullable=False)
    nim_penjual = db.Column(db.String(20), nullable=True)
    deskripsi = db.Column(db.Text, nullable=False)
    harga = db.Column(db.String(100), nullable=False)
    kategori = db.Column(db.String(100), nullable=True)
    kondisi = db.Column(db.String(50), nullable=True)
    fotos = db.Column(db.Text, nullable=True)
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
    return render_template("index.html")

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
        nim_penjual = session.get('nim', None)

      foto_filenames = []
        files = request.files.getlist('fotos')
        for file in files:
            if file and file.filename != '':
                try:
                    result = cloudinary.uploader.upload(file)
                    foto_filenames.append(result['secure_url'])
                except Exception as e:
                    print(f"Upload error: {e}")
        produk_baru = Produk(
            nama=nama, nama_penjual=nama_penjual,
            nim_penjual=nim_penjual,
            deskripsi=deskripsi, harga=harga,
            kategori=kategori, kondisi=kondisi,
            fotos=json.dumps(foto_filenames),
            whatsapp=whatsapp, instagram=instagram, tiktok=tiktok
        )
        db.session.add(produk_baru)
        db.session.commit()
        return redirect(url_for('semua_produk'))
    return render_template("posting.html")

@app.route("/produk/<int:id>")
def detail_produk(id):
    produk = Produk.query.get_or_404(id)
    nim_login = session.get('nim', None)
    bisa_hapus = nim_login and nim_login == produk.nim_penjual
    return render_template("detail_produk.html", produk=produk, bisa_hapus=bisa_hapus)

@app.route("/hapus/<int:id>")
def hapus_produk(id):
    produk = Produk.query.get_or_404(id)
    nim_login = session.get('nim', None)
    if nim_login and nim_login == produk.nim_penjual:
        db.session.delete(produk)
        db.session.commit()
    return redirect(url_for('semua_produk'))

@app.route("/foto/<filename>")
def serve_foto(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nim = request.form.get('nim', '')
        nama = request.form.get('nama', '')
        password = request.form.get('password', '')

        if not nim.isdigit():
            return render_template("register.html", error="NIM harus berupa angka!")

        existing = User.query.filter_by(nim=nim).first()
        if existing:
            return render_template("register.html", error="NIM sudah terdaftar!")

        user_baru = User(
            nim=nim,
            nama=nama,
            password=generate_password_hash(password)
        )
        db.session.add(user_baru)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nim = request.form.get('nim', '')
        password = request.form.get('password', '')

        user = User.query.filter_by(nim=nim).first()
        if user and check_password_hash(user.password, password):
            session['nim'] = user.nim
            session['nama'] = user.nama
            return redirect(url_for('index'))
        return render_template("login.html", error="NIM atau password salah!")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route("/admin-unpas")
def admin():
    users = User.query.all()
    produk_list = Produk.query.order_by(Produk.id.desc()).all()
    return render_template("admin.html", users=users, produk_list=produk_list)

@app.route("/admin-unpas/hapus-user/<int:id>")
def admin_hapus_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('admin'))

@app.route("/admin-unpas/hapus-produk/<int:id>")
def admin_hapus_produk(id):
    produk = Produk.query.get_or_404(id)
    db.session.delete(produk)
    db.session.commit()
    return redirect(url_for('admin'))
def admin():
    users = User.query.all()
    return render_template("admin.html", users=users)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0')