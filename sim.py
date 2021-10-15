'''
-np:
State ID, Customer Count
-p:
State ID, Customer Count, Peering ISP1, Peering ISP2, heuristic{0:default, anything higher is considered a percentile threshold} 
'''

import sys, os, shutil

def checkMemoryAvailable():

    path = os. getcwd() 
    memory = shutil.disk_usage(path) 
    if (memory.free // (10 ** 9)) < 4:
        raise Exception("Not Enough Memory. At Least 4 GB Required")

def checkDataDirectories():
    path = os. getcwd()
    if "Tower Data" not in (os.listdir(path)):
        setTowerDataDirectories()

def setTowerDataDirectories():
    import zipfile

    DATA_URL = "https://ufile.io/uge8t5rw"
    path = os. getcwd()

    while "Tower Data.zip" not in os.listdir(path):
        input(f"Download Data File (.zip) to Working Directory from {DATA_URL} then Press Enter/Return.")

    print("Unzipping folders ... ", end = "")
    with zipfile.ZipFile("./Tower Data.zip", "r") as zip_ref:
        zip_ref.extractall("./")
    print("Done")
    
    print("Removing .zip ...", end="")
    if "__MACOSX" in os.listdir(path):
        shutil.rmtree("__MACOSX")
    os.remove("./Tower Data.zip")
    print("Done")

def environmentSetup():
    from subprocess import call

    call("pip install -r requirements.txt", shell = True)

def checkResultsDirectories():
    
    from subprocess import call
    path = os. getcwd()
    if "Results" not in os.listdir(path):
        call("mkdir -p ./Results/Simulator/Peering", shell=True)
        call("mkdir -p ./Results/Simulator/Roaming", shell=True)
        
        call("mkdir -p ./Results/Figs/Simulator/Roaming", shell=True)
        call("mkdir -p ./Results/Figs/Simulator/Peering", shell=True)
        
        call("mkdir -p ./Results/Experiments/County\ Gain/", shell=True)
        call("mkdir -p ./Results/Experiments/Threshold/", shell=True)
        
        call("mkdir -p ./Results/Figs/Experiments/County\ Gain/", shell=True)
        call("mkdir -p ./Results/Figs/Experiments/Threshold/", shell=True)
        call("mkdir -p ./Results/Figs/Maps/", shell=True)

        call("mkdir -p ./Results/Experiments/County\ Gain/CSVs/", shell=True)
        

if __name__ == "__main__":

    checkMemoryAvailable()
    checkDataDirectories()
    checkResultsDirectories()
    environmentSetup()

    # sys.exit(0)

    from Experiments.peeringSimulator import runSimulator
    from itertools import combinations
    from modules.initialize import initialize
    from modules.indCountyBenefits import indCountyBenefits

    providers = ['VERIZON', 'AT_T', 'T_MOBILE', 'SPRINT']
    pair_combinations = list(combinations(providers,2))
    modes = ["Peering", "Roaming"]
    
    stateID = sys.argv[1]
    customerCount = int(sys.argv[2])
    threshold = int(sys.argv[3])
    customers,state = initialize(stateID, sampleSize=customerCount)

    # sys.exit(0)
    ###
    
    print("Setting up...")
    indCountyBenefits(state, pair_combinations)
    
    ###
    runSimulator(stateID, customers, "No Peering") # Mode: No Peering
    
    for mode in modes:
        for pair in pair_combinations:
            
            runSimulator(state, customers, mode, pair, threshold)
