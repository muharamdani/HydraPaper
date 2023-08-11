# compile markdown to groff

pandoc_exe = find_program('pandoc', required: false)
if pandoc_exe.found()
    message('Compiling man page from markdown to groff')
    r = run_command(
        'pandoc',
        '-s',
        '-t',
        'man',
        meson.project_name() + '.1.md',
        '-o',
        meson.project_name() + '.1'
    )
    if r.returncode() != 0
        warning('Failed to compile man page')
    else
        message('Man page compilation succeeded, installing')
        install_man('hydrapaper.1')
    endif
else
    warning('Pandoc not found, skipping man page compilation')
endif
