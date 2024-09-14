import sys
import json
import uuid
import subprocess
import os
from typing import Dict, List, Optional
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem, QInputDialog, QMessageBox, QFileDialog, QStyle
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QMimeData

class Project:
    def __init__(self, name: str, path: str):
        self.id = str(uuid.uuid4())
        self.name = name
        self.path = path
        self.type = "project"


class Folder:
    def __init__(self, name: str):
        self.id = str(uuid.uuid4())
        self.name = name
        self.children: List[str] = []
        self.type = "folder"


class DraggableTreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QTreeWidget.InternalMove)

    def dropEvent(self, event):
        if event.source() == self:
            dragged_item = self.currentItem()
            target_item = self.itemAt(event.pos())

            if target_item is None:
                # Dropping to the root
                if dragged_item.parent():
                    dragged_item.parent().takeChild(dragged_item.parent().indexOfChild(dragged_item))
                else:
                    self.takeTopLevelItem(self.indexOfTopLevelItem(dragged_item))
                self.addTopLevelItem(dragged_item)
                event.accept()
            elif target_item.text(1) == "Folder":
                # Dropping into a folder
                if dragged_item.parent():
                    dragged_item.parent().takeChild(dragged_item.parent().indexOfChild(dragged_item))
                else:
                    self.takeTopLevelItem(self.indexOfTopLevelItem(dragged_item))
                target_item.addChild(dragged_item)
                target_item.setExpanded(False)  # Expand the folder to show the newly added item
                event.accept()
            else:
                event.ignore()
                return

            self.parent().update_data_from_tree()
        else:
            event.ignore()


class CursorProjectManager(QWidget):
    def __init__(self):
        super().__init__()
        self.projects: Dict[str, Project | Folder] = {}
        self.root_items: List[str] = []

        self.init_icons()
        self.init_ui()
        self.load_data()

    def init_icons(self):
        self.folder_icon = self.style().standardIcon(QStyle.SP_DirIcon)
        self.file_icon = self.style().standardIcon(QStyle.SP_ComputerIcon)

    def init_ui(self):
        self.setWindowTitle('Cursor Project Manager')
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        # Tree widget
        self.tree = DraggableTreeWidget(self)
        self.tree.setHeaderLabels(['Name'])
        layout.addWidget(self.tree)

        # Buttons
        button_layout = QHBoxLayout()
        self.add_project_btn = QPushButton('Add Project', self)
        self.add_folder_btn = QPushButton('Add Folder', self)
        self.edit_btn = QPushButton('Edit', self)
        self.delete_btn = QPushButton('Delete', self)

        button_layout.addWidget(self.add_project_btn)
        button_layout.addWidget(self.add_folder_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Connect signals
        self.add_project_btn.clicked.connect(self.add_project)
        self.add_folder_btn.clicked.connect(self.add_folder)
        self.edit_btn.clicked.connect(self.edit_item)
        self.delete_btn.clicked.connect(self.delete_item)
        self.tree.itemDoubleClicked.connect(self.on_item_double_clicked)

    def add_project(self):
        name, ok = QInputDialog.getText(self, 'Add Project', 'Enter project name:')
        if ok and name:
            path = QFileDialog.getExistingDirectory(self, 'Select Project Directory')
            if path:
                project = Project(name, path)
                self.projects[project.id] = project
                self.root_items.append(project.id)
                self.update_tree()
                self.save_data()

    def add_folder(self):
        name, ok = QInputDialog.getText(self, 'Add Folder', 'Enter folder name:')
        if ok and name:
            folder = Folder(name)
            self.projects[folder.id] = folder
            self.root_items.append(folder.id)
            self.update_tree()
            self.save_data()

    def edit_item(self):
        item = self.tree.currentItem()
        if item:
            new_name, ok = QInputDialog.getText(self, 'Edit Item', 'Enter new name:', text=item.text(0))
            if ok and new_name:
                item_id = item.text(2)
                self.projects[item_id].name = new_name
                self.update_tree()
                self.save_data()

    def delete_item(self):
        item = self.tree.currentItem()
        if item:
            reply = QMessageBox.question(self, 'Delete Item', 'Are you sure you want to delete this item?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                item_id = item.text(2)
                parent_item = item.parent()

                if parent_item:
                    parent_id = parent_item.text(2)
                    parent = self.projects.get(parent_id)
                    if isinstance(parent, Folder):
                        parent.children.remove(item_id)
                else:
                    self.root_items.remove(item_id)

                self.delete_item_recursive(item_id)

                (item.parent() or self.tree.invisibleRootItem()).removeChild(item)

                self.save_data()
    def delete_item_recursive(self, item_id):
        item = self.projects.pop(item_id, None)
        if item and isinstance(item, Folder):
            for child_id in item.children[:]:
                self.delete_item_recursive(child_id)

    def on_item_double_clicked(self, item, column):
        item_id = item.text(2)
        project = self.projects.get(item_id)
        if isinstance(project, Project):
            try:
                subprocess.Popen("code .", shell=True, cwd=project.path)
            except Exception as e:
                QMessageBox.warning(self, 'Error', f"Failed to launch Cursor: {str(e)}")

    def update_tree(self):
        self.tree.clear()
        for item_id in self.root_items:
            if item_id in self.projects:
                self.add_item_to_tree(item_id, self.tree.invisibleRootItem())
        self.tree.expandAll()

    def add_item_to_tree(self, item_id, parent_item):
        item = self.projects[item_id]
        tree_item = QTreeWidgetItem(parent_item)
        tree_item.setText(0, item.name)
        tree_item.setText(1, item.type.capitalize())
        tree_item.setText(2, item.id)

        if isinstance(item, Project):
            tree_item.setIcon(0, self.file_icon)
        else:
            tree_item.setIcon(0, self.folder_icon)

        if isinstance(item, Folder):
            for child_id in item.children:
                self.add_item_to_tree(child_id, tree_item)

    def update_data_from_tree(self):
        self.root_items.clear()
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            self.root_items.append(item.text(2))
            self.update_folder_children(item)
        self.save_data()
        self.update_tree()

    def update_folder_children(self, tree_item):
        item_id = tree_item.text(2)
        item = self.projects.get(item_id)
        if isinstance(item, Folder):
            item.children.clear()
            for i in range(tree_item.childCount()):
                child_item = tree_item.child(i)
                item.children.append(child_item.text(2))
                self.update_folder_children(child_item)

    def save_data(self):
        data = {
            "projects": {k: v.__dict__ for k, v in self.projects.items()},
            "root_items": self.root_items
        }
        with open("projects.json", "w") as f:
            json.dump(data, f, indent=2)

    def load_data(self):
        try:
            with open("projects.json", "r") as f:
                data = json.load(f)

            if not isinstance(data, dict):
                print("Le fichier JSON ne contient pas un objet valide. Initialisation d'une nouvelle structure.")
                return

            self.projects.clear()
            self.root_items = data.get("root_items", [])

            for k, v in data.get("projects", {}).items():
                if isinstance(v, dict):
                    if v.get("type") == "project":
                        project = Project(v["name"], v["path"])
                        project.id = k
                        self.projects[k] = project
                    elif v.get("type") == "folder":
                        folder = Folder(v["name"])
                        folder.id = k
                        folder.children = v.get("children", [])
                        self.projects[k] = folder
                    else:
                        print(f"Type invalide pour l'élément {k}. Ignoré.")
                else:
                    print(f"Données invalides pour l'élément {k}. Ignoré.")

            self.update_tree()

        except FileNotFoundError:
            print("Fichier projects.json non trouvé. Initialisation d'une nouvelle structure.")
        except json.JSONDecodeError:
            print("Le fichier projects.json contient des données JSON invalides. Initialisation d'une nouvelle structure.")
        except Exception as e:
            print(f"Une erreur inattendue s'est produite lors du chargement des données : {e}")


def main():
    app = QApplication(sys.argv)

    app_icon = QIcon("icon.ico")
    app.setWindowIcon(app_icon)

    ex = CursorProjectManager()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()