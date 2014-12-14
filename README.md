# Kallisto, crowd-sourced transcript cleaning

Kallisto is a simple web app that allows many people to contribute to cleaning a transcript, most likely for [Spacelog](http://spacelog.org/) (or another site using the same *Artemis* software). Input is in the form of a set of PNGs of transcript pages, and (optionally) a text file for each to act as an initial "uncleaned" version. In turn, someone using Kallisto will "clean" a single page, attempting to get the text representation to match the original image.

## Notes

This is very early days, but:

 * Ubuntu (14.04) + postgresql-9.3 + imagemagick + ghostscript + libpng12-0
 * Create a database called "kallisto" accessible by "user" with no password
 * Django 1.7 app; `pip install -r requirements.txt` into a virtualenv, then `python manage.py migrate` should get you started
 * You need to make a mission, which must include a mission patch (because we want things to look pretty!)
 * `python manage.py import_pages` will import the text and PNG pages; see its help for how (and how to generate them)

## Author

[James Aylett](https://github.com/jaylett) and the [Spacelog](https://github.com/Spacelog) team.
