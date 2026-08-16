import sys

import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Seismic Visualization and Analysis Tool")
        self.resize(1200, 800)

        self.data = None
        self.current_slice = "Iline"

        # Main widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        # Load button
        self.load_button = QPushButton("Load Seismic Volume")
        self.load_button.clicked.connect(self.load_volume)
        main_layout.addWidget(self.load_button)

        # Slice controls
        controls_layout = QHBoxLayout()

        direction_label = QLabel("Slice direction:")

        self.direction_combo = QComboBox()
        self.direction_combo.addItems(["Iline", "Xline"])
        self.direction_combo.currentTextChanged.connect(
            self.change_direction
        )

        self.index_label = QLabel("Index: 0")

        self.index_slider = QSlider(Qt.Horizontal)
        self.index_slider.setMinimum(0)
        self.index_slider.setMaximum(1)
        self.index_slider.setValue(0)
        self.index_slider.valueChanged.connect(self.update_slice)

        controls_layout.addWidget(direction_label)
        controls_layout.addWidget(self.direction_combo)
        controls_layout.addWidget(self.index_label)
        controls_layout.addWidget(self.index_slider)

        main_layout.addLayout(controls_layout)

        # Status
        self.status_label = QLabel("No seismic volume loaded.")
        main_layout.addWidget(self.status_label)

        # Matplotlib
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        main_layout.addWidget(self.canvas)

    def load_volume(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Seismic Volume",
            "",
            "NumPy Files (*.npy)",
        )

        if not file_path:
            return

        try:
            self.data = np.load(file_path, mmap_mode="r")

            if self.data.ndim != 3:
                self.status_label.setText(
                    "Error: Selected file is not a 3D seismic volume."
                )
                self.data = None
                return

            self.direction_combo.setCurrentText("Iline")

            self.index_slider.setMinimum(0)
            self.index_slider.setMaximum(self.data.shape[0] - 1)

            middle_index = self.data.shape[0] // 2
            self.index_slider.setValue(middle_index)

            self.status_label.setText(
                f"Volume loaded: {self.data.shape}"
            )

            self.update_slice()

        except Exception as error:
            self.status_label.setText(
                f"Error loading volume: {error}"
            )

    def change_direction(self, direction):
        if self.data is None:
            return

        if direction == "Iline":
            maximum = self.data.shape[0] - 1
        else:
            maximum = self.data.shape[1] - 1

        self.index_slider.blockSignals(True)
        self.index_slider.setMinimum(0)
        self.index_slider.setMaximum(maximum)

        middle_index = maximum // 2
        self.index_slider.setValue(middle_index)

        self.index_slider.blockSignals(False)

        self.update_slice()

    def update_slice(self):
        if self.data is None:
            return

        index = self.index_slider.value()
        direction = self.direction_combo.currentText()

        if direction == "Iline":
            seismic_slice = self.data[index, :, :]
        else:
            seismic_slice = self.data[:, index, :]

        self.index_label.setText(f"Index: {index}")

        self.figure.clear()

        ax = self.figure.add_subplot(111)

        image = ax.imshow(
            seismic_slice.T,
            aspect="auto",
            cmap="gray",
            origin="upper",
        )

        ax.set_title(f"{direction} {index}")
        ax.set_xlabel(
            "Xline" if direction == "Iline" else "Iline"
        )
        ax.set_ylabel("Time")

        self.figure.colorbar(
            image,
            ax=ax,
            label="Amplitude",
        )

        self.figure.tight_layout()

        self.canvas.draw()


app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit(app.exec())