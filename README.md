# Kallisto, crowd-sourced transcript cleaning

Kallisto is a simple web app that allows many people to contribute to cleaning a transcript, most likely for [Spacelog](http://spacelog.org/) (or another site using the same *Artemis* software). Input is in the form of a set of PNGs of transcript pages, and (optionally) a text file for each to act as an initial "uncleaned" version. In turn, someone using Kallisto will "clean" a single page, attempting to get the text representation to match the original image.

## Notes

This is very early days, but:

 * Ubuntu (14.04) + postgresql-9.3 + imagemagick + ghostscript + libpng12-0
 * Create a database called "kallisto" accessible by "user" with no password
 * Django 1.7 app; `pip install -r requirements.txt` into a virtualenv, then `python manage.py migrate` should get you started
 * You need to make a mission, which must include a mission patch (because we want things to look pretty!)
 * `python manage.py import_pages` will import the text and PNG pages; see its help for how (and how to generate them)

## Screen sizes

This works well at 1080p full screen in Chrome with presentation mode,
and various smaller resolutions. Firefox doesn’t have presentation mode,
and at 1080p the page is slightly too tall unless you turn off the
bookmarks bar (at which point you can juggle things in full screen
mode).

If you can’t manage 1080p, the best width is probably a little under
1500px (which triggers the two column layout), since it makes the
text nice and large.

There may be some resolutions where the textarea scrolls, although they
should be minimal. This hasn’t been tested on real tablets, only
emulated. All the sizing is based on early pages of MA8, and so will
undoubtedly fail on other missions and possibly on later pages of that
one.

## Author

[James Aylett](https://github.com/jaylett) and the [Spacelog](https://github.com/Spacelog) team.
