Container deployment is deferred. This environment has Podman but cannot initialize
it (read-only `/run/user/1000/libpod`); Docker/Postgres/Redis executables are absent.
No unverified compose file is presented as runnable. PostgreSQL + Redis/RQ and the
networked fixture supervisor remain the intended next deployment stage; do not
expose the development API or SQLite adapter publicly. See ADR-012.
