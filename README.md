# Course Planner

**A Linear Programming (LP) approach to selecting the optimal 10-course plan for the Georgia Tech MS in Computer Science**, focusing on two possible specializations (Interactive Intelligence and Computing Systems). This project combines **data gathering**, **operations research**, and **mathematical optimization** to create an end-to-end solution for picking courses that satisfy Georgia Tech’s official requirements while maximizing your personal preferences (ratings, difficulty, workload, etc.).

The goal is to show how **data science can model and solve real-world problems**, driving data-backed decisions. In this case, *What is the most optimal path of courses I should take?*

## Overview

In Georgia Tech’s MSCS, students must choose 10 courses and **one** specialization. Each specialization has specific rules on how many and which courses you must take. With this project, you can:

1. **Scrape live course data** (ratings, difficulty, workload, etc.) from [omscentral.com](https://www.omscentral.com/) using `src/get_ratings.js`.
2. **Define your personal preferences** (weights) for rating, difficulty, workload, number of reviews, and interest.
3. **Run a CBC solver via PuLP** (`src/main.py`) that:
    - Forces the solution to pick exactly 10 courses.
    - Ensures your chosen specialization’s constraints are satisfied.
    - Maximizes an objective function that captures your weighted preferences.

### Why This Project?

- **Real-world alignment**: Reflects actual Georgia Tech specialization constraints.
- **Demonstrates data gathering**: Showcases a small web-scraping approach for course data.
- **Demonstrates optimization**: Uses integer linear programming to handle constraints and find the best combination of courses.
- **Full pipeline**: Data → Model → Solve → Interpret results.

## Mathematical Approach

This project uses **mixed-integer programming (MIP)** to maximize the following utility function:

$$ U = \sum_{c \in \text{Courses}} \left( w_r R_c + w_d (5 - D_c) + w_w \frac{-W_c}{5} + w_n \log(1 + N_c) + w_i I_c \right) \cdot x_c $$

Where:

- $(U)$: Total utility to maximize.
- $(X_c)$: Decision variable for each course $( x_c \text{ in } \{0, 1\} )$, representing whether a course $(c)$ is selected.
- $(R_c, D_c, W_c, N_c, I_c)$: The course’s rating, difficulty, workload, number of reviews, and interest score.
- $(w_r, w_d, w_w, w_n, w_i)$: Weights for rating, difficulty, workload, number of reviews, and interest, respectively.

Subject to **constraints** that ensure:

- Exactly **10** courses chosen: $\sum_{c} x_c = 10$
- Exactly **one** specialization: $S_{\mathrm{II}} + S_{\mathrm{CS}} = 1$
- If $S_\mathrm{II} = 1$: Must satisfy the Interactive Intelligence sets.
- If $S_\mathrm{CS} = 1$: Must satisfy the Computing Systems sets.

## Project Structure

```bash
.
├── pyproject.toml         # Poetry config file
├── poetry.lock            # Poetry lock file
├── README.md              # This file
├── src
│   ├── main.py            # The main Python entry point
│   ├── get_ratings.js     # Script for scraping from OMSCentral
│   └── ratings.json       # Courses/Ratings from OMSCentral
└── ...
```

- **`pyproject.toml`** / **`poetry.lock`**: Manages dependencies (e.g., `pulp`) and ensures reproducible builds.
- **`src/main.py`**:
    - Contains the linear programming code (using PuLP).
    - Defines constraints for each specialization, sets up the objective function, runs the solver, prints the output.
- **`src/get_ratings.js`**:
    - A small JavaScript snippet to paste into the OMSCentral console to fetch course data.
    - Exports a JSON array you can store in `ratings.json`.

## Getting Started

1. **Clone This Repo**
    
    ```bash
    git clone https://github.com/ChosenQuill/course-planner.git
    cd course-planner
    ```
    
2. **Install Dependencies**
    
    ```bash
    poetry install
    ```
    
3. **Scrape Course Data**
    1. Go to [omscentral.com](https://www.omscentral.com/), open DevTools → Console.
    2. Paste the contents of `src/get_ratings.js`.
    3. Copy the JSON output and paste it into `src/ratings.json`.
4. **Adjust Weights & Constraints**
    - In `src/main.py`, tweak the `weight_rating`, `weight_difficulty`, etc., to reflect your priorities.
    - In `src/ratings.json`, adjust each course’s `interest` to match your personal preference.
    - Interactive Intelligence & Computing Systems constraints are coded, but you can add more if desired.
5. **Run**
    
    ```bash
    poetry run python src/main.py
    ```
    
    The solver will pick 10 courses that meet the chosen specialization’s rules and maximize your total “score.”
    

## Demo

**Example** solver output (your results may vary based on your weights or updated data):

```markdown
Solver status: Optimal
Objective (Max Score) = 821.47
Chosen Specialization: Interactive Intelligence
Courses to take (10 total):
  - Introduction to Graduate Algorithms
  - Artificial Intelligence
  - Deep Learning
  - ...
```

## Credits

- **Course Ratings & Data** from [OMSCentral](https://www.omscentral.com/)
- **Project Inspiration** from [Christopher Dieringer’s “Applied Simplex Method For Deciding Future Coursework”](https://cdaringe.com/applied-simplex-method-for-deciding-years-of-coursework/)
- **Solver**: PuLP for Python-based linear/integer programming
- Georgia Tech’s official Specialization Requirements

---

This project is for demonstration and educational purposes only. Please verify official course requirements with Georgia Tech.
