// 管理面板专用脚本
document.addEventListener('DOMContentLoaded', function() {
    // 如果在管理面板，加载统计图表
    if (document.getElementById('visitsChart') && document.getElementById('downloadsChart')) {
        loadAdminCharts();
    }
    
    // 如果在管理面板，加载热门软件
    if (document.getElementById('topSoftwareTable')) {
        loadTopSoftware();
    }
});

// 加载管理面板统计图表
function loadAdminCharts() {
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
