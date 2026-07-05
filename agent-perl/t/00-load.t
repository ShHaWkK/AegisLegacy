use strict;
use warnings;
use Test::More tests => 4;

use FindBin qw($RealBin);
use lib "$RealBin/../lib";

use_ok('Aegis::Utils');
use_ok('Aegis::Collector');
use_ok('Aegis::Scanner');
use_ok('Aegis::Reporter');
