import matplotlib.pyplot as plt

def scatterPlot(xs, ys, zs=None, cs=None, title="No Title", xlabel="No X Label", ylabel="No Y Label", zlabel="No Z Label", cLabel="No C Label",labels=[], fname="./scatterPlot.pdf", show=False, zeroLine=None):
    '''
    This function can dynamically plot a graph for up to 4 dimensions (4th represented using color).
    @params: 
    xs: x axis data points
    ys: y axis data points
    zs: z axis data points
    cs: c axis data points (Illustrated using color)
    title: Title for the graph
    xlabel: x axis label
    ylabel: y axis label
    fname: output graph file path
    labes: labels for the legend
    show: if True, will also show a preview of the generated graph
    legend: the position for legend placement. in not given, legend will not be displayed

    # '''
    markers = ['.','x']
    # if (not xs ) or (not ys):
    #     raise Exception("X axis or Y axis data points missing")
    if zs:
        from mpl_toolkits.mplot3d import Axes3D
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        if cs:
            from cmaps import cmaps
            for i in range(0,len(xs)):
                cmap = cmaps["Sequential"]
                ax.scatter(xs[i], ys[i], zs[i], c=cs[i], label=labels[i], cmap=cmap[i], alpha=0.6, marker='.')
        else:
            for i in range(0,len(xs)):
                ax.scatter(xs[i], ys[i], zs[i], label=labels[i], alpha=0.6, marker='.')
        ax.legend(fontsize=14)
        ax.set_zlabel(zlabel, fontsize=16)


    else:

        fig = plt.figure(figsize=(8, 5))
        ax = fig.add_subplot(1,1,1)


        if cs:
            from cmaps import cmaps
            for i in range(0,len(xs)):
                cmap = cmaps["Sequential"]
                ax.scatter(xs[i], ys[i], c=cs[i], label=labels[i], cmap=cmap[i], alpha=0.6, marker='.')
        else:
            for i in range(0,len(xs)):
                ax.scatter(xs[i], ys[i], label=labels[i], alpha=0.6, marker=markers[i])
        ax.legend(fontsize=22)

        # ax.autoscale()
        # ax.setxli
    
    plt.xlabel(xlabel, fontsize=24)
    plt.ylabel(ylabel, fontsize=24)
    plt.xticks(fontsize=22)
    plt.yticks(fontsize=22)

    # plt.yscale('log')
    # plt.axhline(y=zeroLine, color='r', linestyle='-.')
    ##########################
    plt.xscale('log')
    plt.xlim(left=10)
    plt.ylim(bottom=1)
    ##########################
    plt.title(title, fontsize=24)

    if show:
        plt.show()
    else:
        plt.savefig(fname, bbox_inches="tight")

    plt.close()
        


def barGraph(ys,title="No Title", xlabel="No X Label", ylabel="No Y Label",xticks=None,labels=[], fname="Error- File Name Required", show=False, legend=True):
############################################################################################################
############################################################################################################
    #Start Checks:
    try:
        def allSameLength(lst):
            for i in range(1,len(lst)):

                if len(lst[0]) != len(lst[i]):

                    return False

            return True

        invalid = (len(labels) < 1) or (len(labels) != len(ys[-1]))
        invalid = invalid or (not allSameLength(ys))

        if invalid:
            raise Exception("Either Data, or the labels provided are invalid.")
    except:
        raise Exception("Either Data, or the labels provided are invalid.")

    #If All Checks Passed:
############################################################################################################    
############################################################################################################
    nGroups = len(labels)
    patterns = [ "\\" , "x", "o", ".", "-" ]
    # colors = ["#808080","#5499C7", "#00FA9A","#FF0000", "#00FFFF"]
    colors = ["#e6debc", "#3d8ca4","#94d69d","#70c7a0","#51b8a4"]

    fig = plt.figure(figsize=(8, 5))
    ax = fig.add_subplot(1,1,1)
    ax.set_axisbelow(True)
    ax.yaxis.grid(color='gray', linestyle='dashed')
    # fig.tight_layout()
    index = range(0,len(ys))
    barWidth = 0.25

    for i in range(0,nGroups):
        plt.bar([x + (i*barWidth) for x in index], [y_[i] for y_ in ys], barWidth, capsize=3, align="center", color=colors[i], label=labels[i], hatch=patterns[i],edgecolor="black")
    
    plt.xlabel(xlabel,fontsize=24)
    plt.ylabel(ylabel,fontsize=24)
    plt.title(title,fontsize=24)
    plt.xticks([x+barWidth for x in index], xticks, fontsize=22)
    plt.yticks(fontsize=22)
    if legend:
        plt.legend(fontsize=22)
    # plt.tight_layout()

    if show:
        plt.show()
        
    else:
        plt.savefig(fname,bbox_inches="tight")
        
    plt.close()

def lineGraph(xs, ys, title="No Title Provided", xlabel="No xlabel provided", ylabel="No ylabel provided", fname="./lineGraph.pdf", labels=[], show=False, legend=False):
    '''
    @params: 
    x: x axis data points
    y: y axis data points
    title: Title for the graph
    xlabel: x axis label
    ylabel: y axis label
    fname: output graph file path
    label: label for the legend
    show: if True, will also show a preview of the generated graph
    legend: the position for legend placement. in not given, legend will not be displayed

    '''

    linestyles = [
        ('solid',                 (0, ())),      # Same as (0, ()) or '-'
        ('dashdotdotted',         (0, (3, 5, 1, 5, 1, 5))),
        ('dotted',                (0, (1, 1))),    # Same as (0, (1, 1)) or '.'
        ('dashed', 'dashed'),    # Same as '--'
        ('dashdot', 'dashdot'),  # Same as '-.'

        ('loosely dashed',        (0, (5, 10))),
        ('dashed',                (0, (5, 5))),

        ('loosely dashdotted',    (0, (3, 10, 1, 10))),
        ('loosely dashdotdotted', (0, (3, 10, 1, 10, 1, 10))),
        ('dashdotted',            (0, (3, 5, 1, 5))),

        ('dashdotdotted',         (0, (3, 5, 1, 5, 1, 5))),
        ('densely dashed',        (0, (5, 1))),
        ('densely dashdotdotted', (0, (3, 1, 1, 1, 1, 1))),
        ('dotted',                (0, (1, 1))),
        ('loosely dotted',        (0, (1, 10)))]

    colors = ["#e6debc","#94d69d","#70c7a0","#51b8a4","#3d8ca4"]

    low = []
    for i in range(0,len(ys[0])):
        low.append(0)

    for i in range(0,len(ys)):
        
        # print(len(ys))
        plt.fill_between(xs[i], low, ys[i], color=colors[i], alpha=0.2)
        # print(xs[i],ys[i],linestyles[i],colors[i],labels[i])
        plt.plot(xs[i],ys[i],linewidth=4, linestyle=linestyles[i][1], color=colors[i], label=labels[i])

    if legend:
        plt.legend(loc=legend, fontsize=22)
        # plt.legend(loc=legend, bbox_to_anchor=(0.5, 1.09),
        #     ncol=3, fancybox=True)
    plt.xlabel(xlabel,fontsize=22)
    plt.ylabel(ylabel,fontsize=22)
    plt.title(title,fontsize=24)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)

    plt.margins(0,0)
    if not show:
        plt.savefig(fname, transparent = True, bbox_inches = 'tight')

    else:
        plt.show()
    plt.close()

def singleLineGraph(x, y, title="No Title Provided", xlabel="No xlabel provided", ylabel="No ylabel provided", fname="./lineGraph.pdf", label="No Label", show=False, legend=False):
    '''
    @params: 
    x: x axis data points
    y: y axis data points
    title: Title for the graph
    xlabel: x axis label
    ylabel: y axis label
    fname: output graph file path
    label: label for the legend
    show: if True, will also show a preview of the generated graph
    legend: the position for legend placement. in not given, legend will not be displayed

    '''

    low = []
    for i in range(0,len(y)):
        low.append(0)

    plt.fill_between(x, low, y, color="#224392", alpha=0.2)

    plt.plot(x,y,linewidth=2, color='#1a237c', label=label)
    if legend:
        plt.legend(loc=legend, fontsize=22)
        # plt.legend(loc=legend, bbox_to_anchor=(0.5, 1.09),
        #     ncol=3, fancybox=True)
    plt.xlabel(xlabel,fontsize=22)
    plt.ylabel(ylabel,fontsize=22)
    plt.title(title,fontsize=24)
    plt.margins(0,0)
    plt.savefig(fname, transparent = True, bbox_inches = 'tight')
    if show:
        plt.show()

# def nLineGraph(xs, ys, title="No Title Provided", xlabel="No xlabel provided", ylabel="No ylabel provided", savefig="./lineGraph.pdf", label="No Label", show=False, legend=False)
    
#     if(len(xs) != len(ys)):
#         raise Exception("X data values != Y data values.")

#     for i in range(0,len(xs)):

    


#######################################################################################################################
################################################# EXAMPLES ############################################################
#######################################################################################################################
# def expectedCSAT():
    
#     import numpy as np
#     x = np.arange(0.0, 1.01, 0.01)
#     y = [i**(1/3.0) for i in x]
#     # print(y)
#     singleLineGraph(x,y,xlabel="Signal,Speed,Coverage", ylabel="Customer Satisfaction (CSAT)", title="Expected Trend in CSAT: The Law of Diminishing Returns", fname="./expectedCSAT.pdf")


