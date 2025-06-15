from flask import Flask, request, render_template, send_file, flash, redirect, url_for, session
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import os
import json
from werkzeug.utils import secure_filename
from base64 import b64encode

app = Flask(__name__)
app.secret_key = 'securekey987654321'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
KEYS_FOLDER = 'keys'
os.makedirs(KEYS_FOLDER, exist_ok=True)

# Tạo tài khoản mặc định
DEFAULT_USERS = ['Hiệp', 'Hoàng', 'Huy']
def initialize_default_users():
    for user in DEFAULT_USERS:
        if not os.path.exists(os.path.join(KEYS_FOLDER, f'{user}_private.pem')):
            generate_key_pair(user)

# Tạo cặp khóa RSA
def generate_key_pair(username):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    
    with open(os.path.join(KEYS_FOLDER, f'{username}_private.pem'), 'wb') as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        )
    
    with open(os.path.join(KEYS_FOLDER, f'{username}_public.pem'), 'wb') as f:
        f.write(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )

# Tải khóa
def load_private_key(username):
    with open(os.path.join(KEYS_FOLDER, f'{username}_private.pem'), 'rb') as f:
        return serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())

def load_public_key(username):
    with open(os.path.join(KEYS_FOLDER, f'{username}_public.pem'), 'rb') as f:
        return serialization.load_pem_public_key(f.read(), backend=default_backend())

# Mã hóa file
def encrypt_file(file_data, recipient_public_key):
    chunk_size = 190  # RSA 2048 với OAEP padding giới hạn ~190 bytes
    encrypted_chunks = []
    for i in range(0, len(file_data), chunk_size):
        chunk = file_data[i:i + chunk_size]
        encrypted_chunk = recipient_public_key.encrypt(
            chunk,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        encrypted_chunks.append(encrypted_chunk)
    return b''.join(encrypted_chunks)

# Giải mã file
def decrypt_file(encrypted_data, private_key):
    chunk_size = 256  # RSA 2048 tạo ra 256 bytes mỗi chunk mã hóa
    decrypted_chunks = []
    for i in range(0, len(encrypted_data), chunk_size):
        chunk = encrypted_data[i:i + chunk_size]
        try:
            decrypted_chunk = private_key.decrypt(
                chunk,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            decrypted_chunks.append(decrypted_chunk)
        except:
            raise ValueError("Lỗi giải mã chunk")
    return b''.join(decrypted_chunks)

# Xác minh chữ ký
def verify_signature(file_data, signature, public_key):
    try:
        public_key.verify(
            signature,
            file_data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except:
        return False

# Kiểm tra đăng nhập
def login_required(f):
    def wrap(*args, **kwargs):
        if 'username' not in session:
            flash('Vui lòng đăng nhập để tiếp tục!')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        if os.path.exists(os.path.join(KEYS_FOLDER, f'{username}_private.pem')):
            session['username'] = username
            flash(f'Chào mừng {username}!')
            return redirect(url_for('index'))
        flash('Tên người dùng không tồn tại!')
        return redirect(url_for('login'))
    users = [f.split('_')[0] for f in os.listdir(KEYS_FOLDER) if f.endswith('_public.pem')]
    return render_template('login.html', users=users)

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Đã đăng xuất!')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    users = [f.split('_')[0] for f in os.listdir(KEYS_FOLDER) if f.endswith('_public.pem')]
    meta_files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.endswith('.meta')]
    metadata_list = []
    for meta_file in meta_files:
        meta_path = os.path.join(app.config['UPLOAD_FOLDER'], meta_file)
        try:
            with open(meta_path, 'r') as f:
                metadata = json.load(f)
            # Kiểm tra chữ ký
            signature_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{metadata['original_filename']}.sig")
            encrypted_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{metadata['original_filename']}.enc")
            signature_status = False
            signature_b64 = ''
            if os.path.exists(signature_path) and os.path.exists(encrypted_path):
                with open(encrypted_path, 'rb') as f:
                    encrypted_data = f.read()
                with open(signature_path, 'rb') as f:
                    signature = f.read()
                    signature_b64 = b64encode(signature).decode('utf-8')
                recipient_private_key = load_private_key(metadata['recipient'])
                try:
                    decrypted_data = decrypt_file(encrypted_data, recipient_private_key)
                    sender_public_key = load_public_key(metadata['sender'])
                    signature_status = verify_signature(decrypted_data, signature, sender_public_key)
                except:
                    signature_status = False
            metadata['signature_status'] = signature_status
            metadata['signature_b64'] = signature_b64
            metadata_list.append((meta_file, metadata))
        except:
            continue
    return render_template('index.html', users=users, metadata_list=metadata_list, current_user=session['username'])

@app.route('/keys')
@login_required
def view_keys():
    username = session['username']
    private_key_path = os.path.join(KEYS_FOLDER, f'{username}_private.pem')
    public_key_path = os.path.join(KEYS_FOLDER, f'{username}_public.pem')
    
    private_key_content = ''
    public_key_content = ''
    
    if os.path.exists(private_key_path):
        with open(private_key_path, 'r') as f:
            private_key_content = f.read()
    
    if os.path.exists(public_key_path):
        with open(public_key_path, 'r') as f:
            public_key_content = f.read()
    
    return render_template('keys.html', private_key=private_key_content, public_key=public_key_content, username=username)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        if not username.isalnum():
            flash('Tên người dùng chỉ chứa chữ và số!')
            return redirect(url_for('register'))
        if os.path.exists(os.path.join(KEYS_FOLDER, f'{username}_private.pem')):
            flash('Tên người dùng đã tồn tại!')
            return redirect(url_for('register'))
        generate_key_pair(username)
        flash('Đăng ký thành công! Vui lòng đăng nhập.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files or 'signature' not in request.files or 'recipient' not in request.form:
        flash('Thiếu file, chữ ký, hoặc thông tin người nhận!')
        return redirect(url_for('index'))
    
    file = request.files['file']
    signature_file = request.files['signature']
    recipient = request.form['recipient']
    sender = session['username']
    
    if file.filename == '' or signature_file.filename == '':
        flash('Chưa chọn file hoặc chữ ký!')
        return redirect(url_for('index'))
    
    if not os.path.exists(os.path.join(KEYS_FOLDER, f'{recipient}_public.pem')):
        flash('Người nhận không tồn tại!')
        return redirect(url_for('index'))
    
    file_data = file.read()
    signature_data = signature_file.read()
    if len(file_data) > 1024 * 1024:  # Giới hạn 1MB
        flash('File quá lớn! Giới hạn 1MB.')
        return redirect(url_for('index'))
    
    # Xác minh chữ ký trước khi lưu
    sender_public_key = load_public_key(sender)
    if not verify_signature(file_data, signature_data, sender_public_key):
        flash('Chữ ký không hợp lệ! Vui lòng cung cấp chữ ký đúng.')
        return redirect(url_for('index'))
    
    recipient_public_key = load_public_key(recipient)
    try:
        encrypted_data = encrypt_file(file_data, recipient_public_key)
    except:
        flash('Lỗi mã hóa file!')
        return redirect(url_for('index'))
    
    filename = secure_filename(file.filename)
    encrypted_filename = f'{filename}.enc'
    with open(os.path.join(app.config['UPLOAD_FOLDER'], encrypted_filename), 'wb') as f:
        f.write(encrypted_data)
    
    with open(os.path.join(app.config['UPLOAD_FOLDER'], f'{filename}.sig'), 'wb') as f:
        f.write(signature_data)
    
    metadata = {
        'original_filename': filename,
        'sender': sender,
        'recipient': recipient
    }
    with open(os.path.join(app.config['UPLOAD_FOLDER'], f'{filename}.meta'), 'w') as f:
        json.dump(metadata, f)
    
    flash('File và chữ ký đã được tải lên thành công!')
    return redirect(url_for('index'))

@app.route('/download/<filename>/<file_type>')
@login_required
def download_file(filename, file_type):
    meta_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{filename}.meta')
    if not os.path.exists(meta_path):
        flash('File không tồn tại!')
        return redirect(url_for('index'))
    
    with open(meta_path, 'r') as f:
        metadata = json.load(f)
    
    sender = metadata['sender']
    recipient = metadata['recipient']
    original_filename = metadata['original_filename']
    
    if recipient != session['username']:
        flash('Bạn không có quyền truy cập file này!')
        return redirect(url_for('index'))
    
    if file_type == 'enc':
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{original_filename}.enc')
        download_name = f'{original_filename}.enc'
    elif file_type == 'sig':
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{original_filename}.sig')
        download_name = f'{original_filename}.sig'
    else:
        flash('Loại file không hợp lệ!')
        return redirect(url_for('index'))
    
    if not os.path.exists(file_path):
        flash('File không tồn tại!')
        return redirect(url_for('index'))
    
    return send_file(file_path, as_attachment=True, download_name=download_name)

@app.route('/download_decrypted/<filename>')
@login_required
def download_decrypted_file(filename):
    meta_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{filename}.meta')
    if not os.path.exists(meta_path):
        flash('File không tồn tại!')
        return redirect(url_for('index'))
    
    with open(meta_path, 'r') as f:
        metadata = json.load(f)
    
    sender = metadata['sender']
    recipient = metadata['recipient']
    original_filename = metadata['original_filename']
    
    if recipient != session['username']:
        flash('Bạn không có quyền truy cập file này!')
        return redirect(url_for('index'))
    
    encrypted_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{original_filename}.enc')
    signature_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{original_filename}.sig')
    
    if not os.path.exists(encrypted_path) or not os.path.exists(signature_path):
        flash('Dữ liệu file không đầy đủ!')
        return redirect(url_for('index'))
    
    with open(encrypted_path, 'rb') as f:
        encrypted_data = f.read()
    
    with open(signature_path, 'rb') as f:
        signature = f.read()
    
    recipient_private_key = load_private_key(recipient)
    try:
        decrypted_data = decrypt_file(encrypted_data, recipient_private_key)
    except:
        flash('Lỗi giải mã file!')
        return redirect(url_for('index'))
    
    sender_public_key = load_public_key(sender)
    if not verify_signature(decrypted_data, signature, sender_public_key):
        flash('Chữ ký không hợp lệ!')
        return redirect(url_for('index'))
    
    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], f'decrypted_{original_filename}')
    with open(temp_path, 'wb') as f:
        f.write(decrypted_data)
    
    response = send_file(temp_path, as_attachment=True, download_name=original_filename)
    os.remove(temp_path)
    return response

if __name__ == '__main__':
    initialize_default_users()
    app.run(debug=True)