import requests
import fitz  # PyMuPDF
from difflib import SequenceMatcher
from PIL import Image
from io import BytesIO
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from app import constants


def _similar(a, b, threshold=0.6):
    # Calculate similarity ratio between two strings
    return SequenceMatcher(None, a, b).ratio() > threshold


def find_and_crop_image(pdf_url, search_text, question_filename):
    # Download PDF content
    response = requests.get(pdf_url)
    pdf_content = BytesIO(response.content)

    # Open the PDF from memory
    doc = fitz.open(stream=pdf_content, filetype="pdf")

    # Search through each page
    for page_num in range(len(doc)):
        page = doc[page_num]

        # Get all text blocks on the page
        blocks = page.get_text("blocks")

        for block in blocks:
            block_text = block[4]  # The text content is at index 4

            # Check if this block is similar to our search text
            if _similar(block_text.lower(), search_text.lower()):
                # Create rectangle from block coordinates
                rect = fitz.Rect(block[:4])  # First 4 elements are coordinates

                # Get page dimensions
                page_rect = page.rect

                # Modify cropped rectangle to span full width but keep vertical position
                rect.x0 = page_rect.x0
                rect.x1 = page_rect.x1
                rect.y0 -= 60
                rect.y1 += 60

                # Convert page to image
                pix = page.get_pixmap(
                    matrix=fitz.Matrix(2, 2)
                )  # 2x zoom for better quality
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                # Convert rect coordinates to zoomed image coordinates
                crop_box = (rect.x0 * 2, rect.y0 * 2, rect.x1 * 2, rect.y1 * 2)

                # Crop image
                cropped_img = img.crop(crop_box)

                # If temp directory does not exist, create it
                os.makedirs(constants.TEMP_DIR, exist_ok=True)

                # Save cropped image
                output_path = f"{constants.TEMP_DIR}/{question_filename}.png"
                cropped_img.save(output_path)
                print(f"Found match on page {page_num + 1}. Saved to {output_path}")
                return True

    print("No matching text found in PDF")
    return False


if __name__ == "__main__":

    CHIJ_PAPER = "https://document.grail.moe/7871f70e5b78485c99cc4cf28cc68458.pdf"
    ACSI_PAPER = "https://document.grail.moe/ee5096dfab614b04b525f87a54128941.pdf"
    BPGHS_PAPER = "https://document.grail.moe/b06fe71b3f3c4f5db97844c79c7a12c1.pdf"
    search_text_dict = {
        "chij_4ii": (
            CHIJ_PAPER,
            "Given that y = 16x^3 - 5x, find (ii) the value of the integral from 0 to 1 of y dx, giving your answer correct to 3 significant figures.",
        ),
        "chij_5ai": (
            CHIJ_PAPER,
            "5(a)(i) Using the substitution z = 1 + x, write down all the terms in the expansion of (1 + x)^6, leaving each term in the form (1 + x)^pk where k and p are integers.",
        ),
        "chij_7iii": (
            CHIJ_PAPER,
            "7(iii) By expressing 5sin \u03b8 - cos \u03b8 in the form R sin(\u03b8 - \u03b1), where R > 0 and 0\u00b0 < \u03b1 < 90\u00b0, find the value of \u03b8.",
        ),
        "chij_9": (
            CHIJ_PAPER,
            "9 The equation of a circle is 224 12 36 x y x y+ \u2212 \u2212 + = 0. The equation of the line L is y = kx, where k is a constant. (i) Find the radius of the circle and the coordinates of its centre.",
        ),
        "acsi_7aii": (
            ACSI_PAPER,
            "Hence find the coefficient of 3x in the expansion of ( )( )6 23 14xx+\u2212 .",
        ),
        "acsi_2a": (
            ACSI_PAPER,
            "A circle with centre O passes through the points P(-1, 7) and Q(0, 8). (a) State the relationship between the perpendicular bisector of PQ and the point O.",
        ),
        "acsi_6ai": (
            ACSI_PAPER,
            "Prove the trigonometric identity: ( )2 2 2cosec 2cotcosec cos sinAAA AA+= +",
        ),
        "acsi_6b": (
            ACSI_PAPER,
            "Given that 1 sin 2cos11 2sin cosxx xx++=++ and x is acute, find the exact value of cos x.",
        ),
        "bpghs_2i": (
            BPGHS_PAPER,
            "At a warehouse sale, all prices are reduced by 15%. The price of a set of ear pods during the sale is $221. \n(i) Find its original price.",
        ),
        "bpghs_3a": (
            BPGHS_PAPER,
            "Ethan measures the amount of rain, in millimetres (mm), each day for 31 days. The bar chart shows his results. \n(a) Write down the median amount of rain.",
        ),
        "bpghs_3b": (BPGHS_PAPER, "Find the mean amount of rain per day."),
        "bpghs_23": (
            BPGHS_PAPER,
            "Given that 2^{3x} = 6 \\times 8, find the value of x.",
        ),
        "bpghs_14": (
            BPGHS_PAPER,
            "\\text{In the diagram, } O \\text{ is the centre of two concentric circles. A and B lie on the circumference of the smaller circle.} \\\\ \\text{C and D lie on the circumference of the larger circle. AD and BC intersect at O.} \\\\ \\text{Prove that} \\\\ (a) \\triangle AOC \\text{ and } \\triangle BOD \\text{ are congruent} \\\\ (b) \\triangle ADB \\text{ and } \\triangle BCA \\text{ are congruent.}",
        ),
        "bpghs_17": (
            BPGHS_PAPER,
            "PQRS \\text{ is a trapezium where } P \\text{ is the point } (-3, 2), Q \\text{ is the point } (5, 8) \\text{ and } R \\text{ is the point } (3, 2). \\\\ PQ \\text{ is parallel to } RS. \\\\ (a) \\text{ Find the equation of the line } RS. \\\\ (b)(i) \\text{ Find the length of } PQ. \\\\ (ii) \\text{ Hence find the perpendicular distance from } R \\text{ to } PQ.",
        ),
        "bpghs_20": (
            BPGHS_PAPER,
            "A, D, B, and C lie on a circle, center O. AP is a tangent to the circle at A and BP is a tangent to the circle at B. \\angle AOB = 142^\\circ \\text{ and } \\angle DAP = 42^\\circ. \\text{ (a) Find the value of } (i) \\angle ACB, (ii) \\angle ADB. \\text{ (b) Is OB parallel to AD? Explain.}",
        ),
        "bpghs_21": (
            BPGHS_PAPER,
            "The admission tickets to the Singapore Zoo are \\$50 \\text{ for an adult}, \\$36 \\text{ for a child, and } \\$20 \\text{ for a senior citizen. On a particular Tuesday, there were 212 adults, 251 children, and 15 senior citizens who visited the Singapore Zoo and on a particular Wednesday, there were 231 adults, 266 children, and 12 senior citizens who visited the Singapore Zoo. The number of visitors on the particular Tuesday and Wednesday can be represented by the matrix V = \\begin{pmatrix} 212 & 251 & 15 \\\\ 231 & 266 & 12 \\end{pmatrix}. (i) Write a 3 \\times 1 matrix, P, to represent the price of the admission tickets. (ii) Find the matrix T = VP. (iii) Explain what each of the elements represents. (iv) Find the total amount collected from the sales of the tickets for the 2 days.",
        ),
        "bpghs_24": (
            BPGHS_PAPER,
            "The angle of elevation of the base of a lighthouse, L, from two fishing boats P and Q are 20^\\circ \\text{ and } 35^\\circ \\text{ respectively. Given that the fishing boat P is 250 m from the lighthouse, find the distance between the two fishing boats.}",
        ),
    }
    for question_filename, (pdf_url, search_text) in search_text_dict.items():
        success = find_and_crop_image(pdf_url, search_text, question_filename)
