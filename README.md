# button-sheet

Python script that evenly spaces and formats images on a PDF for printing and making buttons.

## Configuration

Must be placed in a file called `config.toml`. Image paths should be relative to the exe file (or the project root if running from source.)

```toml
# filename and background colour for each button
[images]
image1 = { filename = "path/to/image1.png", background = "#000000" }
image2 = { filename = "path/to/image2.png", background = "#FFFFFF" }

[output]
rows = 5    # number of rows of buttons per page
columns = 3 # number of columns of buttons per page

dpi = 600              # resolution (in dots per inch) of the generated images
image_diameter_mm = 37 # diameter of the actual image to print on the buttons
margin_width_mm = 6    # width of the solid colour margin on one side (eg. 37 mm diameter and 6 mm margin -> 49 mm total)
border_width_mm = 0.5  # width of the black border around the edges of the buttons (set to 0 to disable)
min_spacing_mm = 2     # minimum allowed spacing between buttons (will display an error if unable to meet this)
page_margin_mm = 5     # empty margin at the edges of each page

# what buttons to put on each page
pages = [
    ["image1"],           # with above rows and columns, this will do 15 of image1
    ["image1", "image2"], # this will do 8 of image1, then 7 of image2
]
```

## Usage

* Download the latest executable from the [Releases](https://github.com/object-Object/button-sheet/releases) page
* Create a file named `config.toml` with the above format
* Generate the PDF by running the exe file

Intermediate images are placed in `build/` and may be overwritten. The final pdf is written to `buttons.pdf`.

## Running from source

* Clone and enter this repo
* Optional: [set up a venv](https://docs.python.org/3/library/venv.html)
* Install dependencies: `pip install -r requirements.txt`
* Create a file named `config.toml` with the above format
* Generate the PDF: `python src/main.py`

## Packaging for release

* Set up the repo as above
  * NOTE: venv is mandatory for this step to limit the amount of libraries added to the executable
* Generate the executable: `pyinstaller main.spec`

The resulting executable will be in `dist/`, eg: `dist/button-sheet-Windows-AMD64/button-sheet-Windows-AMD64.exe`
