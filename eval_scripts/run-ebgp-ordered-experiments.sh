#!/usr/bin/env bash

# Generate evaluation values for all given reqs
NUM_PROCESSES=1
NUM_REPEATS=1


PATH_TO_TOPOS="topos/*/"
#topos/small/Arnes topos/small/Bics topos/small/Canerie topos/small/Renater2008 topos/small/CrlNetworkServices;
#topos/mid/Columbus topos/mid/Esnet topos/mid/Latnet topos/mid/Sinet topos/mid/Uninett2011
#topos/large/Cogentco topos/large/Colt	topos/large/GtsCe  topos/large/TataNld topos/large/UsCarrier


for file in topos/small/Arnes topos/small/Bics topos/small/Canerie topos/small/Renater2008 topos/small/CrlNetworkServices topos/mid/Columbus topos/mid/Esnet topos/mid/Latnet topos/mid/Sinet topos/mid/Uninett2011 topos/large/Cogentco topos/large/Colt topos/large/GtsCe topos/large/TataNld topos/large/UsCarrier;
do
    topo="${file}.graphml"
    values="${file}_ospf_reqs.py "
    req_type="order"
    fixed="0"
    sketch="abs"
    RUN_ID=1
    #for reqs in 1 2 4 8 16;
    for reqs in 4 8 16;
    do
        echo $topo $values $req_type $reqs $fixed $sketch $RUN_ID
    done
done | xargs -n 7 -I{} -P $NUM_PROCESSES sh -c "sh ./eval_scripts/run-ebgp.sh {}"
