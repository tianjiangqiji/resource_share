# 软件资源站部署指南
## 项目截图
- 深色模式: `https://cloud.skyjee.cn/d/lanzou/2025/05/20/682bdd2862461.jpeg`
- 主页:`https://cloud.skyjee.cn/d/lanzou/2025/05/20/682bdd22eb86e.jpeg`
- 设置:`https://cloud.skyjee.cn/d/lanzou/2025/05/20/682bdd2101652.jpeg`
## 项目概述

这是一个基于Flask和SQLite的Material Design风格的·轻量化·软件资源站，具有以下功能：

- 多级分类浏览软件资源
- 软件详情展示和下载统计
- 管理员后台（密钥认证）
- 分类和软件资源的增删改查
- 访问量和下载量统计
- 深色/浅色/系统主题切换
- 移动端自适应布局

## 目录结构

```
software_resource_site/
├── app.py                # Flask应用主程序
├── schema.sql            # 数据库初始化脚本
├── software_resource.db  # SQLite数据库文件（自动创建）
├── static/               # 静态资源目录
│   ├── style.css         # 样式表
│   ├── script.js         # 前端脚本
│   └── admin.js          # 管理后台脚本
└── templates/            # 模板目录
    ├── index.html                    # 首页
    ├── software_detail.html          # 软件详情页
    ├── admin_login.html              # 管理员登录页
    ├── admin_dashboard.html          # 管理员仪表盘
    ├── admin_main_categories.html    # 管理页
    ├── admin_main_category_form.html # 主分类编辑页
    ├── admin_sub_categories.html     # 副分类管理页
    ├── admin_sub_category_form.html  # 副分类编辑页
    ├── admin_software.html           # 软件管理页
    ├── admin_software_form.html      # 软件编辑页
    └── admin_settings.html           # 管理员设置页
```

## 开发环境部署

1. 确保已安装Python 3.6+
2. 安装Flask：
   ```bash
   pip install flask
   ```
3. 进入项目目录：
   ```bash
   cd software_resource_site
   ```
4. 运行应用：
   ```bash
   python app.py
   ```
5. 访问 http://localhost:5000 即可使用

## 生产环境部署

### 方法1：使用Gunicorn和Nginx（推荐）

1. 安装必要的包：
   ```bash
   pip install flask gunicorn
   ```

2. 创建WSGI入口文件 `wsgi.py`：
   ```python
   from app import app
   
   if __name__ == "__main__":
       app.run()
   ```

3. 使用Gunicorn启动应用：
   ```bash
   gunicorn --workers 3 --bind 0.0.0.0:8000 wsgi:app
   ```

4. 配置Nginx反向代理（需要先安装Nginx）：
   ```nginx
   server {
       listen 80;
       server_name your_domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

5. 重启Nginx：
   ```bash
   sudo systemctl restart nginx
   ```

### 方法2：使用systemd服务（Linux系统）

1. 创建systemd服务文件 `/etc/systemd/system/software-resource-site.service`：
   ```ini
   [Unit]
   Description=Software Resource Site
   After=network.target
   
   [Service]
   User=your_username
   WorkingDirectory=/path/to/software_resource_site
   ExecStart=/usr/bin/python3 app.py
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

2. 启动服务：
   ```bash
   sudo systemctl start software-resource-site
   ```

3. 设置开机自启：
   ```bash
   sudo systemctl enable software-resource-site
   ```

## 管理员访问

1. 初始管理员密钥为：`123456`
2. 访问 http://your_domain.com/admin 进入管理员登录页
3. 登录后请在设置页面修改管理员密钥

## 自定义配置

如需修改配置，请编辑 `app.py` 文件中的以下部分：
- 修改数据库路径：`DATABASE = 'software_resource.db'`
- 修改端口：`app.run(host='0.0.0.0', port=5000, debug=False)`

编辑 `index.html` 文件中的以下部分：
- 修改主页标题： 第18行`<h1 class="title">Skyjee 软件资源分享站</h1>`

编辑 `.html` 文件中的以下部分：
- 修改顶部标签页标题：全局搜索`SkyJee 软件资源站</title>`进行替换
- 替换网站图标：替换`static/favicon.ico`为你自己的图标文件
## 备份数据

定期备份SQLite数据库文件：
```bash
cp software_resource.db software_resource.db.backup
```

## 故障排除

1. 如果管理员密钥丢失：
   - 可以直接修改数据库中的密钥值：
     ```sql
     UPDATE admin_settings SET key_value = '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92' WHERE key_name = 'admin_key';
     ```
     (这将密钥重置为"123456")

2. 如果数据库损坏：
   - 使用备份文件恢复
   - 或使用schema.sql重新初始化数据库
