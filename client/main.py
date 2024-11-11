from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QLineEdit, QPushButton, QTableWidget, 
                           QTableWidgetItem, QFileDialog, QComboBox, QSpinBox, 
                           QListWidget, QStackedWidget, QDialog, QFormLayout,
                           QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from publisher import PublishManager, PublishTask
import logging
import json
import os

class AccountDialog(QDialog):
    """账号添加/编辑对话框"""
    def __init__(self, parent=None, account_data=None):
        super().__init__(parent)
        self.setWindowTitle("账号配置")
        self.setMinimumWidth(400)
        
        layout = QFormLayout()
        
        # 账号备注
        self.name_input = QLineEdit()
        if account_data and 'name' in account_data:
            self.name_input.setText(account_data['name'])
        layout.addRow("账号备注:", self.name_input)
        
        # Cookie
        self.cookie_input = QLineEdit()
        if account_data and 'cookie' in account_data:
            self.cookie_input.setText(account_data['cookie'])
        layout.addRow("Cookie:", self.cookie_input)
        
        # 代理
        self.proxy_input = QLineEdit()
        if account_data and 'proxy' in account_data:
            self.proxy_input.setText(account_data['proxy'])
        layout.addRow("代理:", self.proxy_input)
        
        # 发布模式
        self.mode_select = QComboBox()
        self.mode_select.addItems(["正常发布", "循环发布"])
        if account_data and 'mode' in account_data:
            self.mode_select.setCurrentIndex(account_data['mode'] - 1)
        self.mode_select.currentIndexChanged.connect(self.on_mode_changed)
        layout.addRow("发布模式:", self.mode_select)
        
        # 循环发布参数
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 1440)
        self.interval_spin.setValue(30)
        if account_data and 'interval' in account_data:
            self.interval_spin.setValue(account_data['interval'])
        layout.addRow("间隔(分钟):", self.interval_spin)
        
        self.float_spin = QSpinBox()
        self.float_spin.setRange(1, 60)
        self.float_spin.setValue(15)
        if account_data and 'float' in account_data:
            self.float_spin.setValue(account_data['float'])
        layout.addRow("浮动(分钟):", self.float_spin)
        
        self.threshold_spin = QSpinBox()
        self.threshold_spin.setRange(1, 100)
        self.threshold_spin.setValue(10)
        if account_data and 'threshold' in account_data:
            self.threshold_spin.setValue(account_data['threshold'])
        layout.addRow("阈值(条):", self.threshold_spin)
        
        # 确定取消按钮
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addRow(buttons_layout)
        
        self.setLayout(layout)
        self.on_mode_changed(self.mode_select.currentIndex())
    
    def on_mode_changed(self, index):
        is_cycle = index == 1
        self.interval_spin.setVisible(is_cycle)
        self.float_spin.setVisible(is_cycle)
        self.threshold_spin.setVisible(is_cycle)
    
    def get_account_data(self):
        return {
            'name': self.name_input.text(),
            'cookie': self.cookie_input.text(),
            'proxy': self.proxy_input.text(),
            'mode': self.mode_select.currentIndex() + 1,
            'interval': self.interval_spin.value(),
            'float': self.float_spin.value(),
            'threshold': self.threshold_spin.value()
        }

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("小红书发布客户端")
        self.setMinimumSize(1200, 800)
        
        # 初始化发布管理器
        self.publish_manager = PublishManager(max_workers=5)
        
        # 加载账号配置
        self.accounts = self.load_accounts()
        
        # 创建主界面
        self.setup_ui()
        
        # 创建定时器用于更新状态
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(1000)

    def setup_ui(self):
        central_widget = QWidget()
        layout = QHBoxLayout()
        
        # 左侧账号列表
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        
        # 账号列表
        self.account_list = QListWidget()
        self.account_list.currentRowChanged.connect(self.on_account_selected)
        self.update_account_list()
        
        # 账号管理按钮
        account_buttons = QHBoxLayout()
        add_account_btn = QPushButton("添加账号")
        add_account_btn.clicked.connect(self.add_account)
        edit_account_btn = QPushButton("编辑账号")
        edit_account_btn.clicked.connect(self.edit_account)
        del_account_btn = QPushButton("删除账号")
        del_account_btn.clicked.connect(self.delete_account)
        
        account_buttons.addWidget(add_account_btn)
        account_buttons.addWidget(edit_account_btn)
        account_buttons.addWidget(del_account_btn)
        
        left_layout.addWidget(QLabel("账号列表"))
        left_layout.addWidget(self.account_list)
        left_layout.addLayout(account_buttons)
        left_widget.setLayout(left_layout)
        
        # 右侧内容区
        self.content_stack = QStackedWidget()
        
        # 添加到主布局
        layout.addWidget(left_widget, 1)  # 1是拉伸因子
        layout.addWidget(self.content_stack, 4)  # 4是拉伸因子
        
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def create_account_page(self, account_data):
        """创建账号对应的内容页"""
        page = QWidget()
        layout = QVBoxLayout()
        
        # 视频列表
        video_group = QWidget()
        video_layout = QVBoxLayout()
        
        # 文件夹选择
        folder_layout = QHBoxLayout()
        folder_path = QLineEdit()
        folder_path.setReadOnly(True)
        if 'folder' in account_data:
            folder_path.setText(account_data['folder'])
        select_btn = QPushButton("选择视频文件夹")
        select_btn.clicked.connect(lambda: self.select_folder(folder_path))
        folder_layout.addWidget(folder_path)
        folder_layout.addWidget(select_btn)
        
        # 视频表格
        video_table = QTableWidget()
        video_table.setColumnCount(7)
        video_table.setHorizontalHeaderLabels([
            "视频文件", "商品ID", "商品名称", "标题", "正文", "封面路径", "发布时间"
        ])
        
        if 'videos' in account_data:
            self.load_videos_to_table(video_table, account_data['videos'])
        
        video_layout.addLayout(folder_layout)
        video_layout.addWidget(video_table)
        video_group.setLayout(video_layout)
        
        # 发布控制
        control_group = QWidget()
        control_layout = QHBoxLayout()
        
        start_btn = QPushButton("开始发布")
        start_btn.clicked.connect(lambda: self.start_publish(account_data['cookie']))
        pause_btn = QPushButton("暂停发布")
        pause_btn.clicked.connect(lambda: self.pause_publish(account_data['cookie']))
        stop_btn = QPushButton("停止发布")
        stop_btn.clicked.connect(lambda: self.stop_publish(account_data['cookie']))
        
        control_layout.addWidget(start_btn)
        control_layout.addWidget(pause_btn)
        control_layout.addWidget(stop_btn)
        control_group.setLayout(control_layout)
        
        # 状态显示
        status_label = QLabel()
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(video_group)
        layout.addWidget(control_group)
        layout.addWidget(status_label)
        
        page.setLayout(layout)
        return page

    def load_accounts(self):
        """加载账号配置"""
        try:
            if os.path.exists('accounts.json'):
                with open('accounts.json', 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logging.error(f"加载账号配置失败: {e}")
        return {}

    def save_accounts(self):
        """保存账号配置"""
        try:
            with open('accounts.json', 'w', encoding='utf-8') as f:
                json.dump(self.accounts, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"保存账号配置失败: {e}")

    def update_account_list(self):
        """更新账号列表"""
        self.account_list.clear()
        for cookie, account in self.accounts.items():
            self.account_list.addItem(account['name'])

    def add_account(self):
        """添加账号"""
        dialog = AccountDialog(self)
        if dialog.exec():
            account_data = dialog.get_account_data()
            self.accounts[account_data['cookie']] = account_data
            self.save_accounts()
            self.update_account_list()
            
            # 创建并添加账号页面
            page = self.create_account_page(account_data)
            self.content_stack.addWidget(page)

    def edit_account(self):
        """编辑账号"""
        current_row = self.account_list.currentRow()
        if current_row < 0:
            return
            
        cookie = list(self.accounts.keys())[current_row]
        account_data = self.accounts[cookie]
        
        dialog = AccountDialog(self, account_data)
        if dialog.exec():
            new_data = dialog.get_account_data()
            self.accounts[new_data['cookie']] = new_data
            self.save_accounts()
            self.update_account_list()
            
            # 更新账号页面
            page = self.create_account_page(new_data)
            self.content_stack.removeWidget(self.content_stack.widget(current_row))
            self.content_stack.insertWidget(current_row, page)

    def delete_account(self):
        """删除账号"""
        current_row = self.account_list.currentRow()
        if current_row < 0:
            return
            
        cookie = list(self.accounts.keys())[current_row]
        reply = QMessageBox.question(
            self, '确认删除', 
            f'确定要删除账号 {self.accounts[cookie]["name"]} 吗？',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            del self.accounts[cookie]
            self.save_accounts()
            self.update_account_list()
            
            # 删除账号页面
            self.content_stack.removeWidget(self.content_stack.widget(current_row))

    def on_account_selected(self, index):
        """账号选择改变时的处理"""
        if index >= 0:
            self.content_stack.setCurrentIndex(index)

    def select_folder(self, folder_path_widget):
        """选择视频文件夹"""
        folder = QFileDialog.getExistingDirectory(self, "选择视频文件夹")
        if folder:
            folder_path_widget.setText(folder)
            # TODO: 加载视频列表

    def update_status(self):
        """更新状态显示"""
        statuses = self.publish_manager.get_all_status()
        for status in statuses:
            cookie = status['cookie']
            if cookie in self.accounts:
                # TODO: 更新对应账号页面的状态显示

    def closeEvent(self, event):
        """窗口关闭时的处理"""
        reply = QMessageBox.question(
            self, '确认退出', 
            '确定要退出吗？正在运行的任务将被停止。',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.publish_manager.stop_all()
            event.accept()
        else:
            event.ignore()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()