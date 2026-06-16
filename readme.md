# Bubble & Particle Fluid Simulation Project

A multi-language scientific computing project designed to model, simulate, and analyze fluid dynamics, specifically focusing on bubble detection, tracking, particle dynamics, and optical systems. This project integrates physics solvers (C/C++), processing/analysis scripts (Python, MATLAB), a graphical user interface (GUI), and hardware integration (Arduino).

## Overview

This repository contains a comprehensive suite of tools to handle fluid simulation workflows:
* **Simulation Solvers:** Core physics calculations handled via C/C++ (e.g., wave modeling, triangulation, Courant number calculations).
* **Computer Vision & Analysis:** Python and MATLAB scripts dedicated to detecting, tracking, and vector mapping of bubbles.
* **Hardware Integration:** Arduino code to manage physical particle drop experiments.
* **User Interface:** A Python-based GUI/App for easy interaction with the data and models.

---

## Repository Structure

Here is an overview of the key files and directories in this repository:

| File / Folder | Language / Type | Description |
| :--- | :--- | :--- |
| `mesh/` | Directory | Contains mesh generation files for fluid domains. |
| `plots/` | Directory | Output directory for generated figures and data plots. |
| `app.py` / `gui` | Python | Main application entry point and Graphical User Interface files. |
| `bubbleDetection.py` | Python | Computer vision script to isolate bubbles from images/video. |
| `bubbleIDs.py` | Python | Tracks and assigns unique identifiers to individual bubbles across frames. |
| `bubbleVectors.py` | Python | Calculates velocity and direction vectors for detected bubbles. |
| `brightestPoint.py` | Python | Detects laser/light intensity peaks or particle centers. |
| `courant.py` | Python | Computes the Courant–Friedrichs–Lewy (CFL) condition for simulation stability. |
| `flowModel.py` | Python | Mathematical modeling of the fluid flow characteristics. |
| `opticalSystem.py`| Python | Simulates or processes data from the camera/lens setup. |
| `tpc.py` | Python | Three-Phase Contact line or specialized tracking module. |
| `bubble.m` | MATLAB | Prototype script for bubble analysis and data visualization. |
| `wave.cpp` | C++ | Physics solver for wave propagation or free-surface flows. |
| `triangulation.cpp`| C++ | Spatial discretization or 3D reconstruction geometry logic. |
| `collision.h` / `hydrophobicity.H` | C++ Headers | Physics parameters for particle collisions and surface tension/wetting properties. |
| `particleDrop.ino` | Arduino | Firmware for controlling physical particle dropping mechanisms in experiments. |
| `stokes.html` | HTML | Web-based documentation or visualization for Stokes flow equations. |
| `makefile` | Build Script | Compilation configuration script for the C/C++ source code. |

---

## Getting Started

### Prerequisites

Ensure you have the following installed on your system:
* **GCC/Clang** (with `make` support for building C++ files)
* **Python 3.8+**
* **MATLAB** (Optional, for running `.m` analysis)
* **Arduino IDE** (Optional, for uploading hardware controls)

### Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
   cd your-repo-name
