from modules.State import State

def singleProvider(county):
    haveCovg = 0
    for bss in county.basestations.values():
        if len(bss) > 0:
            haveCovg += 1


    return haveCovg < 4


state = State("48")
singleProviderCounties = 0


for county in state.counties.values():

    if singleProvider(county):
        singleProviderCounties += 1

print("Only one provider in {} counties (out of {} total)".format(singleProviderCounties, len(list(state.counties.keys()))))
