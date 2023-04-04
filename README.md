# button-sheet

Python script that evenly spaces and formats images on a PDF for printing and making buttons.

## Usage

* Optional: [set up a venv](https://docs.python.org/3/library/venv.html)
* Install dependencies: `pip install -r requirements.txt`
* Create a file named `config.toml` with the below format
* Generate the PDF: `python src/main.py`

```toml
# filename and background colour for each button
[images]
image1 = { filename = "path/to/image1.png", background = "#000000" }
image2 = { filename = "path/to/image2.png", background = "#FFFFFF" }

[output]
rows = 5    # number of rows of buttons per page
columns = 3 # number of columns of buttons per page

image_diameter_mm = 37 # diameter of the actual image to print on the buttons
margin_width_mm = 6    # width of the solid colour margin (eg. 37 mm diameter and 6 mm margin -> 49 mm total)
min_spacing_mm = 2     # minimum allowed spacing between buttons (will display an error if unable to meet this)
page_margin_mm = 5     # empty margin at the edges of each page

# what buttons to put on each page
pages = [
    ["image1"],           # with above rows and columns, this will do 15 of image1
    ["image1", "image2"], # this will do 8 of image1, then 7 of image2
]
```
