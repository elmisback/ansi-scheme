# ansi-theme

```
$ ansi-theme --help
usage: ansi-theme [-h] {add,mv,set,rm,export,ls,vimfile,print,bg,fg,cs} ...

ansi-theme: terminal themes via ANSI escape codes

positional arguments:
  {add,mv,set,rm,export,ls,vimfile,print,bg,fg,cs}
    add                 adds one or more themes
    mv                  renames a theme
    set                 sets the theme (and brightness)
    rm                  removes one or more themes
    export              prints a theme to stdout
    ls                  lists available themes
    vimfile             prints a vim colorscheme that works for all themes
    print               prints terminal colors 0 - 21
    bg                  sets the background
    fg                  sets the foreground
    cs                  sets the cursor color
```

## Preinstalled themes
Right now, just my favorite themes.
```
$ ansi-theme ls
Package themes:
atelier-heath
atelier-savanna
```

I had this idea while tweaking the vim themefile provided by the base16 project.

# Design documentation

Colorscheme pain points:
* Different formats for schemes in the wild
* Switching schemes on the fly
* Coordinating theme-switching between terminal-based applications

Goals:
* On-the-fly terminal colorschemes without pain
* Simple scheme format
* Grab themes from Github
* Decent standard theme library (probably base16)
* Unambiguous set of sub-commands
* Single palette for all applications

Non-goals:
* Distinguishing between applications (applications can handle this)
