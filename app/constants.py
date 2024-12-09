TEMP_DIR = "temp"
OUTPUT_DIR = "output"

SYSTEM_PROMPT_EVALUATE_STEP_BY_STEP = """You are a mathematical reasoning validation system. Given input containing:
- A question in <question> tags
- Step-by-step workings to arrive at the final answer in <step_{i}> tags  
- A suggested answer in <suggested_answer> tags

Instructions:
1. Analyse the question to understand what is being asked
2. For each step in the workings:
   - Verify if the mathematical operation/logic used is valid for this type of problem
   - Check if the calculations in the step are correct
   - Confirm if the step logically follows from previous steps
3. Determine if the final answer is correctly calculated and formatted:
   - Even if some steps are incorrect, mark the answer as correct if the final answer is right
   - Even if all steps are correct, mark the answer as incorrect if the final answer is wrong

Return a JSON response with:
{
  "question_type": string,  // Description of the type of problem
  "is_correct": boolean,
  "step_validations": [
        {
          "step_number": integer,
          "is_valid": boolean,
          "explanation": string // Explanation of why the step is correct/incorrect
        }
      ],
    "conclusion": string // Final explanation of why answer is correct/incorrect
  }
}"""


SYSTEM_PROMPT_EVALUATE = """Given input containing:
- A question in <question> tags
- A suggested answer in <suggested_answer> tags

Instructions:
1. Analyse the question to understand what is being asked
2. Evaluate, with mathematical reasoning, if the suggested answer is correct

Return a JSON response with two fields:
- "reason": string explaining why you determined the answer is correct or incorrect
- "is_correct": boolean (true if the suggested answer is correct)"""

SYSTEM_PROMPT_GENERATE_QUESTIONS_PLAIN_TEXT = """Given input containing:
- Multiple images, where each image displays a mathematical problem
- Topic in <topic> tags
- Sub-topic in <sub_topic> tags

Instructions:
1. Generate one similar but distinct question that:
- Retains the same topic and sub-topic focus
- Is similar in difficulty and complexity level
- Uses plain text, not LaTeX
2. Introduce diversity by:
- Using varied contexts or scenarios while keeping the mathematical principles intact
- Exploring slightly different representations or formats for the same type of problem (e.g., equations vs. word problems)

Return a JSON response with:
{
"question_text": "Full question text",
"topic": "Mathematical topic",
"sub_topic": "Specific sub-topic",
"steps": [
"Step 1: Description and calculation",
"Step 2: Description and calculation",
],
"answer": "Final numerical or algebraic answer in plain text. The format should be 'Answer: <answer>'"
}"""

SYSTEM_PROMPT_GENERATE_QUESTIONS = """Given input containing:
- Multiple images, where each image displays a mathematical problem
- Topic in <topic> tags
- Sub-topic in <sub_topic> tags

Instructions:
1. Generate one similar but distinct question that:
- Retains the same topic and sub-topic focus
- Is similar in difficulty and complexity level
- Uses LaTeX formatting for mathematical expressions
2. Introduce diversity by:
- Using varied contexts or scenarios while keeping the mathematical principles intact
- Exploring slightly different representations or formats for the same type of problem (e.g., equations vs. word problems)

Return a JSON response with:
{
"question_text": "Full question text",
"topic": "Mathematical topic",
"sub_topic": "Specific sub-topic",
"steps": [
"Step 1: Description and calculation",
"Step 2: Description and calculation",
],
"answer": "Final numerical or algebraic answer. The format should be 'Answer: <answer>'"
}"""

SYSTEM_PROMPT_GENERATE_PYTHON_SCRIPT = """Given input containing:
- A question in <question> tags
- A suggested answer in <suggested_answer> tags

Generate a Python script that can solve the question. The script should:
- Be written in Python 3
- Declare all variables and constants globally
- Include all necessary imports and libraries
- Include all necessary functions and variables
- Include step-by-step code to solve the question
- Output the final answer in the format of the suggested answer found in <suggested_answer> tags
- The python script must contain a function named 'solve_problem' that returns the final answer
- Note: symbols CANNOT be converted into integers

Example Python script structure:
```python
# Imports
import numpy as np
import math
import sympy as sp

# Solution implementation
def solve_problem():
    # Solution steps
    # Error handling
    # Format output
    # Return final answer
```"""


SYSTEM_PROMPT_DEBUG = """Given input containing:
- A question in <question> tags
- A suggested answer in <suggested_answer> tags
- The previously generated Python script in <script> tags
- The error message/traceback from attempting to run the script in <error> tags

Debug and correct the Python script. The corrected script should:
- Address the specific error(s) identified in the error message
- Maintain all original requirements:
  - Be written in Python 3
  - Declare all variables and constants globally
  - Include all necessary imports and libraries
  - Include all necessary functions and variables
  - Include step-by-step code to solve the question
  - Output the final answer in the format of the suggested answer found in <suggested_answer> tags
  - Contain a function named 'solve_problem' that returns the final answer
  - Not convert symbols into integers
- Preserve the original solution approach where possible
- Include comments explaining the fixes made

Output the following in JSON format:
- "python_script": The corrected Python script
- "final_answer": The final answer obtained from the corrected script
- "is_suggested_answer_correct": A boolean indicating if the suggested answer is correct
- "reason": A brief explanation of the fixes made and why they resolve the error
- "changes_made": List of specific changes made to fix the script

Example correction process:
1. Analyse the error message
2. Identify the problematic code section
3. Apply appropriate fixes while maintaining requirements
4. Test the corrected solution
5. Document changes and reasoning"""

SYSTEM_PROMPT_FORMAT_PYTHON_SCRIPT_OUTPUT = """Given input containing:
- A question in <question> tags
- A suggested answer in <suggested_answer> tags
- The previously generated Python script in <script> tags
- The computed answer from the script in <computed_answer> tags

Generate an updated Python script that matches the format of the suggested answer while preserving the original calculations. The updated script should:

1. Analyse Format Differences:
   - Compare the structure and presentation of computed_answer vs suggested_answer
   - Identify differences in:
     * Number formatting (decimal places, thousand separators)
     * Unit representation
     * Text case and spacing
     * Symbol usage and placement
     * Array/list formatting
     * Mathematical expression formatting

2. Preserve Core Logic:
   - Maintain all mathematical calculations from the original script
   - Keep the core problem-solving approach intact
   - Preserve accuracy of numerical results

3. Format Matching Requirements:
   - Add format conversion functions/steps after core calculations
   - Match exact spacing and delimiters
   - Match exact symbol usage and placement
   - Match exact number formatting (decimals, scientific notation)
   - Match exact text case and punctuation
   - Match exact list/array representation
   - Match any special characters or mathematical notation

4. Maintain Original Requirements:
   - Be written in Python 3
   - Declare all variables globally
   - Include all necessary imports
   - Include a solve_problem() function
   - Include clear comments

Output the following in JSON format:
- "python_script": The format-matched Python script
- "format_changes": List of format adjustments made

Example format matching process:
1. Extract format pattern from suggested answer
2. Identify format differences in computed answer
3. Add formatting logic while preserving calculations
4. Verify exact format match
5. Document format changes applied"""

EMATH_TOPICS = {
    "Numbers and their operations": [
        "Classifying numbers",
        "Solving a problem involving negative numbers",
        "Finding the prime factors of a composite number",
        "Finding the highest common factor of 2 numbers",
        "Finding the highest common factor of 3 numbers",
        "Finding the lowest common factor of 2 numbers",
        "Finding the lowest common factor of 3 numbers",
        "Evaluating the square root of a number",
        "Solving a problem involving a perfect square",
        "Evaluating the cube root of a number",
        "Solving a problem involving a perfect cube",
        "Solving a problem involving a cube root",
        "Reciprocals",
        "Rounding a whole number to a specified number of significant figures",
        "Rounding a decimal to a specified number of significant figures",
        "Estimating the answer to a calculation",
        "Performing calculations involving prefixes",
        "Performing calculations involving standard form",
        "Applying the laws of indices",
        "Simplifying expressions involving indices",
    ],
    "Ratio and proportion": [
        "Simplifying ratios involving 2 quantities",
        "Finding the ratio involving 2 quantities",
        "Finding the ratio involving 3 quantities",
        "Finding the actual distance and actual area",
        "Finding the linear scale of a map",
        "Applying direct proportion",
        "Finding an equation when y is directly proportional to x",
        "Finding an equation when y is directly proportional to square root of x",
        "Applying inverse proportion",
        "Finding an equation when y is inversely proportional to x",
        "Finding an equation when cube of x is inversely proportional to y",
    ],
    "Percentage": [
        "Converting between fractions or decimals and percentages",
        "Finding the value, given the percentage",
        "Comparing 2 quantities by percentage",
        "Increasing or decreasing a quantity by a given percentage",
        "Finding the original value using reverse percentages",
        "Applying percentage in real-world contexts",
    ],
    "Rate and speed": [
        "Applying rates in real-world contexts",
        "Converting from km/h to m/s",
        "Finding the distance between 2 points",
        "Finding the average speed",
    ],
    "Algebraic expressions and formulae": [
        "Simplifying an algebraic expression",
        "Evaluating an algebraic formula",
        "Finding the nth term of a sequence with a common difference",
        "Finding the nth term of a sequence involving perfect square",
        "Finding the nth term of a sequence with a common ratio",
        "Solving a problem on number patterns",
        "Finding the product of 2 algebraic expressions",
        "Using algebraic identities in algebraic expansion",
        "Using algebraic identities to evaluate a perfect square",
        "Factorising an algebraic expression by extracting common factors",
        "Factorising an algebraic expression by grouping",
        "Factorising an algebraic expression using algebraic identities",
        "Factorising an algebraic expression using the multiplication frame",
        "Adding and subtracting algebraic fractions",
        "Multiplying and dividing algebraic fractions",
        "Changing the subject of a formula",
    ],
    "Functions and graphs": [
        "Sketching the graph of y=mx+c",
        "Sketching the graph of y=ax2+bx+c",
        "Sketching the graph of y=(x-p)(x-q)",
        "Sketching the graph of y=-(x-h)2+k",
        "Graphs of cubic functions",
        "Graphs of functions in the form a/x and a/x2",
        "Graphs of exponential functions",
        "Finding the solutions of an equation graphically",
        "Estimating the gradient of a curve",
    ],
    "Equations and inequalities": [
        "Solving linear equations",
        "Solving simple fractional equations that can be reduced to linear equations",
        "Solving simultaneous equations using the method of elimination",
        "Solving simultaneous equations using the method of substitution",
        "Solving simultaneous equations using the graphical method",
        "Solving quadratic equations by factorisation",
        "Solving quadratic equations by quadratic formula",
        "Solving quadratic equations by completing the square",
        "Solving quadratic equations using the graphical method",
        "Solving fractional equations that can be reduced to quadratic equations",
        "Applying quadratic equations in real-world contexts",
        "Solving a linear inequality and illustrating the solution on a number line",
        "Solving a linear inequality",
        "Finding the largest and smallest values of an expression",
    ],
    "Set language and notation": [
        "Listing the elements of a set",
        "Determining whether 2 sets are equal",
        "Listing the subsets and proper subsets",
        "Complement sets",
        "Intersection of 2 sets",
        "Shading Venn diagrams, given the set notations",
        "Listing the elements of the intersection and union of 2 sets",
        "Drawing a Venn diagram",
    ],
    "Matrices": [
        "Displaying information in a matrix",
        "Row matrix",
        "Column matrix",
        "Square matrix",
        "Zero or null matrix",
        "Addition and subtraction of matrices",
        "Scalar multiplication of matrices",
        "Multiplication of 2 matrices",
    ],
    "Problems in real-world contexts": [
        "Calculating simple interest",
        "Calculating compound interest",
        "Comparing simple interest and compound interest",
        "Calculating income tax",
        "Calculating utilities bill",
        "Calculating hire-purchase price",
        "Calculating the percentage profit",
        "Calculating the cost price if a loss is made",
        "Calculating money exchange",
        "Interpreting a distance-time graph",
        "Interpreting a speed-time graph",
        "Interpreting other types of graphs",
        "Sketching a water level-time graph",
    ],
    "Angles, triangles and polygons": [
        "Types of angles",
        "Complementary and supplementary angles",
        "Finding an unknown angle involving angles at a point",
        "Finding an unknown angle involving parallel lines",
        "Finding unknown angles in triangles",
        "Finding unknown angles in a parallelogram",
        "Finding unknown angles in a rhombus",
        "Finding unknown angles in a trapezium",
        "Finding unknown angles in a kite",
        "Finding the interior and exterior angles of a regular polygon",
        "Finding the number of sides of a polygon",
        "Solving a problem involving a polygon",
        "Constructing a quadrilateral, a perpendicular bisector, and an angle bisector",
    ],
    "Congruence and similarity": [
        "Proving the 2 triangles are congruent",
        "Solving a pair of congruent triangles",
        "Determining if 2 triangles are similar",
        "Solving a pair of similar triangles",
        "Finding the scale factor of an enlargement",
        "Finding the ratio of the areas of 2 similar triangles",
        "Solving a problem involving triangles",
        "Finding the ratio of the lengths of 2 similar solids",
        "Finding the mass of a similar solid",
        "Finding the ratio of 2 triangles with the same height",
    ],
    "Properties of circles": [
        "Applying the symmetric properties of circles",
        "Applying the angles properties of circles",
    ],
    "Pythagoras’ theorem and trigonometry": [
        "Using Pythagoras’ theorem to find the length of an unknown side",
        "Determining if a triangle is right-angled",
        "Finding an unknown side in a right-angled triangle",
        "Finding the trigonometric ratios of acute and obtuse angles",
        "Solving simple trigonometric equations",
        "Finding the area of a triangle",
        "Using the Sine rule to find an unknown side",
        "Using the Cosine rule to find an unknown side",
        "Applying the Sine and Cosine rule",
        "Finding the distance, given the angle of depression",
        "Stating the bearing of a point",
        "Applying bearings in real-world contexts",
        "Solving a 3-dimensional problem",
    ],
    "Mensuration": [
        "Conversion of units",
        "Converting between degrees and radians",
        "Finding the height of a trapezium",
        "Finding the arc length and area of a sector",
        "Finding the total surface area of a cone",
        "Finding the volume of a sphere",
        "Finding the volume and total surface area of a composite solid",
    ],
    "Coordinate geometry": [
        "Finding the gradient of a line",
        "Finding the length of a line segment",
        "Finding the equation of a straight line",
        "Showing that 2 lines are perpendicular to each other",
    ],
    "Vectors in 2 dimensions": [
        "Vector notations",
        "Finding the magnitude of a vector",
        "Equal vectors",
        "Finding the scalar multiple of a vector",
        "Finding parallel vectors",
        "Proving that 3 points lie in a straight line",
        "Zero vector",
        "Sum or difference of 2 vectors",
        "Relating coordinates to position vectors",
        "Solving a geometric problem involving vectors",
        "Using vectors to find the ratio of the areas of triangles",
    ],
    "Data analysis": [
        "Reading a bar graph and drawing a pictogram",
        "Reading a pie chart",
        "Reading a line graph",
        "Drawing a dot diagram",
        "Drawing a stem-and-leaf diagram",
        "Drawing a stem-and-leaf diagram with split stems",
        "Drawing a back-to-back stem-and-leaf diagram",
        "Drawing a histogram",
        "Finding the mean, median and mode",
        "Interpreting a cumulative frequency curve",
        "Reading a box-and-whisker plot",
        "Finding the mean and standard deviation",
        "Finding the mean and standard deviation using mid-values",
    ],
    "Probability": [
        "Finding the sample space",
        "Finding the probability of single events",
        "Finding the probability involving mutually exclusive events",
        "Finding the probability involving independent events",
        "Finding the probability involving dependent events",
        "Using a possibility diagram",
        "Using a tree diagram",
    ],
}

AMATH_TOPICS = {
    "Quadratic Functions, Equations and Inequalities": [
        "Solving simultaneous equations by substitution",
        "Finding coordinates of intersection points",
        "Finding maximum and minimum value of a quadratic function by completing the square",
        "Sketching graph of quadratic function",
        "Solving quadratic inequalities",
        "Intersection of straight line and curve",
        "Always positive/negative quadratic expression",
        "Quadratic functions in real-world context",
    ],
    "Surds": [
        "Rationalising denominator of surd",
        "Adding and/or subtracting surds",
        "Solving equations involving surds",
        "Word problems involving surds",
    ],
    "Polynomials, cubic equations and partial fractions": [
        "Identities",
        "Identities with an unknown quotient",
        "Long division/synthetic method/remainder theorem",
        "Application of remainder theorem",
        "Sum and difference of 2 cubes",
        "Solving cubic equation",
        "Factor theorem and solving a cubic equation",
        "Factor theorem and sketching of cubic curve",
        "Forming cubic equation/expression",
        "Proper algebraic fraction with linear factors in denominator",
        "Proper algebraic fraction with non-linear factor in denominator",
        "Proper algebraic fraction with repeated factors in the denominator",
        "Improper algebraic fraction",
    ],
    "Binomial theorem and its application": [
        "Finding coefficients of specific terms",
        "Finding values of unknown coefficients",
        "Application of factorial",
        "Application of general term formula",
        "Applications of binomial theorem",
    ],
    "Exponential and logarithmic functions": [
        "Simplifying exponential expressions",
        "Solving exponential equations",
        "Simplifying logarithmic expressions",
        "Applications of laws of logarithms",
        "Solving equations involving natural logarithms",
        "Solving simultaneous equations involving logarithms",
        "Application of change of base",
        "Real-life applications of logarithms",
        "Graphs of exponential and logarithmic functions",
        "Graphical solutions involving exponential/logarithmic graphs",
    ],
    "Coordinate geometry": [
        "Finding equation of perpendicular bisector",
        "Finding fourth vertex of parallelogram",
        "Finding coordinates of unknown collinear point",
        "Finding equation of circle and determining if a point lies on, is inside, or outside a circle",
        "Application of tangent in circle",
    ],
    "Linear law": [
        "Converting from linear form to non-linear equation",
        "Finding values of unknown constants when given non-linear graph",
        "Application of linear law in real-world contexts",
    ],
    "Trigonometric functions and equations": [
        "Finding trigonometric ratios",
        "Solving trigonometric equations in degree mode",
        "Solving trigonometric equations in radian mode",
        "Finding principal values of inverse trigonometric functions",
        "Sketching trigonometric graphs",
        "Finding angle in a right-angled triangle",
        "Real-life modeling using trigonometric function",
    ],
    "Trigonometric identities and formulae": [
        "Finding trigonometric ratios",
        "Solving trigonometric equations using basic trigonometric identity",
        "Solving trigonometric equations using compound angle formulae",
        "Proving trigonometric identities",
        "Evaluating trigonometric ratios using compound angle formulae",
        "Finding exact values of trigonometric ratios of specific angles",
        "R-formula",
        "Application of R-formula in word problems",
    ],
    "Gradients, derivatives and differentiation techniques": [
        "Basic differentiation",
        "Product rule",
        "Quotient rule",
        "Finding gradient of curve at a point",
        "Increasing and decreasing functions",
        "Higher derivatives",
    ],
    "Applications of differentiation": [
        "Applications of differentiation to tangents and normals",
        "Rate of change",
        "Stationary point",
        "Stationary value involving 3 variables",
        "Problem on maxima and minima",
    ],
    "Differentiation of trigonometric, logarithmic, and exponential functions and their applications": [
        "Differentiation of trigonometric functions",
        "Differentiation of logarithmic functions",
        "Differentiation of exponential functions",
        "Applications of differentiation of trigonometric functions",
        "Applications of differentiation of exponential functions",
        "Applications of differentiation of logarithmic functions",
    ],
    "Integration": [
        "Basic integration",
        "Integration of trigonometric functions",
        "Integration of trigonometric functions using trigonometric formulae",
        "Integration of functions in the form of 1/(ax+b)",
        "Integration of exponential functions",
        "Integration involving partial fractions",
        "Finding equation of curve",
        "Integration as a reverse process of differentiation",
        "Integration as a reverse process of differentiation involving multiple functions",
    ],
    "Applications of integration": [
        "Definite integrals involving algebraic functions",
        "Definite integrals involving trigonometric functions",
        "Properties of definite integrals",
        "Integration as a reverse process of differentiation",
        "Integration as a reverse process of differentiation involving multiple functions",
        "Area under curve",
        "Area above and below x-axis",
        "Area bounded by curve, y-axis, and line",
        "Area bounded by curve and line",
        "Applications of tangent and normal to shaded area",
    ],
    "Kinematics": [
        "Applications of differentiation, given displacement",
        "Application of differentiation and integration, given velocity",
        "Application of integration, given acceleration",
        "Problem involving 2 moving particles",
    ],
    "Proofs in plane geometry": [
        "Proof involving congruent and similar triangles",
        "Midpoint theorem",
        "Tangent-chord theorem",
    ],
}

SUBJECT_MAPPING = {
    "elementary_mathematics": EMATH_TOPICS,
    "additional_mathematics": AMATH_TOPICS,
}

RETRIEVED_DOCUMENTS_FOR_SUB_TOPIC = {
    "Multiplication of 2 matrices": [
        {
            "topic": "Matrices",
            "sub_topic": "Multiplication of 2 matrices",
            "question_part": "20b",
            "subject": "elementary_mathematics",
            "paper_number": "1",
            "level": "o_level",
            "exam_type": "preliminary_exam",
            "year": 2024,
            "school": "outram_secondary_school",
            "question_url": "https://document.grail.moe/23757c9d5f564d039af65942e5e4fc9e.pdf#page=17",
            "image_filepath": "temp/outram_secondary_school_elementary_mathematics_preliminary_exam_2024_1_20b.png",
            "question_body": "(b) Evaluate the matrix \\( T = PM \\).",
        },
        {
            "topic": "Matrices",
            "sub_topic": "Multiplication of 2 matrices",
            "question_part": "4e(i)",
            "subject": "elementary_mathematics",
            "paper_number": "2",
            "level": "o_level",
            "exam_type": "preliminary_exam",
            "year": 2023,
            "school": "xinmin_secondary_school",
            "question_url": "https://document.grail.moe/7bf8c34303d54a78a503b712125baf2a.pdf#page=7",
            "image_filepath": "temp/xinmin_secondary_school_elementary_mathematics_preliminary_exam_2023_2_4e(i).png",
            "question_body": "On a particular week, supermarket A was offering a store-wide 20% discount promotion while supermarket B was offering a store-wide 10% discount promotion. Write down a matrix P, such that the product of P and T would give the discounted prices which Ron and Zoe each has to pay if they purchase the items from supermarkets A and B respectively.",
        },
        {
            "topic": "Matrices",
            "sub_topic": "Multiplication of 2 matrices",
            "question_part": "4e(ii)",
            "subject": "elementary_mathematics",
            "paper_number": "2",
            "level": "o_level",
            "exam_type": "preliminary_exam",
            "year": 2023,
            "school": "xinmin_secondary_school",
            "question_url": "https://document.grail.moe/7bf8c34303d54a78a503b712125baf2a.pdf#page=7",
            "image_filepath": "temp/xinmin_secondary_school_elementary_mathematics_preliminary_exam_2023_2_4e(ii).png",
            "question_body": "Hence, using the value of x found in (d), find the product of the matrices P and T.",
        },
    ],
    "Finding the mean median and mode": [
        {
            "topic": "Data analysis",
            "sub_topic": "Finding the mean, median and mode",
            "question_part": "3",
            "subject": "elementary_mathematics",
            "paper_number": "1",
            "level": "o_level",
            "exam_type": "preliminary_exam",
            "year": 2024,
            "school": "fairfield_methodist_school_secondary",
            "question_url": "https://document.grail.moe/30fd5c6dcfdc4ab8ab395c1806733768.pdf#page=3",
            "image_filepath": "temp/fairfield_methodist_school_secondary_elementary_mathematics_preliminary_exam_2024_1_3.png",
            "question_body": "Tristen has written five positive integers. The median of these numbers is 8, the mode is 7 and the mean is 13. The range of these numbers is 21. Find the five numbers.",
        },
        {
            "topic": "Data analysis",
            "sub_topic": "Finding the mean, median and mode",
            "question_part": "5e(ii)",
            "subject": "elementary_mathematics",
            "paper_number": "2",
            "level": "o_level",
            "exam_type": "preliminary_exam",
            "year": 2023,
            "school": "xinmin_secondary_school",
            "question_url": "https://document.grail.moe/7bf8c34303d54a78a503b712125baf2a.pdf#page=10",
            "image_filepath": "temp/xinmin_secondary_school_elementary_mathematics_preliminary_exam_2023_2_5e(ii).png",
            "question_body": "Calculate an estimate of the mean speed.",
        },
        {
            "topic": "Data analysis",
            "sub_topic": "Finding the mean, median and mode",
            "question_part": "3b",
            "subject": "elementary_mathematics",
            "paper_number": "1",
            "level": "o_level",
            "exam_type": "preliminary_exam",
            "year": 2023,
            "school": "bukit_panjang_government_high_school",
            "question_url": "https://document.grail.moe/b06fe71b3f3c4f5db97844c79c7a12c1.pdf#page=4",
            "image_filepath": "temp/bukit_panjang_government_high_school_elementary_mathematics_preliminary_exam_2023_1_3b.png",
            "question_body": "(b) Find the mean amount of rain per day.",
        },
    ],
    "Applying the angles properties of circles": [
        {
            "topic": "Properties of circles",
            "sub_topic": "Applying the angles properties of circles",
            "question_part": "20",
            "subject": "elementary_mathematics",
            "paper_number": "1",
            "level": "o_level",
            "exam_type": "preliminary_exam",
            "year": 2023,
            "school": "bukit_panjang_government_high_school",
            "question_url": "https://document.grail.moe/b06fe71b3f3c4f5db97844c79c7a12c1.pdf#page=17",
            "image_filepath": "temp/bukit_panjang_government_high_school_elementary_mathematics_preliminary_exam_2023_1_20.png",
            "question_body": "A, D, B, and C lie on a circle, center O. AP is a tangent to the circle at A and BP is a tangent to the circle at B. \\angle AOB = 142^\\circ \\text{ and } \\angle DAP = 42^\\circ. \\text{ (a) Find the value of (i) } \\angle ACB, \\text{ (ii) } \\angle ADB. \\text{ (b) Is OB parallel to AD? Explain.}",
        },
        {
            "topic": "Properties of circles",
            "sub_topic": "Applying the angles properties of circles",
            "question_part": "19a(i)",
            "subject": "elementary_mathematics",
            "paper_number": "1",
            "level": "o_level",
            "exam_type": "preliminary_exam",
            "year": 2024,
            "school": "fairfield_methodist_school_secondary",
            "question_url": "https://document.grail.moe/30fd5c6dcfdc4ab8ab395c1806733768.pdf#page=16",
            "image_filepath": "temp/fairfield_methodist_school_secondary_elementary_mathematics_preliminary_exam_2024_1_19a(i).png",
            "question_body": "A, B, C \\text{ and } D \\text{ lie on a circle with centre } O \\text{ and radius } 5 \\text{ cm. } \\angle AOB = 1.8 \\text{ radians. }",
        },
        {
            "topic": "Properties of circles",
            "sub_topic": "Applying the angles properties of circles",
            "question_part": "19a(i)",
            "subject": "elementary_mathematics",
            "paper_number": "1",
            "level": "o_level",
            "exam_type": "preliminary_exam",
            "year": 2024,
            "school": "fairfield_methodist_school_secondary",
            "question_url": "https://document.grail.moe/30fd5c6dcfdc4ab8ab395c1806733768.pdf#page=16",
            "image_filepath": "temp/fairfield_methodist_school_secondary_elementary_mathematics_preliminary_exam_2024_1_19a(i).png",
            "question_body": "\\text{Write down an expression, in terms of } \\pi, \\text{ for the reflex angle } AOB.",
        },
    ],
    "Applying rates in real-world contexts": [
        {
            "topic": "Rate and speed",
            "sub_topic": "Applying rates in real-world contexts",
            "question_part": "26b",
            "subject": "elementary_mathematics",
            "paper_number": "1",
            "level": "o_level",
            "exam_type": "preliminary_exam",
            "year": 2024,
            "school": "fairfield_methodist_school_secondary",
            "question_url": "https://document.grail.moe/30fd5c6dcfdc4ab8ab395c1806733768.pdf#page=23",
            "image_filepath": "temp/fairfield_methodist_school_secondary_elementary_mathematics_preliminary_exam_2024_1_26b.png",
            "question_body": "(b) Find the distance travelled in the first 10 seconds.",
        },
        {
            "topic": "Rate and speed",
            "sub_topic": "Applying rates in real-world contexts",
            "question_part": "26d",
            "subject": "elementary_mathematics",
            "paper_number": "1",
            "level": "o_level",
            "exam_type": "preliminary_exam",
            "year": 2024,
            "school": "fairfield_methodist_school_secondary",
            "question_url": "https://document.grail.moe/30fd5c6dcfdc4ab8ab395c1806733768.pdf#page=23",
            "image_filepath": "temp/fairfield_methodist_school_secondary_elementary_mathematics_preliminary_exam_2024_1_26d.png",
            "question_body": "(d) On the axes in the answer space, sketch the distance-time graph for the first k seconds of the motion of the object.",
        },
        {
            "topic": "Rate and speed",
            "sub_topic": "Applying rates in real-world contexts",
            "question_part": "2b",
            "subject": "elementary_mathematics",
            "paper_number": "2",
            "level": "o_level",
            "exam_type": "preliminary_exam",
            "year": 2024,
            "school": "tampines_secondary_school",
            "question_url": "https://document.grail.moe/23657f63a22a41ef8633c5e0e744e76a.pdf#page=5",
            "image_filepath": "temp/tampines_secondary_school_elementary_mathematics_preliminary_exam_2024_2_2b.png",
            "question_body": "Jane exchanged 500 Singapore dollars ($) into Thai baht (THB) when the exchange rate was $1 = 26.77 THB. She travelled to Thailand and spent 10,600 THB. On her return to Singapore, she exchanged the remaining Thai baht into dollars with the exchange rate $1 = 26.88 THB. Calculate the amount she received in dollars. Correct your answer to the nearest cent.",
        },
    ],
    "Finding the probability of single events": [
        {
            "topic": "Probability",
            "sub_topic": "Finding the probability of single events",
            "question_part": "24i",
            "subject": "elementary_mathematics",
            "paper_number": "1",
            "level": "o_level",
            "exam_type": "preliminary_exam",
            "year": 2024,
            "school": "fairfield_methodist_school_secondary",
            "question_url": "https://document.grail.moe/30fd5c6dcfdc4ab8ab395c1806733768.pdf#page=21",
            "image_filepath": "temp/fairfield_methodist_school_secondary_elementary_mathematics_preliminary_exam_2024_1_24i.png",
            "question_body": "There are 30 blue balls, 20 green balls and 14 yellow balls in a bag. A ball is chosen at random from the bag and then replaced. (i) Find the probability of not picking a green ball, express your answer to the lowest term.",
        },
        {
            "topic": "Probability",
            "sub_topic": "Finding the probability of single events",
            "question_part": "5a",
            "subject": "elementary_mathematics",
            "paper_number": "1",
            "level": "o_level",
            "exam_type": "preliminary_exam",
            "year": 2023,
            "school": "bukit_panjang_government_high_school",
            "question_url": "https://document.grail.moe/b06fe71b3f3c4f5db97844c79c7a12c1.pdf#page=6",
            "image_filepath": "temp/bukit_panjang_government_high_school_elementary_mathematics_preliminary_exam_2023_1_5a.png",
            "question_body": "A drawer contains 40 balls. 15 balls are black, 5 balls are grey and 20 balls are white. Samuel chooses one ball from the drawer at random. (a) Find the probability that the ball is not black.",
        },
        {
            "topic": "Probability",
            "sub_topic": "Finding the probability of single events",
            "question_part": "3c",
            "subject": "elementary_mathematics",
            "paper_number": "1",
            "level": "o_level",
            "exam_type": "preliminary_exam",
            "year": 2023,
            "school": "bukit_panjang_government_high_school",
            "question_url": "https://document.grail.moe/b06fe71b3f3c4f5db97844c79c7a12c1.pdf#page=4",
            "image_filepath": "temp/bukit_panjang_government_high_school_elementary_mathematics_preliminary_exam_2023_1_3c.png",
            "question_body": "(c) Ethan picks one of these days at random. Find the probability that, on that day, the amount of rain was 3 mm or more.",
        },
    ],
    "Solving simultaneous equations using the method of elimination": [
        {
            "topic": "Equations and inequalities",
            "sub_topic": "Solving simultaneous equations using the method of elimination",
            "question_part": "1c",
            "subject": "elementary_mathematics",
            "paper_number": "2",
            "level": "o_level",
            "exam_type": "preliminary_exam",
            "year": 2024,
            "school": "tampines_secondary_school",
            "question_url": "https://document.grail.moe/23657f63a22a41ef8633c5e0e744e76a.pdf#page=4",
            "image_filepath": "temp/tampines_secondary_school_elementary_mathematics_preliminary_exam_2024_2_1c.png",
            "question_body": "Solve the simultaneous equations: \\( 4x + 7y = 23 \\) and \\( 6x - 2y = 3 \\).",
        },
        {
            "topic": "Equations and inequalities",
            "sub_topic": "Solving simultaneous equations using the method of elimination",
            "question_part": "6",
            "subject": "elementary_mathematics",
            "paper_number": "1",
            "level": "o_level",
            "exam_type": "preliminary_exam",
            "year": 2023,
            "school": "bukit_panjang_government_high_school",
            "question_url": "https://document.grail.moe/b06fe71b3f3c4f5db97844c79c7a12c1.pdf#page=7",
            "image_filepath": "temp/bukit_panjang_government_high_school_elementary_mathematics_preliminary_exam_2023_1_6.png",
            "question_body": "Solve the simultaneous equations: \\( 7x + 2y = 8 \\) and \\( 3x - y = 3 \\).",
        },
        {
            "topic": "Equations and inequalities",
            "sub_topic": "Solving simultaneous equations using the method of elimination",
            "question_part": "14b",
            "subject": "elementary_mathematics",
            "paper_number": "1",
            "level": "o_level",
            "exam_type": "preliminary_exam",
            "year": 2024,
            "school": "fairfield_methodist_school_secondary",
            "question_url": "https://document.grail.moe/30fd5c6dcfdc4ab8ab395c1806733768.pdf#page=11",
            "image_filepath": "temp/fairfield_methodist_school_secondary_elementary_mathematics_preliminary_exam_2024_1_14b.png",
            "question_body": "(b) Solve the simultaneous equations and hence find the area of triangle ABC.",
        },
    ],
    "Evaluating an algebraic formula": [
        {
            "topic": "Algebraic expressions and formulae",
            "sub_topic": "Evaluating an algebraic formula",
            "question_part": "3d",
            "subject": "elementary_mathematics",
            "paper_number": "2",
            "level": "o_level",
            "exam_type": "preliminary_exam",
            "year": 2023,
            "school": "xinmin_secondary_school",
            "question_url": "https://document.grail.moe/7bf8c34303d54a78a503b712125baf2a.pdf#page=11",
            "image_filepath": "temp/xinmin_secondary_school_elementary_mathematics_preliminary_exam_2023_2_3d.png",
            "question_body": "(d) x = 5, 6, 7",
        },
        {
            "topic": "Algebraic expressions and formulae",
            "sub_topic": "Evaluating an algebraic formula",
            "question_part": "1bi",
            "subject": "elementary_mathematics",
            "paper_number": "2",
            "level": "o_level",
            "exam_type": "preliminary_exam",
            "year": 2024,
            "school": "tampines_secondary_school",
            "question_url": "https://document.grail.moe/23657f63a22a41ef8633c5e0e744e76a.pdf#page=3",
            "image_filepath": "temp/tampines_secondary_school_elementary_mathematics_preliminary_exam_2024_2_1bi.png",
            "question_body": "Given \\( a = 2bv + xk \\), find \\( x \\) when \\( a = 2 \\), \\( b = 3 \\), \\( v = -4 \\), and \\( k = 5 \\).",
        },
        {
            "topic": "Algebraic expressions and formulae",
            "sub_topic": "Evaluating an algebraic formula",
            "question_part": "23",
            "subject": "elementary_mathematics",
            "paper_number": "1",
            "level": "o_level",
            "exam_type": "preliminary_exam",
            "year": 2023,
            "school": "bukit_panjang_government_high_school",
            "question_url": "https://document.grail.moe/b06fe71b3f3c4f5db97844c79c7a12c1.pdf#page=19",
            "image_filepath": "temp/bukit_panjang_government_high_school_elementary_mathematics_preliminary_exam_2023_1_23.png",
            "question_body": "Given that 2^{32} \\times 1 = 6 \\times 8^x, \\text{ find the value of } x.",
        },
    ],
}
