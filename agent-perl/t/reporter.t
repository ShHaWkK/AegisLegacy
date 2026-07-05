use strict;
use warnings;
use Test::More;

use FindBin qw($RealBin);
use lib "$RealBin/../lib";

use File::Temp qw(tempdir);
use File::Spec;
use JSON::PP qw(decode_json);

use Aegis::Reporter qw(build_report write_json_report);

subtest 'build_report sans finding donne un score parfait' => sub {
    my $report = build_report('/some/path', [], []);

    is($report->{score}, 100, 'score 100 sans finding');
    is($report->{findings_count}, 0);
    is($report->{files_scanned}, 0);
};

subtest 'build_report applique les ponderations par severite' => sub {
    my @findings = (
        { severity => 'critical' },
        { severity => 'critical' },
        { severity => 'low' },
    );

    my $report = build_report('/some/path', [], \@findings);

    # 100 - (2 * 20) - (1 * 2) = 58
    is($report->{score}, 58, 'score calcule correctement');
    is($report->{findings_by_severity}{critical}, 2);
    is($report->{findings_by_severity}{low}, 1);
    is($report->{findings_by_severity}{high}, 0);
};

subtest 'build_report borne le score entre 0 et 100' => sub {
    my @findings = map { { severity => 'critical' } } (1 .. 10);
    my $report = build_report('/some/path', [], \@findings);

    is($report->{score}, 0, 'le score ne descend jamais sous 0');
};

subtest 'write_json_report produit un JSON valide et relisible' => sub {
    my $dir = tempdir(CLEANUP => 1);
    my $path = File::Spec->catfile($dir, 'report.json');
    my $report = build_report('/target', [{ relative_path => 'a.py' }], []);

    write_json_report($report, $path);

    open(my $fh, '<:raw', $path) or die $!;
    local $/;
    my $raw = <$fh>;
    close $fh;

    my $decoded = decode_json($raw);
    is($decoded->{target_path}, '/target');
    is($decoded->{files_scanned}, 1);
};

done_testing();
