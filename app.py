import os
import sqlite3
import hashlib
import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, g, abort

# 创建Flask应用实例
app = Flask(__name__)
app.secret_key = os.urandom(24)  # 使用随机生成的密钥

# 数据库配置
DATABASE = 'software_resource.db'

# 数据库连接函数
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  # 返回字典形式的结果
        db.execute("PRAGMA foreign_keys = ON")  # 启用外键约束
    return db

# 关闭数据库连接
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# 执行SQL查询
def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

# 执行SQL更新
def update_db(query, args=()):
    conn = get_db()
    conn.execute(query, args)
    conn.commit()

# 初始化数据库
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r', encoding='utf-8') as f:
            db.cursor().executescript(f.read())
        db.commit()

# 记录访问统计
def record_visit(page_type, page_id=None):
    ip_address = request.remote_addr
    user_agent = request.user_agent.string
    update_db('INSERT INTO visit_statistics (page_type, page_id, ip_address, user_agent) VALUES (?, ?, ?, ?)',
              [page_type, page_id, ip_address, user_agent])

# 记录下载统计
def record_download(software_id):
    ip_address = request.remote_addr
    user_agent = request.user_agent.string
    update_db('INSERT INTO download_statistics (software_id, ip_address, user_agent) VALUES (?, ?, ?)',
              [software_id, ip_address, user_agent])
    # 更新软件下载计数
    update_db('UPDATE software_resources SET download_count = download_count + 1 WHERE id = ?', [software_id])

# 验证管理员密钥
def verify_admin_key(key):
    hashed_key = hashlib.sha256(key.encode()).hexdigest()
    stored_key = query_db('SELECT key_value FROM admin_settings WHERE key_name = ?', ['admin_key'], one=True)
    if stored_key and stored_key['key_value'] == hashed_key:
        return True
    return False

# 检查是否已登录
def is_admin():
    return session.get('admin_logged_in', False)

# 管理员登录装饰器
def admin_required(f):
    def decorated_function(*args, **kwargs):
        if not is_admin():
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# 首页路由
@app.route('/')
def index():
    record_visit('home')
    main_categories = query_db('SELECT * FROM main_categories ORDER BY display_order, name')
    return render_template('index.html', main_categories=main_categories, is_admin=is_admin())

# 获取副分类
@app.route('/api/subcategories/<int:main_id>')
def get_subcategories(main_id):
    sub_categories = query_db('SELECT * FROM sub_categories WHERE main_category_id = ? ORDER BY display_order, name', [main_id])
    return jsonify([dict(row) for row in sub_categories])

# 获取软件资源
@app.route('/api/software/<int:sub_id>')
def get_software(sub_id):
    software_list = query_db('SELECT * FROM software_resources WHERE sub_category_id = ? ORDER BY version DESC, name', [sub_id])
    return jsonify([dict(row) for row in software_list])

# 软件详情页
@app.route('/software/<int:software_id>')
def software_detail(software_id):
    record_visit('software', software_id)
    software = query_db('SELECT * FROM software_resources WHERE id = ?', [software_id], one=True)
    if software:
        return render_template('software_detail.html', software=software, is_admin=is_admin())
    abort(404)

# 记录下载
@app.route('/download/<int:software_id>')
def download(software_id):
    software = query_db('SELECT download_url FROM software_resources WHERE id = ?', [software_id], one=True)
    if software:
        record_download(software_id)
        return redirect(software['download_url'])
    abort(404)

# 管理员登录页面
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        admin_key = request.form['admin_key']
        if verify_admin_key(admin_key):
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            error = '密钥不正确'
    return render_template('admin_login.html', error=error)

# 管理员登出
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))

# 管理员仪表板
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    # 获取统计数据
    total_software = query_db('SELECT COUNT(*) as count FROM software_resources', one=True)['count']
    total_visits = query_db('SELECT COUNT(*) as count FROM visit_statistics', one=True)['count']
    total_downloads = query_db('SELECT COUNT(*) as count FROM download_statistics', one=True)['count']
    
    # 获取最近访问记录
    recent_visits = query_db('''
        SELECT v.*, 
               CASE 
                   WHEN v.page_type = 'home' THEN '首页' 
                   WHEN v.page_type = 'category' THEN (SELECT name FROM main_categories WHERE id = v.page_id)
                   WHEN v.page_type = 'software' THEN (SELECT name FROM software_resources WHERE id = v.page_id)
               END as page_name
        FROM visit_statistics v
        ORDER BY v.visit_time DESC LIMIT 10
    ''')
    
    # 获取最近下载记录
    recent_downloads = query_db('''
        SELECT d.*, s.name as software_name
        FROM download_statistics d
        JOIN software_resources s ON d.software_id = s.id
        ORDER BY d.download_time DESC LIMIT 10
    ''')
    
    return render_template('admin_dashboard.html', 
                          total_software=total_software,
                          total_visits=total_visits,
                          total_downloads=total_downloads,
                          recent_visits=recent_visits,
                          recent_downloads=recent_downloads)

# 管理主分类
@app.route('/admin/main-categories')
@admin_required
def admin_main_categories():
    categories = query_db('SELECT * FROM main_categories ORDER BY display_order, name')
    return render_template('admin_main_categories.html', categories=categories)

# 添加/编辑主分类
@app.route('/admin/main-category/<int:category_id>', methods=['GET', 'POST'])
@app.route('/admin/main-category/new', methods=['GET', 'POST'])
@admin_required
def admin_main_category(category_id=None):
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        icon = request.form['icon']
        display_order = request.form['display_order'] or 0
        
        if category_id:
            update_db('UPDATE main_categories SET name = ?, description = ?, icon = ?, display_order = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                     [name, description, icon, display_order, category_id])
        else:
            update_db('INSERT INTO main_categories (name, description, icon, display_order) VALUES (?, ?, ?, ?)',
                     [name, description, icon, display_order])
        
        return redirect(url_for('admin_main_categories'))
    
    category = None
    if category_id:
        category = query_db('SELECT * FROM main_categories WHERE id = ?', [category_id], one=True)
        if not category:
            abort(404)
    
    return render_template('admin_main_category_form.html', category=category)

# 删除主分类
@app.route('/admin/main-category/delete/<int:category_id>', methods=['POST'])
@admin_required
def delete_main_category(category_id):
    update_db('DELETE FROM main_categories WHERE id = ?', [category_id])
    return redirect(url_for('admin_main_categories'))

# 管理副分类
@app.route('/admin/sub-categories/<int:main_id>')
@admin_required
def admin_sub_categories(main_id):
    main_category = query_db('SELECT * FROM main_categories WHERE id = ?', [main_id], one=True)
    if not main_category:
        abort(404)
    
    sub_categories = query_db('SELECT * FROM sub_categories WHERE main_category_id = ? ORDER BY display_order, name', [main_id])
    return render_template('admin_sub_categories.html', main_category=main_category, sub_categories=sub_categories)

# 添加/编辑副分类
@app.route('/admin/sub-category/<int:category_id>', methods=['GET', 'POST'])
@app.route('/admin/sub-category/new/<int:main_id>', methods=['GET', 'POST'])
@admin_required
def admin_sub_category(category_id=None, main_id=None):
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        icon = request.form['icon']
        display_order = request.form['display_order'] or 0
        main_category_id = request.form['main_category_id']
        
        if category_id:
            update_db('UPDATE sub_categories SET name = ?, description = ?, icon = ?, display_order = ?, main_category_id = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                     [name, description, icon, display_order, main_category_id, category_id])
        else:
            update_db('INSERT INTO sub_categories (name, description, icon, display_order, main_category_id) VALUES (?, ?, ?, ?, ?)',
                     [name, description, icon, display_order, main_category_id])
        
        return redirect(url_for('admin_sub_categories', main_id=main_category_id))
    
    category = None
    main_categories = query_db('SELECT * FROM main_categories ORDER BY display_order, name')
    
    if category_id:
        category = query_db('SELECT * FROM sub_categories WHERE id = ?', [category_id], one=True)
        if not category:
            abort(404)
        main_id = category['main_category_id']
    
    return render_template('admin_sub_category_form.html', category=category, main_categories=main_categories, main_id=main_id)

# 删除副分类
@app.route('/admin/sub-category/delete/<int:category_id>', methods=['POST'])
@admin_required
def delete_sub_category(category_id):
    sub_category = query_db('SELECT main_category_id FROM sub_categories WHERE id = ?', [category_id], one=True)
    if not sub_category:
        abort(404)
    
    main_id = sub_category['main_category_id']
    update_db('DELETE FROM sub_categories WHERE id = ?', [category_id])
    return redirect(url_for('admin_sub_categories', main_id=main_id))

# 管理软件资源
@app.route('/admin/software/<int:sub_id>')
@admin_required
def admin_software(sub_id):
    sub_category = query_db('SELECT * FROM sub_categories WHERE id = ?', [sub_id], one=True)
    if not sub_category:
        abort(404)
    
    software_list = query_db('SELECT * FROM software_resources WHERE sub_category_id = ? ORDER BY version DESC, name', [sub_id])
    return render_template('admin_software.html', sub_category=sub_category, software_list=software_list)

# 添加/编辑软件资源
@app.route('/admin/software-item/<int:software_id>', methods=['GET', 'POST'])
@app.route('/admin/software-item/new/<int:sub_id>', methods=['GET', 'POST'])
@admin_required
def admin_software_item(software_id=None, sub_id=None):
    if request.method == 'POST':
        name = request.form['name']
        version = request.form['version']
        size = request.form['size']
        system_requirements = request.form['system_requirements']
        description = request.form['description']
        download_url = request.form['download_url']
        image_url = request.form['image_url']
        sub_category_id = request.form['sub_category_id']
        
        if software_id:
            update_db('''UPDATE software_resources 
                       SET name = ?, version = ?, size = ?, system_requirements = ?, 
                           description = ?, download_url = ?, image_url = ?, 
                           sub_category_id = ?, updated_at = CURRENT_TIMESTAMP 
                       WHERE id = ?''',
                     [name, version, size, system_requirements, description, 
                      download_url, image_url, sub_category_id, software_id])
        else:
            update_db('''INSERT INTO software_resources 
                       (name, version, size, system_requirements, description, 
                        download_url, image_url, sub_category_id) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                     [name, version, size, system_requirements, description, 
                      download_url, image_url, sub_category_id])
        
        return redirect(url_for('admin_software', sub_id=sub_category_id))
    
    software = None
    sub_categories = query_db('SELECT sc.*, mc.name as main_name FROM sub_categories sc JOIN main_categories mc ON sc.main_category_id = mc.id ORDER BY mc.display_order, mc.name, sc.display_order, sc.name')
    
    if software_id:
        software = query_db('SELECT * FROM software_resources WHERE id = ?', [software_id], one=True)
        if not software:
            abort(404)
        sub_id = software['sub_category_id']
    
    return render_template('admin_software_form.html', software=software, sub_categories=sub_categories, sub_id=sub_id)

# 删除软件资源
@app.route('/admin/software-item/delete/<int:software_id>', methods=['POST'])
@admin_required
def delete_software(software_id):
    software = query_db('SELECT sub_category_id FROM software_resources WHERE id = ?', [software_id], one=True)
    if not software:
        abort(404)
    
    sub_id = software['sub_category_id']
    update_db('DELETE FROM software_resources WHERE id = ?', [software_id])
    return redirect(url_for('admin_software', sub_id=sub_id))

# 管理员设置
@app.route('/admin/settings', methods=['GET', 'POST'])
@admin_required
def admin_settings():
    if request.method == 'POST':
        current_key = request.form['current_key']
        new_key = request.form['new_key']
        
        if verify_admin_key(current_key):
            hashed_new_key = hashlib.sha256(new_key.encode()).hexdigest()
            update_db('UPDATE admin_settings SET key_value = ?, updated_at = CURRENT_TIMESTAMP WHERE key_name = ?',
                     [hashed_new_key, 'admin_key'])
            return redirect(url_for('admin_dashboard'))
        else:
            error = '当前密钥不正确'
            return render_template('admin_settings.html', error=error)
    
    return render_template('admin_settings.html')

# 统计数据API
@app.route('/api/stats/visits')
@admin_required
def api_stats_visits():
    # 获取过去7天的访问统计
    days = []
    counts = []
    
    for i in range(6, -1, -1):
        date = (datetime.datetime.now() - datetime.timedelta(days=i)).strftime('%Y-%m-%d')
        next_date = (datetime.datetime.now() - datetime.timedelta(days=i-1)).strftime('%Y-%m-%d')
        
        count = query_db('''
            SELECT COUNT(*) as count FROM visit_statistics 
            WHERE visit_time >= ? AND visit_time < ?
        ''', [date, next_date], one=True)['count']
        
        days.append(date)
        counts.append(count)
    
    return jsonify({'days': days, 'counts': counts})

@app.route('/api/stats/downloads')
@admin_required
def api_stats_downloads():
    # 获取过去7天的下载统计
    days = []
    counts = []
    
    for i in range(6, -1, -1):
        date = (datetime.datetime.now() - datetime.timedelta(days=i)).strftime('%Y-%m-%d')
        next_date = (datetime.datetime.now() - datetime.timedelta(days=i-1)).strftime('%Y-%m-%d')
        
        count = query_db('''
            SELECT COUNT(*) as count FROM download_statistics 
            WHERE download_time >= ? AND download_time < ?
        ''', [date, next_date], one=True)['count']
        
        days.append(date)
        counts.append(count)
    
    return jsonify({'days': days, 'counts': counts})

@app.route('/api/stats/top-software')
@admin_required
def api_stats_top_software():
    # 获取下载量最高的软件
    top_software = query_db('''
        SELECT id, name, download_count 
        FROM software_resources 
        ORDER BY download_count DESC 
        LIMIT 10
    ''')
    
    return jsonify([dict(row) for row in top_software])

# 创建数据库文件（如果不存在）
if not os.path.exists(DATABASE):
    init_db()

# 启动应用
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
# 获取主分类
@app.route('/api/main-categories')
def get_main_categories():
    main_categories = query_db('SELECT * FROM main_categories ORDER BY display_order, name')
    return jsonify([dict(row) for row in main_categories])

@app.route('/api/stats/top-software')
@admin_required
def api_stats_top_software():
    # 获取下载量最高的软件
    top_software = query_db('''
        SELECT id, name, download_count 
        FROM software_resources 
        ORDER BY download_count DESC 
        LIMIT 10
    ''')
    
    return jsonify([dict(row) for row in top_software])

# 创建数据库文件（如果不存在）
if not os.path.exists(DATABASE):
    init_db()

# 启动应用
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
