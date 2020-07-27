{ sources ? import ./sources.nix }:     # import the sources
with
  { overlay = _: pkgs:
      { niv = import sources.niv {};    # use the sources :)
      };
  };
let pkgs = import sources.nixpkgs                  # and use them again!
  { overlays = [ overlay ] ; config = { allowUnfree = true; }; };
  python-packages = python-packages: with python-packages; [
    discordpy python-dotenv pylint autopep8
  ]; 
  python = pkgs.python38.withPackages python-packages;

in

pkgs.mkShell {
    name="Discord-Bot-Env";
    buildInputs = [python];

}
