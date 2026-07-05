package Aegis::Reporter;

use strict;
use warnings;
use utf8;
use v5.16;

use JSON::PP ();
use HTTP::Tiny ();
use Exporter qw(import);

our @EXPORT_OK = qw(build_report write_json_report send_report);

=head1 NAME

Aegis::Reporter - Assemble le rapport de scan et l'exporte (fichier ou HTTP).

=cut

our $AGENT_VERSION = '0.1.0';

our %SEVERITY_WEIGHTS = (
    critical => 20,
    high     => 10,
    medium   => 5,
    low      => 2,
    info     => 0.5,
);

# build_report($target_path, \@files, \@findings) -> hashref
sub build_report {
    my ($target_path, $files, $findings) = @_;

    my %by_severity = (critical => 0, high => 0, medium => 0, low => 0, info => 0);
    for my $finding (@$findings) {
        my $sev = $finding->{severity} // 'info';
        $by_severity{$sev}++ if exists $by_severity{$sev};
    }

    my $score = 100;
    for my $sev (keys %by_severity) {
        $score -= $SEVERITY_WEIGHTS{$sev} * $by_severity{$sev};
    }
    $score = 0   if $score < 0;
    $score = 100 if $score > 100;

    return {
        agent_version    => $AGENT_VERSION,
        target_path      => $target_path,
        generated_at     => scalar gmtime() . ' UTC',
        files_scanned    => scalar @$files,
        findings_count   => scalar @$findings,
        score            => $score,
        findings_by_severity => \%by_severity,
        files            => $files,
        findings         => $findings,
    };
}

sub write_json_report {
    my ($report, $path) = @_;

    my $json = JSON::PP->new->utf8->canonical->pretty;
    open(my $fh, '>:raw', $path) or die "Impossible d'écrire $path: $!\n";
    print $fh $json->encode($report);
    close $fh;

    return 1;
}

# send_report($report, $url) -> ($success, $status_code_or_error_message)
sub send_report {
    my ($report, $url) = @_;

    my $json = JSON::PP->new->utf8->canonical->encode($report);
    my $http = HTTP::Tiny->new(timeout => 10);
    my $response = $http->post(
        $url,
        {
            headers => { 'Content-Type' => 'application/json' },
            content => $json,
        },
    );

    return (1, $response->{status}) if $response->{success};
    return (0, "$response->{status} $response->{reason}");
}

1;
