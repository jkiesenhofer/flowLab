# Chemical Flotation Flow Lab Automation & Analytics

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green.svg)](https://opencv.org/)

An open-source suite of Python scripts and tools designed to automate data acquisition, image processing, and hydrodynamic modeling for laboratory-scale chemical flotation columns and cells. 

This repository provides general-purpose utilities for researchers and metallurgical engineers to monitor froth kinetics, calculate gas holdup, analyze bubble size distributions (BSD), and interface with lab hardware.

---

## Core Features & Scripts

The repository is organized into distinct modules based on experimental workflows:

### 1. Computer Vision & Froth Analytics (`/vision`)
* `froth_velocity.py`: Utilizes optical flow algorithms (Lucas-Kanade and Farneback) to track froth surface velocity and stability in real-time.
* `bubble_segmentation.py`: An OpenCV/Water-shed segmentation pipeline to extract bubble size distributions ($BSD$) and Sauter mean diameter ($d_{32}$) from high-speed camera feeds.

### 2. Hydrodynamics & Data Logging (`/hydrodynamics`)
* `gas_holdup.py`: Calculates gas holdup ($\varepsilon_g$) using differential pressure transmitter data inputs.
* `flow_controller_interface.py`: Modbus/Serial protocols to dynamically control and log mass flow controllers (MFCs) for superficial gas velocity ($J_g$) adjustments.

### 3. Kinetic Modeling (`/kinetics`)
* `flotation_kinetics_fitter.py`: Fits experimental recovery data against classic kinetic models (First-order rectangular, Klimpel, Kelsall) using non-linear least squares regression.

---

## Installation

### Prerequisites
* Python 3.10 or higher
* C++ Compiler (for certain OpenCV optimization flags, optional)

### Setup
1. Clone the repository:
   ```bash
   git clone [https://github.com/yourusername/flowLab.git](https://github.com/yourusername/fowLab.git)
   cd flowLab
