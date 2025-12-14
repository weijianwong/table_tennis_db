import os
import sys
import mysql.connector
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QLineEdit, QComboBox, QMessageBox,
    QDialog, QFormLayout, QDateTimeEdit, QSpinBox, QAbstractItemView, QHeaderView
)
from PyQt6.QtCore import Qt, QDateTime
from PyQt6 import uic

from captain import CaptainPage
from login import LoginPage


class DatabaseConnection:
    """数据库连接管理类"""

    def __init__(self):
        self.connection = None

    def connect(self, host='localhost', user='root', password='password', database='table_tennis_db'):
        try:
            self.connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                charset='utf8mb4'
            )
            return True
        except mysql.connector.Error as err:
            print(f"数据库连接错误: {err}")
            return False

    def execute_query(self, query, params=None):
        """执行查询"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            results = cursor.fetchall()
            cursor.close()
            return results
        except mysql.connector.Error as err:
            print(f"查询错误: {err}")
            return []

    def execute_update(self, query, params=None):
        """执行更新/插入/删除"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            self.connection.commit()
            cursor.close()
            return True
        except mysql.connector.Error as err:
            print(f"更新错误: {err}")
            self.connection.rollback()
            return False


class AddDialog(QDialog):
    """通用添加/编辑对话框"""

    def __init__(self, title, fields, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.fields = fields
        self.inputs = {}
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        for field_name, field_config in self.fields.items():
            field_type = field_config.get('type', 'text')

            if field_type == 'text':
                widget = QLineEdit()
            elif field_type == 'combo':
                widget = QComboBox()
                widget.addItems(field_config.get('options', []))
            elif field_type == 'datetime':
                widget = QDateTimeEdit()
                widget.setDateTime(QDateTime.currentDateTime())
                widget.setCalendarPopup(True)
            elif field_type == 'number':
                widget = QSpinBox()
                widget.setRange(field_config.get('min', 0), field_config.get('max', 9999))
            else:
                widget = QLineEdit()

            self.inputs[field_name] = widget
            layout.addRow(field_config.get('label', field_name), widget)

        # 按钮
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("保存")
        btn_cancel = QPushButton("取消")
        btn_save.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)

        layout.addRow(btn_layout)
        self.setLayout(layout)

    def get_values(self):
        """获取所有输入值"""
        values = {}
        for field_name, widget in self.inputs.items():
            if isinstance(widget, QLineEdit):
                values[field_name] = widget.text()
            elif isinstance(widget, QComboBox):
                values[field_name] = widget.currentText()
            elif isinstance(widget, QDateTimeEdit):
                values[field_name] = widget.dateTime().toString("yyyy-MM-dd HH:mm:ss")
            elif isinstance(widget, QSpinBox):
                values[field_name] = widget.value()
            else:
                values[field_name] = getattr(widget, 'text', lambda: '')()
        return values

    def set_values(self, values):
        """设置输入值（用于编辑）"""
        for field_name, value in values.items():
            if field_name in self.inputs:
                widget = self.inputs[field_name]
                if isinstance(widget, QLineEdit):
                    widget.setText(str(value) if value is not None else '')
                elif isinstance(widget, QComboBox):
                    index = widget.findText(str(value))
                    if index >= 0:
                        widget.setCurrentIndex(index)
                elif isinstance(widget, QSpinBox):
                    widget.setValue(int(value) if value is not None else 0)
                elif isinstance(widget, QDateTimeEdit):
                    try:
                        dt = QDateTime.fromString(str(value), "yyyy-MM-dd HH:mm:ss")
                        if dt.isValid():
                            widget.setDateTime(dt)
                    except Exception:
                        pass


class TableManager(QWidget):
    """表格管理基类"""

    def __init__(self, db_conn, table_name, columns, ui_file=None, parent=None):
        super().__init__(parent)
        self.db_conn = db_conn
        self.table_name = table_name
        self.columns = columns
        self.search_columns = [0]  # Default search column (first column)
        self.current_data = []  # Store current displayed data
        self.all_data = []  # Store all data
        self.load_ui(ui_file)
        self.init_connections()
        self.load_data()

    def load_ui(self, ui_file):
        """加载UI文件"""
        ui_path = os.path.join('ui_pages', ui_file)
        uic.loadUi(ui_path, self)
        self.get_table_widget().horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.get_table_widget().verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.get_table_widget().setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.get_table_widget().setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

    def init_connections(self):
        """初始化信号连接"""
        try:
            # 尝试连接UI文件中的按钮
            if hasattr(self, 'btnAdd'):
                self.btnAdd.clicked.connect(self.add_record)
            if hasattr(self, 'btnEdit'):
                self.btnEdit.clicked.connect(self.edit_record)
            if hasattr(self, 'btnDelete'):
                self.btnDelete.clicked.connect(self.delete_record)
            if hasattr(self, 'btnRefresh'):
                self.btnRefresh.clicked.connect(self.load_data)
            if hasattr(self, 'btnSearch'):
                self.btnSearch.clicked.connect(self.search_data)
            if hasattr(self, 'btnClearSearch'):
                self.btnClearSearch.clicked.connect(self.clear_search)

        except Exception as e:
            print(f"初始化连接失败: {e}")

    def get_table_widget(self):
        """获取表格控件（处理不同的UI结构）"""
        if hasattr(self, 'tableWidget'):
            return self.tableWidget
        elif hasattr(self, 'table'):
            return self.table
        else:
            # 如果都没有，创建默认表格
            self.table = QTableWidget()
            layout = self.layout()
            if layout:
                layout.addWidget(self.table)
            return self.table

    def get_search_text(self):
        """获取搜索文本"""
        if hasattr(self, 'txtSearch'):
            return self.txtSearch.text().strip()
        return ""

    def set_search_columns(self, column_index):
        """设置搜索列索引"""
        self.search_columns = column_index

    def get_base_query(self):
        """获取基础查询 - 子类可以重写此方法以提供JOIN查询"""
        return f"SELECT * FROM {self.table_name}"

    def populate_table(self, data):
        """填充表格数据 - 处理字典数据"""
        table = self.get_table_widget()
        table.setRowCount(0)

        # Set column headers if not set
        if table.columnCount() == 0:
            table.setColumnCount(len(self.columns))
            headers = [col['label'] for col in self.columns]
            table.setHorizontalHeaderLabels(headers)

        for row_num, row_data in enumerate(data):
            table.insertRow(row_num)
            for col_num, column_info in enumerate(self.columns):
                column_name = column_info['name']
                value = row_data.get(column_name, '')
                item = QTableWidgetItem(str(value))
                table.setItem(row_num, col_num, item)

        self.current_data = data

    def build_search_query(self, search_text):
        """构建搜索查询SQL"""
        if not self.search_columns:
            return self.get_base_query(), []

        where_conditions = []
        params = []

        # Use base query for consistency
        base_query = self.get_base_query()

        # Convert search columns to actual database column names
        for column_index in self.search_columns:
            if 0 <= column_index < len(self.columns):
                column_name = self.columns[column_index]['name']
                where_conditions.append(f"{column_name} LIKE %s")
                params.append(f"%{search_text}%")

        if where_conditions:
            where_clause = " OR ".join(where_conditions)
            # Check if base query already has WHERE clause
            if "WHERE" in base_query.upper():
                query = f"{base_query} AND ({where_clause})"
            else:
                query = f"{base_query} WHERE {where_clause}"
        else:
            query = base_query

        return query, params

    def search_data(self):
        """使用SQL查询进行搜索"""
        search_text = self.get_search_text().strip()

        try:
            if not search_text:
                # If no search text, show all data
                self.load_data()
                return

            # Build and execute search query
            query, params = self.build_search_query(search_text)

            params_tuple = tuple(params) if params else ()

            rows = self.db_conn.execute_query(query, params_tuple)
            print(f"Found {len(rows)} matches")
            # Convert results to list of dictionaries
            self.populate_table(rows)


            if not rows:
                QMessageBox.information(self, "搜索结果", f"未找到包含 '{search_text}' 的记录")

        except Exception as e:
            QMessageBox.critical(self, "搜索错误", f"搜索失败: {e}")
            print(f"Search error: {e}")

    def clear_search(self):
        """清除搜索"""
        if hasattr(self, 'txtSearch'):
            self.txtSearch.clear()
        self.populate_table(self.all_data)


    def load_data(self):
        """加载数据 - 子类需要实现"""
        pass

    def add_record(self):
        """添加记录 - 子类需要实现"""
        pass

    def edit_record(self):
        """编辑记录 - 子类需要实现"""
        pass

    def delete_record(self):
        """删除记录 - 子类需要实现"""
        pass


class CollegeManager(TableManager):
    """院系管理"""

    def __init__(self, db_conn, parent=None):
        columns = [
            {'name': 'dept_id', 'label': '院系编号'},
            {'name': 'dept_name', 'label': '院系名称'},
            {'name': 'contact_person', 'label': '联系人'},
            {'name': 'phone', 'label': '电话'}
        ]
        super().__init__(db_conn, 'College', columns, 'college_manager.ui', parent)
        self.set_search_columns([1])



    def load_data(self):
        query = self.get_base_query()
        data = self.db_conn.execute_query(query)
        self.all_data = data
        self.populate_table(data)

    def add_record(self):
        fields = {
            'dept_name': {'label': '院系名称', 'type': 'text'},
            'contact_person': {'label': '联系人', 'type': 'text'},
            'phone': {'label': '电话', 'type': 'text'}
        }
        dialog = AddDialog("添加院系", fields, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            values = dialog.get_values()
            query = "INSERT INTO College (dept_name, contact_person, phone) VALUES (%s, %s, %s)"
            if self.db_conn.execute_update(query, (values['dept_name'], values['contact_person'], values['phone'])):
                QMessageBox.information(self, "成功", "添加成功！")
                self.load_data()
            else:
                QMessageBox.warning(self, "错误", "添加失败！")

    def edit_record(self):
        table = self.get_table_widget()
        current_row = table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "警告", "请选择要编辑的记录！")
            return

        dept_id = table.item(current_row, 0).text()
        fields = {
            'dept_name': {'label': '院系名称', 'type': 'text'},
            'contact_person': {'label': '联系人', 'type': 'text'},
            'phone': {'label': '电话', 'type': 'text'}
        }
        dialog = AddDialog("编辑院系", fields, self)

        current_values = {
            'dept_name': table.item(current_row, 1).text(),
            'contact_person': table.item(current_row, 2).text(),
            'phone': table.item(current_row, 3).text()
        }
        dialog.set_values(current_values)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            values = dialog.get_values()
            query = "UPDATE College SET dept_name=%s, contact_person=%s, phone=%s WHERE dept_id=%s"
            if self.db_conn.execute_update(query,
                                           (values['dept_name'], values['contact_person'], values['phone'], dept_id)):
                QMessageBox.information(self, "成功", "更新成功！")
                self.load_data()
            else:
                QMessageBox.warning(self, "错误", "更新失败！")


    def delete_record(self):
        table = self.get_table_widget()
        current_row = table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "警告", "请选择要删除的记录！")
            return

        reply = QMessageBox.question(
            self,
            "确认删除",
            "确定要删除该记录吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            dept_id = table.item(current_row, 0).text()
            query = "DELETE FROM College WHERE dept_id=%s"

            try:
                if self.db_conn.execute_update(query, (dept_id,)):
                    QMessageBox.information(self, "成功", "删除成功！")
                    self.load_data()
                else:
                    QMessageBox.warning(self, "错误", "删除失败！可能存在关联数据。")
            except Exception as e:
                QMessageBox.critical(self, "数据库错误", f"删除失败！错误信息：{e}")


class TeamManager(TableManager):
    """球队管理"""

    def __init__(self, db_conn, parent=None):
        columns = [
            {'name': 'team_id', 'label': '球队ID'},
            {'name': 'team_name', 'label': '球队名称'},
            {'name': 'established_year', 'label': '成立年份'},
            {'name': 'dept_name', 'label': '所属院系'}
        ]
        super().__init__(db_conn, 'Team', columns, 'team_manager.ui', parent)
        self.set_search_columns([1,3])

    def get_base_query(self):
        return """
        SELECT t.team_id, t.team_name, t.established_year, c.dept_name
        FROM Team t
        LEFT JOIN College c ON t.dept_id = c.dept_id
        """

    def load_data(self):
        query = self.get_base_query()
        data = self.db_conn.execute_query(query)
        self.all_data = data
        self.populate_table(data)

    def add_record(self):
        colleges = self.db_conn.execute_query("SELECT dept_id, dept_name FROM College")
        college_options = [f"{c['dept_id']}: {c['dept_name']}" for c in colleges]

        fields = {
            'team_name': {'label': '球队名称', 'type': 'text'},
            'established_year': {'label': '成立年份', 'type': 'number', 'min': 1900, 'max': 2100},
            'dept': {'label': '所属院系', 'type': 'combo', 'options': college_options}
        }
        dialog = AddDialog("添加球队", fields, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            values = dialog.get_values()
            dept_id = values['dept'].split(':')[0]
            query = "INSERT INTO Team (team_name, established_year, dept_id) VALUES (%s, %s, %s)"
            if self.db_conn.execute_update(query, (values['team_name'], values['established_year'], dept_id)):
                QMessageBox.information(self, "成功", "添加成功！")
                self.load_data()
            else:
                QMessageBox.warning(self, "错误", "添加失败！")

    def edit_record(self):
        table = self.get_table_widget()
        current_row = table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "警告", "请选择要编辑的记录！")
            return

        team_id = table.item(current_row, 0).text()
        colleges = self.db_conn.execute_query("SELECT dept_id, dept_name FROM College")

        fields = {
            'team_name': {'label': '球队名称', 'type': 'text'},
            'established_year': {'label': '成立年份', 'type': 'number', 'min': 1900, 'max': 2100}
        }
        dialog = AddDialog("编辑球队", fields, self)

        current_values = {
            'team_name': table.item(current_row, 1).text(),
            'established_year': int(table.item(current_row, 2).text())
        }
        dialog.set_values(current_values)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            values = dialog.get_values()
            query = "UPDATE Team SET team_name=%s, established_year=%s WHERE team_id=%s"
            if self.db_conn.execute_update(query, (values['team_name'], values['established_year'], team_id)):
                QMessageBox.information(self, "成功", "更新成功！")
                self.load_data()
            else:
                QMessageBox.warning(self, "错误", "更新失败！")

    def delete_record(self):
        table = self.get_table_widget()
        current_row = table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "警告", "请选择要删除的记录！")
            return

        reply = QMessageBox.question(
            self,
            "确认删除",
            "确定要删除该记录吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            team_id = table.item(current_row, 0).text()
            query = "DELETE FROM Team WHERE team_id=%s"

            try:
                if self.db_conn.execute_update(query, (team_id,)):
                    QMessageBox.information(self, "成功", "删除成功！")
                    self.load_data()
                else:
                    QMessageBox.warning(self, "错误", "删除失败！可能存在关联数据。")
            except Exception as e:
                QMessageBox.critical(self, "数据库错误", f"删除失败！错误信息：{e}")

    def build_search_query(self, search_text):
        """Team表专用搜索查询"""
        if not self.search_columns:
            return self.get_base_query(), []

        where_conditions = []
        params = []

        for column_index in self.search_columns:
            if column_index == 1:  # team_name
                where_conditions.append("t.team_name LIKE %s")
                params.append(f"%{search_text}%")
            elif column_index == 3:  # dept_name
                where_conditions.append("c.dept_name LIKE %s")
                params.append(f"%{search_text}%")

        base_query = self.get_base_query()

        if where_conditions:
            where_clause = " OR ".join(where_conditions)
            query = f"{base_query} WHERE {where_clause}"
        else:
            query = base_query

        return query, params


class PlayerManager(TableManager):
    """球员管理"""

    def __init__(self, db_conn, parent=None):
        columns = [
            {'name': 'student_id', 'label': '学号'},
            {'name': 'name', 'label': '姓名'},
            {'name': 'gender', 'label': '性别'},
            {'name': 'grade', 'label': '年级'},
            {'name': 'phone', 'label': '电话'},
            {'name': 'team_name', 'label': '球队'},
            {'name': 'role', 'label': '角色'}
        ]
        super().__init__(db_conn, 'Player', columns, 'player_manager.ui', parent)
        self.set_search_columns([1,5])

    def get_base_query(self):
        return """
        SELECT p.student_id, p.name, p.gender, p.grade, p.phone, 
               t.team_name, p.role
        FROM Player p
        LEFT JOIN Team t ON p.team_id = t.team_id
        """

    def build_search_query(self, search_text):
        """Player表专用搜索查询"""
        if not self.search_columns:
            return self.get_base_query(), []

        where_conditions = []
        params = []

        for column_index in self.search_columns:
            if column_index == 1:  # name
                where_conditions.append("p.name LIKE %s")
                params.append(f"%{search_text}%")
            elif column_index == 5:  # team_name
                where_conditions.append("t.team_name LIKE %s")
                params.append(f"%{search_text}%")
        base_query = self.get_base_query()

        if where_conditions:
            where_clause = " OR ".join(where_conditions)
            query = f"{base_query} WHERE {where_clause}"
        else:
            query = base_query

        return query, params

    def load_data(self):
        query = self.get_base_query()
        data = self.db_conn.execute_query(query)
        self.all_data = data
        self.populate_table(data)

    def add_record(self):
        teams = self.db_conn.execute_query("SELECT team_id, team_name FROM Team")
        team_options = [f"{t['team_id']}: {t['team_name']}" for t in teams]

        fields = {
            'student_id': {'label': '学号', 'type': 'text'},
            'name': {'label': '姓名', 'type': 'text'},
            'gender': {'label': '性别', 'type': 'combo', 'options': ['男', '女']},
            'grade': {'label': '年级', 'type': 'text'},
            'phone': {'label': '电话', 'type': 'text'},
            'team': {'label': '球队', 'type': 'combo', 'options': team_options},
            'role': {'label': '角色', 'type': 'combo', 'options': ['队员', '队长']}
        }
        dialog = AddDialog("添加球员", fields, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            values = dialog.get_values()
            team_id = values['team'].split(':')[0]
            query = "INSERT INTO Player (student_id, name, gender, grade, phone, team_id, role) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            if self.db_conn.execute_update(query, (values['student_id'], values['name'], values['gender'],
                                                   values['grade'], values['phone'], team_id, values['role'])):
                QMessageBox.information(self, "成功", "添加成功！")
                self.load_data()
            else:
                QMessageBox.warning(self, "错误", "添加失败！")

    def edit_record(self):
        table = self.get_table_widget()
        current_row = table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "警告", "请选择要编辑的记录！")
            return

        student_id = table.item(current_row, 0).text()
        teams = self.db_conn.execute_query("SELECT team_id, team_name FROM Team")
        team_options = [f"{t['team_id']}: {t['team_name']}" for t in teams]

        fields = {
            'name': {'label': '姓名', 'type': 'text'},
            'gender': {'label': '性别', 'type': 'combo', 'options': ['男', '女']},
            'grade': {'label': '年级', 'type': 'text'},
            'phone': {'label': '电话', 'type': 'text'},
            'team': {'label': '球队', 'type': 'combo', 'options': team_options},
            'role': {'label': '角色', 'type': 'combo', 'options': ['队员', '队长']}
        }
        dialog = AddDialog("编辑球员", fields, self)

        current_values = {
            'name': table.item(current_row, 1).text(),
            'gender': table.item(current_row, 2).text(),
            'grade': table.item(current_row, 3).text(),
            'phone': table.item(current_row, 4).text(),
            'role': table.item(current_row, 6).text()
        }
        dialog.set_values(current_values)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            values = dialog.get_values()
            team_id = values['team'].split(':')[0]
            query = "UPDATE Player SET name=%s, gender=%s, grade=%s, phone=%s, team_id=%s, role=%s WHERE student_id=%s"
            if self.db_conn.execute_update(query, (values['name'], values['gender'], values['grade'],
                                                   values['phone'], team_id, values['role'], student_id)):
                QMessageBox.information(self, "成功", "更新成功！")
                self.load_data()
            else:
                QMessageBox.warning(self, "错误", "更新失败！")

    def delete_record(self):
        table = self.get_table_widget()
        current_row = table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "警告", "请选择要删除的记录！")
            return

        reply = QMessageBox.question(
            self,
            "确认删除",
            "确定要删除该记录吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            student_id = table.item(current_row, 0).text()
            query = "DELETE FROM Player WHERE student_id=%s"

            try:
                if self.db_conn.execute_update(query, (student_id,)):
                    QMessageBox.information(self, "成功", "删除成功！")
                    self.load_data()
                else:
                    QMessageBox.warning(self, "错误", "删除失败！可能存在关联数据。")
            except Exception as e:
                QMessageBox.critical(self, "数据库错误", f"删除失败！错误信息：{e}")


class TournamentManager(TableManager):
    """赛事管理"""

    def __init__(self, db_conn, parent=None):
        columns = [
            {'name': 'tournament_id', 'label': '赛事ID'},
            {'name': 'tournament_name', 'label': '赛事名称'},
            {'name': 'year', 'label': '年份'},
            {'name': 'status', 'label': '状态'}
        ]
        super().__init__(db_conn, 'Tournament', columns, 'tournament_manager.ui', parent)
        self.set_search_columns([1,2])

    def load_data(self):
        query = self.get_base_query()
        data = self.db_conn.execute_query(query)
        self.all_data = data
        self.populate_table(data)

    def get_base_query(self):
        return "SELECT * FROM Tournament ORDER BY year DESC, tournament_id DESC"

    def add_record(self):
        fields = {
            'tournament_name': {'label': '赛事名称', 'type': 'text'},
            'year': {'label': '年份', 'type': 'number', 'min': 2000, 'max': 2100},
            'status': {'label': '状态', 'type': 'combo', 'options': ['未开始', '进行中', '已结束']}
        }
        dialog = AddDialog("添加赛事", fields, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            values = dialog.get_values()
            query = "INSERT INTO Tournament (tournament_name, year, status) VALUES (%s, %s, %s)"
            if self.db_conn.execute_update(query, (values['tournament_name'], values['year'], values['status'])):
                QMessageBox.information(self, "成功", "添加成功！")
                self.load_data()
            else:
                QMessageBox.warning(self, "错误", "添加失败！")

    def edit_record(self):
        table = self.get_table_widget()
        current_row = table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "警告", "请选择要编辑的记录！")
            return

        tournament_id = table.item(current_row, 0).text()
        fields = {
            'tournament_name': {'label': '赛事名称', 'type': 'text'},
            'year': {'label': '年份', 'type': 'number', 'min': 2000, 'max': 2100},
            'status': {'label': '状态', 'type': 'combo', 'options': ['未开始', '进行中', '已结束']}
        }
        dialog = AddDialog("编辑赛事", fields, self)

        current_values = {
            'tournament_name': table.item(current_row, 1).text(),
            'year': int(table.item(current_row, 2).text()),
            'status': table.item(current_row, 3).text()
        }
        dialog.set_values(current_values)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            values = dialog.get_values()
            query = "UPDATE Tournament SET tournament_name=%s, year=%s, status=%s WHERE tournament_id=%s"
            if self.db_conn.execute_update(query, (values['tournament_name'], values['year'], values['status'], tournament_id)):
                QMessageBox.information(self, "成功", "更新成功！")
                self.load_data()
            else:
                QMessageBox.warning(self, "错误", "更新失败！")

    def delete_record(self):
        table = self.get_table_widget()
        current_row = table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "警告", "请选择要删除的记录！")
            return

        reply = QMessageBox.question(
            self,
            "确认删除",
            "确定要删除该记录吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            tournament_id = table.item(current_row, 0).text()
            query = "DELETE FROM Tournament WHERE tournament_id=%s"

            try:
                if self.db_conn.execute_update(query, (tournament_id,)):
                    QMessageBox.information(self, "成功", "删除成功！")
                    self.load_data()
                else:
                    QMessageBox.warning(self, "错误", "删除失败！可能存在关联数据。")
            except Exception as e:
                QMessageBox.critical(self, "数据库错误", f"删除失败！错误信息：{e}")

    def build_search_query(self, search_text):
        """Tournament表专用搜索查询"""
        if not self.search_columns:
            return self.get_base_query(), []

        where_conditions = []
        params = []

        for column_index in self.search_columns:
            if column_index == 1:  # tournament_name
                where_conditions.append("tournament_name LIKE %s")
                params.append(f"%{search_text}%")
            elif column_index == 2:  # year
                where_conditions.append("year LIKE %s")
                params.append(f"%{search_text}%")

        base_without_order = "SELECT * FROM Tournament"
        order_clause = "ORDER BY year DESC, tournament_id DESC"

        if where_conditions:
            where_clause = " OR ".join(where_conditions)
            query = f"{base_without_order} WHERE {where_clause} {order_clause}"
        else:
            query = f"{base_without_order} {order_clause}"

        return query, params


class MatchManager(TableManager):
    """比赛管理"""

    def __init__(self, db_conn, parent=None):
        columns = [
            {'name': 'match_id', 'label': '比赛ID'},
            {'name': 'scheduled_time', 'label': '比赛时间'},
            {'name': 'venue', 'label': '场地'},
            {'name': 'tournament_name', 'label': '赛事'},
            {'name': 'home_team', 'label': '主队'},
            {'name': 'away_team', 'label': '客队'},
            {'name': 'referee', 'label': '裁判'},
            {'name': 'final_score', 'label': '总比分'}
        ]
        super().__init__(db_conn, 'Match', columns, 'match_manager.ui', parent)
        self.set_search_columns([3])

    def get_base_query(self):
        return """
        SELECT m.match_id, m.scheduled_time, m.venue, 
               t.tournament_name, 
               ht.team_name as home_team,
               at.team_name as away_team,
               m.referee, m.final_score
        FROM `Match` m
        LEFT JOIN Tournament t ON m.tournament_id = t.tournament_id
        LEFT JOIN Team ht ON m.home_team_id = ht.team_id
        LEFT JOIN Team at ON m.away_team_id = at.team_id
        """
    def load_data(self):
        query = self.get_base_query() + " ORDER BY m.scheduled_time DESC"
        data = self.db_conn.execute_query(query)
        self.all_data = data
        self.populate_table(data)
    def add_record(self):
        tournaments = self.db_conn.execute_query("SELECT tournament_id, tournament_name FROM Tournament")
        tournament_options = [f"{t['tournament_id']}: {t['tournament_name']}" for t in tournaments]

        teams = self.db_conn.execute_query("SELECT team_id, team_name FROM Team")
        team_options = [f"{team['team_id']}: {team['team_name']}" for team in teams]

        fields = {
            'scheduled_time': {'label': '比赛时间', 'type': 'datetime'},
            'venue': {'label': '场地', 'type': 'text'},
            'tournament': {'label': '赛事', 'type': 'combo', 'options': tournament_options},
            'home_team': {'label': '主队', 'type': 'combo', 'options': team_options},
            'away_team': {'label': '客队', 'type': 'combo', 'options': team_options},
            'referee': {'label': '裁判', 'type': 'text'}
        }
        dialog = AddDialog("添加比赛", fields, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            values = dialog.get_values()
            tournament_id = values['tournament'].split(':')[0]
            home_team_id = values['home_team'].split(':')[0]
            away_team_id = values['away_team'].split(':')[0]
            if home_team_id == away_team_id:
                QMessageBox.warning(self, "错误", "主队和客队不能相同！")
                return

            # Don't include final_score in INSERT - it will be '0:0' by default or NULL
            query = """
            INSERT INTO `Match` (scheduled_time, venue, tournament_id, home_team_id, away_team_id, referee, final_score)
            VALUES (%s, %s, %s, %s, %s, %s, '0:0')
            """
            if self.db_conn.execute_update(query, (values['scheduled_time'], values['venue'], tournament_id,
                                                   home_team_id, away_team_id, values['referee'])):
                QMessageBox.information(self, "成功", "添加成功！总比分将根据盘次对决自动更新。")
                self.load_data()
            else:
                QMessageBox.warning(self, "错误", "添加失败！")

    def edit_record(self):
        table = self.get_table_widget()
        current_row = table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "警告", "请选择要编辑的记录！")
            return

        match_id = table.item(current_row, 0).text()

        tournaments = self.db_conn.execute_query("SELECT tournament_id, tournament_name FROM Tournament")
        tournament_options = [f"{t['tournament_id']}: {t['tournament_name']}" for t in tournaments]

        teams = self.db_conn.execute_query("SELECT team_id, team_name FROM Team")
        team_options = [f"{team['team_id']}: {team['team_name']}" for team in teams]

        fields = {
            'scheduled_time': {'label': '比赛时间', 'type': 'datetime'},
            'venue': {'label': '场地', 'type': 'text'},
            'tournament': {'label': '赛事', 'type': 'combo', 'options': tournament_options},
            'home_team': {'label': '主队', 'type': 'combo', 'options': team_options},
            'away_team': {'label': '客队', 'type': 'combo', 'options': team_options},
            'referee': {'label': '裁判', 'type': 'text'}
        }
        dialog = AddDialog("编辑比赛", fields, self)

        current_values = {
            'scheduled_time': table.item(current_row, 1).text(),
            'venue': table.item(current_row, 2).text(),
            'tournament': table.item(current_row, 3).text(),
            'home_team': table.item(current_row, 4).text(),
            'away_team': table.item(current_row, 5).text(),
            'referee': table.item(current_row, 6).text()
        }
        dialog.set_values(current_values)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            values = dialog.get_values()
            tournament_id = values['tournament'].split(':')[0]
            home_team_id = values['home_team'].split(':')[0]
            away_team_id = values['away_team'].split(':')[0]

            # Don't update final_score - it's managed by triggers
            query = """
            UPDATE `Match` SET scheduled_time=%s, venue=%s, tournament_id=%s,
                               home_team_id=%s, away_team_id=%s, referee=%s
            WHERE match_id=%s
            """
            if self.db_conn.execute_update(query, (values['scheduled_time'], values['venue'], tournament_id,
                                                   home_team_id, away_team_id, values['referee'], match_id)):
                QMessageBox.information(self, "成功", "更新成功！")
                self.load_data()
            else:
                QMessageBox.warning(self, "错误", "更新失败！")

    def delete_record(self):
        table = self.get_table_widget()
        current_row = table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "警告", "请选择要删除的记录！")
            return

        reply = QMessageBox.question(
            self,
            "确认删除",
            "确定要删除该记录吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            match_id = table.item(current_row, 0).text()
            query = "DELETE FROM `Match` WHERE match_id=%s"

            try:
                if self.db_conn.execute_update(query, (match_id,)):
                    QMessageBox.information(self, "成功", "删除成功！")
                    self.load_data()
                else:
                    QMessageBox.warning(self, "错误", "删除失败！可能存在关联数据。")
            except Exception as e:
                QMessageBox.critical(self, "数据库错误", f"删除失败！错误信息：{e}")

    def build_search_query(self, search_text):
        """Tournament表专用搜索查询"""
        if not self.search_columns:
            return self.get_base_query(), []

        where_conditions = []
        params = []

        for column_index in self.search_columns:
            if column_index == 3:  # tournament_name
                where_conditions.append("tournament_name LIKE %s")
                params.append(f"%{search_text}%")

        # Get base query without ORDER BY for WHERE clause insertion
        base_query = self.get_base_query()

        if where_conditions:
            where_clause = " OR ".join(where_conditions)
            query = f"{base_query} WHERE {where_clause} ORDER BY m.scheduled_time DESC"
        else:
            query = base_query + " ORDER BY m.scheduled_time DESC"

        return query, params


class GameManager(TableManager):
    """盘次对决管理"""

    def __init__(self, db_conn, parent=None):
        columns = [
            {'name': 'match_id', 'label': '比赛ID'},
            {'name': 'game_id', 'label': '盘次ID'},
            {'name': 'game_type', 'label': '比赛类型'},
            {'name': 'home_score', 'label': '主队得分'},
            {'name': 'away_score', 'label': '客队得分'},
            {'name': 'winner', 'label': '获胜方'},
            {'name': 'match_info', 'label': '比赛信息'}
        ]
        super().__init__(db_conn, 'Game', columns, 'game_manager.ui', parent)

    def get_base_query(self):
        return """
        SELECT g.match_id, g.game_id, g.game_type, g.home_score, g.away_score, g.winner,
               CONCAT(ht.team_name, ' vs ', at.team_name, ' (', t.tournament_name, ')') as match_info,
               m.final_score
        FROM Game g
        LEFT JOIN `Match` m ON g.match_id = m.match_id
        LEFT JOIN Team ht ON m.home_team_id = ht.team_id
        LEFT JOIN Team at ON m.away_team_id = at.team_id
        LEFT JOIN Tournament t ON m.tournament_id = t.tournament_id
        ORDER BY g.match_id DESC, g.game_id ASC
        """
    def load_data(self):
        query = self.get_base_query()
        data = self.db_conn.execute_query(query)
        self.all_data = data
        self.populate_table(data)

    def add_record(self):
        matches = self.db_conn.execute_query("""
            SELECT m.match_id, 
                   CONCAT(ht.team_name, ' vs ', at.team_name, ' (', DATE_FORMAT(m.scheduled_time, '%Y-%m-%d'), ')') as match_info
            FROM `Match` m
            LEFT JOIN Team ht ON m.home_team_id = ht.team_id
            LEFT JOIN Team at ON m.away_team_id = at.team_id
        """)
        match_options = [f"{m['match_id']}: {m['match_info']}" for m in matches]

        fields = {
            'match': {'label': '比赛', 'type': 'combo', 'options': match_options},
            'game_id': {'label': '盘次ID', 'type': 'number', 'min': 1, 'max': 10},
            'game_type': {'label': '比赛类型', 'type': 'combo', 'options': ['男单', '女单', '男双', '女双', '混双']},
            'home_score': {'label': '主队得分', 'type': 'number', 'min': 0, 'max': 30},
            'away_score': {'label': '客队得分', 'type': 'number', 'min': 0, 'max': 30},
            'winner': {'label': '获胜方', 'type': 'combo', 'options': ['主队', '客队']}
        }
        dialog = AddDialog("添加盘次对决", fields, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            values = dialog.get_values()
            match_id = values['match'].split(':')[0]

            query = "INSERT INTO Game (match_id, game_id, game_type, home_score, away_score, winner) VALUES (%s, %s, %s, %s, %s, %s)"
            if self.db_conn.execute_update(query, (match_id, values['game_id'], values['game_type'],
                                                   values['home_score'], values['away_score'], values['winner'])):
                # Get updated score
                score_query = "SELECT final_score FROM `Match` WHERE match_id = %s"
                score_result = self.db_conn.execute_query(score_query, (match_id,))
                new_score = score_result[0]['final_score'] if score_result else '未知'

                QMessageBox.information(self, "成功", f"添加成功！\n总比分已自动更新为: {new_score}")
                self.load_data()
            else:
                QMessageBox.warning(self, "错误", "添加失败！可能盘次ID重复。")

    def edit_record(self):
        table = self.get_table_widget()
        current_row = table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "警告", "请选择要编辑的记录！")
            return

        match_id = table.item(current_row, 0).text()
        game_id = table.item(current_row, 1).text()

        fields = {
            'game_type': {'label': '比赛类型', 'type': 'combo', 'options': ['男单', '女单', '男双', '女双', '混双']},
            'home_score': {'label': '主队得分', 'type': 'number', 'min': 0, 'max': 30},
            'away_score': {'label': '客队得分', 'type': 'number', 'min': 0, 'max': 30},
            'winner': {'label': '获胜方', 'type': 'combo', 'options': ['主队', '客队']}
        }
        dialog = AddDialog("编辑盘次对决", fields, self)

        current_values = {
            'game_type': table.item(current_row, 2).text(),
            'home_score': int(table.item(current_row, 3).text()) if table.item(current_row, 3).text() else 0,
            'away_score': int(table.item(current_row, 4).text()) if table.item(current_row, 4).text() else 0,
            'winner': table.item(current_row, 5).text()
        }
        dialog.set_values(current_values)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            values = dialog.get_values()
            query = "UPDATE Game SET game_type=%s, home_score=%s, away_score=%s, winner=%s WHERE match_id=%s AND game_id=%s"
            if self.db_conn.execute_update(query, (values['game_type'], values['home_score'], values['away_score'],
                                                   values['winner'], match_id, game_id)):
                # Get updated score
                score_query = "SELECT final_score FROM `Match` WHERE match_id = %s"
                score_result = self.db_conn.execute_query(score_query, (match_id,))
                new_score = score_result[0]['final_score'] if score_result else '未知'

                QMessageBox.information(self, "成功", f"更新成功！\n总比分已自动更新为: {new_score}")
                self.load_data()
            else:
                QMessageBox.warning(self, "错误", "更新失败！")

    def delete_record(self):
        table = self.get_table_widget()
        current_row = table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "警告", "请选择要删除的记录！")
            return

        reply = QMessageBox.question(
            self,
            "确认删除",
            "确定要删除该记录吗？\n总比分将自动重新计算。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            match_id = table.item(current_row, 0).text()
            game_id = table.item(current_row, 1).text()
            query = "DELETE FROM Game WHERE match_id=%s AND game_id=%s"

            try:
                if self.db_conn.execute_update(query, (match_id, game_id)):
                    # Get updated score
                    score_query = "SELECT final_score FROM `Match` WHERE match_id = %s"
                    score_result = self.db_conn.execute_query(score_query, (match_id,))
                    new_score = score_result[0]['final_score'] if score_result else '未知'

                    QMessageBox.information(self, "成功", f"删除成功！\n总比分已自动更新为: {new_score}")
                    self.load_data()
                else:
                    QMessageBox.warning(self, "错误", "删除失败！可能存在关联数据。")
            except Exception as e:
                QMessageBox.critical(self, "数据库错误", f"删除失败！错误信息：{e}")

class PlayerInGameManager(TableManager):
    """参赛球员管理"""

    def __init__(self, db_conn, parent=None):
        columns = [
            {'name': 'match_id', 'label': '比赛ID'},
            {'name': 'game_id', 'label': '盘次ID'},
            {'name': 'student_id', 'label': '学号'},
            {'name': 'player_name', 'label': '球员姓名'},
            {'name': 'team_name', 'label': '球队'},
            {'name': 'game_type', 'label': '比赛类型'}
        ]
        super().__init__(db_conn, 'Player_In_Game', columns, 'player_in_game_manager.ui', parent)
        self.set_search_columns([3,4])

    def get_base_query(self):
        return """
        SELECT pig.match_id, pig.game_id, pig.student_id,
               p.name as player_name, t.team_name, g.game_type
        FROM Player_In_Game pig
        LEFT JOIN Player p ON pig.student_id = p.student_id
        LEFT JOIN Team t ON p.team_id = t.team_id
        LEFT JOIN Game g ON pig.match_id = g.match_id AND pig.game_id = g.game_id
        """
    def load_data(self):
        query = self.get_base_query()
        data = self.db_conn.execute_query(query)
        self.all_data = data
        self.populate_table(data)

    def add_record(self):
        games = self.db_conn.execute_query("""
            SELECT g.match_id, g.game_id, g.game_type,
                   CONCAT('比赛', g.match_id, '-盘', g.game_id, ' (', g.game_type, ')') as game_info
            FROM Game g
        """)
        game_options = [f"{g['match_id']}-{g['game_id']}: {g['game_info']}" for g in games]

        players = self.db_conn.execute_query("""
            SELECT p.student_id, p.name, t.team_name
            FROM Player p
            LEFT JOIN Team t ON p.team_id = t.team_id
        """)
        player_options = [f"{p['student_id']}: {p['name']} ({p['team_name']})" for p in players]

        fields = {
            'game': {'label': '盘次对决', 'type': 'combo', 'options': game_options},
            'player': {'label': '球员', 'type': 'combo', 'options': player_options}
        }
        dialog = AddDialog("添加参赛球员", fields, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            values = dialog.get_values()
            game_parts = values['game'].split(':')[0].split('-')
            match_id = game_parts[0]
            game_id = game_parts[1]
            student_id = values['player'].split(':')[0]

            query = "INSERT INTO Player_In_Game (match_id, game_id, student_id) VALUES (%s, %s, %s)"
            if self.db_conn.execute_update(query, (match_id, game_id, student_id)):
                QMessageBox.information(self, "成功", "添加成功！")
                self.load_data()
            else:
                QMessageBox.warning(self, "错误", "添加失败！可能已存在该记录。")

    def edit_record(self):
        QMessageBox.information(self, "提示", "参赛球员记录不支持编辑，请删除后重新添加。")

    def delete_record(self):
        table = self.get_table_widget()
        current_row = table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "警告", "请选择要删除的记录！")
            return

        reply = QMessageBox.question(
            self,
            "确认删除",
            "确定要删除该记录吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            match_id = table.item(current_row, 0).text()
            game_id = table.item(current_row, 1).text()
            student_id = table.item(current_row, 2).text()
            query = "DELETE FROM Player_In_Game WHERE match_id=%s AND game_id=%s AND student_id=%s"

            try:
                if self.db_conn.execute_update(query, (match_id, game_id, student_id)):
                    QMessageBox.information(self, "成功", "删除成功！")
                    self.load_data()
                else:
                    QMessageBox.warning(self, "错误", "删除失败！")
            except Exception as e:
                QMessageBox.critical(self, "数据库错误", f"删除失败！错误信息：{e}")

    def build_search_query(self, search_text):
        """Player_In_Game表专用搜索查询"""
        if not self.search_columns:
            return self.get_base_query() + " ORDER BY pig.match_id DESC, pig.game_id ASC", []

        where_conditions = []
        params = []

        for column_index in self.search_columns:
            if column_index == 3:  # player_name
                where_conditions.append("p.name LIKE %s")
                params.append(f"%{search_text}%")
            elif column_index == 4:  # team_name
                where_conditions.append("t.team_name LIKE %s")
                params.append(f"%{search_text}%")

        base_query = self.get_base_query()

        if where_conditions:
            where_clause = " OR ".join(where_conditions)
            query = f"{base_query} WHERE {where_clause} ORDER BY pig.match_id DESC, pig.game_id ASC"
        else:
            query = base_query + " ORDER BY pig.match_id DESC, pig.game_id ASC"

        return query, params


class MainWindow(QMainWindow):
    """主窗口 - 使用UI文件"""

    def __init__(self, on_logout_callback=None):
        super().__init__()
        self.db_conn = DatabaseConnection()
        self.on_logout_callback = on_logout_callback

        # 连接数据库
        if not self.connect_database():
            QMessageBox.critical(self, "错误", "无法连接到数据库！请检查配置。")
            sys.exit(1)

        # 加载UI文件
        self.load_ui()
        self.setup_tabs()
        self.setup_logout_button()

    def setup_logout_button(self):
        """设置退出登录按钮"""
        # ADD this entire method
        logout_btn = self.findChild(QPushButton, 'btnLogout')
        if logout_btn:
            logout_btn.clicked.connect(self.handle_logout)

    def handle_logout(self):
        """处理退出登录"""
        # ADD this entire method
        reply = QMessageBox.question(
            self,
            "确认退出",
            "确定要退出登录吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.close()
            if self.on_logout_callback:
                self.on_logout_callback()

    def connect_database(self):
        """连接数据库"""
        return self.db_conn.connect(
            host='localhost',
            user='root',
            password='password',
            database='table_tennis_db'
        )

    def load_ui(self):
        """加载UI文件"""
        try:
            uic.loadUi('ui_pages/main.ui', self)
        except FileNotFoundError:
            QMessageBox.critical(self, "错误", "找不到main.ui文件！")
            sys.exit(1)

    def setup_tabs(self):
        """设置标签页内容"""
        # 获取UI中的标签页控件
        tab_widget = self.findChild(QTabWidget, 'tabWidget')

        if not tab_widget:
            QMessageBox.warning(self, "警告", "无法找到标签页控件！")
            return

        # 清空现有标签页
        tab_widget.clear()

        # 重新添加所有管理页面
        tab_widget.addTab(CollegeManager(self.db_conn), "院系管理")
        tab_widget.addTab(TeamManager(self.db_conn), "球队管理")
        tab_widget.addTab(PlayerManager(self.db_conn), "球员管理")
        tab_widget.addTab(TournamentManager(self.db_conn), "赛事管理")
        tab_widget.addTab(MatchManager(self.db_conn), "比赛管理")
        tab_widget.addTab(GameManager(self.db_conn), "盘次对决管理")
        tab_widget.addTab(PlayerInGameManager(self.db_conn), "参赛球员管理")


def main():
    app = QApplication(sys.argv)

    # Create database connection
    db_conn = DatabaseConnection()
    if not db_conn.connect(
            host='localhost',
            user='root',
            password='password',
            database='table_tennis_db'
    ):
        QMessageBox.critical(None, "错误", "无法连接到数据库！请检查配置。")
        sys.exit(1)

    # MODIFY: Initialize windows as None
    admin_window = None
    captain_window = None
    login_window = None

    def show_login_window():
        """显示登录窗口"""
        # ADD this entire function
        nonlocal login_window
        login_window = LoginPage(
            db_conn=db_conn,
            on_admin_login=show_admin_window,
            on_captain_login=show_captain_window
        )
        login_window.show()

    def show_admin_window():
        # MODIFY: Add logout callback and close login window
        nonlocal admin_window, login_window
        if login_window:
            login_window.close()
        admin_window = MainWindow(on_logout_callback=show_login_window)
        admin_window.show()

    def show_captain_window(student_id):
        # MODIFY: Add logout callback and close login window
        nonlocal captain_window, login_window
        if login_window:
            login_window.close()
        captain_window = CaptainPage(
            db_conn,
            student_id,
            on_logout_callback=show_login_window
        )
        captain_window.show()

    # MODIFY: Use the new function instead of direct instantiation
    show_login_window()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()