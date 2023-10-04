# O-Chem-Identifier

<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#about">About</a></li>
    <li><a href="#prerequisites">Prerequisites</a></li>
    <li><a href="#quick-start">Quick Start</a></li>
    <li><a href="#user-manual">User Manual</a></li>
    <li><a href="#outside-cases">Outside Cases</a></li>
  </ol>
</details>
 

## About

Created by David Guest, Danny Nash, Kevin Reisch, and Andrew Bissel. This application enables users to convert hand-drawn organic chemistry molecules into digital copies. Even if the handwriting is challenging to decipher, a machine learning model will adjust it to produce recognizable characters in the final digital copy. The README which will provide instructions and accompanying pictures, will be finalized on 10/5/2023 to guide users in making the application executable on their machine.

## Prerequisites

Below are the tools needed to create and run this application:

- [Create an account on GitHub](https://github.com/join)
- [Install GitHub Desktop](https://desktop.github.com/)
- [Install Python (should come with pip, which is needed)](https://www.python.org/downloads/)
- [Install Visual Studio Code](https://code.visualstudio.com/download)

## Quick Start

To run the application:

1. Clone this repository to GitHub Desktop. Clone to a path that will be easy to access, e.g C:\Users\dguest390\Documents\O-Chem-Identifier
<p align="center">
  <img width="1250" src="media\clone_pic.png" alt="Clone Picture">
</p>

2. In GitHub Desktop open the application in Visual Studio Code
<p align="center">
  <img width="1250" src="media\VSCode.png" alt="Open with VSCode">
</p>

3. In VS Code use the top navigation bar to click terminal - select new terminal
<p align="center">
  <img width="1250" src="media\new_terminal.png" alt="New Terminal">
</p>


4. Make sure the path in the terminal is set to the location of where the application is on your machine, e.g. C:\Users\dguest390\Documents\O-Chem-Identifier. If it is not there, change directories to the correct path [How To Change](https://www.howtogeek.com/659411/how-to-change-directories-in-command-prompt-on-windows-10/)

5. Create a Virtual Environment to execute the application. In the terminal run this command to create an environment called "ochem":
<p>
<code>python -m venv ochem</code>
</p>

6. Run the Virtual Environment with this command:
<p>
  <code>ochem\Scripts\activate</code>
</p>
  
6. Install these packages into the new V.E. by entering this command in the terminal:
<p>
  <code>pip install pillow opencv-python keras tensorflow matplotlib imutils</code>
</p>

7. Execute the program in the terminal by entering:
<p>
  <code>python main.py</code>
</p>

## User Manual

//picture to show layout of running application

- At any point if there is an issue such as, not enough electrons to form a certain bond, it will be displayed in the lower textbox the exact issue

// picture of textbox

- Top navigation bar allows atoms and polyatomic atoms to be selceted and placed on the canvas

// either picture of atoms placed on canvas or short video showing the process

#### Side Navigation Bar

- Single, Double, Triple - allow bonds to be created between atoms that already exist on the canvas

// picture of bonds created or short video

- Delete - allow bonds or atoms/polyatomic atoms to be deleted one by one

// picure or video

- Clear - clear the entire canvas - a conformation box will appear to make sure the action was intended

// picture or video

- Import - import an image on your local device of a hand-drawn organic chemistry molecule. Once selected the option to "crop" will appear so a specific molecule can be selected

// pic or vid

- Translate - will translate the recently "cropped" hand-drawn molecule into a digital version

// pic or vid

- Photo - requires this application to be running on a raspberry pi with a camera setup and touch display screen. This is currently outside the purview of this tutorial

## Outside Cases

// respond to issues with certain molecules not translating perfectly and how we would work to fix them for future updates
