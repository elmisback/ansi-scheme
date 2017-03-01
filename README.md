# ansi-scheme

```
to be implemented:
* set
* display
* default_style
* Decent standard scheme library (probably base16)
```

I had this idea while tweaking the vim colorschemefile provided by the base16 project.

# Design documentation

Colorscheme pain points:
* Different formats for schemes in the wild
* Switching schemes on the fly
* Coordinating scheme-switching between terminal-based applications

Goals:
* On-the-fly terminal colorschemes without pain
* Grab schemes from Github
* Single palette for all applications

Non-goals:
* Distinguishing between applications (applications can handle this)

## `.ANSISCHEME` Format
```
{
  "colors": {
    "Black": "#000000",
    ...
    "BrightBlack": "222222",
    ...
    "BrightWhite": "ffffff",
    "16": "ab cd ef",
    "18": "cc cc cc",
    ...
    "21": "12 34 56"
  },
  "styles": {
    "extra-dark": {
      "foreground": "BrightBlack",
      "background": "Black",
      "cursor": "33 33 33"
    },
    "dark": {
      "foreground": "White",
      "background": "Black",
      "cursor": "33 33 33"
    },
    "light": {
      "foreground": "BrightBlack",
      "background": "White",
      "cursor": "33 33 33"
    }
  },
  "default_style": "dark"
}

# How are the colors parsed?
Use the first 3 pairs of hex digits or fall back to named colors.

# Why are non-(0-15) colors allowed?
Sometimes people like to set other colors.
