/**
 * Logger service for tracking API requests and responses
 */
export interface LogEntry {
  id: string;
  timestamp: string;
  method: string;
  url: string;
  status?: number;
  statusText?: string;
  requestData?: any;
  responseData?: any;
  error?: string;
  duration?: number;
  type: 'request' | 'response' | 'error';
}

class LoggerService {
  private logs: LogEntry[] = [];
  private maxLogs = 1000; // Giới hạn số lượng logs

  /**
   * Thêm log entry mới
   */
  addLog(entry: Omit<LogEntry, 'id' | 'timestamp'>): void {
    const logEntry: LogEntry = {
      id: this.generateId(),
      timestamp: new Date().toISOString(),
      ...entry
    };

    this.logs.unshift(logEntry); // Thêm vào đầu array

    // Giới hạn số lượng logs
    if (this.logs.length > this.maxLogs) {
      this.logs = this.logs.slice(0, this.maxLogs);
    }

    // Lưu vào localStorage
    this.saveToStorage();
  }

  /**
   * Lấy tất cả logs
   */
  getLogs(): LogEntry[] {
    return this.logs;
  }

  /**
   * Lấy logs theo filter
   */
  getLogsByFilter(filter: {
    type?: string;
    status?: number;
    method?: string;
    url?: string;
    startDate?: string;
    endDate?: string;
  }): LogEntry[] {
    return this.logs.filter(log => {
      if (filter.type && log.type !== filter.type) return false;
      if (filter.status && log.status !== filter.status) return false;
      if (filter.method && log.method !== filter.method) return false;
      if (filter.url && !log.url.includes(filter.url)) return false;
      if (filter.startDate && log.timestamp < filter.startDate) return false;
      if (filter.endDate && log.timestamp > filter.endDate) return false;
      return true;
    });
  }

  /**
   * Xóa tất cả logs
   */
  clearLogs(): void {
    this.logs = [];
    this.saveToStorage();
  }

  /**
   * Xóa logs cũ hơn 24h
   */
  clearOldLogs(): void {
    const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();
    this.logs = this.logs.filter(log => log.timestamp > oneDayAgo);
    this.saveToStorage();
  }

  /**
   * Lưu logs vào localStorage
   */
  private saveToStorage(): void {
    try {
      localStorage.setItem('api_logs', JSON.stringify(this.logs));
    } catch (error) {
      console.warn('Failed to save logs to localStorage:', error);
    }
  }

  /**
   * Load logs từ localStorage
   */
  loadFromStorage(): void {
    try {
      const stored = localStorage.getItem('api_logs');
      if (stored) {
        this.logs = JSON.parse(stored);
      }
    } catch (error) {
      console.warn('Failed to load logs from localStorage:', error);
    }
  }

  /**
   * Tạo ID duy nhất
   */
  private generateId(): string {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
  }

  /**
   * Export logs ra file
   */
  exportLogs(): void {
    const dataStr = JSON.stringify(this.logs, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `api-logs-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    URL.revokeObjectURL(url);
  }

  /**
   * Lấy thống kê logs
   */
  getStats(): {
    total: number;
    byType: Record<string, number>;
    byStatus: Record<string, number>;
    byMethod: Record<string, number>;
    errors: number;
    avgDuration: number;
  } {
    const stats = {
      total: this.logs.length,
      byType: {} as Record<string, number>,
      byStatus: {} as Record<string, number>,
      byMethod: {} as Record<string, number>,
      errors: 0,
      avgDuration: 0
    };

    let totalDuration = 0;
    let durationCount = 0;

    this.logs.forEach(log => {
      // Count by type
      stats.byType[log.type] = (stats.byType[log.type] || 0) + 1;
      
      // Count by status
      if (log.status) {
        stats.byStatus[log.status.toString()] = (stats.byStatus[log.status.toString()] || 0) + 1;
      }
      
      // Count by method
      stats.byMethod[log.method] = (stats.byMethod[log.method] || 0) + 1;
      
      // Count errors
      if (log.type === 'error' || (log.status && log.status >= 400)) {
        stats.errors++;
      }
      
      // Calculate average duration
      if (log.duration) {
        totalDuration += log.duration;
        durationCount++;
      }
    });

    stats.avgDuration = durationCount > 0 ? totalDuration / durationCount : 0;

    return stats;
  }
}

// Tạo singleton instance
export const loggerService = new LoggerService();

// Load logs từ storage khi khởi tạo
loggerService.loadFromStorage();

// Auto clear old logs mỗi 1 giờ
setInterval(() => {
  loggerService.clearOldLogs();
}, 60 * 60 * 1000);
