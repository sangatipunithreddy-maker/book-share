from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os
import sqlite3

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'bookshare.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ===== Models =====
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False)
    author = db.Column(db.String(200))
    pub_year = db.Column(db.Integer)

class BookAd(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)   # poster / seller
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='available')  # available | pending | sold | reserved...
    description = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    sold_to = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    book = db.relationship('Book')
    owner = db.relationship('User', foreign_keys=[owner_id])
    sold_to_user = db.relationship('User', foreign_keys=[sold_to])

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad_id = db.Column(db.Integer, db.ForeignKey('book_ad.id'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(50))           # purchase | reserve
    status = db.Column(db.String(50), default='pending')  # pending | completed | cancelled
    date = db.Column(db.DateTime, default=datetime.utcnow)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    to_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text)
    date_received = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author_name = db.Column(db.String(200), nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

# ===== Initialize DB + safe migrations (non-destructive) =====
def safe_alter_add_column(table, column_def):
    """Run an ALTER TABLE ADD COLUMN safely using sqlite - ignore if exists."""
    # sqlite doesn't support IF NOT EXISTS for add column; check pragma table_info first
    colname = column_def.split()[0]
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("PRAGMA table_info(%s)" % table)
    cols = [r[1] for r in c.fetchall()]
    if colname not in cols:
        try:
            c.execute("ALTER TABLE %s ADD COLUMN %s" % (table, column_def))
            conn.commit()
        except Exception as e:
            print("Safe alter failed:", e)
    conn.close()

def init_db():
    # Create tables if missing
    with app.app_context():
        db.create_all()
        # Make sure BookAd.sold_to exists (safe add)
        safe_alter_add_column('book_ad', 'sold_to INTEGER')
        # create a few demo users/records only if empty
        if User.query.count() == 0:
            u1 = User(name='Alice Student', email='alice.student@example.com', password='student123', role='student')
            u2 = User(name='Bob Faculty', email='bob.faculty@example.com', password='faculty123', role='faculty')
            u3 = User(name='Carol Admin', email='carol.admin@example.com', password='admin123', role='admin')
            db.session.add_all([u1,u2,u3]); db.session.commit()
            b1 = Book(name='Introduction to Algorithms', author='Cormen', pub_year=2009)
            b2 = Book(name='Clean Code', author='Robert C. Martin', pub_year=2008)
            b3 = Book(name='Design Patterns', author='Gamma et al.', pub_year=1994)
            db.session.add_all([b1,b2,b3]); db.session.commit()
            ad1 = BookAd(book_id=b1.id, owner_id=u1.id, price=40, description='Good condition')
            ad2 = BookAd(book_id=b2.id, owner_id=u2.id, price=35, description='Slightly used')
            ad3 = BookAd(book_id=b3.id, owner_id=u1.id, price=50, description='Hardcover')
            db.session.add_all([ad1,ad2,ad3]); db.session.commit()

# ===== Routes =====
@app.route('/')
def index():
    return render_template('bookshare.html')

# --- Auth ---
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password','')
    role = data.get('role','')
    user = User.query.filter_by(email=email).first()
    if not user or user.password != password or user.role != role:
        return jsonify({'ok':False, 'message':'Invalid credentials'}), 400
    return jsonify({'ok':True, 'user':{'id':user.id,'name':user.name,'email':user.email,'role':user.role}})

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.json or {}
    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password','')
    role = data.get('role','')
    if not name or not email or not password or not role:
        return jsonify({'ok':False,'message':'Missing fields'}),400
    if User.query.filter_by(email=email).first():
        return jsonify({'ok':False,'message':'Email already used'}),400
    user = User(name=name,email=email,password=password,role=role)
    db.session.add(user); db.session.commit()
    return jsonify({'ok':True, 'user':{'id':user.id,'name':user.name,'email':user.email,'role':user.role}})

# --- Ads ---
@app.route('/api/ads', methods=['GET','POST'])
def api_ads():
    if request.method=='GET':
        # ONLY return available ads for listing
        ads = BookAd.query.filter_by(status='available').order_by(BookAd.date_posted.desc()).all()
        out = []
        for a in ads:
            out.append({
                'adID': a.id,
                'book': {'name': a.book.name, 'author': a.book.author, 'pubYear': a.book.pub_year},
                'ownerProfileID': a.owner_id,
                'price': a.price,
                'status': a.status,
                'description': a.description
            })
        return jsonify({'ok':True, 'ads': out})
    else:
        data = request.json or {}
        title = data.get('title'); author = data.get('author'); year = data.get('year'); price = data.get('price'); desc = data.get('desc',''); owner_id = data.get('owner_id')
        if not title or not author or price is None or owner_id is None:
            return jsonify({'ok':False,'message':'Missing fields (title/author/price/owner required)'}),400
        book = Book(name=title, author=author, pub_year=year)
        db.session.add(book); db.session.commit()
        ad = BookAd(book_id=book.id, owner_id=owner_id, price=float(price), description=desc)
        db.session.add(ad); db.session.commit()
        n = Notification(to_user_id=owner_id, content=f'Your ad ({ad.id}) was created for \"{book.name}\".')
        db.session.add(n); db.session.commit()
        return jsonify({'ok':True, 'adID': ad.id})

@app.route('/api/ads/<int:ad_id>', methods=['DELETE'])
def api_delete_ad(ad_id):
    data = request.json or {}
    requester_id = data.get('requester_id')
    ad = BookAd.query.get_or_404(ad_id)
    owner = User.query.get(ad.owner_id)
    requester = User.query.get(requester_id) if requester_id else None
    allowed = False
    if requester and requester.role=='admin':
        allowed = True
    elif requester and requester.role=='faculty' and owner and owner.role=='student':
        allowed = True
    elif requester and owner and requester.id==owner.id:
        allowed = True
    if not allowed:
        return jsonify({'ok':False,'message':'Not allowed'}),403
    db.session.delete(ad); db.session.commit()
    if owner:
        n = Notification(to_user_id=owner.id, content=f'Your ad #{ad_id} was removed by user {requester.name if requester else "system"}')
        db.session.add(n); db.session.commit()
    return jsonify({'ok':True})

# --- Transactions (create request) ---
@app.route('/api/transactions', methods=['POST'])
def api_transactions():
    data = request.json or {}
    ad_id = data.get('ad_id')
    buyer_id = data.get('buyer_id')
    type_tx = data.get('type', 'purchase')

    if ad_id is None or buyer_id is None:
        return jsonify({'ok':False,'message':'ad_id and buyer_id required'}),400

    ad = BookAd.query.get_or_404(ad_id)
    buyer = User.query.get(buyer_id)
    if not buyer:
        return jsonify({'ok': False, 'message': 'Buyer not found'}), 400
    if ad.owner_id == buyer_id:
        return jsonify({'ok': False, 'message': 'You cannot buy your own book'}), 400

    # Can't request if not available
    if ad.status != 'available':
        return jsonify({'ok':False,'message':'Ad not available for requests'}), 400
    # Can't request if not available
    if ad.status != 'available':
        return jsonify({'ok':False,'message':'Ad not available for requests'}), 400

    # create pending transaction
    t = Transaction(ad_id=ad_id, buyer_id=buyer_id, type=type_tx, status='pending')
    db.session.add(t)
    # mark ad as pending so others can't request
    ad.status = 'pending'
    db.session.commit()

    # notify owner and buyer
    owner = User.query.get(ad.owner_id)
    if owner:
        n1 = Notification(
            to_user_id=owner.id,
            content=f'New {type_tx} request for your book \"{ad.book.name}\" (Ad #{ad.id}) from {buyer.name}. Transaction ID: {t.id}'
        )
        db.session.add(n1)
    n2 = Notification(
        to_user_id=buyer.id,
        content=f'Your {type_tx} request for \"{ad.book.name}\" is pending owner approval (Transaction ID: {t.id}).'
    )
    db.session.add(n2)
    db.session.commit()
    return jsonify({'ok': True, 'transactionID': t.id})

# --- Accept transaction (owner completes sale) ---
@app.route('/api/transactions/<int:tx_id>/accept', methods=['POST'])
def api_accept_transaction(tx_id):
    data = request.json or {}
    owner_id = data.get('owner_id')
    if owner_id is None:
        return jsonify({'ok':False,'message':'owner_id required'}),400

    t = Transaction.query.get_or_404(tx_id)
    ad = BookAd.query.get_or_404(t.ad_id)
    if ad.owner_id != owner_id:
        return jsonify({'ok':False,'message':'Only the ad owner can accept this transaction'}),403

    if t.status != 'pending':
        return jsonify({'ok':False,'message':'Transaction is not pending'}),400

    buyer = User.query.get(t.buyer_id)
    if not buyer:
        return jsonify({'ok':False,'message':'Buyer not found'}),400

    # Accept: mark completed, set sold_to, change ad.status to sold
    t.status = 'completed'
    ad.status = 'sold'
    ad.sold_to = buyer.id
    db.session.commit()

    seller = User.query.get(owner_id)
    n_to_buyer = Notification(
        to_user_id=buyer.id,
        content=f'Your request (Transaction #{t.id}) for \"{ad.book.name}\" was accepted by {seller.name}. Payment completed.'
    )
    n_to_owner = Notification(
        to_user_id=owner_id,
        content=f'You accepted Transaction #{t.id}. Book \"{ad.book.name}\" marked sold to {buyer.name}.'
    )
    db.session.add_all([n_to_buyer, n_to_owner])
    db.session.commit()

    return jsonify({'ok':True, 'transactionID': t.id})

# --- Sales list for owners (pending requests) ---
@app.route('/api/sales/<int:user_id>', methods=['GET'])
def api_sales(user_id):
    ads = BookAd.query.filter_by(owner_id=user_id).all()
    ad_ids = [a.id for a in ads]
    if not ad_ids:
        return jsonify({'ok':True, 'sales': []})
    pending_txs = Transaction.query.filter(Transaction.ad_id.in_(ad_ids), Transaction.status=='pending').order_by(Transaction.date.desc()).all()
    out = []
    for t in pending_txs:
        ad = BookAd.query.get(t.ad_id)
        buyer = User.query.get(t.buyer_id)
        out.append({
            'transactionID': t.id,
            'adID': ad.id,
            'book': ad.book.name,
            'author': ad.book.author,
            'price': ad.price,
            'type': t.type,
            'date': t.date.isoformat(),
            'buyer': {'id': buyer.id, 'name': buyer.name, 'email': buyer.email}
        })
    return jsonify({'ok':True, 'sales': out})

# --- Blogs (new feature) ---
@app.route('/api/blogs', methods=['GET','POST'])
def api_blogs():
    if request.method == 'GET':
        blogs = Blog.query.order_by(Blog.date_posted.desc()).all()
        out = []
        for b in blogs:
            out.append({
                'id': b.id,
                'title': b.title,
                'content': b.content,
                'author_id': b.author_id,
                'author_name': b.author_name,
                'date_posted': b.date_posted.isoformat()
            })
        return jsonify({'ok':True, 'blogs': out})
    else:
        data = request.json or {}
        title = (data.get('title') or '').strip()
        content = (data.get('content') or '').strip()
        author_id = data.get('author_id')
        if not title or not content or not author_id:
            return jsonify({'ok':False, 'message':'Missing fields (title/content/author_id)'}),400
        author = User.query.get(author_id)
        if not author:
            return jsonify({'ok':False, 'message':'Author not found'}),400
        # Only students and faculty can post
        if author.role not in ['student', 'faculty']:
            return jsonify({'ok':False, 'message':'Only students and faculty can post blogs'}),403
        b = Blog(title=title, content=content, author_id=author.id, author_name=author.name)
        db.session.add(b); db.session.commit()
        return jsonify({'ok':True, 'blog': {'id': b.id, 'title': b.title}})

@app.route('/api/blogs/<int:blog_id>', methods=['PUT','DELETE'])
def api_blog_modify(blog_id):
    b = Blog.query.get_or_404(blog_id)
    data = request.json or {}
    user_id = data.get('user_id')
    if user_id is None:
        return jsonify({'ok':False,'message':'user_id required'}),400
    user = User.query.get(user_id)
    if not user:
        return jsonify({'ok':False,'message':'user not found'}),400

    if request.method == 'PUT':
        # Edit: author OR faculty OR admin
        if not (user.id == b.author_id or user.role in ['faculty','admin']):
            return jsonify({'ok':False,'message':'Not allowed to edit blog'}),403
        title = (data.get('title') or '').strip()
        content = (data.get('content') or '').strip()
        if title: b.title = title
        if content: b.content = content
        db.session.commit()
        return jsonify({'ok':True, 'blog': {'id': b.id, 'title': b.title}})

    else:
        # DELETE: only faculty or admin
        if user.role not in ['faculty','admin']:
            return jsonify({'ok':False,'message':'Not allowed to delete blog'}),403
        db.session.delete(b); db.session.commit()
        return jsonify({'ok':True})

# --- Notifications and users and history ---
@app.route('/api/notifications/<int:user_id>', methods=['GET'])
def api_notifications(user_id):
    notes = Notification.query.filter_by(to_user_id=user_id).order_by(Notification.date_received.desc()).all()
    out = [{'id':n.id,'content':n.content,'date':n.date_received.isoformat(),'is_read':n.is_read} for n in notes]
    return jsonify({'ok':True,'notifications':out})

@app.route('/api/users', methods=['GET','DELETE'])
def api_users():
    if request.method=='GET':
        users = User.query.all()
        out = [{'id':u.id,'name':u.name,'email':u.email,'role':u.role} for u in users]
        return jsonify({'ok':True,'users':out})
    else:
        data = request.json or {}
        user_id = data.get('user_id')
        requester_id = data.get('requester_id')
        if not user_id:
            return jsonify({'ok':False,'message':'user_id required'}),400
        if requester_id is None:
            return jsonify({'ok':False,'message':'requester_id required'}),400
        requester = User.query.get(requester_id)
        if not requester:
            return jsonify({'ok':False,'message':'requester not found'}),400
        # Only admin can delete accounts, and admin cannot delete other admins
        if requester.role != 'admin':
            return jsonify({'ok':False,'message':'Only admin can delete accounts'}),403
        target = User.query.get_or_404(user_id)
        if target.role == 'admin':
            return jsonify({'ok':False,'message':'Admins cannot delete other admins'}),403
        db.session.delete(target); db.session.commit()
        return jsonify({'ok':True})

@app.route('/api/history/<int:user_id>')
def api_history(user_id):
    transactions = Transaction.query.filter_by(buyer_id=user_id).order_by(Transaction.date.desc()).all()
    purchased, reserved, pending = [], [], []

    for t in transactions:
        ad = BookAd.query.get(t.ad_id)
        if not ad:
            continue
        item = {
            'ad_id': ad.id,
            'book': ad.book.name,
            'author': ad.book.author,
            'price': ad.price,
            'type': t.type,
            'status': t.status,
            'date': t.date.strftime("%Y-%m-%d %H:%M")
        }
        if t.status == 'pending':
            pending.append(item)
        elif t.type == 'purchase' and t.status == 'completed':
            purchased.append(item)
        elif t.type == 'reserve' and t.status == 'completed':
            reserved.append(item)

    # sold ads (ads owned by this user that were sold)
    sold_ads = BookAd.query.filter_by(owner_id=user_id, status='sold').all()
    sold = [{'ad_id': ad.id, 'book': ad.book.name, 'price': ad.price,
             'description': ad.description, 'status': ad.status, 'sold_to': ad.sold_to}
            for ad in sold_ads]

    return jsonify({'ok': True, 'pending': pending, 'purchased': purchased, 'reserved': reserved, 'sold': sold})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
