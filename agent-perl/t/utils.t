use strict;
use warnings;
use Test::More;

use FindBin qw($RealBin);
use lib "$RealBin/../lib";

use File::Temp qw(tempdir);
use File::Spec;

use Aegis::Utils qw(sha256_hex_of_file read_text_file relative_path is_binary_content);

subtest 'is_binary_content' => sub {
    ok(!is_binary_content("hello world\n"), 'texte normal -> pas binaire');
    ok(is_binary_content("hello\0world"), "octet NUL -> binaire");
    ok(!is_binary_content(''), 'chaine vide -> pas binaire');
    ok(!is_binary_content(undef), 'undef -> pas binaire (ne meurt pas)');
};

subtest 'read_text_file' => sub {
    my $dir = tempdir(CLEANUP => 1);
    my $text_path = File::Spec->catfile($dir, 'script.py');
    open(my $fh, '>:raw', $text_path) or die $!;
    print $fh "print('hello')\n";
    close $fh;

    is(read_text_file($text_path), "print('hello')\n", 'lit un fichier texte normal');

    my $bin_path = File::Spec->catfile($dir, 'image.bin');
    open(my $bfh, '>:raw', $bin_path) or die $!;
    print $bfh "\xFF\xD8\x00\xFE";
    close $bfh;

    is(read_text_file($bin_path), undef, 'renvoie undef pour un fichier binaire');

    is(
        read_text_file(File::Spec->catfile($dir, 'absent.txt')),
        undef,
        "renvoie undef pour un fichier qui n'existe pas (ne meurt pas)"
    );
};

subtest 'sha256_hex_of_file' => sub {
    my $dir = tempdir(CLEANUP => 1);
    my $path = File::Spec->catfile($dir, 'a.txt');
    open(my $fh, '>:raw', $path) or die $!;
    print $fh 'hello';
    close $fh;

    is(
        sha256_hex_of_file($path),
        '2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824',
        'hash sha256 correct pour un contenu connu'
    );
};

subtest 'relative_path' => sub {
    is(relative_path('/root/sub/file.pl', '/root'), 'sub/file.pl', 'chemin POSIX simple');
    is(
        relative_path('C:\\root\\sub\\file.pl', 'C:\\root'),
        'sub/file.pl',
        'chemin Windows normalisé en /'
    );
};

done_testing();
