import sys
import socket
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QVBoxLayout, QPushButton, QFormLayout, QTabWidget, QListWidget, QMessageBox
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class HealthMonitoringUI(QMainWindow):
    def _init_(self):
        super()._init_()

        # Set window title
        self.setWindowTitle("Health Monitoring System")

        # Create a central widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Create a layout for the central widget
        layout = QVBoxLayout()

        # Create a form layout to add patient details
        form_layout = QFormLayout()

        # Add widgets for patient details: name, age, sex, and patient number
        self.name_label = QLabel("Name:")
        self.name_input = QLineEdit()
        form_layout.addRow(self.name_label, self.name_input)

        self.age_label = QLabel("Age:")
        self.age_input = QLineEdit()
        form_layout.addRow(self.age_label, self.age_input)

        self.sex_label = QLabel("Sex:")
        self.sex_input = QLineEdit()
        form_layout.addRow(self.sex_label, self.sex_input)

        self.patient_number_label = QLabel("Patient Number:")
        self.patient_number_input = QLineEdit()
        form_layout.addRow(self.patient_number_label, self.patient_number_input)

        # Add the form layout to the main layout
        layout.addLayout(form_layout)

        # Create a button to submit patient details
        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(self.submit_patient_details)
        layout.addWidget(submit_button)

        # Create buttons to plot different types of data
        plot_heart_rate_button = QPushButton("Plot Heart Rate")
        plot_heart_rate_button.clicked.connect(lambda: self.show_plot_data_dialog("heart_rate"))
        layout.addWidget(plot_heart_rate_button)

        # ... Add similar buttons for ECG and temperature plots ...

        # Create a tab widget for patient list and patient details
        tab_widget = QTabWidget()

        # Create a list widget for the patient list tab
        self.patient_list_widget = QListWidget()
        self.patient_list_widget.itemDoubleClicked.connect(self.show_patient_details)
        tab_widget.addTab(self.patient_list_widget, "List of Patients")

        layout.addWidget(tab_widget)

        # Set the layout for the central widget
        central_widget.setLayout(layout)

        # Dictionary to store patient data
        self.patient_data = {}

        # Real-time data plotting
        self.fig, self.ax = plt.subplots()
        self.anim = None

    def submit_patient_details(self):
        # Retrieve and process patient details when the submit button is clicked
        name = self.name_input.text()
        age = self.age_input.text()
        sex = self.sex_input.text()
        patient_number = self.patient_number_input.text()

        # Add the patient to the list of patients in the UI
        self.patient_list_widget.addItem(f"{name} ({patient_number})")

        # Store patient details in the dictionary
        self.patient_data[patient_number] = {
            'name': name,
            'age': age,
            'sex': sex,
            'heart_rate': 'N/A',
            'ecg': 'N/A',
            'body_temperature': 'N/A'
        }

        # Clear the input fields
        self.name_input.clear()
        self.age_input.clear()
        self.sex_input.clear()
        self.patient_number_input.clear()

    def show_patient_details(self, item):
        patient_info = item.text().split(" ")
        patient_number = patient_info[-1][1:-1]
        if patient_number in self.patient_data:
            patient_details = self.patient_data[patient_number]
            details_window = PatientDetailsUI(patient_details)
            details_window.show()

    def plot_data(self, patient_number, data_type):
        if patient_number in self.patient_data:
            patient_details = self.patient_data[patient_number]
            data = patient_details[data_type]

            if data != 'N/A':
                data = [float(value) for value in data.split(',')]
                self.ax.clear()
                self.ax.plot(data)
                self.ax.set_xlabel('Time')
                self.ax.set_ylabel(data_type)
                self.ax.set_title(f'{data_type} Chart for Patient {patient_number}')
                self.fig.canvas.draw()
                self.fig.canvas.flush_events()
            else:
                QMessageBox.warning(self, 'Warning', f'{data_type} data is not available for this patient.')

    def show_plot_data_dialog(self, data_type):
        def plot_data():
            selected_item = self.patient_list_widget.currentItem()
            if selected_item:
                patient_info = selected_item.text().split(" ")
                patient_number = patient_info[-1][1:-1]
                self.plot_data(patient_number, data_type)

        return plot_data

class PatientDetailsUI(QMainWindow):
    def _init_(self, patient_data):
        super().__init()

        self.setWindowTitle("Patient Details")

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        patient_label = QLabel(f"Name: {patient_data['name']}, Age: {patient_data['age']}, Sex: {patient_data['sex']}")
        layout.addWidget(patient_label)

        heart_rate_label = QLabel(f"Heart Rate: {patient_data['heart_rate']}")
        layout.addWidget(heart_rate_label)

        ecg_label = QLabel(f"ECG: {patient_data['ecg']}")
        layout.addWidget(ecg_label)

        body_temperature_label = QLabel(f"Body Temperature: {patient_data['body_temperature']}")
        layout.addWidget(body_temperature_label)

        central_widget.setLayout(layout)

def run_health_monitoring_server():
    # Raspberry Pi's IP address and port to listen on
    host = '0.0.0.0'  # Bind to all available network interfaces
    port = 12345  # Use a port that is not already in use

    # Create a socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the address and port
    server_socket.bind((host, port))

    # Listen for incoming connections
    server_socket.listen(5)

    print("Listening for incoming connections...")

    while True:
        # Accept a connection
        client_socket, client_address = server_socket.accept()
        print(f"Accepted connection from {client_address}")

        # Receive data from the Arduino
        data = client_socket.recv(1024).decode()
        print(f"Received data: {data}")

        # Process the received data and update patient data
        update_patient_data(data)

        # Close the client socket
        client_socket.close()

def update_patient_data(data):
    # Parse the received data and update patient data
    parts = data.split(',')
    if len(parts) == 2:
        patient_number, heart_rate = parts
        if patient_number in window.patient_data:
            window.patient_data[patient_number]['heart_rate'] = heart_rate

        # Trigger an update of the heart rate plot
        window.plot_data(patient_number, "heart_rate")

if _name_ == "_main_":
    # Start the server in a separate thread
    import threading
    server_thread = threading.Thread(target=run_health_monitoring_server)
    server_thread.start()

    # Start the PyQt application
    app = QApplication(sys.argv)
    window = HealthMonitoringUI()
    window.show()
    sys.exit(app.exec_())