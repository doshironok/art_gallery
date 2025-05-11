import sys
from PyQt5.QtWidgets import QApplication
from gui import ArtGalleryApp

def main():
    app = QApplication(sys.argv)
    with open('styles.qss', 'r') as f:
        app.setStyleSheet(f.read())
    window = ArtGalleryApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()