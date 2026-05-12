from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///perpustakaan_digital.db'
app.config['SECRET_KEY'] = 'kunci_rahasia_123'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Akun(db.Model):
    __tablename__ = 'akun'
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    tanggal_daftar = db.Column(db.DateTime, default=datetime.utcnow)

    kutipan_rel = db.relationship('Kutipan', backref='pembuat', lazy=True)

class Lisensi(db.Model):
    __tablename__ = 'lisensi'
    id = db.Column(db.Integer, primary_key=True)
    jenis_akses = db.Column(db.String(50), nullable=False)
    ebooks = db.relationship('EBook', backref='lisensi_ref', lazy=True)

class EBook(db.Model):
    __tablename__ = 'ebook'
    isbn = db.Column(db.String(20), primary_key=True)
    judul = db.Column(db.String(200), nullable=False)
    penulis = db.Column(db.String(100), nullable=False)
    fk_id_lisensi = db.Column(db.Integer, db.ForeignKey('lisensi.id'))
    kutipan_buku = db.relationship('Kutipan', backref='buku', lazy=True)

class Kutipan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teks_kutipan = db.Column(db.Text, nullable=False)
    fk_id_akun = db.Column(db.Integer, db.ForeignKey('akun.id'), nullable=False)
    fk_isbn = db.Column(db.String(20), db.ForeignKey('ebook.isbn'), nullable=False)


@app.route('/')
@app.route('/admin')
def admin_dashboard():

    return render_template('index.html', 
                           akuns=Akun.query.all(), 
                           ebooks=EBook.query.all(),
                           lisensis=Lisensi.query.all(),
                           kutipans=Kutipan.query.all())

@app.route('/add_akun', methods=['POST'])
def add_akun():
    baru = Akun(nama=request.form['nama'], email=request.form['email'])
    db.session.add(baru)
    db.session.commit()
    flash('Akun berhasil ditambahkan!')
    return redirect(url_for('admin_dashboard'))

@app.route('/add_ebook', methods=['POST'])
def add_ebook():
    baru = EBook(
        isbn=request.form['isbn'],
        judul=request.form['judul'],
        penulis=request.form['penulis'],
        fk_id_lisensi=request.form['lisensi_id']
    )
    db.session.add(baru)
    db.session.commit()
    flash('E-Book berhasil didaftarkan!')
    return redirect(url_for('admin_dashboard'))

@app.route('/add_kutipan', methods=['POST'])
def add_kutipan():
    baru = Kutipan(
        teks_kutipan=request.form['teks'],
        fk_id_akun=request.form['akun_id'],
        fk_isbn=request.form['isbn']
    )
    db.session.add(baru)
    db.session.commit()
    flash('Kutipan sosial berhasil dibagikan!')
    return redirect(url_for('admin_dashboard'))


@app.route('/delete_akun/<int:id>')
def delete_akun(id):
    target = Akun.query.get_or_404(id)
    db.session.delete(target)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/update_akun/<int:id>', methods=['POST'])
def update_akun(id):
    target = Akun.query.get_or_404(id)
    target.nama = request.form['nama']
    target.email = request.form['email']
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
     
        if not Lisensi.query.first():
            db.session.add(Lisensi(jenis_akses="Publik"))
            db.session.add(Lisensi(jenis_akses="Premium"))
            db.session.commit()
    app.run(debug=True)