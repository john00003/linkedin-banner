# linkedin-banner

After getting my first professional headshots done, I felt like it was now appropriate for me to invest some time into making a banner that complemented it.
I wanted to make something that matched the colors in my headshot, looked beautiful, and gave a quick overview of my interests in CS.

## Generating the ASCII art
I had made this ASCII art a while ago for my (currently WIP) [personal portfolio webpage](https://john00003.github.io/).
I generated it using the Linux command line tool [figlet](https://linux.die.net/man/6/figlet), and the custom `cosmic` font from [this repository of custom figlet fonts](https://github.com/hIMEI29A/FigletFonts).
You can use the command `showfigfonts <text>` to view all the available renderings of `<text>` in different ASCII fonts.

## Selecting the background image
As stated in `ATTRIBUTION.txt`, I modified the "Anomaly" Ubuntu 26.04 background made by Ian Ryge. What a beautiful work of art, it's my favorite computer background.

I selected a region of the original image on the right hand side that matched LinkedIn's banner resolution (1584 x 396), that when flipped horizontally, would provide a space on the right hand side that wasn't very busy, so that the overlaid text was clearly visible.

I created a look-up table (LUT) defining the modified colors to remap the original colors to.
I calculated the [relative luminance](https://en.wikipedia.org/wiki/Relative_luminance) of the original colors in the image using the [sRGB constants](https://en.wikipedia.org/wiki/SRGB), and assuming the RGB of the original image was already in linear light.
Combined, this remapped the plum background to grey, and remapped the different shades of yellow/orange to shades of green.
