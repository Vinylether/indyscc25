#!/usr/bin/perl

$f1 = $ARGV[0];
$f2 = $ARGV[1];


@X1 = `cat $f1 | grep -v "T" | sort -n -t , -k 3`;
@X2 = `cat $f2 | grep -v "T" | sort -n -t , -k 3`;

if ($#X1 != $#X2) {
    print "ERROR: files are not the same size:\n";
    print "    $f1: $#X1\n";
    print "    $f2: $#X2\n";
    exit(1);
}

$ERR=0;
$MaxErr = 1.0e-6;
foreach $i (0 .. $#X1) {

    @D1 = split(",",$X1[$i]);
    @D2 = split(",",$X2[$i]);

    foreach $j (0 .. 2) {
        $d = abs(1.- $D2[$j]/$D1[$j]);

        if ($d > $MaxErr) { $ERR++; print "$i $j   $D1[$j] $D2[$j]   diff: $d\n"; }
    }
    
}

if ($ERR == 0) {
    print "all OK!\n";
    exit(0);
} else {
    print "substantial differences found\n";
    exit(1);
}
