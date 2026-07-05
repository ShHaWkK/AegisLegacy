use strict;
use warnings;
use Test::More;

use FindBin qw($RealBin);
use lib "$RealBin/../lib";

use Aegis::Scanner qw(scan_file);

sub file_meta {
    my ($relative_path, $extension) = @_;
    return { relative_path => $relative_path, extension => $extension };
}

subtest 'detecte system() en Perl' => sub {
    my @findings = scan_file(
        file_meta('legacy.pl', '.pl'),
        qq{use strict;\nsystem("rm -rf \$input");\n},
    );

    is(scalar @findings, 1, 'un seul finding');
    is($findings[0]->{rule_id}, 'AGENT-CMD-001', 'rule_id correct');
    is($findings[0]->{severity}, 'critical', 'severite critical');
    is($findings[0]->{line}, 2, 'numero de ligne correct');
    is($findings[0]->{file}, 'legacy.pl', 'chemin relatif propage');
};

subtest 'ne detecte pas les regles Python sur un fichier Perl' => sub {
    my @findings = scan_file(
        file_meta('script.pl', '.pl'),
        "subprocess.run(cmd, shell=True)\n",
    );

    is(scalar @findings, 0, 'la regle python ne s appplique pas a un .pl');
};

subtest 'detecte shell=True en Python, y compris avec parentheses imbriquees' => sub {
    my @findings = scan_file(
        file_meta('script.py', '.py'),
        "subprocess.run(build_cmd(x), shell=True)\n",
    );

    is(scalar @findings, 1, 'un finding malgre la parenthese imbriquee');
    is($findings[0]->{rule_id}, 'AGENT-SUBPROC-001');
};

subtest 'regle any s applique a n importe quelle extension' => sub {
    my @findings = scan_file(
        file_meta('creds.conf', '.conf'),
        qq{password = "hunter2super"\n},
    );

    is(scalar @findings, 1, 'secret detecte dans un fichier .conf');
    is($findings[0]->{rule_id}, 'AGENT-SECRET-001');
};

subtest 'contenu indefini ne fait pas planter le scan' => sub {
    my @findings = scan_file(file_meta('bin.dat', '.dat'), undef);
    is(scalar @findings, 0, 'liste vide, pas de crash');
};

subtest 'plusieurs correspondances sur la meme ligne sont toutes remontees' => sub {
    my @findings = scan_file(
        file_meta('double.pl', '.pl'),
        qq{system("a"); system("b");\n},
    );

    is(scalar @findings, 2, 'deux findings sur la meme ligne');
    is($findings[0]->{line}, 1);
    is($findings[1]->{line}, 1);
};

done_testing();
