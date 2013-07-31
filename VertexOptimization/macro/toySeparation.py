from optparse import OptionParser, make_option
import fnmatch, glob, os, sys, json, itertools

objs = []

def getSep(sigma2,sigma1=0.014,draw=False):

    g1 = ROOT.TF1("g1","gaus",-1,1)
    g2 = ROOT.TF1("g2","gaus",-1,1)
    g1.SetParameters(1,0,sigma1)
    g2.SetParameters(1,0,sigma2)
    g2.SetParameter(0, g1.Integral(-1,1)/g2.Integral(-1,1) )
    
    llr = ROOT.TF1("llr","[0]-log(g1/g2)",-1,1)
    llr.SetParameter(0,-llr.Eval(0))
    h1 = ROOT.TH1F("h1_%1.0f" % ( sigma2 * 100. ),"h1",200,0,200)
    h2 = ROOT.TH1F("h2_%1.0f" % ( sigma2 * 100. ),"h2",200,0,200)
    for ii in range(100000):
        h1.Fill( llr.Eval( g1.GetRandom() ) )
        h2.Fill( llr.Eval( g2.GetRandom() ) )

    roc = ROCBuilder("roc_%1.0f" % ( sigma2 * 100. ),"roc_%1.0f" % ( sigma2 * 100. ),h1,h2).getRoc()
    
    if draw:
        canv = ROOT.TCanvas("pdfs","pdfs")
        canv.cd()
        h1.DrawNormalized()
        h2.DrawNormalized("same")
        
        sep = ROOT.TCanvas("sep","sep")
        sep.cd()
        roc.Draw()
        
    objs.append( (h1,h2,g1,h2,llr,roc) )
    return h1,h2,roc

# -----------------------------------------------------------------------------------------------------------
def main(options,args):

    colors = [ ROOT.kRed, ROOT.kOrange, ROOT.kMagenta, ROOT.kBlue, ROOT.kGreen ]
    rocs = []
    leg = ROOT.TLegend(0.15,0.15,0.5,0.4)
    leg.SetFillColor(0)
    for sigma2 in [0.02, 0.05, 0.1, 0.2, 0.5 ]:
        h1,h2,roc = getSep( sigma2 )
        roc.SetTitle( "#sigma_{2} = %1.2g" % sigma2 )
        leg.AddEntry( roc, "", "l" )
        roc.SetLineColor(colors.pop(0))
        rocs.append(roc)

        
    rocs[0].Draw()
    for roc in rocs[1:]:
        roc.Draw("same")
    leg.Draw("same")

    objs.append(leg)

if __name__ == "__main__":
    parser = OptionParser(option_list=[
            ])

    (options, args) = parser.parse_args()
    
    import ROOT
    from roctools import ROCIntegrator, ROCBuilder

    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetOptTitle(0)

    main(options, args)
