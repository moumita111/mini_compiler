Mini Compiler Project

Author: Moumita Afreen
Department: CSE, University of Asia Pacific

Overview

This project is a Mini Compiler implemented in Python using PLY (Lex & Yacc) and Tkinter. It demonstrates the fundamental stages of compilation: lexical analysis, syntax and semantic checking, symbol table creation, intermediate code generation, assembly-like code generation, and provides a user-friendly GUI for interactive compilation.

Features

Tokenizes source code into keywords, identifiers, numbers, operators, and symbols

Detects syntax and semantic errors such as undeclared variables and redeclarations

Generates Three-Address Code (Intermediate Code)

Converts intermediate code into a simple assembly-like representation

Provides a Tkinter GUI to visualize tokens, symbol table, intermediate code, assembly, and errors

Requirements

Python 3.x

PLY library (pip install ply)

Tkinter (usually included with Python)

Usage

Clone the repository:

git clone <repository_url>


Navigate to the project directory:

cd mini-compiler


Run the compiler:

python main.py


Type or paste your source code in the GUI editor and click Compile Code to see outputs for all compiler stages.

Sample Input
int a;
int b;
a = 5;
b = 10;
if (a < b) {
    a = a + b;
} else {
    b = b - a;
}
while (a > 0) {
    a = a - 1;
}

Outputs

Tokens

Symbol Table

Intermediate Code (Three-Address Code)

Assembly-like Code

Error Handling

License

This project is for academic purposes. You may freely use and modify it for learning and educational projects.
