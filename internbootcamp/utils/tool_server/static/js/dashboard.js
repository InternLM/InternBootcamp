/**
 * 仪表板自动刷新和实时更新逻辑
 */

class Dashboard {
    constructor() {
        this.refreshInterval = 3000; // 3秒
        this.refreshTimer = null;
        this.isRefreshing = false;
        this.apiBase = '/api/dashboard';
    }

    /**
     * 初始化仪表板
     */
    init() {
        console.log('仪表板初始化...');
        this.startAutoRefresh();
        this.setupEventListeners();
    }

    /**
     * 设置事件监听器
     */
    setupEventListeners() {
        // 可以添加手动刷新按钮等
    }

    /**
     * 开始自动刷新
     */
    startAutoRefresh() {
        this.refreshTimer = setInterval(() => {
            if (!this.isRefreshing) {
                this.refreshData();
            }
        }, this.refreshInterval);
    }

    /**
     * 停止自动刷新
     */
    stopAutoRefresh() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
            this.refreshTimer = null;
        }
    }

    /**
     * 刷新数据
     */
    async refreshData() {
        if (this.isRefreshing) {
            return;
        }

        this.isRefreshing = true;
        try {
            const response = await fetch(this.apiBase);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            this.updateDashboard(data);
        } catch (error) {
            console.error('刷新数据失败:', error);
            this.showError('刷新数据失败，请稍后重试');
        } finally {
            this.isRefreshing = false;
        }
    }

    /**
     * 更新仪表板
     */
    updateDashboard(data) {
        // 更新统计信息
        this.updateStats(data.stats);
        
        // 更新Worker列表
        this.updateWorkers(data.workers);
        
        // 更新工具列表
        this.updateTools(data.tools);
        
        // 更新最后更新时间
        this.updateTime(data.update_time);
    }

    /**
     * 更新统计信息
     */
    updateStats(stats) {
        // 添加更新动画
        const workersStat = document.getElementById('workers-stat');
        const toolsStat = document.getElementById('tools-stat');
        const instancesStat = document.getElementById('instances-stat');

        if (workersStat) {
            workersStat.classList.add('updating');
            setTimeout(() => {
                workersStat.textContent = `${stats.alive_workers}/${stats.total_workers}`;
                workersStat.classList.remove('updating');
            }, 150);
        }

        if (toolsStat) {
            toolsStat.classList.add('updating');
            setTimeout(() => {
                toolsStat.textContent = stats.total_tools;
                toolsStat.classList.remove('updating');
            }, 150);
        }

        if (instancesStat) {
            instancesStat.classList.add('updating');
            setTimeout(() => {
                instancesStat.textContent = stats.total_instances;
                instancesStat.classList.remove('updating');
            }, 150);
        }
    }

    /**
     * 更新Worker列表
     */
    updateWorkers(workers) {
        const container = document.getElementById('workers-container');
        if (!container) return;

        if (workers.length === 0) {
            container.innerHTML = '<div class="no-workers">暂无已注册的Worker节点</div>';
            return;
        }

        // 创建Worker卡片HTML
        const workersHTML = workers.map(worker => {
            const statusClass = worker.is_healthy ? 'status-alive' : 'status-dead';
            const statusText = worker.is_healthy ? '🟢 在线' : '🔴 离线';
            const hostInfo = worker.host_info || {};
            
            return `
                <div class="worker-card ${statusClass}" data-worker-id="${worker.worker_id}">
                    <div class="worker-header">
                        <h3>${this.escapeHtml(worker.worker_id)}</h3>
                        <span class="status-badge">${statusText}</span>
                    </div>
                    <div class="worker-info">
                        <p><strong>🌐 URL:</strong> <code>${this.escapeHtml(worker.worker_url)}</code></p>
                        <p><strong>🔧 工具:</strong> <span class="tools-list">${this.escapeHtml(worker.tools_list)}</span></p>
                        <p><strong>📦 活跃实例:</strong> <span class="instance-count">${worker.instance_count}</span></p>
                        <p><strong>💓 最后心跳:</strong> <span class="heartbeat-time">${this.escapeHtml(worker.heartbeat_text)}</span></p>
                        <p><strong>🖥️  主机:</strong> ${this.escapeHtml(hostInfo.hostname || 'N/A')} (${this.escapeHtml(hostInfo.ip || 'N/A')})</p>
                        <p><strong>📅 注册时间:</strong> ${this.escapeHtml(worker.registered_at || 'N/A')}</p>
                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = workersHTML;
    }

    /**
     * 更新工具列表
     */
    updateTools(tools) {
        const container = document.getElementById('tools-container');
        if (!container) return;

        if (tools.length === 0) {
            container.innerHTML = '<div class="no-tools">暂无可用工具</div>';
            return;
        }

        // 创建工具卡片HTML
        const toolsHTML = tools.map(tool => {
            const statusClass = tool.worker_count > 0 ? 'tool-available' : 'tool-unavailable';
            return `
                <div class="tool-item ${statusClass}" data-tool-name="${this.escapeHtml(tool.name)}">
                    <span class="tool-name">${this.escapeHtml(tool.name)}</span>
                    <span class="tool-workers">${tool.worker_count} 个Worker可用</span>
                </div>
            `;
        }).join('');

        container.innerHTML = toolsHTML;
    }

    /**
     * 更新最后更新时间
     */
    updateTime(time) {
        const updateTimeElement = document.getElementById('update-time');
        if (updateTimeElement) {
            updateTimeElement.textContent = time;
        }
    }

    /**
     * 显示错误信息
     */
    showError(message) {
        // 可以添加错误提示UI
        console.error(message);
    }

    /**
     * HTML转义
     */
    escapeHtml(text) {
        if (text == null) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    const dashboard = new Dashboard();
    dashboard.init();
});

