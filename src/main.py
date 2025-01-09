import pulp
from math import log
import json

# ============================
# WEIGHTS / IMPORTANCE FACTORS
# ============================
weight_rating     = 12.0  # rating is highly important
weight_difficulty = 4.0  # difficulty is somewhat important (we invert it so easier is better)
weight_workload   = 4.0  # moderate weight for workload (higher workload => negative score)
weight_numreviews = 6.0  # low weight for # of reviews
weight_interest   = 10.0 # personal interest is extremely important

# ============================
# LOAD COURSE DATA
# ============================

def load_json(fname):
    with open(fname) as f:
        return json.load(f)

courses_data = load_json("src/ratings.json")

# ============================
# BUILDING THE LP MODEL
# ============================
model = pulp.LpProblem("Course_Specialization_Choice", pulp.LpMaximize)

# 1) CREATE A BINARY VARIABLE x_c FOR EVERY COURSE
#    x_c = 1 if you TAKE the course; 0 otherwise
x_vars = {}
for c in courses_data:
    cname = c["codes"]  # e.g. "CS-6515"
    x_vars[cname] = pulp.LpVariable(f"x_{cname}", cat=pulp.LpBinary)

# 2) CREATE BINARY VARIABLES FOR THE SPECIALIZATIONS
#    Exactly ONE specialization must be chosen: Interactive Intelligence OR Computing Systems
S_II = pulp.LpVariable("S_II", cat=pulp.LpBinary)  # 1 => Interactive Intelligence
S_CS = pulp.LpVariable("S_CS", cat=pulp.LpBinary)  # 1 => Computing Systems

# Exactly ONE specialization
model += (S_II + S_CS == 1, "Pick_exactly_one_specialization")

# ============================
# SCORING FUNCTION
# ============================
def get_course_score(course):
    """
    Convert the raw data for a course into a single numeric utility score,
    based on rating, difficulty, workload, number of reviews, and interest.
    """
    rating_val     = weight_rating * (course["rating"])         # out of 5
    difficulty_val = weight_difficulty * (5.0 - course["difficulty"])
    # Scale workload to avoid overshadowing. For example, /5 to dampen effect:
    workload_val   = weight_workload * (-(course["workload"]) / 5.0)
    # Take log of (1 + numReviews) to keep big numbers from dominating:
    reviews_val    = weight_numreviews * log(1.0 + course["numReviews"])
    interest_val   = weight_interest * (course["interest"])
    
    return rating_val + difficulty_val + workload_val + reviews_val + interest_val

# BUILD THE OBJECTIVE (SUM OF WEIGHTED SCORES * x_c FOR ALL COURSES)
total_score_expr = []
for course in courses_data:
    cname = course["codes"]
    score = get_course_score(course)
    total_score_expr.append(score * x_vars[cname])

model += pulp.lpSum(total_score_expr), "Maximize_Personal_Score"

# ============================
# CONSTRAINTS FOR 10 TOTAL COURSES
# ============================
# We want exactly 10 total courses, no matter which specialization is chosen.
# Because S_II + S_CS = 1, we can do:
#    sum(x_c) = 10 * (S_II + S_CS) => sum(x_c) = 10
model += (pulp.lpSum([x_vars[c] for c in x_vars]) == 10, "Total_of_10_courses")

# ============================
# INTERACTIVE INTELLIGENCE CONSTRAINTS
# ============================
# For the Interactive Intelligence specialization (S_II=1) we have:
#   1) 3 "Core" courses: 
#      (A) One from {CS 6300, CS 6515}
#      (B) Two from {CS 6601, CS 7637, CS 7641}
#   2) 2 "Electives" from these sets combined:
#      Interaction: {CS 6440, CS 6460, CS 6603, CS 6750}
#      AI Methods: {CS 6476, CS 7632, CS 7643, CS 7650}
#      Cognition:  {CS 6795}
#      => total of 2 across all of them
#   3) The rest (5) are "Free Electives" from anywhere (since we want a total of 10).
# But we enforce the official rule: "At least 1 from (6300,6515), at least 2 from (6601,7637,7641),
# and at least 2 from (the union of all those electives)."

ii_alg_design    = {"CS-6300", "CS-6515"} 
ii_core_ai       = {"CS-6601", "CS-7637", "CS-7641"}
ii_interaction   = {"CS-6440", "CS-6460", "CS-6603", "CS-6750"}
ii_ai_methods    = {"CS-6476", "CS-7632", "CS-7643", "CS-7650"}
ii_cognition     = {"CS-6795"}

# (A) At least 1 from {6300,6515}
model += (pulp.lpSum(x_vars[c] for c in ii_alg_design if c in x_vars) >= 1 * S_II), "II_alg_design"

# (B) At least 2 from {6601,7637,7641}
model += (pulp.lpSum(x_vars[c] for c in ii_core_ai if c in x_vars) >= 2 * S_II), "II_core_ai"

# (C) At least 2 from (ii_interaction U ii_ai_methods U ii_cognition)
ii_electives_union = (ii_interaction | ii_ai_methods | ii_cognition)
model += (pulp.lpSum(x_vars[c] for c in ii_electives_union if c in x_vars) >= 2 * S_II), "II_electives"

# ============================
# COMPUTING SYSTEMS CONSTRAINTS
# ============================
# For the Computing Systems specialization (S_CS=1) we have:
# 1) 3 "Core" courses total:
#    - Must take CS 6515
#    - Pick 2 from {CS 6210, CS 6250, CS 6290, CS 6300, CS 6301, CS 6400}
#      (note GT says "CS6300 or CS6301" but we’ll treat them as a 2-element set so the solver
#       can pick either or both if it wants, which is still valid.)
# 2) 3 "Electives" from:
#    {CS 6035, CS 6200, CS 6238, CS 6260, CS 6262, CS 6263, CS 6291, CS 6310, CS 6340,
#     CS 6422, CS 6675, CS 7210, CS 7280, CSE 6220,
#     plus any SCS-taught special topics: CS 6211, CS 6264, CS 7400, CS 8803-O08}
# 3) The rest (4) are free electives => total of 10.

cs_core_alg_required = {"CS-6515"}
cs_core_pick2 = {
    "CS-6210", "CS-6250", "CS-6290", "CS-6300", "CS-6301", "CS-6400"
}

cs_electives = {
    "CS-6035", "CS-6200", "CS-6238", "CS-6260", "CS-6262", "CS-6263", "CS-6291",
    "CS-6310", "CS-6340", "CS-6422", "CS-6675", "CS-7210", "CS-7280", "CSE-6220",
    "CS-6211", "CS-6264", "CS-7400", "CS-8803-O08"
}

# (1a) Must pick CS6515 if S_CS=1
model += (pulp.lpSum(x_vars[c] for c in cs_core_alg_required if c in x_vars) >= 1 * S_CS), "CS_must_have_6515"

# (1b) At least 2 from the second core set
model += (pulp.lpSum(x_vars[c] for c in cs_core_pick2 if c in x_vars) >= 2 * S_CS), "CS_core_pick2"

# (2) At least 3 from the electives set
model += (pulp.lpSum(x_vars[c] for c in cs_electives if c in x_vars) >= 3 * S_CS), "CS_electives_pick3"

# ============================
# SOLVE THE MODEL
# ============================
solution = model.solve(pulp.PULP_CBC_CMD(msg=0))  # set msg=1 if you want solver details
print(f"Solver status: {pulp.LpStatus[solution]}")

if pulp.LpStatus[solution] == "Optimal":
    # Show objective value
    print(f"Objective (Max Score) = {pulp.value(model.objective):.2f}")
    
    # Which specialization was chosen?
    if pulp.value(S_II) > 0.5:
        chosen_specialization = "Interactive Intelligence"
    else:
        chosen_specialization = "Computing Systems"
    print(f"Chosen Specialization: {chosen_specialization}")
    
    # Which courses are chosen?
    chosen_courses = []
    for c in courses_data:
        cname = c["codes"]
        if pulp.value(x_vars[cname]) > 0.5:
            chosen_courses.append(c["courseName"])
    
    print("Courses to take (10 total):")
    for course_name in chosen_courses:
        print("  -", course_name)

else:
    print("No optimal solution found.")
