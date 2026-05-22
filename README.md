# 🚀 Brut3Zero — Advanced Brute Force & Login Discovery Framework

<p align="center">
  <b>Professional Python-Based Cybersecurity Automation Tool for Ethical Hacking & Penetration Testing</b>
</p>

---

## 🔥 Overview

**Brut3Zero** is an advanced GUI-based cybersecurity tool developed for **ethical hacking, penetration testing, and security research**.
The application automates authentication testing against multiple protocols while intelligently discovering hidden login portals using an integrated web crawler.

Designed with performance, usability, and deployment in mind, the tool combines **multithreading**, **dynamic login detection**, and a **modern graphical interface** into a standalone Windows executable.

---

# ✨ Core Features

## 🌐 Multi-Protocol Brute Force Engine

* HTTP Login Form Authentication Testing
* FTP Credential Testing
* SSH Authentication Testing
* Dynamic session handling
* Automatic success detection mechanisms

---

## 🕷 Intelligent Login Page Discovery

* Recursive website crawling
* Automatic admin/login portal discovery
* Smart login form identification using HTML parsing
* URL prioritization using authentication keywords
* Configurable crawl depth support

---

## 🖥 Modern GUI Interface

Built using **Tkinter + ttkbootstrap**

### Interface Features

* Modern responsive design
* Animated splash screen
* Real-time activity logs
* Interactive file dialogs
* Progress monitoring
* Success popup notifications
* User-friendly workflow

---

## ⚡ High-Performance Multithreading

* Concurrent credential testing
* Adjustable brute-force speed
* Optimized using `ThreadPoolExecutor`
* Improved execution efficiency

---

## 🔐 Credential Management

* Custom username/password wordlists
* Built-in default credential libraries
* Bulk authentication testing support

---

## 📩 Notification System

* Email alerts for successful authentication
* Animated credential success notifications
* Real-time attack monitoring

---

## 📊 Logging & Reporting

* Real-time console output
* Exportable attack logs
* Browser-integrated project documentation
* Project information viewer

---

# 🛠 Technologies Used

## 💻 Programming Language

* Python 3.10

## 🎨 GUI Framework

* Tkinter
* ttkbootstrap

## 🌍 Networking & Security

* requests
* ftplib
* paramiko

## 🔎 Web Crawling & Parsing

* BeautifulSoup (bs4)
* urllib.parse

## ⚙ Concurrency

* threading
* concurrent.futures

## 📧 Email Integration

* smtplib
* MIMEText / MIMEMultipart

## 🖼 Image Processing

* PIL (Pillow)

## 📦 Packaging & Deployment

* PyInstaller

---

# ⚙ Technical Functionalities

## 🔓 HTTP Brute Force Engine

* Automatic login form detection
* Dynamic field extraction
* GET & POST authentication support
* Session-based authentication handling
* Login success detection through:

  * Redirect analysis
  * Dashboard keyword detection
  * Response length comparison

---

## 📡 FTP Authentication Module

* Automated FTP credential testing
* Authentication failure handling
* Timeout management

---

## 🔑 SSH Authentication Module

* Secure SSH testing using Paramiko
* Automated credential validation
* Robust exception handling

---

## 🕸 Smart Web Crawler

* Recursive website crawling
* Login/admin panel discovery
* Intelligent authentication-page identification
* Keyword-based prioritization engine

---

# 🖥 GUI Components

## User Inputs

* Target URL / IP Address
* Username Wordlist
* Password Wordlist
* Protocol Selection
* Port Configuration
* Thread Management
* Notification Email

---

## Interactive Features

* Browse file dialogs
* Toggle default wordlists
* Export logs
* Real-time activity console

---

# 📦 Standalone Executable Deployment

The project was successfully converted into a fully standalone **Windows Executable (.exe)** using **PyInstaller**.

### Packaging Components

* `.spec` configuration
* `.toc` analysis files
* Runtime hook integration
* Dependency packaging
* Asset bundling

### Generated Build Files

* `added.spec`
* `Analysis-00.toc`
* `EXE-00.toc`
* `PKG-00.toc`
* `PYZ-00.pyz`
* `added.pkg`

---

# 🎯 Key Cybersecurity Concepts Demonstrated

* Ethical Hacking
* Penetration Testing
* Authentication Security Testing
* Brute Force Automation
* Web Crawling
* Concurrent Programming
* GUI Application Development
* Network Security
* Executable Packaging
* Python Automation

---

# 📚 Educational Purpose

This project was developed strictly for:

* Ethical Hacking Practice
* Cybersecurity Research
* Penetration Testing Demonstrations
* Educational & Learning Purposes

---

# 👨‍💻 Developer Notes

Brut3Zero demonstrates the integration of:

* Advanced Python automation
* Networking & security concepts
* GUI engineering
* Concurrent programming
* Executable deployment pipelines

The project focuses on building a realistic penetration-testing workflow while maintaining a professional desktop application experience.

---

<p align="center">
  <b>⚠ Disclaimer:</b> This project is intended strictly for authorized security testing and educational purposes only.
</p>
