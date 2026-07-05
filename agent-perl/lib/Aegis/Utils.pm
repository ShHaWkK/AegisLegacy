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

Rien de spécifique au métier ici : hachage, lecture de fichier, calcul de
chemin relatif. Ces fonctions sont utilisées par Aegis::Collector et
Aegis::Scanner.

=cut

# Heuristique simple : un octet NUL dans les premiers Ko indique un fichier
# binaire. Ce n'est pas parfait mais suffit pour éviter de scanner des
# fichiers .db, images, etc.
sub is_binary_content {
    my ($content) = @_;
    return 0 unless defined $content;
    my $sample = substr($content, 0, 8192);
    return index($sample, "\0") >= 0 ? 1 : 0;
}

# Lit un fichier en entier. Retourne undef (sans mourir) si le fichier est
# illisible ou binaire, plutôt que de faire planter tout le scan pour un
# seul fichier problématique dans un gros arbre legacy.
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

# Chemin de $path relatif à $root, avec des séparateurs '/' partout (même
# sous Windows) pour que le JSON produit soit stable quelle que soit la
# plateforme d'exécution de l'agent.
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
