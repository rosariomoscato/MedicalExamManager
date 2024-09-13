{pkgs}: {
  deps = [
    pkgs.gettext
    pkgs.glibcLocales
    pkgs.postgresql
  ];
}
