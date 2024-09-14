# Cursor Project Manager

Cursor Project Manager is a PyQt5-based desktop application that helps you organize and manage your coding projects and folders. It provides an intuitive graphical interface for adding, editing, and deleting projects and folders, as well as a tree view for easy navigation.

## Features

- Add and manage coding projects with associated file paths
- Create and organize folders to group related projects
- Drag-and-drop functionality for easy reorganization
- Edit project and folder names
- Delete projects and folders (with confirmation)
- Double-click to open projects in Cursor (VS Code)
- Persistent storage of project data in JSON format

## Requirements

- Python 3.6+
- PyQt5
- Cursor (Visual Studio Code) installed on your system

## Installation

1. Clone this repository or download the source code.
2. Install the required dependencies:

```
pip install PyQt5
```

3. Ensure you have Cursor (VS Code) installed on your system.

## Usage

Run the application using Python:

```
python cursor_project_manager.py
```

### Adding a Project

1. Click the "Add Project" button.
2. Enter a name for the project.
3. Select the project directory using the file dialog.

### Adding a Folder

1. Click the "Add Folder" button.
2. Enter a name for the folder.

### Editing an Item

1. Select a project or folder in the tree view.
2. Click the "Edit" button.
3. Enter the new name for the item.

### Deleting an Item

1. Select a project or folder in the tree view.
2. Click the "Delete" button.
3. Confirm the deletion in the popup dialog.

### Opening a Project

Double-click on a project in the tree view to open it in Cursor (VS Code).

## Data Storage

The application stores project data in a `projects.json` file in the same directory as the script. This file is automatically created and updated as you make changes to your projects and folders.

## Icon

The application uses an icon file named `icon.ico`. Make sure this file is present in the same directory as the script for the application icon to display correctly.

## Contributing

Contributions to improve the Cursor Project Manager are welcome. Please feel free to submit pull requests or open issues to suggest improvements or report bugs.

## License

This project is open-source and available under the MIT License.
