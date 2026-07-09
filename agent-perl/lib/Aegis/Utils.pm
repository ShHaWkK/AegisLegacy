package Aegis::Utils;

use strict;
use warnings;
use utf8;
use v5.16;

use Digest::SHA ();
use Exporter qw(import);

our @EXPORT_OK = qw(sha256_hex_of_file read_text_file relative_path is_binary_content);

=head1 NAME

Aegis::Utils - Petites fonctions utilitaires partagées par l'agent.

=head1 DESCRIPTION

Juste des petites briques utilisées par Collector et Scanner : hacher un
fichier, le lire, calculer un chemin relatif. Rien de plus.

=cut

# Un octet NUL dans les premiers Ko, ça sent le fichier binaire. C'est une
# heuristique toute simple, pas infaillible, mais ça suffit à écarter les
# .db, images, etc. sans se compliquer la vie.
sub is_binary_content {
    my ($content) = @_;
    return 0 unless defined $content;
    my $sample = substr($content, 0, 8192);
    return index($sample, "\0") >= 0 ? 1 : 0;
}

# Lit tout le fichier d'un coup. Si c'est illisible ou binaire, on renvoie
# undef plutôt que de planter — un fichier bizarre ne doit pas faire
# tomber le scan de tout un arbre legacy.
sub read_text_file {
    my ($path) = @_;

    open(my $fh, '<:raw', $path) or return undef;
    local $/;
    my $content = <$fh>;
    close $fh;

    return undef unless defined $content;
    return undef if is_binary_content($content);

    return $content;
}

sub sha256_hex_of_file {
    my ($path) = @_;

    open(my $fh, '<:raw', $path) or return undef;
    my $sha = Digest::SHA->new(256);
    $sha->addfile($fh);
    close $fh;

    return $sha->hexdigest;
}

# Chemin de $path relatif à $root. On met des '/' partout, même sous
# Windows, pour que le JSON de sortie soit le même quelle que soit la
# machine sur laquelle tourne l'agent.
sub relative_path {
    my ($path, $root) = @_;

    my $rel = $path;
    $rel =~ s/\\/\//g;
    my $root_norm = $root;
    $root_norm =~ s/\\/\//g;
    $root_norm =~ s{/+$}{};

    if (index($rel, $root_norm) == 0) {
        $rel = substr($rel, length($root_norm));
        $rel =~ s{^/+}{};
    }

    return $rel;
}

1;
