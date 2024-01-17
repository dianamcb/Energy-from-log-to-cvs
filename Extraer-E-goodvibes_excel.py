#!/usr/bin/python3

# Author: Diana Marlen Castaneda Bagatella
# Description: After a Gaussian calculation finished and the energy was extracted by GoodVibes. This script extracts the electronic energy with the corrections ans scaling factor and extract the numbers from the txt file to a cvs file.

import os, re
import numpy as np
import pandas as pd

def SearchTxtFiles():
    fileNameMatch = ".txt"
    txtFiles,txtRoots = [], []
    for root, dirs, files in os.walk("./"):
        for file in files:
            if file.endswith(fileNameMatch):
                txtFiles.append(os.path.join(root,file))
                txtRoots.append(root[2:])
    return txtFiles, txtRoots

def ReadTxtHeader(txtFile):
    header = False
    with open(txtFile, "r") as file: fileLines = file.readlines()
    for i in range(len(fileLines)):
        if re.search("Structure", fileLines[i]):
            header = fileLines[i]
            break
    if not header: exit(f"Header not found in file: {txtFile}\n"
                         "Please check the file and rerun the script.")
    return header.split()

def EditTxtFile(txtFile):
    with open(txtFile, "r") as file: fileLines = file.readlines()
    for i in range(2,len(fileLines)):
        if re.search("GoodVibes v\d", fileLines[i]):
            fileLines = fileLines[:i]
            break
    for i in range(len(fileLines)):
        fileLines[i] = re.sub("(^.+)Warning!.+", r"\1NaN\tNaN\tNaN\tNaN\tNaN\tNaN", fileLines[i])
    with open("tmpFile.tmp", "w") as file: file.write(" ".join(fileLines))

def CountRowsToSkip(txtFile):
    nRowsToSkip = False
    with open(txtFile, "r") as file: fileLines = file.readlines()
    for i in range(len(fileLines)):
        if re.search("\*{10,}", fileLines[i]):
            nRowsToSkip = i+1
            break
    if not nRowsToSkip: exit(f"Something is wrong with the file {txtFile}\n"
                              "Please check the file and rerun the script.")
    return nRowsToSkip

if __name__ == '__main__':
    txtFiles, txtRoots = SearchTxtFiles()
    header = ReadTxtHeader(txtFiles[0])
    EditTxtFile(txtFiles[0])
    nRowsToSkip = CountRowsToSkip(txtFiles[0])
    fileContent = pd.read_csv("tmpFile.tmp", engine='python', names=header, sep="\s+", skiprows=nRowsToSkip, skipfooter=1)
    fileContent["Root"] = txtRoots[0]
    fileContent.reset_index(drop=True, inplace=True)
    for i in range(1,len(txtFiles)):
        EditTxtFile(txtFiles[i])
        nRowsToSkip = CountRowsToSkip(txtFiles[i])
        newContent = pd.read_csv("tmpFile.tmp", engine='python', names=header, sep="\s+", skiprows=nRowsToSkip, skipfooter=1)
        newContent["Root"] = txtRoots[i]
        newContent.reset_index(drop=True, inplace=True)
        fileContent = pd.concat([fileContent, newContent], ignore_index=True)
    rootColumn = fileContent.pop("Root")
    fileContent.insert(0, "Root", rootColumn)
    fileContent.to_csv("./collectedData.csv", index=False)
    os.remove("tmpFile.tmp")
# EoS

