
# SmartAttend - Face Recognition Employee Attendance System

A real-time **face recognition-based employee attendance system** designed for organizations to automate and secure attendance tracking using artificial intelligence and computer vision.

---

## 🚀 Tech Stack

- **Backend**: Python, Flask  
- **Frontend**: HTML, CSS, JavaScript  
- **Database**: SQLite  
- **Libraries/Frameworks**: OpenCV, dlib, face_recognition, DeepFace

---

## 🔧 Built With

<table> <tr> <td><img src="https://img.icons8.com/color/48/000000/opencv.png"/></td> <td><strong><a href="https://opencv.org/">OpenCV</a></strong><br/>For real-time image processing and computer vision</td> </tr> <tr> <td><img src="https://upload.wikimedia.org/wikipedia/commons/1/1b/Dlib_logo.png" width="48"/></td> <td><strong><a href="http://dlib.net/">dlib</a></strong><br/>Machine learning toolkit for face detection</td> </tr> <tr> <td><img src="https://avatars.githubusercontent.com/u/1961952?s=200&v=4" width="48"/></td> <td><strong><a href="https://github.com/ageitgey/face_recognition">face_recognition</a></strong><br/>Python-based facial recognition</td> </tr> <tr> <td><img src="https://raw.githubusercontent.com/serengil/deepface/master/icon/deepface-icon.png" width="48"/></td> <td><strong><a href="https://github.com/serengil/deepface">DeepFace</a></strong><br/>Deep learning for facial analysis</td> </tr> <tr> <td><img src="https://img.icons8.com/ios-filled/50/000000/flask.png"/></td> <td><strong><a href="https://flask.palletsprojects.com/">Flask</a></strong><br/>Lightweight web framework for backend logic</td> </tr> <tr> <td><img src="https://www.sqlite.org/images/sqlite370_banner.gif" width="48"/></td> <td><strong>SQLite</strong><br/>Lightweight, serverless database engine</td> </tr> </table>
- **SQLite** – Lightweight, serverless database engine

> 📌 Developed using **Python 3.8.13**

---

## 📸 Project Screenshots

### 🏠 1. Home Page

<img src="https://github.com/Rohan-Todkar-2003/SmartAttend-Facial_Recognition_Attendance_System/blob/main/Project%20Image/(Home%20Page)Index.html.png" alt="Home Page" width="100%"/>

This is the main homepage of the application.  
- **Left Panel:** Quick links for social media and help  
- **Right Panel:** Access buttons for:
  - Add Employee
  - Attendance Recognizer
  - Daily Attendance Sheet
  - Attendance Statistics  
- **Bottom Right:** Integrated chatbot for assistance  
- **Top Navbar:** Navigation controls for different sections

---

### 🧑‍💼 2. Known Face Recognition

<img src="Project Image/Attendance marking for known.png" alt="Known Face Attendance" width="100%"/>

When a known employee’s face is detected, the system will:
- Recognize the face for **3 seconds**
- If matched successfully, it **automatically marks attendance**

---

### 🚫 3. Anti-Spoofing Detection

<img src="https://github.com/Rohan-Todkar-2003/SmartAttend-Facial_Recognition_Attendance_System/blob/main/Project%20Image/Attendance%20taking%20of%20spoof.png" alt="Spoof Detection" width="100%"/>

The system integrates **anti-spoofing** detection to prevent fake attendance:
- Detects attempts using printed photos or mobile screens  
- Flags such attempts as **"Spoof"** and **does not mark attendance**

🔒 _Note:_ The anti-spoofing model code is **not included** in this repository.  
To access the model, visit this restricted link:  
[Access Anti-Spoofing Model](https://drive.google.com/file/d/17CJGSiXeuKlPpphWcFj0nhCsYonecVTE/view?usp=drive_link)  
For access, contact via [LinkedIn](https://www.linkedin.com/in/rohantodkar0705/) or [Email Me](mailto:rohantodkar@example.com)

---

### ❓ 4. Unknown Face Detection

<img src="https://github.com/Rohan-Todkar-2003/SmartAttend-Facial_Recognition_Attendance_System/blob/main/Project%20Image/Attendance%20taking%20of%20Unknown.png" alt="Unknown Face" width="100%"/>

If the system detects a face that is **not stored** in the employee database:
- It flags the individual as **"Unknown"**
- **Attendance is not marked** for unregistered users

---

## ⚙️ How to Run the Project

### 1. Clone the Repository

```bash
git clone https://github.com/Rohan-Todkar-2003/SmartAttend-Employee-Facial-Attendance-System.git
cd SmartAttend-Employee-Facial-Attendance-System
```

### 2. Set Up the Virtual Environment

```bash
conda env create -f msenv.yml
```

### 3. Activate the Virtual Environment

```bash
conda activate msenv
```

### 4. Run the Application

```bash
python app.py
```

---

## ✨ Features

✅ **Automated Attendance** – Marks attendance automatically using face recognition  
✅ **Real-Time Detection** – Uses webcam feed to detect and identify employees  
✅ **Web Interface** – Simple and clean web UI for managing employees and records  
✅ **Anti-Spoofing** – Prevents fake entries via photo or video using liveness detection  
✅ **Reporting** – Export attendance records for review and storage

---

## 📖 About the Project

Face recognition technology is revolutionizing security and time management in offices and institutions. This project combines AI-based face recognition with a web-based interface to offer a **touchless, secure, and efficient** employee attendance tracking solution.

With real-time detection and anti-spoofing measures, the system ensures high accuracy and prevents misuse. The interface allows users to manage records and export reports easily.

---

## 🚧 Future Enhancements

🔹 Mobile App Integration for remote check-ins  
🔹 Voice Recognition as fallback authentication  
🔹 Cloud-based storage and synchronization  
🔹 Admin Dashboard with analytics and insights  

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you’d like to change. Let's build something great together!

---

## 📬 Contact

📩 _Feel free to connect for collaboration, feedback, or access requests!_

**Rohan Todkar**  
[GitHub Profile](https://github.com/Rohan-Todkar-2003)  
[LinkedIn](https://www.linkedin.com/in/rohantodkar0705/)
[Email Me](mailto:rohantodkar2003@example.com) 

---

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.
