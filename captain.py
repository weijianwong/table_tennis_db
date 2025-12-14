from PyQt6.QtWidgets import (
    QMainWindow, QDialog, QTableWidgetItem, QMessageBox,
    QHeaderView, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QProgressBar, QFrame, QPushButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6 import uic
import os


class AddPlayerDialog(QDialog):
    """Add player dialog for team captains"""

    def __init__(self, parent=None):
        super().__init__(parent)
        # Load UI file
        ui_path = os.path.join(os.path.dirname(__file__), 'ui_pages/add_player_dialog.ui')
        uic.loadUi(ui_path, self)

    def get_values(self):
        """Get input values from the dialog"""
        return {
            'student_id': self.studentIdInput.text().strip(),
            'name': self.nameInput.text().strip(),
            'gender': self.genderCombo.currentText(),
            'grade': self.gradeInput.text().strip(),
            'phone': self.phoneInput.text().strip()
        }


class PlayerStatCard(QFrame):
    """Custom widget for displaying player statistics in a card format"""

    def __init__(self, player_data, parent=None):
        super().__init__(parent)

        # Load UI file
        ui_path = os.path.join(os.path.dirname(__file__), 'ui_pages/player_stat_card.ui')
        uic.loadUi(ui_path, self)

        # Populate with data
        self.set_player_data(player_data)

    def set_player_data(self, data):
        """Set player data to the card"""
        # Set player name and info
        self.nameLabel.setText(f"<b>{data['name']}</b>")
        self.infoLabel.setText(f"学号: {data['student_id']} | {data['gender']} | {data['role']}")

        # Set match count
        self.matchesCountLabel.setText(str(data['total_matches']))

        # Set win rate
        win_rate = data['win_rate']
        wins = data['wins']
        losses = data['losses']

        self.winratePercentLabel.setText(f"{win_rate:.1f}%")
        self.winrateProgressBar.setValue(int(win_rate))
        self.recordLabel.setText(f"{wins}胜 - {losses}负")


class CaptainPage(QMainWindow):
    """Team Captain Dashboard"""

    def __init__(self, db_conn, student_id, on_logout_callback=None):
        super().__init__()
        self.db_conn = db_conn
        self.student_id = student_id
        self.team_info = self.get_team_info()
        self.on_logout_callback = on_logout_callback

        if not self.team_info:
            QMessageBox.critical(self, "错误", "未找到您的球队信息！")
            self.close()
            return

        # Load UI file
        ui_path = os.path.join(os.path.dirname(__file__), 'ui_pages/captain_page.ui')
        uic.loadUi(ui_path, self)

        self.init_ui()
        self.connect_signals()
        self.load_all_data()
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

    def get_team_info(self):
        """Get team information for the logged-in captain"""
        query = """
        SELECT t.team_id, t.team_name, t.established_year, c.dept_name
        FROM Player p
        JOIN Team t ON p.team_id = t.team_id
        JOIN College c ON t.dept_id = c.dept_id
        WHERE p.student_id = %s AND p.role = '队长'
        """
        result = self.db_conn.execute_query(query, (self.student_id,))
        return result[0] if result else None

    def init_ui(self):
        """Initialize UI elements"""
        # Set window title
        self.setWindowTitle(f"队长管理系统 - {self.team_info['team_name']}")

        # Update header labels
        self.titleLabel.setText(f"🏓 {self.team_info['team_name']}")
        self.infoLabel.setText(
            f"所属院系: {self.team_info['dept_name']} | "
            f"成立年份: {self.team_info['established_year']}"
        )

        # Configure tables to stretch columns
        self.playersTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tournamentsTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.matchesTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Set scroll area background
        self.statsScrollArea.setStyleSheet("background-color: #f5f5f5;")

    def connect_signals(self):
        """Connect button signals to slots"""
        # Players tab
        self.btnSearchPlayer.clicked.connect(self.search_players)
        self.btnClearPlayerSearch.clicked.connect(self.clear_player_search)
        self.btnAddPlayer.clicked.connect(self.add_player)
        self.btnRemovePlayer.clicked.connect(self.remove_player)
        self.btnRefreshPlayers.clicked.connect(self.load_team_players)
        self.searchPlayerInput.returnPressed.connect(self.search_players)

        # Player stats tab
        self.btnRefreshStats.clicked.connect(self.load_player_statistics)
        self.statsSortCombo.currentIndexChanged.connect(self.load_player_statistics)

        # Tournaments tab
        self.btnSearchTournament.clicked.connect(self.search_tournaments)
        self.btnClearTournamentSearch.clicked.connect(self.clear_tournament_search)
        self.searchTournamentInput.returnPressed.connect(self.search_tournaments)

        # Matches tab
        self.btnSearchMatch.clicked.connect(self.search_matches)
        self.btnClearMatchSearch.clicked.connect(self.clear_match_search)
        self.btnRefreshMatches.clicked.connect(self.load_team_matches)
        self.searchMatchInput.returnPressed.connect(self.search_matches)

    def load_all_data(self):
        """Load all data on initialization"""
        self.load_team_players()
        self.load_player_statistics()
        self.load_team_tournaments()
        self.load_team_matches()

    def load_team_players(self):
        """Load all team players"""
        query = """
        SELECT student_id, name, gender, grade, phone, role
        FROM Player
        WHERE team_id = %s
        ORDER BY role DESC, name
        """
        self._populate_players_table(query, (self.team_info['team_id'],))

    def search_players(self):
        """Search players by student ID, name, or grade"""
        search_text = self.searchPlayerInput.text().strip()

        if not search_text:
            self.load_team_players()
            return

        query = """
        SELECT student_id, name, gender, grade, phone, role
        FROM Player
        WHERE team_id = %s
        AND (student_id LIKE %s OR name LIKE %s OR grade LIKE %s)
        ORDER BY role DESC, name
        """
        search_pattern = f"%{search_text}%"
        self._populate_players_table(
            query,
            (self.team_info['team_id'], search_pattern, search_pattern, search_pattern)
        )

    def clear_player_search(self):
        """Clear player search and reload all players"""
        self.searchPlayerInput.clear()
        self.load_team_players()

    def _populate_players_table(self, query, params):
        """Helper method to populate players table"""
        data = self.db_conn.execute_query(query, params)

        self.playersTable.setRowCount(len(data))
        for row_idx, row_data in enumerate(data):
            self.playersTable.setItem(row_idx, 0, QTableWidgetItem(row_data['student_id']))
            self.playersTable.setItem(row_idx, 1, QTableWidgetItem(row_data['name']))
            self.playersTable.setItem(row_idx, 2, QTableWidgetItem(row_data['gender']))
            self.playersTable.setItem(row_idx, 3, QTableWidgetItem(row_data['grade'] or ''))
            self.playersTable.setItem(row_idx, 4, QTableWidgetItem(row_data['phone'] or ''))
            self.playersTable.setItem(row_idx, 5, QTableWidgetItem(row_data['role']))

    def load_player_statistics(self):
        """Load player win rate statistics"""
        # Determine sort order
        sort_index = self.statsSortCombo.currentIndex()
        if sort_index == 0:  # By win rate
            order_by = "win_rate DESC, total_games DESC"
        elif sort_index == 1:  # By match count
            order_by = "total_games DESC, win_rate DESC"
        else:  # By name
            order_by = "p.name"

        query = f"""
        SELECT 
            p.student_id,
            p.name,
            p.gender,
            p.role,
            COUNT(DISTINCT CONCAT(pig.match_id, '-', pig.game_id)) as total_games,
            SUM(CASE 
                WHEN (g.winner = '主队' AND m.home_team_id = p.team_id) 
                  OR (g.winner = '客队' AND m.away_team_id = p.team_id) 
                THEN 1 
                ELSE 0 
            END) as wins,
            SUM(CASE 
                WHEN (g.winner = '客队' AND m.home_team_id = p.team_id) 
                  OR (g.winner = '主队' AND m.away_team_id = p.team_id) 
                THEN 1 
                ELSE 0 
            END) as losses,
            CASE 
                WHEN COUNT(DISTINCT CONCAT(pig.match_id, '-', pig.game_id)) = 0 THEN 0
                ELSE (SUM(CASE 
                    WHEN (g.winner = '主队' AND m.home_team_id = p.team_id) 
                      OR (g.winner = '客队' AND m.away_team_id = p.team_id) 
                    THEN 1 
                    ELSE 0 
                END) * 100.0 / COUNT(DISTINCT CONCAT(pig.match_id, '-', pig.game_id)))
            END as win_rate
        FROM Player p
        LEFT JOIN Player_In_Game pig ON p.student_id = pig.student_id
        LEFT JOIN Game g ON pig.match_id = g.match_id AND pig.game_id = g.game_id
        LEFT JOIN `Match` m ON pig.match_id = m.match_id
        WHERE p.team_id = %s
        GROUP BY p.student_id, p.name, p.gender, p.role
        ORDER BY {order_by}
        """

        data = self.db_conn.execute_query(query, (self.team_info['team_id'],))

        # Clear existing cards
        layout = self.statsCardsLayout
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Add player stat cards
        if not data:
            no_data_label = QLabel("暂无球员统计数据")
            no_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_data_label.setStyleSheet("color: #999; font-size: 14pt; padding: 50px;")
            layout.addWidget(no_data_label)
        else:
            for player_data in data:
                # Rename 'total_games' to 'total_matches' for the card display
                player_data['total_matches'] = player_data['total_games']
                card = PlayerStatCard(player_data)
                layout.addWidget(card)

    def load_team_tournaments(self):
        """Load all tournaments that the team participates in"""
        query = """
        SELECT DISTINCT t.tournament_id, t.tournament_name, t.year, t.status
        FROM Tournament t
        JOIN `Match` m ON t.tournament_id = m.tournament_id
        WHERE m.home_team_id = %s OR m.away_team_id = %s
        ORDER BY t.year DESC, t.tournament_id DESC
        """
        self._populate_tournaments_table(
            query,
            (self.team_info['team_id'], self.team_info['team_id'])
        )

    def search_tournaments(self):
        """Search tournaments by name or year"""
        search_text = self.searchTournamentInput.text().strip()

        if not search_text:
            self.load_team_tournaments()
            return

        query = """
        SELECT DISTINCT t.tournament_id, t.tournament_name, t.year, t.status
        FROM Tournament t
        JOIN `Match` m ON t.tournament_id = m.tournament_id
        WHERE (m.home_team_id = %s OR m.away_team_id = %s)
        AND (t.tournament_name LIKE %s OR t.year LIKE %s)
        ORDER BY t.year DESC, t.tournament_id DESC
        """
        search_pattern = f"%{search_text}%"
        self._populate_tournaments_table(
            query,
            (self.team_info['team_id'], self.team_info['team_id'],
             search_pattern, search_pattern)
        )

    def clear_tournament_search(self):
        """Clear tournament search and reload all tournaments"""
        self.searchTournamentInput.clear()
        self.load_team_tournaments()

    def _populate_tournaments_table(self, query, params):
        """Helper method to populate tournaments table"""
        data = self.db_conn.execute_query(query, params)

        self.tournamentsTable.setRowCount(len(data))
        for row_idx, row_data in enumerate(data):
            self.tournamentsTable.setItem(row_idx, 0, QTableWidgetItem(str(row_data['tournament_id'])))
            self.tournamentsTable.setItem(row_idx, 1, QTableWidgetItem(row_data['tournament_name']))
            self.tournamentsTable.setItem(row_idx, 2, QTableWidgetItem(str(row_data['year'])))
            self.tournamentsTable.setItem(row_idx, 3, QTableWidgetItem(row_data['status']))

    def load_team_matches(self):
        """Load all team matches"""
        query = """
        SELECT 
            m.match_id,
            m.scheduled_time,
            m.venue,
            t.tournament_name,
            CASE 
                WHEN m.home_team_id = %s THEN away_t.team_name
                ELSE home_t.team_name
            END as opponent,
            m.final_score,
            m.referee
        FROM `Match` m
        JOIN Tournament t ON m.tournament_id = t.tournament_id
        JOIN Team home_t ON m.home_team_id = home_t.team_id
        JOIN Team away_t ON m.away_team_id = away_t.team_id
        WHERE m.home_team_id = %s OR m.away_team_id = %s
        ORDER BY m.scheduled_time DESC
        """
        self._populate_matches_table(
            query,
            (self.team_info['team_id'], self.team_info['team_id'], self.team_info['team_id'])
        )

    def search_matches(self):
        """Search matches by opponent name or venue"""
        search_text = self.searchMatchInput.text().strip()

        if not search_text:
            self.load_team_matches()
            return

        query = """
        SELECT 
            m.match_id,
            m.scheduled_time,
            m.venue,
            t.tournament_name,
            CASE 
                WHEN m.home_team_id = %s THEN away_t.team_name
                ELSE home_t.team_name
            END as opponent,
            m.final_score,
            m.referee
        FROM `Match` m
        JOIN Tournament t ON m.tournament_id = t.tournament_id
        JOIN Team home_t ON m.home_team_id = home_t.team_id
        JOIN Team away_t ON m.away_team_id = away_t.team_id
        WHERE (m.home_team_id = %s OR m.away_team_id = %s)
        AND (home_t.team_name LIKE %s OR away_t.team_name LIKE %s OR m.venue LIKE %s)
        ORDER BY m.scheduled_time DESC
        """
        search_pattern = f"%{search_text}%"
        self._populate_matches_table(
            query,
            (self.team_info['team_id'], self.team_info['team_id'], self.team_info['team_id'],
             search_pattern, search_pattern, search_pattern)
        )

    def clear_match_search(self):
        """Clear match search and reload all matches"""
        self.searchMatchInput.clear()
        self.load_team_matches()

    def _populate_matches_table(self, query, params):
        """Helper method to populate matches table"""
        data = self.db_conn.execute_query(query, params)

        self.matchesTable.setRowCount(len(data))
        for row_idx, row_data in enumerate(data):
            self.matchesTable.setItem(row_idx, 0, QTableWidgetItem(str(row_data['match_id'])))
            self.matchesTable.setItem(row_idx, 1, QTableWidgetItem(str(row_data['scheduled_time'])))
            self.matchesTable.setItem(row_idx, 2, QTableWidgetItem(row_data['venue'] or ''))
            self.matchesTable.setItem(row_idx, 3, QTableWidgetItem(row_data['tournament_name']))
            self.matchesTable.setItem(row_idx, 4, QTableWidgetItem(row_data['opponent']))
            self.matchesTable.setItem(row_idx, 5, QTableWidgetItem(row_data['final_score'] or ''))
            self.matchesTable.setItem(row_idx, 6, QTableWidgetItem(row_data['referee'] or ''))

    def add_player(self):
        """Add a new player to the team"""
        dialog = AddPlayerDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            values = dialog.get_values()

            # Validate input
            if not values['student_id'] or not values['name']:
                QMessageBox.warning(self, "输入错误", "学号和姓名不能为空！")
                return

            # Insert player
            query = """
            INSERT INTO Player (student_id, name, gender, grade, phone, team_id, role)
            VALUES (%s, %s, %s, %s, %s, %s, '队员')
            """
            if self.db_conn.execute_update(
                    query,
                    (values['student_id'], values['name'], values['gender'],
                     values['grade'], values['phone'], self.team_info['team_id'])
            ):
                QMessageBox.information(self, "成功", "球员添加成功！")
                self.load_team_players()
                self.load_player_statistics()
                self.searchPlayerInput.clear()
            else:
                QMessageBox.warning(self, "错误", "添加失败！该学号可能已存在。")

    def remove_player(self):
        """Remove a player from the team"""
        current_row = self.playersTable.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "警告", "请选择要移除的球员！")
            return

        student_id = self.playersTable.item(current_row, 0).text()
        role = self.playersTable.item(current_row, 5).text()

        # Cannot remove captain
        if role == '队长':
            QMessageBox.warning(self, "警告", "不能移除队长！")
            return

        reply = QMessageBox.question(
            self,
            "确认移除",
            f"确定要移除球员 {self.playersTable.item(current_row, 1).text()} 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            query = "DELETE FROM Player WHERE student_id = %s"
            if self.db_conn.execute_update(query, (student_id,)):
                QMessageBox.information(self, "成功", "球员移除成功！")
                self.load_team_players()
                self.load_player_statistics()
                self.searchPlayerInput.clear()
            else:
                QMessageBox.warning(self, "错误", "移除失败！")