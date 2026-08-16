import sys
import numpy as np

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
)

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Seismic Visualization and Analysis Tool")
        self.resize(1200, 800)

        self.data = None

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        self.load_button = QPushButton("Load Seismic Volume")
        self.load_button.clicked.connect(self.load_volume)
        layout.addWidget(self.load_button)

        self.status_label = QLabel("No seismic volume loaded.")
        layout.addWidget(self.status_label)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        layout.addWidget(self.canvas)

    def load_volume(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Seismic Volume",
            "",
            "NumPy Files (*.npy)"
        )

        if not file_path:
            return

        try:
            self.data = np.load(file_path, mmap_mode="r")

            if self.data.ndim != 3:
                self.status_label.setText(
                    "Error: The selected file is not a 3D volume."
                )
                self.data = None
                return

            iline_index = self.data.shape[0] // 2
            iline_slice = self.data[iline_index, :, :]

            self.figure.clear()

            ax = self.figure.add_subplot(111)

            image = ax.imshow(
                iline_slice.T,
                aspect="auto",
                cmap="gray",
                origin="upper"
            )

            ax.set_title(f"Iline {iline_index}")
            ax.set_xlabel("Xline")
            ax.set_ylabel("Time")

            self.figure.colorbar(image, ax=ax, label="Amplitude")

            self.canvas.draw()

            self.status_label.setText(
                f"Volume loaded: {self.data.shape}"
            )

        except Exception as error:
            self.status_label.setText(
                f"Error loading volume: {error}"
            )


app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit(app.exec())