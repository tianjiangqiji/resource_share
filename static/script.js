// 全局变量
let currentTheme = localStorage.getItem('theme') || 'theme-light';
let currentMainCategoryId = null;
let currentSubCategoryId = null;

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 应用保存的主题
    applyTheme(currentTheme);
    
    // 设置抽屉的初始状态
    setDrawerState();
    
    // 加载主分类（如果在前台页面）
    if (document.getElementById('main-categories')) {
        loadMainCategories();
    }
    
    // 如果在管理面板，加载统计图表
    if (document.getElementById('visitsChart') && document.getElementById('downloadsChart')) {
        loadCharts();
    }
    
    // 如果在管理面板，加载热门软件
    if (document.getElementById('topSoftwareTable')) {
        loadTopSoftware();
    }
});

// 切换抽屉菜单的显示与隐藏
function toggleDrawer() {
    const drawer = document.getElementById('drawer');
    drawer.classList.toggle('active');
    
    // 在大屏幕上调整主内容区域和底栏的边距
    if (window.matchMedia('(min-width: 768px)').matches) {
        const mainContent = document.querySelector('.main-content');
        const footer = document.querySelector('.app-footer');
        
        if (drawer.classList.contains('active')) {
            mainContent.style.marginLeft = '280px';
            if (footer) footer.style.marginLeft = '280px';
        } else {
            mainContent.style.marginLeft = '0';
            if (footer) footer.style.marginLeft = '0';
        }
    }
}

// 点击页面其他区域时关闭抽屉（仅在移动设备上）
document.addEventListener('click', function(event) {
    const drawer = document.getElementById('drawer');
    const menuButton = document.querySelector('.menu-button');
    
    if (!drawer || !menuButton) return;

    // 如果点击的是抽屉外的区域且不是菜单按钮
    if (!drawer.contains(event.target) && event.target !== menuButton && !menuButton.contains(event.target)) {
        if (window.matchMedia('(max-width: 767px)').matches) {
            // 手机浏览时才收起抽屉
            drawer.classList.remove('active');
        }
    }
});

// 根据屏幕宽度设置抽屉的初始状态
function setDrawerState() {
    const drawer = document.getElementById('drawer');
    if (!drawer) return;
    
    const mainContent = document.querySelector('.main-content');
    const footer = document.querySelector('.app-footer');
    
    if (window.matchMedia('(max-width: 767px)').matches) {
        // 手机浏览时自动收起抽屉
        drawer.classList.remove('active');
        if (mainContent) mainContent.style.marginLeft = '0';
        if (footer) footer.style.marginLeft = '0';
    } else {
        // 电脑或大屏上默认展开抽屉
        drawer.classList.add('active');
        if (mainContent) mainContent.style.marginLeft = '280px';
        if (footer) footer.style.marginLeft = '280px';
    }
}

// 窗口大小变化时更新抽屉状态
window.addEventListener('resize', setDrawerState);

// 切换主题
function toggleTheme() {
    if (currentTheme === 'theme-light') {
        currentTheme = 'theme-dark';
    } else if (currentTheme === 'theme-dark') {
        currentTheme = 'theme-system';
    } else {
        currentTheme = 'theme-light';
    }
    
    applyTheme(currentTheme);
    localStorage.setItem('theme', currentTheme);
}

// 应用主题
function applyTheme(theme) {
    document.body.className = theme;
    
    // 更新主题图标
    const themeIcons = document.querySelectorAll('.theme-icon');
    themeIcons.forEach(icon => {
        if (theme === 'theme-light') {
            icon.textContent = 'light_mode';
        } else if (theme === 'theme-dark') {
            icon.textContent = 'dark_mode';
        } else {
            icon.textContent = 'devices';
        }
    });
}

// 加载主分类
function loadMainCategories() {
    fetch('/api/main-categories')
        .then(response => response.json())
        .then(mainCategories => {
            const mainCategoriesContainer = document.getElementById('main-categories');
            
            // 清空现有内容
            mainCategoriesContainer.innerHTML = '';
            
            // 使用获取的主分类数据
            mainCategories.forEach(category => {
                const categoryItem = document.createElement('div');
                categoryItem.className = 'category-item';
                categoryItem.innerHTML = `
                    <div class="category-header" onclick="toggleSubcategories(${category.id})">
                        <span class="material-icons">${category.icon || 'folder'}</span>
                        <span>${category.name}</span>
                        <span class="material-icons expand-icon">expand_more</span>
                    </div>
                    <div class="subcategories" id="subcategories-${category.id}">
                        <!-- 副分类将通过AJAX加载 -->
                    </div>
                `;
                mainCategoriesContainer.appendChild(categoryItem);
            });
        })
        .catch(error => console.error('Error loading categories:', error));
}

// 切换副分类显示
function toggleSubcategories(mainCategoryId) {
    const subcategoriesContainer = document.getElementById(`subcategories-${mainCategoryId}`);
    const categoryHeader = subcategoriesContainer.previousElementSibling;
    
    // 切换展开状态
    categoryHeader.classList.toggle('active');
    subcategoriesContainer.classList.toggle('active');
    
    // 如果是首次展开，加载副分类
    if (subcategoriesContainer.classList.contains('active') && subcategoriesContainer.children.length === 0) {
        loadSubcategories(mainCategoryId);
    }
}

// 加载副分类
function loadSubcategories(mainCategoryId) {
    fetch(`/api/subcategories/${mainCategoryId}`)
        .then(response => response.json())
        .then(subcategories => {
            const subcategoriesContainer = document.getElementById(`subcategories-${mainCategoryId}`);
            
            // 清空现有内容
            subcategoriesContainer.innerHTML = '';
            
            // 添加副分类
            subcategories.forEach(subcategory => {
                const subcategoryItem = document.createElement('div');
                subcategoryItem.className = 'subcategory-item';
                subcategoryItem.onclick = () => loadSoftware(subcategory.id);
                subcategoryItem.innerHTML = `
                    <span class="material-icons">${subcategory.icon || 'folder_open'}</span>
                    <span>${subcategory.name}</span>
                `;
                subcategoriesContainer.appendChild(subcategoryItem);
            });
        })
        .catch(error => console.error('Error loading subcategories:', error));
}

// 加载软件列表
function loadSoftware(subCategoryId) {
    currentSubCategoryId = subCategoryId;
    
    fetch(`/api/software/${subCategoryId}`)
        .then(response => response.json())
        .then(softwareList => {
            const softwareListContainer = document.getElementById('software-list');
            const welcomeSection = document.querySelector('.welcome-section');
            const softwareDetail = document.getElementById('software-detail');
            
            // 隐藏欢迎区域和软件详情
            if (welcomeSection) welcomeSection.style.display = 'none';
            if (softwareDetail) softwareDetail.style.display = 'none';
            
            // 显示软件列表
            softwareListContainer.style.display = 'grid';
            
            // 清空现有内容
            softwareListContainer.innerHTML = '';
            
            // 添加软件卡片
            softwareList.forEach(software => {
                const softwareCard = document.createElement('div');
                softwareCard.className = 'software-card';
                softwareCard.onclick = () => showSoftwareDetail(software);
                
                let imageHtml = '';
                if (software.image_url) {
                    imageHtml = `<img src="${software.image_url}" alt="${software.name}">`;
                } else {
                    imageHtml = `<span class="material-icons">description</span>`;
                }
                
                softwareCard.innerHTML = `
                    <div class="card-image">
                        ${imageHtml}
                    </div>
                    <div class="card-content">
                        <h3 class="card-title">${software.name}</h3>
                        <div class="card-subtitle">${software.version || ''} ${software.size ? '| ' + software.size : ''}</div>
                    </div>
                    <div class="card-actions">
                        <a href="/download/${software.id}" class="button" onclick="event.stopPropagation();">
                            <span class="material-icons">download</span>
                            <span>下载</span>
                        </a>
                    </div>
                `;
                
                softwareListContainer.appendChild(softwareCard);
            });
            
            // 如果没有软件
            if (softwareList.length === 0) {
                softwareListContainer.innerHTML = '<div class="empty-message">该分类下暂无软件</div>';
            }
            
            // 在移动设备上自动关闭抽屉
            if (window.matchMedia('(max-width: 767px)').matches) {
                const drawer = document.getElementById('drawer');
                if (drawer) drawer.classList.remove('active');
            }
        })
        .catch(error => console.error('Error loading software:', error));
}

// 显示软件详情
function showSoftwareDetail(software) {
    const softwareListContainer = document.getElementById('software-list');
    const welcomeSection = document.querySelector('.welcome-section');
    const softwareDetail = document.getElementById('software-detail');
    
    // 隐藏欢迎区域和软件列表
    if (welcomeSection) welcomeSection.style.display = 'none';
    if (softwareListContainer) softwareListContainer.style.display = 'none';
    
    // 显示软件详情
    softwareDetail.style.display = 'block';
    
    // 使用模板填充详情
    const template = document.getElementById('software-detail-template');
    if (template) {
        const content = template.content.cloneNode(true);
        
        // 填充数据
        content.querySelector('.software-name').textContent = software.name;
        content.querySelector('.software-version').textContent = software.version || '';
        
        const imageContainer = content.querySelector('.detail-image-container');
        const image = content.querySelector('.software-image');
        
        if (software.image_url) {
            image.src = software.image_url;
            image.alt = software.name;
            imageContainer.style.display = 'block';
        } else {
            imageContainer.style.display = 'none';
        }
        
        content.querySelector('.software-size').textContent = software.size || '未知';
        content.querySelector('.software-requirements').textContent = software.system_requirements || '无特殊要求';
        content.querySelector('.software-description').textContent = software.description || '暂无描述';
        
        const downloadButton = content.querySelector('.download-button');
        downloadButton.href = `/download/${software.id}`;
        
        // 清空并添加新内容
        softwareDetail.innerHTML = '';
        softwareDetail.appendChild(content);
    } else {
        // 如果没有模板，直接跳转到详情页
        window.location.href = `/software/${software.id}`;
    }
}

// 加载统计图表
function loadCharts() {
    // 访问统计图表
    fetch('/api/stats/visits')
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('visitsChart').getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.days,
                    datasets: [{
                        label: '访问量',
                        data: data.counts,
                        backgroundColor: 'rgba(63, 81, 181, 0.2)',
                        borderColor: 'rgba(63, 81, 181, 1)',
                        borderWidth: 2,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                precision: 0
                            }
                        }
                    }
                }
            });
        })
        .catch(error => console.error('Error loading visit stats:', error));
    
    // 下载统计图表
    fetch('/api/stats/downloads')
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('downloadsChart').getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.days,
                    datasets: [{
                        label: '下载量',
                        data: data.counts,
                        backgroundColor: 'rgba(255, 64, 129, 0.2)',
                        borderColor: 'rgba(255, 64, 129, 1)',
                        borderWidth: 2,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                precision: 0
                            }
                        }
                    }
                }
            });
        })
        .catch(error => console.error('Error loading download stats:', error));
}

// 加载热门软件
function loadTopSoftware() {
    fetch('/api/stats/top-software')
        .then(response => response.json())
        .then(data => {
            const tableBody = document.getElementById('topSoftwareTable');
            
            // 清空现有内容
            tableBody.innerHTML = '';
            
            // 添加热门软件
            data.forEach(software => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${software.name}</td>
                    <td>${software.download_count}</td>
                `;
                tableBody.appendChild(row);
            });
            
            // 如果没有数据
            if (data.length === 0) {
                const row = document.createElement('tr');
                row.innerHTML = '<td colspan="2">暂无数据</td>';
                tableBody.appendChild(row);
            }
        })
        .catch(error => console.error('Error loading top software:', error));
}
