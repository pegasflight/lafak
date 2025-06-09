
import streamlit as st
import pandas as pd

# Load the programs table (replace with your actual file path)
@st.cache_data
def load_programs():
    return pd.read_excel('TABAN_2024_with_RIASEC.xlsx')

# Branch weights (as previously defined)
branch_weights = """S,M,MT,ECO,PHILO,LANG,ART
Arabic Language,3,3,2,3,6,5,4
French Language,2,2,2,2,3,5,2
English Language,2,2,2,2,3,5,2
Islamic Sciences,2,2,2,2,2,2,2
History & Geography,2,2,2,4,4,3,2
Mathematics,5,7,6,5,2,2,2
Nature & Life Sciences,6,2,-,-,-,-,2
Physics,5,6,6,-,-,-,2
Philosophy,2,2,2,2,6,2,2
Sports,1,1,1,1,1,1,1
Engineering Subject,-,-,7,-,-,-,-
Economy & Management,-,-,-,5,-,-,-
Law,-,-,-,2,-,-,-
Accounting and Financial Management,-,-,-,6,-,-,-
Foreign Language,-,-,-,-,-,4,-
Amazigh Language,-,-,-,-,-,-,2
Art Subject 1,-,-,-,-,-,-,5
Art Subject 2,-,-,-,-,-,-,5"""

branch_weights_df = pd.read_csv(pd.compat.StringIO(branch_weights))
branch_weights_df = branch_weights_df.set_index(branch_weights_df.columns[0])

branch_options = branch_weights_df.columns.tolist()

# Helper: get subjects for a branch
def get_subjects_for_branch(branch):
    subjects = branch_weights_df[branch]
    return [s for s in subjects.index if subjects[s] != '-' and pd.notnull(subjects[s])]

# Helper: get weights for a branch
def get_weights_for_branch(branch):
    return branch_weights_df[branch].replace('-', 0).astype(float).to_dict()

# BAC average calculation
def calculate_bac_average(branch, subject_scores):
    weights = get_weights_for_branch(branch)
    total = 0
    total_weights = 0
    for subject, score in subject_scores.items():
        if score is not None:
            total += score * weights.get(subject, 0)
            total_weights += weights.get(subject, 0)
    if total_weights == 0:
        return None
    return round(total / total_weights, 2)

# PON calculation (as before)
def calculate_pon(branch, subject_scores, bac_avg):
    pon = {}
    if branch in ['S', 'M']:
        pon['PON S'] = round(((bac_avg * 2) + subject_scores.get('Nature & Life Sciences', 0)) / 3, 2)
    elif branch == 'MT':
        pon['PON S'] = bac_avg
    if branch in ['S', 'M', 'MT']:
        math_score = subject_scores.get('Mathematics', 0)
        physics_score = subject_scores.get('Physics', 0)
        pon['PON ST'] = round(((bac_avg * 2) + ((math_score + physics_score) / 2)) / 3, 2)
    if branch == 'MT':
        math_score = subject_scores.get('Mathematics', 0)
        eng_score = subject_scores.get('Engineering Subject', 0)
        pon['PON MT'] = round(((bac_avg * 2) + ((math_score + eng_score) / 2)) / 3, 2)
    if branch in ['S', 'M', 'MT']:
        math_score = subject_scores.get('Mathematics', 0)
        pon['PON MI'] = round(((bac_avg * 2) + math_score) / 3, 2)
    if branch in ['S', 'M', 'MT']:
        math_score = subject_scores.get('Mathematics', 0)
        physics_score = subject_scores.get('Physics', 0)
        pon['PON ARCHI'] = round(((bac_avg * 2) + ((math_score + physics_score) / 2)) / 3, 2)
    if branch in ['PHILO', 'LANG']:
        lang_scores = [subject_scores.get('Arabic Language', 0), subject_scores.get('French Language', 0), subject_scores.get('English Language', 0)]
        pon['PON LLE'] = round(((bac_avg * 2) + (sum(lang_scores) / 3)) / 3, 2)
    if branch in ['LANG', 'PHILO', 'ECO', 'S', 'ART']:
        pon['PON FR'] = round(((bac_avg * 2) + subject_scores.get('French Language', 0)) / 3, 2)
        pon['PON EN'] = round(((bac_avg * 2) + subject_scores.get('English Language', 0)) / 3, 2)
    if branch == 'LANG':
        pon['PON AL/ES'] = round(((bac_avg * 2) + subject_scores.get('Foreign Language', 0)) / 3, 2)
    elif branch in ['PHILO', 'ECO', 'S', 'ART']:
        pon['PON AL/ES'] = bac_avg
    return pon

# Streamlit UI
st.title('Algerian University Program Eligibility Advisor')

st.write('Select your high school branch and enter your subject scores:')
branch = st.selectbox('High School Branch', branch_options)
subjects = get_subjects_for_branch(branch)

subject_scores = {}
for subject in subjects:
    score = st.number_input(subject + ' score', min_value=0.0, max_value=20.0, step=0.01, format='%0.2f')
    subject_scores[subject] = score

if st.button('Calculate Eligibility'):
    bac_avg = calculate_bac_average(branch, subject_scores)
    st.write('**Your BAC General Average:**', bac_avg)
    pon = calculate_pon(branch, subject_scores, bac_avg)
    st.write('**Your Weighted Averages (PONs):**')
    st.dataframe(pd.DataFrame(list(pon.items()), columns=['PON', 'Value']))
    # Load programs
    df = load_programs()
    # Filtering logic (simplified):
    eligible_programs = []
    for idx, row in df.iterrows():
        # Check branch eligibility (priority columns)
        priorities = str(row.get('Priorite', ''))
        if branch not in priorities:
            continue
        # Determine which average to use
        moyen_type = str(row.get('Moyen Classement', 'BAC')).strip().upper()
        if moyen_type == 'BAC':
            avg = bac_avg
        else:
            avg = pon.get(moyen_type, None)
        # Check minimum required average
        min1 = row.get('Min1', 0)
        try:
            min1 = float(min1)
        except:
            min1 = 0
        if avg is not None and avg >= min1:
            eligible_programs.append(row)
    if eligible_programs:
        st.write('**Eligible University Programs:**')
        st.dataframe(pd.DataFrame(eligible_programs))
    else:
        st.write('No eligible programs found for your profile.')
