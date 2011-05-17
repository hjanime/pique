#!/usr/bin/env python
import numpy
import yaml
import sys
import pique
"""
This is an itterative peak recovery script. It is designed to tell you
where the noise threshold is in your data, and provides an upper limit
to the number of statistically significant peaks that can be
recovered.

Usage : ./piquant.py <config.yaml>
"""

# Parse config file, set runtime parameters
num_opts = [    'steps',                \
                'l_thresh',             \
                'too_big',              \
                'too_small'             ]
str_opts = [    'track_name',           \
                'forward_ChIP_track',   \
                'forward_bgnd_track',   \
                'reverse_ChIP_track',   \
                'masking_loci',         \
                'reverse_bgnd_track'    ]

opt_dict = yaml.load( open( sys.argv[1] ).read() )

for opt in num_opts + str_opts :
    if not opt_dict.has_key( opt ) :
        print 'config file missing option : ' + opt
        quit()
    setattr( sys.modules[__name__], opt, opt_dict[opt] )

pique.msg( 'reading track data...' )
data_ff = pique.readtrack( forward_ChIP_track )
data_rr = pique.readtrack( reverse_ChIP_track )
b_ff    = pique.readtrack( forward_bgnd_track )
b_rr    = pique.readtrack( reverse_bgnd_track )

pique.msg( 'applying mask...' )
is_elements = []
for line in open( masking_loci ) :
    if line.__contains__('#') :
        continue
    start, stop = map( int, line.split()[:2] )
    is_elements.append( { 'start':start, 'stop':stop } )

data_ff = pique.mask( data_ff, is_elements )
data_rr = pique.mask( data_rr, is_elements )
b_ff    = pique.mask( b_ff,    is_elements )
b_rr    = pique.mask( b_rr,    is_elements )

pique.msg( 'running filters...' )
data_f  = pique.filterset( data_ff, 300, l_thresh )
data_r  = pique.filterset( data_rr, 300, l_thresh )
b_f     = pique.filterset( b_ff,    300, l_thresh )
b_r     = pique.filterset( b_rr,    300, l_thresh )

pique.msg( 'running evaporating lake...' )

top = max( ( max(data_f), max(data_r) ) )
bot = min( ( min(data_f), min(data_r) ) )
step = ( top - bot ) / steps
#top = 500
lake_overlaps = []
lake_forward  = []
lake_reverse  = []
lake_bg_overlaps = []
lake_bg_forward  = []
lake_bg_reverse  = []
X = top - numpy.arange( bot, top+step, step )
for i,n in enumerate( X ) :
    forward  = pique.findregions( data_f, n )
    reverse  = pique.findregions( data_r, n )
    envelope = pique.overlaps( forward, reverse )

    lake_overlaps.append( envelope )
    lake_forward.append(  forward  )
    lake_reverse.append(  reverse  )
    
    forward  = pique.findregions( b_f, n )
    reverse  = pique.findregions( b_r, n )
    envelope = pique.overlaps( forward, reverse )

    lake_bg_overlaps.append( envelope )
    lake_bg_forward.append( forward )
    lake_bg_reverse.append( reverse )
    if i%10 == 0 :
        pique.msg( '   iteration : ' + str(i) + ', peaks recovered : ' + str(len(envelope) ))
