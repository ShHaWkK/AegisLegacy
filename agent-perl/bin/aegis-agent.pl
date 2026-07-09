#!/usr/bin/env perl

use strict;
use warnings;
use utf8;
use v5.16;

use FindBin qw($RealBin);
use lib "$RealBin/../lib";

use Getopt::Long qw(GetOptions);

use Aegis::Collector qw(collect_files);
use Aegis::Scanner qw(scan_file);
use Aegis::Reporter qw(build_report write_json_report send_report);
use Aegis::Utils qw(read_text_file);

=head1 NAME

aegis-agent.pl - Agent Perl autonome de scan de sécurité pour code legacy.

=head1 SYNOPSIS

  perl bin/aegis-agent.pl --path ./demo-legacy-app --output scan.json
  perl bin/aegis-agent.pl --path ./demo-legacy-app --api http://localhost:8000/api/v1/scans

=head1 OPTIONS

  --path PATH     Dossier à scanner (obligatoire)
  --output FILE   Écrit le rapport JSON dans ce fichier
  --api URL       Envoie le rapport JSON en POST vers cette URL
  --help          Affiche cette aide

Sans --output ni --api, le rapport JSON est simplement affiché sur STDOUT.

=head1 EXIT CODES

  0  scan terminé, aucun finding critique
  2  scan terminé, au moins un finding critique
  1  erreur (chemin invalide, échec d'écriture ou d'envoi, usage incorrect)

=cut

# On n'utilise pas Pod::Usage : sur ce Cygwin par exemple, il n'est même
# pas installé par défaut. Autant faire un affichage d'aide à la main que
# de rajouter une dépendance qui peut manquer.
sub print_usage {
    print <<'USAGE';
Usage : aegis-agent.pl --path DOSSIER [--output FICHIER.json] [--api URL]

  --path PATH     Dossier à scanner (obligatoire)
  --output FILE   Écrit le rapport JSON dans ce fichier
  --api URL       Envoie le rapport JSON en POST vers cette URL
  --help          Affiche cette aide

Sans --output ni --api, le rapport JSON est affiché sur STDOUT.
USAGE
    return;
}

sub main {
    my %opt;
    my $parsed_ok = GetOptions(
        \%opt,
        'path=s',
        'output=s',
        'api=s',
        'help',
    );

    if ($opt{help}) {
        print_usage();
        return 0;
    }

    unless ($parsed_ok && $opt{path}) {
        print_usage();
        return 1;
    }

    unless (-d $opt{path}) {
        print STDERR "Erreur : le chemin '$opt{path}' n'existe pas ou n'est pas un dossier.\n";
        return 1;
    }

    my $files = collect_files($opt{path});

    my @findings;
    for my $file_meta (@$files) {
        my $content = read_text_file($file_meta->{path});
        push @findings, scan_file($file_meta, $content);
    }

    my $report = build_report($opt{path}, $files, \@findings);

    if ($opt{output}) {
        eval { write_json_report($report, $opt{output}); 1 }
            or do {
                print STDERR "Erreur d'écriture du rapport : $@";
                return 1;
            };
        print "Rapport écrit dans $opt{output}\n";
    }

    if ($opt{api}) {
        my ($ok, $status) = send_report($report, $opt{api});
        unless ($ok) {
            print STDERR "Échec de l'envoi vers $opt{api} : $status\n";
            return 1;
        }
        print "Rapport envoyé vers $opt{api} (statut $status)\n";
    }

    unless ($opt{output} || $opt{api}) {
        require JSON::PP;
        print JSON::PP->new->utf8->canonical->pretty->encode($report);
    }

    printf STDERR "Scan terminé : %d fichier(s), %d finding(s), score %s/100\n",
        scalar @$files, scalar @findings, $report->{score};

    return $report->{findings_by_severity}{critical} > 0 ? 2 : 0;
}

exit main();
