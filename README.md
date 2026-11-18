![Imgur](https://i.imgur.com/yopQ6IM.gif)

# Optician Sans

Optician Sans is a free typeface based on the 10 historical optotype letters seen on millions of eye charts around the world, finalising the work that was started decades ago.
 
The universal optometrist eye charts have been around for decades and seen by millions of people worldwide. The first standardised chart was created by Hermann Snellen in the Netherlands in 1862, before Louise Sloan designed a new set in 1959. These letters make up the now universal chart for testing visual acuity, also known as the LogMAR chart, which was developed by National Vision Research Institute of Australia. But ever since 1959, they have consisted of only 10 letters.
 
Optician Sans is a fully functional typeface based on the historical optotype letters, including numbers and special characters.

Read [our Medium post](https://medium.com/@schikulski/completing-a-typeface-that-was-started-decades-ago-a9c977c9cf08) for more background information about the project. Or check out [the website optician-sans.com](https://optician-sans.com/?utm_source=github&utm_medium=optician-sans).

## Changes in this fork (v1.003)

This is a fork of [anewtypeofinterference/Optician-Sans](https://github.com/anewtypeofinterference/Optician-Sans). It adds the characters the original lacks for technical headlines, so text like `$PATH`, `<script>` or `~/.ssh` no longer falls back to another font mid-word.

| Character | Glyph | Notes |
|---|---|---|
| `$` | `dollar` | A slightly shortened S with stem stubs that reach just past the baseline and cap height |
| `<` `>` | `less`, `greater` | A V turned on its side, sized to match `+` and `=` |
| `~` | `asciitilde` | A single wave at the hyphen's weight, on the same centre line |
| `…` | `ellipsis` | Three periods at the period's own spacing |
| `` ` `` | `grave.quote` | A backtick at quote height. The original accent-height `grave` is kept for the accented letters, but U+0060 now points at this glyph |

The new glyphs are drawn by [`scripts/add_glyphs.py`](scripts/add_glyphs.py), which patches the compiled fonts in `OpenType-PS/` and `OpenType-TT/` and regenerates the web fonts in `Web-PS/` and `Web-TT/`. To rebuild:

```
pip install fonttools brotli skia-pathops
python scripts/add_glyphs.py
```

Two things to know:

- The FontLab source in `VFC/` does not contain these glyphs. They exist only in the compiled fonts.
- The new glyphs are unhinted, and the original digital signature has been removed because it cannot survive a modification.

## Contributing

If you have any suggestions, feature requests or you want to help expanding the typeface, we'd love to hear from you in the issue section or contact [Simen](https://github.com/schikulski) or [Fábio](https://github.com/scannerlicker).

## Future Updates
There are no future updates planned, at the moment.

## Licensing
This Font Software is licensed under the SIL Open Font License, Version 1.1. [More details in the license file](LICENSE.md).

### Credits

Optician Sans is created by [ANTI Hamar](https://instagram.com/anti_hamar) and [Fábio Duarte Martins](https://github.com/scannerlicker). The typeface is a part of the visual identity for optician Optiker-K in Norway.

**Art director & designer** [Simen Schikulski](https://github.com/schikulski)

**Type Designer** [Fábio Duarte Martins](https://github.com/scannerlicker)

**Adviser** Kjetil Wold

**Designer** Vivi-Ann Slaatsveen

**VFX** Magnus Vanem

**Marketing** Tor Hernan Floor
