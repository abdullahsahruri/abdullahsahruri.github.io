# Adding conferences

The list on /conferences comes from one file: `_data/conferences.csv`.
Open it in any text editor (or Excel, saved back as CSV) and add a line:

    name,url,deadline,date,note
    FCCM 2027,https://www.fccm.org/,2027-01-12,2027-05-03,abstract 2027-01-05

- `deadline` is the paper deadline, `date` is the conference start, both YYYY-MM-DD.
- Leave `deadline` or `date` empty when not known yet; the page shows TBD.
- `note` is optional (shown in small text under the deadline).
- Order does not matter; the page sorts by deadline. Delete a line to remove a conference.

Then double-click `publish.bat` (Windows) or run `./publish.sh`. It commits the file and pushes;
GitHub Pages rebuilds the site within a couple of minutes.
