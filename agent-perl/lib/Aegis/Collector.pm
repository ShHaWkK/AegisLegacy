package Aegis::Collector;

use strict;
use warnings;
use utf8;
use v5.16;

use File::Find ();
use File::Spec;
use Exporter qw(import);

use Aegis::Utils qw(sha256_hex_of_file relative_path);

our @EXPORT_OK = qw(collect_files);

=head1 NAME

Aegis::Collector - Parcourt un arbre de fichiers legacy et en extrait les métadonnées.

=head1 DESCRIPTION

Ne fait aucune détection : Collector se contente de trouver les fichiers
pertinents et de calculer leurs métadonnées (taille, date, hash). La
détection de patterns est le travail d'Aegis::Scanner.

=cut

# Extensions surveillées par défaut, alignées sur le moteur Python
# (backend/app/domain/language.py) pour rester cohérent entre les deux
# scanners.
our @DEFAULT_EXTENSIONS = qw(.pl .pm .cgi .py .sh .conf .env);

our @IGNORED_DIRECTORIES = qw(.git __pycache__ node_modules venv .venv blib _build .idea .vscode);

sub _is_ignored_dir {
    my ($dirname) = @_;
    return grep { $_ eq $dirname } @IGNORED_DIRECTORIES;
}

# collect_files($root, \@extensions) -> liste de hashrefs
#   { path, relative_path, extension, size, mtime, sha256 }
# \@extensions est optionnel ; par défaut @DEFAULT_EXTENSIONS.
sub collect_files {
    my ($root, $extensions) = @_;
    $extensions //= \@DEFAULT_EXTENSIONS;
    my %wanted_ext = map { lc($_) => 1 } @$extensions;

    my @files;

    File::Find::find(
        {
            wanted => sub {
                my $path = $File::Find::name;

                if (-d $path) {
                    my @parts = File::Spec->splitdir($path);
                    if (@parts && _is_ignored_dir($parts[-1])) {
                        $File::Find::prune = 1;
                    }
                    return;
                }

                return unless -f $path;

                my ($ext) = $path =~ /(\.[^.\/\\]+)$/;
                $ext = defined $ext ? lc($ext) : '';
                return unless $wanted_ext{$ext};

                my @stat = stat($path);
                return unless @stat;

                push @files, {
                    path          => $path,
                    relative_path => relative_path($path, $root),
                    extension     => $ext,
                    size          => $stat[7],
                    mtime         => $stat[9],
                    sha256        => sha256_hex_of_file($path),
                };
            },
        },
        $root,
    );

    return \@files;
}

1;
