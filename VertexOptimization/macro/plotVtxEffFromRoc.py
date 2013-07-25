#!/usr/bin/env python
# 

from optparse import OptionParser, make_option
import fnmatch, glob, os, sys, json, itertools

objs = []

# -----------------------------------------------------------------------------------------------------------
def loadSettings(cfgs,dest):
    for cfg in cfgs.split(","):
        if cfg == "":
            continue
        cf = open(cfg)
        settings = json.load(cf)
        for k,v in settings.iteritems():
            setattr(dest,k,v)
        cf.close()

# -----------------------------------------------------------------------------------------------------------
def main(options,args):

    from roctools import ROCIntegrator, ROCBuilder
    
    fin = ROOT.TFile.Open(options.infile)
    fout = ROOT.TFile.Open(options.outfile, "recreate")

    ROOT.gROOT.SetStyle("Plain")
    
    rocs = []
    effs = []
    colors = [ROOT.kBlue, ROOT.kMagenta, ROOT.kRed, ROOT.kGreen]
    markers = [ROOT.kOpenCircle, ROOT.kFullTriangleUp, ROOT.kOpenDiamond, ROOT.kFullCircle]
    
    for classifier in options.classifiers:
        ctype,name = classifier.split(":")
        if ctype == "Category":
            rocpath = "Method_%s/%s/MVA_%s_rejBvsS" % ( ctype, name, name )
        else:
            rocpath = "Method_%s/MVA_%s/MVA_%s_rejBvsS" % ( ctype, name, name )
        print rocpath
        roc = fin.Get(rocpath)
        eff = ROCIntegrator(name,roc).getGraph(options.fro,options.to)
        effs.append(eff)
        
    for histo in options.histopairs:
        tf = fin
        if type(histo) == str:
            if ":" in histo:
                fname, histo = histo.split(":")
                tf = TFile.Open(fname)
            sig,bkg = histo.split(",")
        else:
            sig,bkg = histo

        hsig = tf.Get(sig)
        hbkg = tf.Get(bkg)

        builder = ROCBuilder(hsig.GetName(),hsig.GetName(),hsig,hbkg)
        eff = ROCIntegrator(hsig.GetName(),builder.getRoc()).getGraph(options.fro,options.to)
        effs.append(eff)
   	builder.getRoc().Print('all')
 	rocs.append(builder.getRoc())

    for rocname in options.rocs:
        tf = fin
        print rocname
        if ":" in rocname:
            fname, rocname = rocname.split(":")
            tf = ROOT.TFile.Open(fname)
        if "," in rocname:
            rocname,roclabel = rocname.split(',')
        else:
            roclabel = None
        roc = tf.Get(rocname)
        if roclabel:
            roc.SetTitle(roclabel)
        eff = ROCIntegrator(roc.GetName(),roc).getGraph(options.fro,options.to)
        effs.append(eff)
 	rocs.append(roc)
        
    count = 0    
    for eff in effs:
	title = 'Efficiency vs. nVtx %d, ggh;n_{vtx}-1;#varepsilon' % count
        eff.SetTitle(title) 
        eff.SetLineColor(colors[0])
        eff.SetMarkerColor(colors[0])
        eff.SetMarkerStyle(markers[0])
        colors.pop(0), markers.pop(0)
    	count = count + 1

    fout.cd()
    print count
    canv = ROOT.TCanvas("rocs","rocs",500,500)
    canv.SetGridx()
    canv.SetGridy()
    canv.cd()
    effs[0].Draw("CAP")
    effs[0].Write()
    for roc in rocs:
	roc.Write()
    for eff in effs[1:]:
        eff.Draw("CP")
	eff.Write()
    objs.extend(effs)
    objs.append(canv)
    canv.SaveAs("canv_%s" % options.outfile)
    fout.Close();  

if __name__ == "__main__":
    parser = OptionParser(option_list=[
            make_option("-i", "--input",
                        action="store", type="string", dest="infile",
                        default="",
                        help="input file"
                        ),
            make_option("-o", "--outfile",
                        action="store", type="string", dest="outfile",
                        default="",
                        help="outputfile", metavar="FILE"
                        ),
            make_option("-c", "--classifier", action="append",
                        default=[], dest="classifiers",
                        help="plot ROC for given classifier"
                        ),
            make_option("-p", "--histopair", action="append",
                        default=[], dest="histopairs",
                        help="plot ROC from signal and backgroud pdf (format: [rootfile:]<signal>,<background>)"
                        ),
            make_option("-r", "--roc", action="append", type="string",
                        default=[], dest="rocs",
                        help="get specified ROC (format: [rootfile:]<roc>,[label])"
                        ),
            make_option("-f","--from", action="store", default=1, type="int",
                        dest="fro",
                        help="plot range lower boundary"
                        ),
            make_option("-t","--to", action="store", default=50, type="int",
                        dest="to",
                        help="plot range upper boundary"
                        ),
            make_option("-l", "--load",
                        action="store", dest="load", type="string",
                        default="",
                        help="load options from json file"
                        ),
            make_option("-v", "--verbose",
                        action="store_true", dest="verbose",
                        default=False,
                        ),
            ])

    (options, args) = parser.parse_args()
    loadSettings(options.load, options)

    print options.rocs
    
    import ROOT

    main(options, args)
