# CPL-Compiler
Final Project in "Compilers - 20364" @ The Open University of Israel.

Provided below are options to use the compiler without installation or install it as an executable binary file.
## Installing Dependencies
Make sure you have all the necessary dependencies by executing the following comment from the `CPL-Compiler` directory.
```
pip install -r requirements.txt
```
Or alternatively installing sly directly.
```
pip install sly==0.5
```
## Running without installation
You should be able to use the compiler directly with Python:
```
python3 src/cpq.py <input.ou>
```

## Installing as an executable
Make sure you have `pyinstaller` installed first.
```
pip install pyinstaller
```
Then, from the directory `CPL-Compiler`, execute:
```
pyinstaller -F src/cpq.py
```
The executable file will reside in `CPL-Compiler/dist/cpq.exe` or `CPL-Compiler/dist/cpq` for UNIX.
