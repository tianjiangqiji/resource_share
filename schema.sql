-- 主分类表
CREATE TABLE main_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    icon TEXT,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 副分类表
CREATE TABLE sub_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    main_category_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    icon TEXT,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (main_category_id) REFERENCES main_categories(id) ON DELETE CASCADE
);

-- 软件资源表
CREATE TABLE software_resources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sub_category_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    version TEXT,
    size TEXT,
    system_requirements TEXT,
    description TEXT,
    download_url TEXT NOT NULL,
    image_url TEXT,
    download_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sub_category_id) REFERENCES sub_categories(id) ON DELETE CASCADE
);

-- 访问统计表
CREATE TABLE visit_statistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    page_type TEXT NOT NULL,
    page_id INTEGER,
    ip_address TEXT,
    user_agent TEXT,
    visit_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 下载统计表
CREATE TABLE download_statistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    software_id INTEGER NOT NULL,
    ip_address TEXT,
    user_agent TEXT,
    download_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (software_id) REFERENCES software_resources(id) ON DELETE CASCADE
);

-- 管理员密钥表
CREATE TABLE admin_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key_name TEXT NOT NULL,
    key_value TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 初始数据
-- 管理员密钥初始化 (SHA-256加密的"123456")
INSERT INTO admin_settings (key_name, key_value) 
VALUES ('admin_key', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92');

-- 添加测试主分类
INSERT INTO main_categories (name, description) 
VALUES ('测试主分类', '这是一个测试主分类');

-- 添加测试副分类
INSERT INTO sub_categories (main_category_id, name, description) 
VALUES (1, '测试副分类', '这是一个测试副分类');

-- 添加测试软件资源
INSERT INTO software_resources (sub_category_id, name, version, size, system_requirements, description, download_url) 
VALUES (1, '测试软件', '1.0', '10MB', 'Windows 10/macOS/Linux', '这是一个测试软件的详细描述。', 'https://example.com/download');
