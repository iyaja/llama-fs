{
  description = "LlamaFS — a self-organizing file manager powered by Llama 3";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        python = pkgs.python312;


        # agentops is not yet packaged in nixpkgs; build it from PyPI.
        agentops-pkg = python.pkgs.buildPythonPackage rec {
          pname = "agentops";
          version = "0.4.21";
          pyproject = true;
          src = python.pkgs.fetchPypi {
            inherit pname version;
            hash = "sha256-R3Wcbf1upYutL3dkJX5HeMsuNK4YDO9kL2D1atztZRA=";
          };
          build-system = [ python.pkgs.hatchling ];
          pythonRelaxDeps = true; # agentops upper bounds lag behind nixpkgs
          propagatedBuildInputs = with python.pkgs; [
            aiohttp
            httpx
            opentelemetry-api
            opentelemetry-exporter-otlp-proto-http
            opentelemetry-instrumentation
            opentelemetry-sdk
            opentelemetry-semantic-conventions
            ordered-set
            packaging
            psutil
            pyyaml
            requests
            termcolor
            wrapt
          ];
          doCheck = false;
        };

        pythonDeps = ps: with ps; [
          # LLM clients
          groq
          ollama
          litellm

          # Document loading & indexing
          # Use llama-index-core instead of the metapackage to avoid a bin/ conflict
          # between llama-index and llama-index-cli in the Python env.
          llama-index-core
          chromadb

          # Observability (agentops built inline above; weave is optional — see patch)
          agentops-pkg

          # LangChain (imported but used lightly)
          langchain
          langchain-core

          # Web server
          fastapi
          uvicorn

          # File watching
          watchdog

          # CLI & display
          click
          colorama
          termcolor
          asciitree

          # Misc
          python-dotenv
          pydantic
        ];

        pythonEnv = python.withPackages pythonDeps;

        llamafs = python.pkgs.buildPythonApplication {
          pname = "llama-fs";
          version = "0.1.0";
          src = self;

          format = "other"; # no setup.py / pyproject.toml

          postPatch = ''
            # weave (wandb) is not in nixpkgs and not actively called — make it optional.
            substituteInPlace src/loader.py \
              --replace-fail 'import weave' \
'try:
    import weave
except ImportError:
    pass'

            # agentops 0.4+ removed record_function / record_tool.
            # Inject a no-op shim right after the agentops import.
            substituteInPlace src/loader.py \
              --replace-fail 'import agentops' \
'import agentops
if not hasattr(agentops, '"'"'record_function'"'"'):
    def _noop(name):
        def decorator(f): return f
        return decorator
    agentops.record_function = _noop
    agentops.record_tool = _noop'
          '';

          propagatedBuildInputs = pythonDeps python.pkgs;

          nativeBuildInputs = [ pkgs.makeWrapper ];

          installPhase = ''
            runHook preInstall

            # Install source tree
            mkdir -p $out/lib/llama-fs
            cp -r . $out/lib/llama-fs/

            mkdir -p $out/bin

            # CLI entry point (batch mode)
            # PYTHONPATH so Python can find src/*, but no --chdir so the
            # working directory stays where the user invoked the command
            # (agentops writes agentops.log to CWD, which must be writable).
            makeWrapper ${pythonEnv}/bin/python $out/bin/llama-fs \
              --add-flags "$out/lib/llama-fs/main.py" \
              --prefix PYTHONPATH : "$out/lib/llama-fs"

            # Server entry point (watch / batch API)
            # --app-dir tells uvicorn where to find server:app without cd.
            makeWrapper ${pythonEnv}/bin/uvicorn $out/bin/llama-fs-server \
              --add-flags "server:app --app-dir $out/lib/llama-fs --host 127.0.0.1 --port 8000"

            runHook postInstall
          '';

          meta = with pkgs.lib; {
            description = "Self-organizing file manager powered by Llama 3 via Groq";
            homepage = "https://github.com/iyaja/llama-fs";
            license = licenses.mit;
            platforms = platforms.linux ++ platforms.darwin;
            mainProgram = "llama-fs-server";
          };
        };

      in
      {
        # ── packages ────────────────────────────────────────────────────────────
        packages.default = llamafs;
        packages.llama-fs = llamafs;

        # ── apps ────────────────────────────────────────────────────────────────
        # `nix run github:iyaja/llama-fs` starts the FastAPI server on :8000
        apps.default = {
          type = "app";
          program = "${llamafs}/bin/llama-fs-server";
        };

        # ── dev shell ───────────────────────────────────────────────────────────
        # `nix develop` drops you into a shell with all Python deps + Ollama
        devShells.default = pkgs.mkShell {
          buildInputs = [ pythonEnv pkgs.ollama ];
          shellHook = ''
            echo ""
            echo "  LlamaFS dev environment"
            echo "  ── server:  fastapi dev server.py"
            echo "  ── cli:     python main.py <src> <dst>"
            echo ""
            echo "  Required env vars (copy .env.example → .env):"
            echo "    GROQ_API_KEY    https://console.groq.com/keys"
            echo "    AGENTOPS_API_KEY https://app.agentops.ai"
            echo ""
          '';
        };

        # ── NixOS module ────────────────────────────────────────────────────────
        # Optionally expose a systemd service:
        #   services.llama-fs.enable = true;
        nixosModules.default = { config, lib, ... }:
          let cfg = config.services.llama-fs; in
          {
            options.services.llama-fs = {
              enable = lib.mkEnableOption "LlamaFS self-organizing file server";

              port = lib.mkOption {
                type = lib.types.port;
                default = 8000;
                description = "TCP port the FastAPI server listens on.";
              };

              host = lib.mkOption {
                type = lib.types.str;
                default = "127.0.0.1";
                description = "Bind address for the FastAPI server.";
              };

              environmentFile = lib.mkOption {
                type = lib.types.path;
                description = ''
                  Path to a file containing environment variables (EnvironmentFile).
                  Must export at least GROQ_API_KEY and AGENTOPS_API_KEY.
                  Keep this file outside the Nix store (not world-readable).
                '';
              };
            };

            config = lib.mkIf cfg.enable {
              systemd.services.llama-fs = {
                description = "LlamaFS self-organizing file server";
                wantedBy = [ "multi-user.target" ];
                after = [ "network.target" ];
                serviceConfig = {
                  ExecStart = "${llamafs}/bin/llama-fs-server --host ${cfg.host} --port ${toString cfg.port}";
                  EnvironmentFile = cfg.environmentFile;
                  Restart = "on-failure";
                  DynamicUser = true;
                  # Harden the service — it only needs to read the user's directories
                  NoNewPrivileges = true;
                  ProtectSystem = "strict";
                  ProtectHome = "read-only";
                };
              };
            };
          };
      }
    );
}
