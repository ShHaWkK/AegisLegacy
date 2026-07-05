use strict;
use warnings;
use Test::More;

use FindBin qw($RealBin);
use lib "$RealBin/../lib";

use File::Temp qw(tempdir);
use File::Spec;
use File::Path qw(make_path);

use Aegis::Collector qw(collect_files);

sub write_file {
    my ($path, $content) = @_;
    open(my $fh, '>:raw', $path) or die "$path: $!";
    print $fh $content;
    close $fh;
}

subtest 'collecte les fichiers avec une extension surveillee' => sub {
    my $dir = tempdir(CLEANUP => 1);
    write_file(File::Spec->catfile($dir, 'legacy.pl'), "print 1;\n");
    write_file(File::Spec->catfile($dir, 'notes.txt'), "rien d'interessant\n");

    my $files = collect_files($dir);
    my @names = map { $_->{relative_path} } @$files;

    is(scalar @$files, 1, 'un seul fichier retenu');
    is($names[0], 'legacy.pl', 'le .txt est ignore, pas le .pl');
};

subtest 'ignore les dossiers exclus' => sub {
    my $dir = tempdir(CLEANUP => 1);
    my $git_dir = File::Spec->catdir($dir, '.git');
    make_path($git_dir);
    write_file(File::Spec->catfile($git_dir, 'hooks.py'), "eval(x)\n");
    write_file(File::Spec->catfile($dir, 'app.py'), "x = 1\n");

    my $files = collect_files($dir);
    my @names = map { $_->{relative_path} } @$files;

    is(scalar @$files, 1, 'seul le fichier hors .git est retenu');
    is($names[0], 'app.py');
};

subtest 'chaque entree a les metadonnees attendues' => sub {
    my $dir = tempdir(CLEANUP => 1);
    write_file(File::Spec->catfile($dir, 'a.py'), 'hello');

    my $files = collect_files($dir);
    my $entry = $files->[0];

    ok(defined $entry->{size}, 'taille presente');
    ok(defined $entry->{mtime}, 'date de modification presente');
    is(length($entry->{sha256}), 64, 'hash sha256 en hexa (64 caracteres)');
};

subtest 'dossier vide -> liste vide' => sub {
    my $dir = tempdir(CLEANUP => 1);
    my $files = collect_files($dir);
    is(scalar @$files, 0);
};

done_testing();
