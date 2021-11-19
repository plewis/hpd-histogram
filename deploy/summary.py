import sys,shutil,os,glob,re

use_comma_separated_values = True

def summarizeGSS(partition_scheme):
    # read output files
    outfilenames = glob.glob('%s/gss/%s-*.out' % (partition_scheme,partition_scheme))
    assert len(outfilenames) == 1
    outfn = outfilenames[0]

    errfilenames = glob.glob('%s/gss/%s-*.err' % (partition_scheme,partition_scheme))
    assert len(errfilenames) == 1
    errfn = errfilenames[0]

    # read output file 
    outstuff = open(outfn, 'r').read()
    errstuff = open(errfn, 'r').read()
    stuff = outstuff + errstuff

    # set default values in case there are no results yet for this analysis
    rnseed = 0
    secs1  = 0.0
    secs2  = 0.0
    logL   = 0.0
    
    # get seed
    m = re.search('Pseudorandom number seed: (\d+)', stuff, re.M | re.S)
    if m is not None:
        rnseed = int(m.group(1))

    # grab marginal likelihood estimate
    m = re.search('^log\(marginal likelihood\) = ([-.0-9]+)', stuff, re.M | re.S)
    if m is not None:
        logL = float(m.group(1))

        # grab time of MCMC analysis
        m1 = re.search('user-seconds\s+([.0-9]+)', stuff, re.M | re.S)
        assert m1 is not None, 'could not find user-seconds for MCMC analysis in file "%s"' % fn
        secs1 = float(m1.group(1))
        
        # grab time of GSS analysis
        m2 = re.search('user-seconds\s+([.0-9]+)', stuff[m1.end():], re.M | re.S)
        assert m2 is not None, 'could not find user-seconds for GSS analysis in file "%s"' % fn
        secs2 = float(m2.group(1))
    
    return {
        'rnseed':rnseed, 
        'secs':secs1+secs2, 
        'logL':logL
    }

def summarizeLoRaD(partition_scheme):
    # read output files
    outfilenames = glob.glob('%s/lorad/%s-*.out' % (partition_scheme,partition_scheme))
    assert len(outfilenames) == 1
    outfn = outfilenames[0]

    errfilenames = glob.glob('%s/lorad/%s-*.err' % (partition_scheme,partition_scheme))
    assert len(errfilenames) == 1
    errfn = errfilenames[0]

    # read output file 
    outstuff = open(outfn, 'r').read()
    errstuff = open(errfn, 'r').read()
    stuff = outstuff + errstuff

    # set default values in case there are no results yet for this analysis
    rnseed   = 0
    secs     = 0.0
    
    cov1reg  = 0.0
    cov1     = 0.0
    beta01   = 0.0
    beta11   = 0.0
    beta21   = 0.0
    logL1reg = 0.0
    logL1    = 0.0

    cov2reg  = 0.0
    cov2     = 0.0
    beta02   = 0.0
    beta12   = 0.0
    beta22   = 0.0
    logL2reg = 0.0
    logL2    = 0.0

    cov3reg  = 0.0
    cov3     = 0.0
    beta03   = 0.0
    beta13   = 0.0
    beta23   = 0.0
    logL3reg = 0.0
    logL3    = 0.0
    
    # get seed
    m = re.search('Pseudorandom number seed: (\d+)', stuff, re.M | re.S)
    if m is not None:
        rnseed = int(m.group(1))
    
    # grab times
    m = re.search('user-seconds\s+([.0-9]+)', stuff, re.M | re.S)
    if m is not None:
        secs = float(m.group(1))

    # grab marginal likelihood estimate for each of the three coverage values
    results = re.findall(' Determining working parameter space for coverage = ([.0-9]+?)[.][.][.].+?log\(marginal likelihood\) = ([-.0-9]+)', stuff, re.M | re.S)
    nresults = len(results)               
    if nresults == 6:
        #print('***** LoRaD cov/logL results below *****')
        #print(results)
        #print('***** LoRaD cov/logL results above *****')
        cov1reg  = float(results[0][0])
        cov2reg  = float(results[1][0])
        cov3reg  = float(results[2][0])
        cov1     = float(results[3][0])
        cov2     = float(results[4][0])
        cov3     = float(results[5][0])
        
        assert cov1 == cov1reg
        assert cov2 == cov2reg
        assert cov3 == cov3reg
        
        logL1reg = float(results[0][1])
        logL2reg = float(results[1][1])
        logL3reg = float(results[2][1])
        logL1    = float(results[3][1])
        logL2    = float(results[4][1])
        logL3    = float(results[5][1])
        
        results = re.findall('Polynomial regression:\s+beta0 = ([0-9.-]+)\s+beta1 = ([0-9.-]+)\s+beta2 = ([0-9.-]+)', stuff, re.M | re.S)
        nresults = len(results)               
        if nresults == 3:
            #print('***** LoRaD beta results below *****')
            #print(results)
            #print('***** LoRaD beta results above *****')
            beta01 = float(results[0][0])
            beta11 = float(results[0][1])
            beta21 = float(results[0][2])
            beta02 = float(results[1][0])
            beta12 = float(results[1][1])
            beta22 = float(results[1][2])
            beta03 = float(results[2][0])
            beta13 = float(results[2][1])
            beta23 = float(results[2][2])

    return {
        'rnseed':rnseed, 
        'secs':secs, 
        'cov1':cov1, 
        'beta01':beta01, 
        'beta11':beta11, 
        'beta21':beta21, 
        'logL1reg':logL1reg, 
        'logL1':logL1, 
        'cov2':cov2, 
        'beta02':beta02, 
        'beta12':beta12, 
        'beta22':beta22, 
        'logL2reg':logL2reg, 
        'logL2':logL2, 
        'cov3':cov3, 
        'beta03':beta03, 
        'beta13':beta13, 
        'beta23':beta23, 
        'logL3reg':logL3reg,
        'logL3':logL3
    }
    
lorad = {}
lorad['unpart']  = summarizeLoRaD('unpart')
lorad['bygene']  = summarizeLoRaD('bygene')
lorad['bycodon'] = summarizeLoRaD('bycodon')
lorad['byboth']  = summarizeLoRaD('byboth')

gss = {}
gss['unpart']  = summarizeGSS('unpart')
gss['bygene']  = summarizeGSS('bygene')
gss['bycodon'] = summarizeGSS('bycodon')
gss['byboth']  = summarizeGSS('byboth')

outf = open('output-summary.txt','w')
if use_comma_separated_values:
    headers      = 'partition,seed,secs,gss,seed,secs,cov1,beta01,beta11,beta21,lorad1,cov2,beta02,beta12,beta22,lorad2,cov3,beta03,beta13,beta23,lorad3\n'
    unpart_line  = 'unpart ,%d,%.3f,%.5f,%d,%.3f,%.1f,%.5f,%.5f,%.5f,%.5f,%.1f,%.5f,%.5f,%.5f,%.5f,%.1f,%.5f,%.5f,%.5f,%.5f\n'
    bygene_line  = 'bygene ,%d,%.3f,%.5f,%d,%.3f,%.1f,%.5f,%.5f,%.5f,%.5f,%.1f,%.5f,%.5f,%.5f,%.5f,%.1f,%.5f,%.5f,%.5f,%.5f\n' 
    bycodon_line = 'bycodon,%d,%.3f,%.5f,%d,%.3f,%.1f,%.5f,%.5f,%.5f,%.5f,%.1f,%.5f,%.5f,%.5f,%.5f,%.1f,%.5f,%.5f,%.5f,%.5f\n'
    byboth_line  = 'byboth ,%d,%.3f,%.5f,%d,%.3f,%.1f,%.5f,%.5f,%.5f,%.5f,%.1f,%.5f,%.5f,%.5f,%.5f,%.1f,%.5f,%.5f,%.5f,%.5f\n'
else:
    headers      = 'partition\tseed\tsecs\tgss\tseed\tsecs\tcov1\tbeta01\tbeta11\tbeta21\tlorad1\tcov2\tbeta02\tbeta12\tbeta22\tlorad2\tcov3\tbeta03\tbeta13\tbeta23\tlorad3\n'
    unpart_line  = 'unpart \t%d\t%.3f\t%.5f\t%d\t%.3f\t%.1f\t%.5f\t%.5f\t%.5f\t%.5f\t%.1f\t%.5f\t%.5f\t%.5f\t%.5f\t%.1f\t%.5f\t%.5f\t%.5f\t%.5f\n'
    bygene_line  = 'bygene \t%d\t%.3f\t%.5f\t%d\t%.3f\t%.1f\t%.5f\t%.5f\t%.5f\t%.5f\t%.1f\t%.5f\t%.5f\t%.5f\t%.5f\t%.1f\t%.5f\t%.5f\t%.5f\t%.5f\n' 
    bycodon_line = 'bycodon\t%d\t%.3f\t%.5f\t%d\t%.3f\t%.1f\t%.5f\t%.5f\t%.5f\t%.5f\t%.1f\t%.5f\t%.5f\t%.5f\t%.5f\t%.1f\t%.5f\t%.5f\t%.5f\t%.5f\n'
    byboth_line  = 'byboth \t%d\t%.3f\t%.5f\t%d\t%.3f\t%.1f\t%.5f\t%.5f\t%.5f\t%.5f\t%.1f\t%.5f\t%.5f\t%.5f\t%.5f\t%.1f\t%.5f\t%.5f\t%.5f\t%.5f\n'
    
outf.write(headers)
outf.write(unpart_line % (
    gss['unpart']['rnseed'],
    gss['unpart']['secs'],
    gss['unpart']['logL'],
    lorad['unpart']['rnseed'],
    lorad['unpart']['secs'],
    lorad['unpart']['cov1'],
    lorad['unpart']['beta01'],
    lorad['unpart']['beta11'],
    lorad['unpart']['beta21'],
    lorad['unpart']['logL1reg'],
    lorad['unpart']['cov2'],
    lorad['unpart']['beta02'],
    lorad['unpart']['beta12'],
    lorad['unpart']['beta22'],
    lorad['unpart']['logL2reg'],
    lorad['unpart']['cov3'],
    lorad['unpart']['beta03'],
    lorad['unpart']['beta13'],
    lorad['unpart']['beta23'],
    lorad['unpart']['logL3reg']
))
outf.write(unpart_line % (
    gss['unpart']['rnseed'],
    gss['unpart']['secs'],
    gss['unpart']['logL'],
    lorad['unpart']['rnseed'],
    lorad['unpart']['secs'],
    lorad['unpart']['cov1'],
    0.0,
    0.0,
    0.0,
    lorad['unpart']['logL1'],
    lorad['unpart']['cov2'],
    0.0,
    0.0,
    0.0,
    lorad['unpart']['logL2'],
    lorad['unpart']['cov3'],
    0.0,
    0.0,
    0.0,
    lorad['unpart']['logL3']
))
outf.write(bygene_line % (
    gss['bygene']['rnseed'],
    gss['bygene']['secs'],
    gss['bygene']['logL'],
    lorad['bygene']['rnseed'],
    lorad['bygene']['secs'],
    lorad['bygene']['cov1'],
    lorad['bygene']['beta01'],
    lorad['bygene']['beta11'],
    lorad['bygene']['beta21'],
    lorad['bygene']['logL1reg'],
    lorad['bygene']['cov2'],
    lorad['bygene']['beta02'],
    lorad['bygene']['beta12'],
    lorad['bygene']['beta22'],
    lorad['bygene']['logL2reg'],
    lorad['bygene']['cov3'],
    lorad['bygene']['beta03'],
    lorad['bygene']['beta13'],
    lorad['bygene']['beta23'],
    lorad['bygene']['logL3reg']
))
outf.write(unpart_line % (
    gss['bygene']['rnseed'],
    gss['bygene']['secs'],
    gss['bygene']['logL'],
    lorad['bygene']['rnseed'],
    lorad['bygene']['secs'],
    lorad['bygene']['cov1'],
    0.0,
    0.0,
    0.0,
    lorad['bygene']['logL1'],
    lorad['bygene']['cov2'],
    0.0,
    0.0,
    0.0,
    lorad['bygene']['logL2'],
    lorad['bygene']['cov3'],
    0.0,
    0.0,
    0.0,
    lorad['bygene']['logL3']
))
outf.write(bycodon_line % (
    gss['bycodon']['rnseed'],
    gss['bycodon']['secs'],
    gss['bycodon']['logL'],
    lorad['bycodon']['rnseed'],
    lorad['bycodon']['secs'],
    lorad['bycodon']['cov1'],
    lorad['bycodon']['beta01'],
    lorad['bycodon']['beta11'],
    lorad['bycodon']['beta21'],
    lorad['bycodon']['logL1reg'],
    lorad['bycodon']['cov2'],
    lorad['bycodon']['beta02'],
    lorad['bycodon']['beta12'],
    lorad['bycodon']['beta22'],
    lorad['bycodon']['logL2reg'],
    lorad['bycodon']['cov3'],
    lorad['bycodon']['beta03'],
    lorad['bycodon']['beta13'],
    lorad['bycodon']['beta23'],
    lorad['bycodon']['logL3reg']
))
outf.write(unpart_line % (
    gss['bycodon']['rnseed'],
    gss['bycodon']['secs'],
    gss['bycodon']['logL'],
    lorad['bycodon']['rnseed'],
    lorad['bycodon']['secs'],
    lorad['bycodon']['cov1'],
    0.0,
    0.0,
    0.0,
    lorad['bycodon']['logL1'],
    lorad['bycodon']['cov2'],
    0.0,
    0.0,
    0.0,
    lorad['bycodon']['logL2'],
    lorad['bycodon']['cov3'],
    0.0,
    0.0,
    0.0,
    lorad['bycodon']['logL3']
))
outf.write(byboth_line % (
    gss['byboth']['rnseed'],
    gss['byboth']['secs'],
    gss['byboth']['logL'],
    lorad['byboth']['rnseed'],
    lorad['byboth']['secs'],
    lorad['byboth']['cov1'],
    lorad['byboth']['beta01'],
    lorad['byboth']['beta11'],
    lorad['byboth']['beta21'],
    lorad['byboth']['logL1reg'],
    lorad['byboth']['cov2'],
    lorad['byboth']['beta02'],
    lorad['byboth']['beta12'],
    lorad['byboth']['beta22'],
    lorad['byboth']['logL2reg'],
    lorad['byboth']['cov3'],
    lorad['byboth']['beta03'],
    lorad['byboth']['beta13'],
    lorad['byboth']['beta23'],
    lorad['byboth']['logL3reg']
))
outf.write(unpart_line % (
    gss['byboth']['rnseed'],
    gss['byboth']['secs'],
    gss['byboth']['logL'],
    lorad['byboth']['rnseed'],
    lorad['byboth']['secs'],
    lorad['byboth']['cov1'],
    0.0,
    0.0,
    0.0,
    lorad['byboth']['logL1'],
    lorad['byboth']['cov2'],
    0.0,
    0.0,
    0.0,
    lorad['byboth']['logL2'],
    lorad['byboth']['cov3'],
    0.0,
    0.0,
    0.0,
    lorad['byboth']['logL3']
))
outf.close()
