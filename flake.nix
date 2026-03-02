{
  description = "DevShell - Fullstack Web Dev";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
      in {
        devShells = {
          default = pkgs.mkShell {
            name = "fs-devshell";
            buildInputs = with pkgs; [
              nodejs
              yarn
              typescript
              eslint
              prettier
              tailwindcss
              playwright

              python314
              uv
              black
              ruff
              postgresql
              redis

              docker
              docker-compose

              httpie
              pre-commit

              gcc
              pkg-config
              stdenv.cc.cc.lib
            ];
            shellHook = ''
              # Check for pyproject.toml and set up the Python environment
              if [ -f backend/pyproject.toml ]; then
                echo "pyproject.toml found. Running 'uv sync'..."
                cd backend && uv sync && uv sync --group dev
                echo "uv sync complete."

                # Project-local directory for PostgreSQL socket and data
                export PGDATA=$PWD/.tmp
                export PGHOST=$PGDATA
                export PGUSER=devuser
                export PGDATABASE=aerops
                mkdir -p $PGDATA

                # Initialize DB if not present
                if [ ! -f "$PGDATA/PG_VERSION" ]; then
                  initdb -D $PGDATA
                  pg_ctl -D $PGDATA -o "-k $PGDATA" -l $PGDATA/logfile start
                  psql -h $PGDATA -U $USER -d postgres -tc "SELECT 1 FROM pg_roles WHERE rolname='devuser'" | grep -q 1 || \
                    psql -h $PGDATA -U $USER -d postgres -c "CREATE ROLE devuser WITH LOGIN SUPERUSER;"
                  psql -h $PGDATA -U $USER -d postgres -tc "SELECT 1 FROM pg_database WHERE datname='aerops'" | grep -q 1 || \
                    psql -h $PGDATA -U $USER -d postgres -c "CREATE DATABASE aerops OWNER devuser;"
                  echo "Initialized new PostgreSQL DB at $PGDATA"
                fi

                # Start PostgreSQL using a socket inside .tmp
                if ! pg_ctl -D $PGDATA status > /dev/null 2>&1; then
                  pg_ctl -D $PGDATA -o "-k $PGDATA" -l $PGDATA/logfile start
                fi
                echo "PostgreSQL server running (socket: $PGDATA)"

                # Optional ephemeral mode: deletes DB on shell exit
                if [ "$SS_EPHEMERAL_DB" = "1" ]; then
                    trap 'pg_ctl -D $PGDATA stop; rm -rf $PGDATA' EXIT
                else
                    trap 'pg_ctl -D $PGDATA stop' EXIT
                fi

                # Start Redis in the background
                redis-server --port 6302 --daemonize yes

                fi

              cd ..

              # Check for package.json and install Node.js dependencies
              if [ -f frontend/package.json ]; then
                echo "package.json found. Running 'npm install'..."
                cd frontend && npm install
                echo "npm install complete."
              fi

              # Start the Fish shell
              export LD_LIBRARY_PATH=${
                  pkgs.lib.makeLibraryPath [
                  pkgs.stdenv.cc.cc.lib
                  pkgs.postgresql
                  pkgs.openssl
                ]
              }:$LD_LIBRARY_PATH
              echo "🚀 AeroOps DevShell Loaded"
              exec fish
            '';
          };
        };
      }
    );
}
